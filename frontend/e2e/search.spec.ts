// mutation-check: characterisation
import { expect, test, type Page } from '@playwright/test'
import type { SearchRequest, SearchResponse } from '../src/types/funding'


// The API that playwright.config.ts starts; the tests ask it directly for the
// ranking they expect the UI to show.
const API = 'http://127.0.0.1:8001'

async function searchFromHome(page: Page, description: string, citizenship = '') {
  await page.goto('/')
  //if (citizenship) {await page.getByText('Citizenship – Any').click();
  //await page.getByLabel('Citizenship').getByRole('radio').filter({ visible: true }).count()}
  if (citizenship) {
  const citizenshipLabels: Record<string, string> = {
    AU: 'Australia',
    NZ: 'New Zealand',
    GB: 'United Kingdom',
    US: 'United States',
    CN: 'China',
    IN: 'India',
  }
  await page.getByText('Citizenship – Any').click()
  await page.getByText(citizenshipLabels[citizenship], { exact: true }).click()
  await page.getByRole('heading', { name: /Find Me Funding/i }).click()
}
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

  const expected = await (await request.post(`${API}/api/search`, { data: sent })).json() as SearchResponse
  expect(expected.total, 'the corpus in backend/evals/corpus.json should have open opportunities').toBeGreaterThan(0)

  await expect(page.getByText(`${expected.total} Results Found`)).toBeVisible()
  expect(await shownTitles(page)).toEqual(expected.results.map((result) => result.opportunity.title))
})

test('each result explains its rating against every criterion and links out', async ({ page }) => {
  await searchFromHome(page, 'climate')
  const first = page.getByRole('article').first()
  await first.locator('summary').click();
  await expect(first).toBeVisible()

  for (const criterion of ['Eligibility', 'Research match', 'Funding value', 'Time to deadline']) {
    await expect(first.getByRole('heading', { level: 3, name: criterion })).toBeVisible()
  }
  await expect(first.getByRole('link', { name: 'View opportunity' })).toHaveAttribute('href', /^https?:\/\//)
})

test('show more appends the next page of results', async ({ page, request }) => {
  const sent = await searchFromHome(page, 'research')
  const firstPage = await (await request.post(`${API}/api/search`, { data: sent })).json() as SearchResponse
  expect(
    firstPage.total,
    'fewer than 11 open corpus opportunities: corpus deadlines have lapsed, refresh backend/evals/corpus.json',
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

  //await page.getByLabel('Career Stage').selectOption({ index: 1 })
  await page.getByText('Career Stage – Any').click();
  //await page.getByRole('radio', { name: 'Undergraduate' }).check();
  await page.getByText('Undergraduate', { exact: true }).click()
  await page.getByLabel('Research description').fill('quantum computing')
  const sent = page.waitForRequest((request) => request.url().endsWith('/api/search'))
  await page.getByRole('button', { name: 'Search', exact: true }).click()

  const body = (await sent).postDataJSON() as SearchRequest
  expect(body.research_description).toBe('quantum computing')
  expect(body.career_stage).not.toBeNull()
  await expect(page.getByText(/\d+ Results Found/)).toBeVisible()
})
