import type { RankedOpportunity, SearchResponse } from '../types/funding';
export const ranked: RankedOpportunity = {
  opportunity: { id: 'arc', title: 'ARC Research Grant', funder: 'ARC', url: 'https://www.arc.gov.au/',
    source_urls: [], summary: 'Research funding', amount_aud: null, amount_note: 'Varies by project',
    deadline: null, opens_at: null, countries: [], citizenships_allowed: [], employer_types_allowed: [],
    career_stages_allowed: [], funding_types_offered: [], for_codes: [], toa_codes: [], keywords: [],
    eligibility_text: '', status: 'active' }, overall: 0.8,
  eligibility: { score: 0.5, label: 'potentially_eligible', reasons: ['Check the funder eligibility rules.'] },
  research_match: { score: 1, label: 'high', reasons: ['Matches your field of research.'] },
  funding_value: { score: 0.5, label: 'unknown', reasons: ['Funding amount not stated.'] },
  deadline: { score: 1, label: 'over_60_days', reasons: ['More than 60 days remaining.'] },
};
export const page: SearchResponse = { results: [ranked], total: 1, limit: 10, offset: 0,
  weights: { eligibility: 0.4, research_match: 0.3, funding_value: 0.15, deadline: 0.15 } };
