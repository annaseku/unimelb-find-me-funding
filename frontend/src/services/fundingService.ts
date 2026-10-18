import { filterOptions, type FilterKey, type FilterValues } from '../data/filterOptions';
import type { CareerStage, DataStatus, EmployerType, FundingType, LlmStopReason, PipelineRun, SearchRequest, SearchResponse } from '../types/funding';

const baseUrl = (import.meta.env.VITE_API_BASE_URL?.trim() || 'https://find-me-funding-api.onrender.com').replace(/\/+$/, '');
const list = (value: string) => value ? [value] : [];
// Every value a filter may hold; a selection outside it (a stale deep link, a removed option) is rejected before it reaches the API.
const knownValues: Record<FilterKey, Set<string>> = {
  fieldOfResearch: new Set(filterOptions.fieldOfResearch.flatMap((division) => [division.value, ...division.groups.map((group) => group.value)])),
  typeOfActivity: new Set(filterOptions.typeOfActivity.map((option) => option.value)),
  citizenship: new Set(filterOptions.citizenship.map((option) => option.value)),
  employerType: new Set(filterOptions.employerType.map((option) => option.value)),
  careerStage: new Set(filterOptions.careerStage.map((option) => option.value)),
  fundingType: new Set(filterOptions.fundingType.map((option) => option.value)),
};
export function buildSearchRequest(search: string, filters: FilterValues, offset = 0): SearchRequest {
  for (const key of Object.keys(knownValues) as FilterKey[]) {
    const selected = filters[key];
    const values = Array.isArray(selected) ? selected : list(selected);
    if (values.some((value) => !knownValues[key].has(value))) {
      throw new Error('A selected filter is no longer available. Please clear it and choose again.');
    }
  }
  return {
    research_description: search.trim(),
    for_codes: list(filters.fieldOfResearch), toa_codes: list(filters.typeOfActivity),
    citizenships: filters.citizenship,
    employer_type: (filters.employerType || null) as EmployerType | null,
    career_stage: (filters.careerStage || null) as CareerStage | null,
    funding_types: list(filters.fundingType) as FundingType[],
    include_closed: false, hide_ineligible: false, limit: 10, offset,
  };
}
export async function fetchResults(search: string, filters: FilterValues, offset = 0, signal?: AbortSignal): Promise<SearchResponse> {
  const timeout = AbortSignal.timeout(120_000);
  try {
    const response = await fetch(`${baseUrl}/api/search`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildSearchRequest(search, filters, offset)),
      signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
    });
    if (!response.ok) throw new Error(response.status === 422
      ? 'The search filters were not accepted. Please check your selections and try again.'
      : 'The funding service is unavailable. Please try again shortly.');
    return await response.json() as SearchResponse;
  } catch (error) {
    if (timeout.aborted && !signal?.aborted) throw new Error('The funding service took too long to respond. Please try again.', { cause: error });
    if (error instanceof TypeError) throw new Error('Could not reach the funding service. Check your connection and try again.', { cause: error });
    throw error;
  }
}
// The notice is advisory, so any failure here hides it rather than blocking the results.
export async function fetchStatus(signal?: AbortSignal): Promise<DataStatus | null> {
  try {
    const response = await fetch(`${baseUrl}/api/status`, { signal });
    return response.ok ? await response.json() as DataStatus : null;
  } catch {
    return null;
  }
}
const day = (iso: string) => new Date(iso).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
const stopMessages: Record<LlmStopReason, (run: PipelineRun) => string> = {
  daily_quota: (run) => `AI summaries are paused: the Gemini plan's daily request limit was reached during the last data refresh (${day(run.finished_at)}).`,
  plan_error: (run) => `AI summaries are unavailable: Gemini rejected the API key or plan during the last data refresh (${run.llm_stop_detail || day(run.finished_at)}).`,
  not_configured: () => 'AI summaries are off: the last data refresh ran without a Gemini API key.',
};
export function statusNotice(status: DataStatus | null): string | null {
  if (!status) return null;
  const run = status.last_run;
  const stop = run?.llm_stop_reason ? stopMessages[run.llm_stop_reason](run) : '';
  const count = status.rule_only_summaries > 0
    ? `${status.rule_only_summaries} of ${status.opportunities} opportunities show a shorter automatic summary instead of an AI one.`
    : '';
  return [stop, count].filter(Boolean).join(' ') || null;
}
