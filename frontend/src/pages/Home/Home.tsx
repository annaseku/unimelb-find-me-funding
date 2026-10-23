import styles from './Home.module.css';
import { useId, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FilterPanel from '../../components/FilterPanel/FilterPanel';
import { defaultFilterValues } from '../../data/filterOptions';

function Home() {
  const [search, setSearch] = useState('');
  const searchId = useId();
  const [filters, setFilters] = useState(defaultFilterValues);
  const navigate = useNavigate();

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();

    // Only data routers return a promise here; under BrowserRouter navigation is synchronous.
    void navigate('/results', {
      state: {
        search,
        filters,
      },
    });
  };

  return (
    <section className={styles.hero} aria-label="Find research funding">
      <div className={styles.homeContainer}>
        <h1 className={styles.title}>Find Me Funding</h1>
        <FilterPanel filters={filters} onChange={setFilters} />
        <p className={styles.searchLabel}>
          <label htmlFor={searchId}>Search by description of project or research:</label>
        </p>

        <form onSubmit={handleSearch} className={styles.searchSubmit}>
          <div className={styles.searchbarContainer}>
            <input
              id={searchId}
              className={styles.searchbar}
              type="text"
              placeholder="What kind of research are you searching for funding for?"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <button type="submit" className={styles.searchButton} aria-label="Search funding">
              Search
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}

export default Home;
