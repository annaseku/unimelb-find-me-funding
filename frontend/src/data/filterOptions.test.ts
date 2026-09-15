import { expect, it } from 'vitest';
import { defaultFilterValues, filterOptions } from './filterOptions';
it('provides unique backend values and readable labels for all six filters', () => {
  expect(Object.keys(filterOptions)).toEqual(Object.keys(defaultFilterValues));
  for (const options of Object.values(filterOptions)) {
    expect(options.length).toBeGreaterThan(0);
    expect(new Set(options.map((option) => option.value)).size).toBe(options.length);
    options.forEach((option) => { expect(option.value).not.toBe(''); expect(option.label).not.toBe(''); });
  }
  expect(filterOptions.employerType.map((option) => option.value)).toEqual(['university', 'research_institute', 'industry', 'philanthropic']);
});
