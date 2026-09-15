import { filterOptions, type FilterValues } from '../data/filterOptions';
import type { CareerStage, EmployerType, FundingType, SearchRequest, SearchResultsResponse } from '../types/funding';

const baseUrl = (import.meta.env.VITE_API_BASE_URL?.trim() || 'https://find-me-funding-api.onrender.com').replace(/\/+$/, '');
const list = (value: string) => value ? [value] : [];
export function buildSearchRequest(search: string, filters: FilterValues, offset = 0): SearchRequest {
  for (const key of Object.keys(filterOptions) as (keyof FilterValues)[]) {
    if (filters[key] && !filterOptions[key].some((option) => option.value === filters[key])) {
      throw new Error('A selected filter is no longer available. Please clear it and choose again.');
    }
  }
  return {
    research_description: search.trim(),
    for_codes: list(filters.fieldOfResearch), toa_codes: list(filters.typeOfActivity),
    citizenships: list(filters.citizenship),
    employer_type: (filters.employerType || null) as EmployerType | null,
    career_stage: (filters.careerStage || null) as CareerStage | null,
    funding_types: list(filters.fundingType) as FundingType[],
    include_closed: false, hide_ineligible: false, limit: 10, offset,
  };
}
export async function fetchResults(search: string, filters: FilterValues, offset = 0, signal?: AbortSignal): Promise<SearchResultsResponse> {
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
    return await response.json() as SearchResultsResponse;
  } catch (error) {
    if (timeout.aborted && !signal?.aborted) throw new Error('The funding service took too long to respond. Please try again.', { cause: error });
    if (error instanceof TypeError) throw new Error('Could not reach the funding service. Check your connection and try again.', { cause: error });
    throw error;
  }
}
