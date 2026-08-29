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
      <p>Search by description of project or research:</p>
      <input className={styles.searchbar} type="text" placeholder='What kind of research are you searching for funding for?' />
      </div>
    </>
  )
}

export default Home