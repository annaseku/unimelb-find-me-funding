import styles from './Home.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Dropdown from '../../components/Dropdown/Dropdown';

function Home() {

  // use states for 6 dropdowns
  const [employerType, setEmployerType] = useState('');
  const [careerStage, setCareerStage] = useState('');
  const [fundingType, setFundingType] = useState('');
  const [fieldOfResearch, setFieldOfResearch] = useState('');
  const [typeOfActivity, setTypeOfActivity] = useState('');
  const [citizenship, setCitizenship] = useState('');

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
        <Dropdown label="Field of Research" 
        options = {[
          {value: '31', label: 'Biological Sciences'},
          {value: '3103', label: 'Ecology'},
          {value: '3708', label: 'Oceanography'},
        ]} 
        value={fieldOfResearch}
        onChange={setFieldOfResearch}
        />
        <Dropdown label="Type of Activity" 
        options = {[
          {value: '1', label: 'Pure basic research'},
          {value: '2', label: 'Strategic basic research'},
          {value: '3', label: 'Applied research'},
          {value: '4', label: 'Experimental development'},
        ]} 
        value={typeOfActivity}
        onChange={setTypeOfActivity}
        />
        <Dropdown label="Citizenship" 
        options = {[
          {value: 'AU', label: 'Australia'},
          {value: 'NZ', label: 'New Zealand'},
          {value: 'GB', label: 'United Kingdom'},
          {value: 'US', label: 'United States'},
          {value: 'CN', label: 'China'},
          {value: 'IN', label: 'India'},
        ]} 
        value={citizenship}
        onChange={setCitizenship}
        />
        <Dropdown label="Employer Type"
        options = {[
          {value: 'university', label: 'University'},
          {value: 'research_institute', label: 'Research Institute'},
          {value: 'industry', label: 'Industry'},
          {value: 'philanthropic', label: 'Philanthropic organisation'},
        ]} 
        value={employerType}
        onChange={setEmployerType}
        />
        <Dropdown label="Career Stage" 
        options = {[
          {value: 'undergraduate', label: 'Undergraduate'},
          {value: 'graduate_student', label: 'Graduate Student'},
          {value: 'postdoc_0_2', label: 'Postdoctoral (0-2 years)'},
          {value: 'postdoc_2_5', label: 'Postdoctoral (2-5 years)'},
          {value: 'postdoc_5_10', label: 'Postdoctoral (5-10 years)'},
          {value: 'postdoc_10_plus', label: 'Postdoctoral (10+ years)'},
        ]} 
        value={careerStage}
        onChange={setCareerStage}
        />
        <Dropdown label="Funding Type" 
        options = {[
          {value: 'salary', label: 'Salary'},
          {value: 'consumables', label: 'Consumables'},
          {value: 'equipment', label: 'Equipment'},
          {value: 'all', label: 'All categories'},
          {value: 'any', label: 'Any category'},
        ]} 
        value={fundingType}
        onChange={setFundingType}
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
              <span data-icon="search"  data-size="sm" aria-label="Search"></span>
            </div>
        </form>
      </div>
    </>
  )
}

export default Home
