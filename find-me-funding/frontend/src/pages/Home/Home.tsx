import styles from './Home.module.css';
import Dropdown from '../../components/Dropdown/Dropdown';

function Home() {

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
        <div className={styles.searchbarContainer}>
          <input
            className={styles.searchbar}
            type="text"
            placeholder="What kind of research are you searching for funding for?"
            />
          <span data-icon="search"  data-size="sm" aria-label="Search"></span>
        </div>
      </div>
    </>
  )
}

export default Home