import styles from './Navbar.module.css'
import UniMelbLogo from '../../assets/icons/UniMelbLogo'

function Navbar() {

  return (
    <>
        <nav className={styles.navbar}>
            <UniMelbLogo />
        </nav>
    </>
  )
}

export default Navbar
