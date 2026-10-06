import type {
  BackendSearchRequest,
  RankedOpportunity,
  SearchFilters,
  SearchResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

function toBackendRequest(filters: SearchFilters): BackendSearchRequest {
  const citizenship = filters.citizenship.trim().toUpperCase();
  const hasCitizenship = citizenship && citizenship !== 'ANY';
  const hasEmployerType = filters.employerType && filters.employerType !== 'Any';
  const hasFundingType = filters.fundingType && filters.fundingType !== 'Any';

  return {
    for_codes: filters.fieldOfResearch.trim() ? [filters.fieldOfResearch.trim()] : [],
    toa_codes: filters.typeOfActivity.trim() ? [filters.typeOfActivity.trim()] : [],
    citizenships: hasCitizenship ? [citizenship] : [],
    ...(hasEmployerType ? { employer_type: filters.employerType } : {}),
    ...(filters.careerStage ? { career_stage: filters.careerStage } : {}),
    funding_types: hasFundingType ? [filters.fundingType] : [],
    research_description: filters.description.trim(),
    limit: 10,
    offset: 0,
  };
}

export async function searchFunding(filters: SearchFilters): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(toBackendRequest(filters)),
  });

  if (!response.ok) {
    throw new Error(`Search failed with status ${response.status}`);
  }

  return response.json() as Promise<SearchResponse>;
}

export function formatRankedOpportunity(result: RankedOpportunity) {
  const amount = result.opportunity.amount_aud
    ? `$${result.opportunity.amount_aud.toLocaleString()} AUD`
    : result.opportunity.amount_note || 'Amount not specified';
  const deadline = result.opportunity.deadline
    ? `Deadline: ${result.opportunity.deadline}`
    : 'Deadline not specified';

  return {
    title: result.opportunity.title,
    description: result.opportunity.summary,
    fundingAmount: amount,
    deadline,
    matchScore: result.research_match.label,
    eligibility: result.eligibility.label,
    url: result.opportunity.url,
    funder: result.opportunity.funder,
  };
}