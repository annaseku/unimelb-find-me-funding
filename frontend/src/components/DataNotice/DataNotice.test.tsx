import { render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import DataNotice from './DataNotice';
import type { DataStatus } from '../../types/funding';

const run = { finished_at: '2026-10-18T09:05:00Z', llm_calls: 5, llm_failures: 1, llm_stop_reason: null, llm_stop_detail: '' };
const status = (overrides: Partial<DataStatus> = {}): DataStatus => ({ last_run: run, opportunities: 164, rule_only_summaries: 0, ...overrides });
const serve = (body: DataStatus | null, ok = true) => vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok, json: async () => body }));
afterEach(() => vi.unstubAllGlobals());

it('warns when the last refresh hit the daily plan limit, with how many summaries are rule-built', async () => {
  serve(status({ last_run: { ...run, llm_stop_reason: 'daily_quota' }, rule_only_summaries: 159 }));
  render(<DataNotice />);
  const note = await screen.findByRole('note');
  expect(note).toHaveTextContent("daily request limit was reached during the last data refresh (18 Oct 2026)");
  expect(note).toHaveTextContent('159 of 164 opportunities show a shorter automatic summary');
});
it('names a rejected key or plan', async () => {
  serve(status({ last_run: { ...run, llm_stop_reason: 'plan_error', llm_stop_detail: '403 PERMISSION_DENIED' } }));
  render(<DataNotice />);
  expect(await screen.findByRole('note')).toHaveTextContent('Gemini rejected the API key or plan during the last data refresh (403 PERMISSION_DENIED)');
});
it('says when refreshes run without a Gemini key', async () => {
  serve(status({ last_run: { ...run, llm_stop_reason: 'not_configured' } }));
  render(<DataNotice />);
  expect(await screen.findByRole('note')).toHaveTextContent('without a Gemini API key');
});
it('shows nothing when every summary came from the AI', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => status() });
  vi.stubGlobal('fetch', fetch);
  render(<DataNotice />);
  await vi.waitFor(() => expect(fetch).toHaveBeenCalled());
  expect(screen.queryByRole('note')).not.toBeInTheDocument();
});
it('stays hidden when the status endpoint fails', async () => {
  const fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
  vi.stubGlobal('fetch', fetch);
  render(<DataNotice />);
  await vi.waitFor(() => expect(fetch).toHaveBeenCalled());
  expect(screen.queryByRole('note')).not.toBeInTheDocument();
});
