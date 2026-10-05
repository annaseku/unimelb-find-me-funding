// mutation-check: characterisation
import { expect, test, type Page } from '@playwright/test'
import type { SearchRequest, SearchResultsResponse } from '../src/types/funding'

// The API that playwright.config.ts starts; the tests ask it directly for the
// ranking they expect the UI to show.
const API = 'http://127.0.0.1:8001'

async function searchFromHome(page: Page, description: string, citizenship = '') {
  await page.goto('/')
  if (citizenship) await page.getByLabel('Citizenship').selectOption(citizenship)
  await page.getByPlaceholder('What kind of research are you searching for funding for?').fill(description)
  const sent = page.waitForRequest((request) => request.url().endsWith('/api/search'))
  await page.getByRole('button', { name: 'Search funding' }).click()
  return (await sent).postDataJSON() as SearchRequest
}

async function shownTitles(page: Page) {
  return page.getByRole('article').getByRole('heading', { level: 2 }).allTextContents()
}

test('a search from the home page shows the API ranking in order', async ({ page, request }) => {
  const sent = await searchFromHome(page, 'marine ecology', 'AU')
  expect(sent).toMatchObject({ research_description: 'marine ecology', citizenships: ['AU'], offset: 0, limit: 10 })

  const expected = await (await request.post(`${API}/api/search`, { data: sent })).json() as SearchResultsResponse
  expect(expected.total, 'the mock data set should have open opportunities').toBeGreaterThan(0)

  await expect(page.getByText(`${expected.total} Results Found`)).toBeVisible()
  expect(await shownTitles(page)).toEqual(expected.results.map((result) => result.opportunity.title))
})

test('each result explains its rating against every criterion and links out', async ({ page }) => {
  await searchFromHome(page, 'climate')
  const first = page.getByRole('article').first()
  await expect(first).toBeVisible()

  for (const criterion of ['Eligibility', 'Research match', 'Funding value', 'Time to deadline']) {
    await expect(first.getByRole('heading', { level: 3, name: criterion })).toBeVisible()
  }
  await expect(first.getByRole('link', { name: 'View opportunity' })).toHaveAttribute('href', /^https?:\/\//)
})

test('show more appends the next page of results', async ({ page, request }) => {
  const sent = await searchFromHome(page, 'research')
  const firstPage = await (await request.post(`${API}/api/search`, { data: sent })).json() as SearchResultsResponse
  expect(
    firstPage.total,
    'fewer than 11 open mock opportunities: mock deadlines have lapsed, refresh backend/data/mock_opportunities.json',
  ).toBeGreaterThan(10)
  await expect(page.getByRole('article')).toHaveCount(10)

  const nextSent = page.waitForRequest((r) => r.url().endsWith('/api/search'))
  await page.getByRole('button', { name: 'Show more' }).click()
  expect((await nextSent).postDataJSON()).toMatchObject({ offset: 10 })

  await expect(page.getByRole('article')).toHaveCount(Math.min(firstPage.total, 20))
  const titles = await shownTitles(page)
  expect(titles.slice(0, 10)).toEqual(firstPage.results.map((result) => result.opportunity.title))
  expect(new Set(titles).size, 'the second page should not repeat the first').toBe(titles.length)
})

test('refining the search on the results page sends the new criteria', async ({ page }) => {
  await searchFromHome(page, 'marine ecology')
  await expect(page.getByRole('article').first()).toBeVisible()

  await page.getByLabel('Career Stage').selectOption({ index: 1 })
  await page.getByLabel('Research description').fill('quantum computing')
  const sent = page.waitForRequest((request) => request.url().endsWith('/api/search'))
  await page.getByRole('button', { name: 'Search', exact: true }).click()

  const body = (await sent).postDataJSON() as SearchRequest
  expect(body.research_description).toBe('quantum computing')
  expect(body.career_stage).not.toBeNull()
  await expect(page.getByText(/\d+ Results Found/)).toBeVisible()
})
