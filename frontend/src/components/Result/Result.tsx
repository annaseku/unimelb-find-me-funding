import styles from './Result.module.css'

function Result() {

  return (
    <>
        <div className={styles.resultContainer}>
            <h5 className={styles.title}>Funding Result 1</h5>
            <p className={styles.description}>Description of funding ... Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec nisi a ipsum fringilla gravida. Duis convallis viverra quam. Suspendisse potenti. Nam id convallis lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Praesent vitae auctor libero.</p>
        </div>        
    </>
  )
}

export default Result