export type FundingOpportunity = {
  url: string;
  title: string;
  raw_text: string;
  deadline_raw?: string | null;
  deadline_parsed?: string | null;
  funding_amount_raw?: string | null;
  eligibility_snippet?: string | null;
  source_query?: string | null;
  fetched_at?: string | null;
};

export type SearchResultsResponse = {
  results: FundingOpportunity[];
  total: number;
};
