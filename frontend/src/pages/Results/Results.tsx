import styles from './Results.module.css'
import { useEffect } from "react"
import Dropdown from '../../components/Dropdown/Dropdown'
import Result from '../../components/Result/Result'

function Results() {

    useEffect(() => {
        window.uom?.initAllComponents()
      }, [])

  return (
    <>
      <div className={styles.resultsContainer}>
        <h1 className={styles.title}>Search Results</h1>
        <div className={styles.dropdownContainer}> 
        <Dropdown label="Field of Research" />
        <Dropdown label="Type of Activity" />
        <Dropdown label="Citizenship" />
        <Dropdown label="Employer Type" />
        <Dropdown label="Career Stage" />
        <Dropdown label="Funding Type" />
        </div>
        <p className={styles.numResults}>[placeholder number] Results Found</p>
        <Result />
      </div>
    </>
  )
}

export default Results