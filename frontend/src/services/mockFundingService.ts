import type { SearchResultsResponse } from '../types/funding';
import { defaultFilterValues } from '../data/filterOptions';

export async function fetchMockResults(
  search = '',
  filters: typeof defaultFilterValues = defaultFilterValues,
): Promise<SearchResultsResponse> {
  const mockResults = [
    {
      url: 'https://example.org/fund/1',
      title: 'Early Career Research Grant',
      raw_text:
        'Funding for early career marine biology researchers working on coastal ecosystem resilience and biodiversity adaptation projects.',
      deadline_raw: '31 October 2026',
      deadline_parsed: '2026-10-31',
      funding_amount_raw: 'AUD 500,000',
      eligibility_snippet:
        'Open to postdoctoral researchers based in Australia who are conducting marine systems research.',
      source_query: 'marine biology research grant',
      fetched_at: '2026-09-06T00:00:00Z',
    },
    {
      url: 'https://example.org/fund/2',
      title: 'Climate and Ocean Research Fellowship',
      raw_text:
        'Fellowship funding for interdisciplinary climate science projects investigating ocean acidification and coral reef resilience.',
      deadline_raw: '15 September 2026',
      deadline_parsed: '2026-09-15',
      funding_amount_raw: 'AUD 1,200,000',
      eligibility_snippet:
        'Applicants must be early career researchers with evidence of marine ecosystem research experience.',
      source_query: 'marine biology research fellowship',
      fetched_at: '2026-09-06T00:00:00Z',
    },
    {
      url: 'https://example.org/fund/3',
      title: 'Computer Science Research Infrastructure Grant',
      raw_text:
        'Funding for computer science teams building data-intensive research infrastructure, machine learning systems, and computational modelling tools.',
      deadline_raw: '12 November 2026',
      deadline_parsed: '2026-11-12',
      funding_amount_raw: 'AUD 750,000',
      eligibility_snippet:
        'Open to university-based computer science research groups and interdisciplinary teams with computational methods.',
      source_query: 'computer science funding opportunity',
      fetched_at: '2026-09-06T00:00:00Z',
    },
  ];

  const normalizedSearch = search.trim().toLowerCase();
  const activeFilters = Object.entries(filters).filter(([, value]) => !!value && value !== 'Any');

  const filteredResults = mockResults.filter((result) => {
    const haystack = `${result.title} ${result.raw_text} ${result.eligibility_snippet ?? ''}`.toLowerCase();

    const matchesSearch = !normalizedSearch || haystack.includes(normalizedSearch);
    const matchesFilters = activeFilters.every(([key, value]) => {
      const lowerValue = value.toLowerCase();

      switch (key) {
        case 'fieldOfResearch':
          return haystack.includes(lowerValue) || result.source_query?.toLowerCase().includes(lowerValue) || false;
        case 'typeOfActivity':
          return haystack.includes(lowerValue) || result.source_query?.toLowerCase().includes(lowerValue) || false;
        case 'careerStage':
          return haystack.includes(lowerValue) || result.eligibility_snippet?.toLowerCase().includes(lowerValue) || false;
        case 'fundingType':
          return haystack.includes(lowerValue) || result.title.toLowerCase().includes(lowerValue) || false;
        case 'citizenship':
          return true;
        case 'employerType':
          return true;
        default:
          return true;
      }
    });

    return matchesSearch && matchesFilters;
  });

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        results: filteredResults,
        total: filteredResults.length,
      });
    }, 300);
  });
}
