import styles from './Dropdown.module.css'
import SortDown from '../../assets/icons/SortDown'

interface DropdownProps {
    label: string;
}

function Dropdown({ label }: DropdownProps) {
    return (
    <>
        <div className={styles.dropdown}>
            <span>{label}</span>
            <SortDown className={styles.dropdownIcon}/>
        </div>
    </>
    )
}

export default Dropdown;