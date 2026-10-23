import styles from './Home.module.css';
import { useId, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Dropdown from '../../components/Dropdown/Dropdown';
import FieldOfResearchDropdown from '../../components/FieldOfResearchDropdown/FieldOfResearchDropdown';
import CitizenshipDropdown from '../../components/CitizenshipDropdown/CitizenshipDropdown';

import { filterOptions, defaultFilterValues, type FilterKey } from '../../data/filterOptions';

function Home() {
  const [search, setSearch] = useState('');
  const searchId = useId();
  const [filters, setFilters] = useState(defaultFilterValues);
  const navigate = useNavigate();

  const handleFilterChange = (key: FilterKey, value: string | string[]) => {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  };

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
        <div className={styles.dropdownContainer}>
          <FieldOfResearchDropdown
            value={filters.fieldOfResearch}
            onChange={(value) => handleFilterChange('fieldOfResearch', value)}
          />
          <Dropdown
            label="Type of Activity"
            options={filterOptions.typeOfActivity}
            value={filters.typeOfActivity}
            onChange={(value) => handleFilterChange('typeOfActivity', value)}
          />
          <CitizenshipDropdown
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
        <label htmlFor={searchId} className={styles.searchLabel}>
          Search by description of project or research:
        </label>

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
