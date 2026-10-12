export type SearchFilters = {
  fieldOfResearch: string;
  typeOfActivity: string;
  citizenship: string;
  employerType: string;
  careerStage: string;
  fundingType: string;
  description: string;
};

export type FrontendFilters = Omit<SearchFilters, 'description'>;

export type BackendSearchRequest = {
  for_codes: string[];
  toa_codes: string[];
  citizenships: string[];
  employer_type?: string;
  career_stage?: string;
  funding_types: string[];
  research_description: string;
  limit: number;
  offset: number;
};

export type CriterionResult = {
  score: number;
  label: string;
  reasons: string[];
};

export type BackendOpportunity = {
  id: string;
  title: string;
  funder: string;
  url: string;
  summary: string;
  amount_aud: number | null;
  amount_note: string;
  deadline: string | null;
  status: string;
};

export type RankedOpportunity = {
  opportunity: BackendOpportunity;
  overall: number;
  eligibility: CriterionResult;
  research_match: CriterionResult;
  funding_value: CriterionResult;
  deadline: CriterionResult;
};

export type SearchResponse = {
  results: RankedOpportunity[];
  total: number;
  limit: number;
  offset: number;
  weights: Record<string, number>;
};

export type FilterOptionSet = Record<string, string[]>;
