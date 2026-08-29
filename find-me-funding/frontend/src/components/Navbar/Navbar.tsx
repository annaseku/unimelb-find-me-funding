import styles from './Navbar.module.css'
import Profile from '../../assets/icons/Profile'

function Navbar() {

  return (
    <>
        <nav className={styles.navbar}>
            <p className={styles.title}>Find Me Funding</p>
            <Profile className={styles.profile} />
        </nav>
    </>
  )
}

export default Navbar