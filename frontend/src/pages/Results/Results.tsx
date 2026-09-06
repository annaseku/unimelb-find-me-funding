import styles from './Results.module.css';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import Dropdown from '../../components/Dropdown/Dropdown';
import Result from '../../components/Result/Result';
import { fetchMockResults } from '../../services/mockFundingService';
import { defaultFilterValues, filterOptions, type FilterKey } from '../../data/filterOptions';
import type { FundingOpportunity } from '../../types/funding';

function Results() {
  const location = useLocation();
  const [results, setResults] = useState<FundingOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState(defaultFilterValues);

  const runSearch = () => {
    setLoading(true);

    fetchMockResults(search, filters)
      .then((response) => {
        setResults(response.results);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    window.uom?.initAllComponents();

    const incomingState = location.state as { search?: string; filters?: typeof defaultFilterValues } | null;
    const nextSearch = incomingState?.search ?? '';
    const nextFilters = incomingState?.filters ?? defaultFilterValues;

    setSearch(nextSearch);
    setFilters(nextFilters);

    fetchMockResults(nextSearch, nextFilters)
      .then((response) => {
        setResults(response.results);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [location.state]);

  const handleFilterChange = (key: FilterKey, value: string) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  return (
    <>
      <div className={styles.resultsContainer}>
        <h1 className={styles.title}>Search Results</h1>
        <div className={styles.dropdownContainer}>
          <Dropdown
            label="Field of Research"
            options={filterOptions.fieldOfResearch}
            value={filters.fieldOfResearch}
            onChange={(value) => handleFilterChange('fieldOfResearch', value)}
          />
          <Dropdown
            label="Type of Activity"
            options={filterOptions.typeOfActivity}
            value={filters.typeOfActivity}
            onChange={(value) => handleFilterChange('typeOfActivity', value)}
          />
          <Dropdown
            label="Citizenship"
            options={filterOptions.citizenship}
            value={filters.citizenship}
            onChange={(value) => handleFilterChange('citizenship', value)}
          />
          <Dropdown
            label="Employer Type"
            options={filterOptions.employerType}
            value={filters.employerType}
            onChange={(value) => handleFilterChange('employerType', value)}
          />
          <Dropdown
            label="Career Stage"
            options={filterOptions.careerStage}
            value={filters.careerStage}
            onChange={(value) => handleFilterChange('careerStage', value)}
          />
          <Dropdown
            label="Funding Type"
            options={filterOptions.fundingType}
            value={filters.fundingType}
            onChange={(value) => handleFilterChange('fundingType', value)}
          />
        </div>

        <div className={styles.searchControls}>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search by keyword"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <button type="button" onClick={runSearch} className={styles.searchButton}>
            Search
          </button>
        </div>

        <p className={styles.numResults}>
          {loading ? 'Loading...' : `${results.length} Results Found`}
        </p>

        {results.map((result) => (
          <Result key={result.url} opportunity={result} />
        ))}
      </div>
    </>
  );
}

export default Results;