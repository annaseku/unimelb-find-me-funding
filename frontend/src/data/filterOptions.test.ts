import { describe, expect, it } from 'vitest';
import { defaultFilterValues, filterOptions } from './filterOptions';

const filtersWithAnyLast = ['citizenship', 'employerType', 'fundingType'] as const;

describe('filterOptions', () => {
  it('has the same keys in defaultFilterValues as in filterOptions', () => {
    expect(Object.keys(defaultFilterValues).sort()).toEqual(Object.keys(filterOptions).sort());
  });

  it('defaults every filter value to an empty string', () => {
    for (const value of Object.values(defaultFilterValues)) {
      expect(value).toBe('');
    }
  });

  it('gives every filter a non-empty list of unique, non-empty options', () => {
    for (const options of Object.values(filterOptions)) {
      expect(options.length).toBeGreaterThan(0);
      expect(new Set(options).size).toBe(options.length);
      for (const option of options) {
        expect(option).not.toBe('');
      }
    }
  });

  it.each(filtersWithAnyLast)('puts "Any" last in the %s options', (key) => {
    const options = filterOptions[key];
    expect(options[options.length - 1]).toBe('Any');
  });

  it('does not include "Any" in the careerStage options, since the Dropdown adds its own', () => {
    expect(filterOptions.careerStage).not.toContain('Any');
  });
});
