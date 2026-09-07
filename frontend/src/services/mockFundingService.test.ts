import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchMockResults } from './mockFundingService';
import { defaultFilterValues } from '../data/filterOptions';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

async function resolveFetch(search?: string, filters?: typeof defaultFilterValues) {
  const promise = fetchMockResults(search, filters);
  await vi.advanceTimersByTimeAsync(300);
  return promise;
}

describe('fetchMockResults', () => {
  it('returns all three results with no search and default filters', async () => {
    const response = await resolveFetch();

    expect(response.total).toBe(3);
    expect(response.results).toHaveLength(3);
  });

  it('returns only the matching opportunity when searching "coral"', async () => {
    const response = await resolveFetch('coral');

    expect(response.results).toHaveLength(1);
    expect(response.results[0].title).toBe('Climate and Ocean Research Fellowship');
  });

  it('is case-insensitive and trims whitespace from the search term', async () => {
    const response = await resolveFetch('  CORAL  ');

    expect(response.results).toHaveLength(1);
    expect(response.results[0].title).toBe('Climate and Ocean Research Fellowship');
  });

  it('returns an empty result set when the search matches nothing', async () => {
    const response = await resolveFetch('nonexistent funding topic xyz');

    expect(response.results).toEqual([]);
    expect(response.total).toBe(0);
  });

  it('filters by fieldOfResearch, matching against source_query as well as visible text', async () => {
    const response = await resolveFetch('', { ...defaultFilterValues, fieldOfResearch: 'Computer Science' });

    expect(response.results).toHaveLength(1);
    expect(response.results[0].title).toBe('Computer Science Research Infrastructure Grant');
  });

  it('ignores the literal value "Any" as an active filter', async () => {
    const response = await resolveFetch('', { ...defaultFilterValues, citizenship: 'Any' });

    expect(response.total).toBe(3);
  });

  it('does not yet apply the citizenship and employerType filters to results (current behaviour, not a goal)', async () => {
    const response = await resolveFetch('', { ...defaultFilterValues, employerType: 'Hospital' });

    expect(response.total).toBe(3);
  });

  it('keeps the FundingOpportunity shape on every result', async () => {
    const response = await resolveFetch();

    for (const result of response.results) {
      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('title');
      expect(result).toHaveProperty('raw_text');
    }
  });
});
