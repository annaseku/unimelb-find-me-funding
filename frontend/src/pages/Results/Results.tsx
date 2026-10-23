import styles from './Results.module.css';
import { useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import FilterPanel from '../../components/FilterPanel/FilterPanel';
import Result from '../../components/Result/Result';
import DataNotice from '../../components/DataNotice/DataNotice';
import { fetchResults } from '../../services/fundingService';
import { defaultFilterValues, type FilterValues } from '../../data/filterOptions';
import { criteria, type CriterionKey, type SearchResponse } from '../../types/funding';

type Query = { search: string; filters: FilterValues };

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;
const text = (value: unknown) => (typeof value === 'string' ? value : '');
const textList = (value: unknown) =>
  Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];

// Router state can come from browser history or a hand-built link, so it is checked, not trusted.
function queryFromState(state: unknown): Query {
  const query = isRecord(state) ? state : {};
  const filters = isRecord(query.filters) ? query.filters : {};
  return {
    search: text(query.search),
    filters: {
      ...defaultFilterValues,
      fieldOfResearch: text(filters.fieldOfResearch),
      typeOfActivity: text(filters.typeOfActivity),
      citizenship: textList(filters.citizenship),
      employerType: text(filters.employerType),
      careerStage: text(filters.careerStage),
      fundingType: text(filters.fundingType),
    },
  };
}

export default function Results() {
  const location = useLocation();
  const [initial] = useState<Query>(() => queryFromState(location.state));
  const [search, setSearch] = useState(initial.search);
  const [filters, setFilters] = useState(initial.filters);
  const [submitted, setSubmitted] = useState(initial);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const controller = useRef<AbortController | null>(null);

  function load(query: Query, offset = 0) {
    controller.current?.abort();
    const request = new AbortController();
    controller.current = request;
    return fetchResults(query.search, query.filters, offset, request.signal)
      .then((page) => {
        if (request.signal.aborted) return;
        setResponse((previous) => ({
          ...page,
          results: offset > 0 ? [...(previous?.results ?? []), ...page.results] : page.results,
        }));
      })
      .catch((failure: unknown) => {
        if (!request.signal.aborted)
          setError(failure instanceof Error ? failure.message : 'Search failed. Please try again.');
      })
      .finally(() => {
        if (!request.signal.aborted) setLoading(false);
      });
  }

  useEffect(() => {
    window.uom?.initAllComponents();
    void load(initial);
    return () => controller.current?.abort();
  }, [initial]);

  function startSearch(query: Query, offset = 0) {
    setLoading(true);
    setError('');
    if (offset === 0) setResponse(null);
    void load(query, offset);
  }

  const runSearch = () => {
    const query = { search, filters: { ...filters } };
    setSubmitted(query);
    startSearch(query);
  };
  // Appended results already include earlier pages, so their length is the next offset.
  const loaded = response?.results.length ?? 0;
  return (
    <div className={styles.resultsContainer}>
      <h1 className={styles.title}>Search Results</h1>
      <FilterPanel filters={filters} onChange={setFilters} />

      <form
        className={styles.searchControls}
        onSubmit={(event) => {
          event.preventDefault();
          runSearch();
        }}
      >
        <input
          className={styles.searchInput}
          aria-label="Research description"
          placeholder="Search by keyword"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <button type="submit" className={styles.searchButton}>
          Search
        </button>
      </form>
      {loading && (
        <p role="status">
          Searching for funding. The service may be waking up; the first search can take about a
          minute.
        </p>
      )}
      {error && (
        <div role="alert">
          <p>{error}</p>
          <button type="button" onClick={() => startSearch(submitted, response ? loaded : 0)}>
            Try again
          </button>
        </div>
      )}
      {response && (
        <>
          <DataNotice />
          <p className={styles.numResults}>{response.total} Results Found</p>
          {response.total === 0 && (
            <p>No funding opportunities found. Try changing your filters.</p>
          )}
          <details>
            <summary>How results are ranked</summary>
            <ul>
              {(Object.keys(criteria) as CriterionKey[]).map((key) => (
                <li key={key}>
                  {criteria[key]}: {Math.round(response.weights[key] * 100)}%
                </li>
              ))}
            </ul>
          </details>
          {response.results.map((result) => (
            <Result key={result.opportunity.id} result={result} />
          ))}
          {loaded < response.total && (
            <button
              className={styles.searchButton}
              type="button"
              disabled={loading}
              onClick={() => startSearch(submitted, loaded)}
            >
              Show more
            </button>
          )}
        </>
      )}
    </div>
  );
}
