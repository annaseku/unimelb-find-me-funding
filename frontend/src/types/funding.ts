export type EmployerType = 'university' | 'research_institute' | 'industry' | 'philanthropic';
export type CareerStage =
  | 'undergraduate'
  | 'graduate_student'
  | 'postdoc_0_2'
  | 'postdoc_2_5'
  | 'postdoc_5_10'
  | 'postdoc_10_plus';
export type FundingType = 'salary' | 'consumables' | 'equipment' | 'all' | 'any';
export type EligibilityState =
  'eligible' | 'potentially_eligible' | 'unknown' | 'likely_ineligible';
export type MatchLevel = 'high' | 'medium' | 'low';
export type DeadlineBand =
  'over_60_days' | 'days_60_to_30' | 'days_30_to_15' | 'under_15_days' | 'closed' | 'unknown';
export type FundingBand = 'under_1m' | 'from_1m_to_2m' | 'from_2m_to_5m' | 'over_5m' | 'unknown';

export const eligibilityLabels: Record<EligibilityState, string> = {
  eligible: 'Eligible',
  potentially_eligible: 'Potentially eligible',
  unknown: 'Unknown',
  likely_ineligible: 'Likely ineligible',
};

export const matchLabels: Record<MatchLevel, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
};

export const deadlineLabels: Record<DeadlineBand, string> = {
  over_60_days: 'Over 60 days',
  days_60_to_30: '30–60 days',
  days_30_to_15: '15–30 days',
  under_15_days: 'Under 15 days',
  closed: 'Closed',
  unknown: 'Unknown',
};

export const fundingLabels: Record<FundingBand, string> = {
  under_1m: 'Under $1M',
  from_1m_to_2m: '$1M–$2M',
  from_2m_to_5m: '$2M–$5M',
  over_5m: 'Over $5M',
  unknown: 'Unknown',
};

export interface Opportunity {
  id: string;
  title: string;
  funder: string;
  url: string;
  source_urls: string[];
  summary: string;
  amount_aud: number | null;
  amount_note: string;
  deadline: string | null;
  opens_at: string | null;
  countries: string[];
  citizenships_allowed: string[];
  employer_types_allowed: EmployerType[];
  career_stages_allowed: CareerStage[];
  funding_types_offered: FundingType[];
  for_codes: string[];
  toa_codes: string[];
  keywords: string[];
  eligibility_text: string;
  status: 'active' | 'closed';
}

export interface CriterionResult {
  score: number;
  label: string;
  reasons: string[];
}

export const criteria = {
  eligibility: 'Eligibility',
  research_match: 'Research match',
  funding_value: 'Funding value',
  deadline: 'Time to deadline',
} as const;

export type CriterionKey = keyof typeof criteria;

export interface RankedOpportunity {
  opportunity: Opportunity;
  overall: number;
  eligibility: CriterionResult;
  research_match: CriterionResult;
  funding_value: CriterionResult;
  deadline: CriterionResult;
}

export type LlmStopReason = 'daily_quota' | 'plan_error' | 'not_configured';

export interface PipelineRun {
  finished_at: string;
  llm_calls: number;
  llm_failures: number;
  llm_stop_reason: LlmStopReason | null;
  llm_stop_detail: string;
}

export interface DataStatus {
  last_run: PipelineRun | null;
  opportunities: number;
  rule_only_summaries: number;
}

export interface SearchResponse {
  results: RankedOpportunity[];
  total: number;
  limit: number;
  offset: number;
  weights: Record<string, number>;
}

export interface SearchRequest {
  for_codes: string[];
  toa_codes: string[];
  citizenships: string[];
  employer_type: EmployerType | null;
  career_stage: CareerStage | null;
  funding_types: FundingType[];
  research_description: string;
  hide_ineligible: boolean;
  include_closed: boolean;
  limit: number;
  offset: number;
  weights?: Record<string, number> | null;
}
