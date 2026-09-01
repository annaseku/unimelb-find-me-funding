import styles from './Home.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Dropdown from '../../components/Dropdown/Dropdown';

function Home() {

  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();

    if (search.trim() === '') {
      return;
    }

    navigate('/results');
  }


  return (
    <>
      <div className={styles.homeContainer}>
        <h1 className={styles.title}>Find Me Funding</h1>
        <div className={styles.dropdownContainer}> 
        <Dropdown label="Field of Research" />
        <Dropdown label="Type of Activity" />
        <Dropdown label="Citizenship" />
        <Dropdown label="Employer Type" />
        <Dropdown label="Career Stage" />
        <Dropdown label="Funding Type" />
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
              <span data-icon="search"  data-size="sm" aria-label="Search"></span>
            </div>
        </form>
      </div>
    </>
  )
}

export default Home