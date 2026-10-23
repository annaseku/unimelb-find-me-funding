import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import Results from './Results';
import { page, ranked } from '../../test/fundingFixture';
import { defaultFilterValues } from '../../data/filterOptions';
// DataNotice makes its own status request and has its own tests; here it only counts mounts.
const notice = vi.hoisted(() => ({ mounts: 0 }));
vi.mock('../../components/DataNotice/DataNotice', async () => {
  const { useEffect } = await import('react');
  return {
    default: function DataNotice() {
      useEffect(() => {
        notice.mounts += 1;
      }, []);
      return null;
    },
  };
});
const fetchMock = vi.fn();
const response = (body = page) => ({ ok: true, json: async () => body });
beforeEach(() => {
  notice.mounts = 0;
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(() => vi.unstubAllGlobals());
function show(
  state: unknown = {
    search: 'coral',
    filters: { ...defaultFilterValues, fieldOfResearch: '31' },
  },
) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/results', state }]}>
      <Results />
    </MemoryRouter>,
  );
}
it('explains cold starts and shows the total from the server, not the page count', async () => {
  fetchMock.mockResolvedValue(response({ ...page, total: 27 }));
  show();
  expect(screen.getByRole('status')).toHaveTextContent('first search can take about a minute');
  await screen.findByText('27 Results Found');
  expect(
    screen.getByRole('button', { name: 'Field of Research Biological Sciences' }),
  ).toBeInTheDocument();
  expect(screen.getByText('ARC Research Grant')).toBeInTheDocument();
});
it('appends pages using the submitted filters, then resets on a new search', async () => {
  const user = userEvent.setup();
  fetchMock
    .mockResolvedValueOnce(response({ ...page, total: 2 }))
    .mockResolvedValueOnce(
      response({
        ...page,
        total: 2,
        offset: 1,
        results: [
          {
            ...ranked,
            opportunity: { ...ranked.opportunity, id: 'wellcome', title: 'Wellcome Grant' },
          },
        ],
      }),
    )
    .mockResolvedValueOnce(response({ ...page, results: [], total: 0 }));
  show();
  await screen.findByText('2 Results Found');
  await user.clear(screen.getByPlaceholderText('Search by keyword'));
  await user.type(screen.getByPlaceholderText('Search by keyword'), 'new research');
  await user.click(screen.getByRole('button', { name: 'Field of Research Biological Sciences' }));
  await user.click(screen.getByRole('button', { name: /31\s*Biological Sciences/i }));
  await user.click(screen.getByRole('button', { name: 'Show more' }));
  await screen.findByText('Wellcome Grant');
  expect(screen.getByText('ARC Research Grant')).toBeInTheDocument();
  expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toMatchObject({
    offset: 1,
    research_description: 'coral',
    for_codes: ['31'],
  });
  expect(screen.queryByRole('button', { name: 'Show more' })).not.toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Search' }));
  await screen.findByText('0 Results Found');
  expect(JSON.parse(fetchMock.mock.calls[2][1].body)).toMatchObject({
    offset: 0,
    research_description: 'new research',
    for_codes: ['31'],
  });
  expect(screen.queryByText('ARC Research Grant')).not.toBeInTheDocument();
});
it('shows an error and lets the researcher retry', async () => {
  const user = userEvent.setup();
  fetchMock.mockRejectedValueOnce(new TypeError('offline')).mockResolvedValueOnce(response());
  show();
  expect(await screen.findByRole('alert')).toHaveTextContent('connection');
  await user.click(screen.getByRole('button', { name: 'Try again' }));
  await screen.findByText('ARC Research Grant');
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});
it('ignores a stale response when a newer search has completed', async () => {
  let finish!: (value: ReturnType<typeof response>) => void;
  fetchMock
    .mockReturnValueOnce(
      new Promise((resolve) => {
        finish = resolve;
      }),
    )
    .mockResolvedValueOnce(response({ ...page, total: 0, results: [] }));
  const user = userEvent.setup();
  show();
  await user.click(screen.getByRole('button', { name: 'Search' }));
  await screen.findByText('0 Results Found');
  await act(async () => {
    finish(response());
  });
  expect(screen.queryByText('ARC Research Grant')).not.toBeInTheDocument();
  expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
});
it('aborts an in-flight request on unmount', () => {
  fetchMock.mockReturnValue(new Promise(() => {}));
  const view = show();
  view.unmount();
  expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
});
it('ignores router state of the wrong shape instead of sending it to the API', async () => {
  fetchMock.mockResolvedValue(response());
  show({ search: 42, filters: { citizenship: 'AU', careerStage: ['undergraduate'] } });
  await screen.findByText('ARC Research Grant');
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toMatchObject({
    research_description: '',
    citizenships: [],
    career_stage: null,
  });
});
it('says "Result" for a single result', async () => {
  fetchMock.mockResolvedValue(response());
  show();
  expect(await screen.findByText('1 Result Found')).toBeInTheDocument();
});
it('lists only the ranking weights the API sent as numbers', async () => {
  fetchMock.mockResolvedValue(
    response({ ...page, weights: { eligibility: 0.5, research_match: null } as never }),
  );
  show();
  await screen.findByText('ARC Research Grant');
  expect(screen.getByText('Eligibility: 50%')).toBeInTheDocument();
  expect(screen.queryByText(/NaN/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Research match:/)).not.toBeInTheDocument();
});
it('mentions the cold start only before the first search succeeds', async () => {
  const user = userEvent.setup();
  fetchMock
    .mockResolvedValueOnce(response({ ...page, total: 2 }))
    .mockReturnValueOnce(new Promise(() => {}));
  show();
  expect(screen.getByRole('status')).toHaveTextContent('waking up');
  await screen.findByText('2 Results Found');

  await user.click(screen.getByRole('button', { name: 'Show more' }));
  expect(screen.getByRole('status')).toHaveTextContent('Searching for funding.');
  expect(screen.getByRole('status')).not.toHaveTextContent('waking up');
});
it('keeps one data notice across searches instead of refetching the status', async () => {
  const user = userEvent.setup();
  fetchMock.mockResolvedValue(response());
  show();
  await screen.findByText('ARC Research Grant');
  await user.click(screen.getByRole('button', { name: 'Search' }));
  await screen.findByText('ARC Research Grant');
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(notice.mounts).toBe(1);
});
