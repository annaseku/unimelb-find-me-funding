import styles from './Home.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Dropdown from '../../components/Dropdown/Dropdown';
import {
  filterOptions,
  defaultFilterValues,
  type FilterKey,
} from '../../data/filterOptions';

function Home() {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState(defaultFilterValues);
  const navigate = useNavigate();

  const handleFilterChange = (key: FilterKey, value: string) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();

    navigate('/results', {
      state: {
        search,
        filters,
      },
    });
  };

  return (
    <>
      <div className={styles.homeContainer}>
        <h1 className={styles.title}>Find Me Funding</h1>
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
        <p className={styles.searchLabel}>Search by description of project or research:</p>

        <form onSubmit={handleSearch} className={styles.searchSubmit}>
          <div className={styles.searchbarContainer}>
            <input
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
    </>
  );
}

export default Home;