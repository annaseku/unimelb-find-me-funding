import styles from './Dropdown.module.css'

interface DropdownProps {
    label: string;
}

function Dropdown({ label }: DropdownProps) {
    return (
    <>
        <div className={styles.dropdown}>
            <span>{label}</span>
            <span 
                data-icon="sort-down" 
                data-size="sm"
                data-hide-label="true">
            </span>
        </div>
    </>
    )
}
export default Dropdown;