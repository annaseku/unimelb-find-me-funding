import { afterEach, expect, it, vi } from 'vitest';
import { buildSearchRequest, fetchResults } from './fundingService';
import { defaultFilterValues } from '../data/filterOptions';
import { page } from '../test/fundingFixture';
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.resetModules();
});
it('sends backend codes, pagination and default visibility rules as JSON', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => page });
  vi.stubGlobal('fetch', fetch);
  await fetchResults(
    ' coral ',
    {
      fieldOfResearch: ['3103', '31'],
      typeOfActivity: '3',
      citizenship: ['AU'],
      employerType: 'research_institute',
      careerStage: 'postdoc_2_5',
      fundingType: 'equipment',
    },
    10,
  );
  expect(fetch).toHaveBeenCalledWith(
    'https://find-me-funding-api.onrender.com/api/search',
    expect.objectContaining({ method: 'POST' }),
  );
  expect(JSON.parse(fetch.mock.calls[0]?.[1].body)).toEqual({
    research_description: 'coral',
    for_codes: ['3103', '31'],
    toa_codes: ['3'],
    citizenships: ['AU'],
    employer_type: 'research_institute',
    career_stage: 'postdoc_2_5',
    funding_types: ['equipment'],
    limit: 10,
    offset: 10,
    include_closed: false,
    hide_ineligible: false,
  });
});
it('rejects a selection that is no longer an option, including a stale citizenship code', () => {
  expect(() =>
    buildSearchRequest('', { ...defaultFilterValues, fieldOfResearch: ['3103', '99'] }),
  ).toThrow(/no longer available/);
  expect(() =>
    buildSearchRequest('', { ...defaultFilterValues, citizenship: ['AU', 'XX'] }),
  ).toThrow(/no longer available/);
  expect(() =>
    buildSearchRequest('', {
      ...defaultFilterValues,
      fieldOfResearch: ['3103', '31'],
      citizenship: ['AU', 'NZ'],
    }),
  ).not.toThrow();
});
it('leaves unselected filters unrestricted', () => {
  expect(buildSearchRequest('', defaultFilterValues)).toMatchObject({
    employer_type: null,
    career_stage: null,
    for_codes: [],
    citizenships: [],
    funding_types: [],
  });
});
it.each([422, 500])('reports HTTP %s without showing mock data', async (status) => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status }));
  await expect(fetchResults('', defaultFilterValues)).rejects.toThrow(
    status === 422 ? /not accepted/ : /unavailable/,
  );
});
it('reports a timeout when the service takes too long, but not a caller cancelling', async () => {
  const timeout = new AbortController();
  vi.spyOn(AbortSignal, 'timeout').mockReturnValue(timeout.signal);
  const fetch = vi.fn().mockImplementation(() => {
    timeout.abort();
    return Promise.reject(new DOMException('The operation timed out.', 'TimeoutError'));
  });
  vi.stubGlobal('fetch', fetch);
  await expect(fetchResults('', defaultFilterValues)).rejects.toThrow(
    'The funding service took too long to respond. Please try again.',
  );

  const caller = new AbortController();
  caller.abort();
  await expect(fetchResults('', defaultFilterValues, 0, caller.signal)).rejects.not.toThrow(
    /took too long/,
  );
});
it('reports connection failures', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
  await expect(fetchResults('', defaultFilterValues)).rejects.toThrow(/connection/);
});
it('uses the configured base URL without duplicating slashes', async () => {
  vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000/');
  vi.resetModules();
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => page });
  vi.stubGlobal('fetch', fetch);
  const service = await import('./fundingService');
  await service.fetchResults('', defaultFilterValues);
  expect(fetch.mock.calls[0]?.[0]).toBe('http://localhost:8000/api/search');
});
