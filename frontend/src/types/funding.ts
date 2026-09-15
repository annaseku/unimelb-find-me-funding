export type EmployerType = 'university' | 'research_institute' | 'industry' | 'philanthropic';
export type CareerStage = 'undergraduate' | 'graduate_student' | 'postdoc_0_2' | 'postdoc_2_5' | 'postdoc_5_10' | 'postdoc_10_plus';
export type FundingType = 'salary' | 'consumables' | 'equipment' | 'all' | 'any';
export interface Opportunity {
  id: string; title: string; funder: string; url: string; source_urls: string[];
  summary: string; amount_aud: number | null; amount_note: string;
  deadline: string | null; opens_at: string | null; countries: string[];
  citizenships_allowed: string[]; employer_types_allowed: EmployerType[];
  career_stages_allowed: CareerStage[]; funding_types_offered: FundingType[];
  for_codes: string[]; toa_codes: string[]; keywords: string[];
  eligibility_text: string; status: 'active' | 'closed';
}
export interface CriterionResult { score: number; label: string; reasons: string[] }
export const criteria = {
  eligibility: 'Eligibility', research_match: 'Research match',
  funding_value: 'Funding value', deadline: 'Time to deadline',
} as const;
export type CriterionKey = keyof typeof criteria;
export type RankedOpportunity = { opportunity: Opportunity; overall: number } & Record<CriterionKey, CriterionResult>;
export interface SearchResultsResponse {
  results: RankedOpportunity[]; total: number; limit: number; offset: number;
  weights: Record<CriterionKey, number>;
}
export interface SearchRequest {
  for_codes: string[]; toa_codes: string[]; citizenships: string[];
  employer_type: EmployerType | null; career_stage: CareerStage | null;
  funding_types: FundingType[]; research_description: string;
  hide_ineligible: boolean; include_closed: boolean; limit: number; offset: number;
}
