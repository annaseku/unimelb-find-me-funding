import styles from './Dropdown.module.css'

interface DropdownProps {
    label: string;
    options?: { value: string; label: string }[];
    value?: string;
    onChange?: (value: string) => void;
}

function Dropdown({ label, options = [], value = '', onChange }: DropdownProps) {
    return (
    <select
        className={styles.dropdown}
        aria-label={label}
        value={value}
        disabled={options.length === 0 || !onChange}
        onChange={(e) => onChange?.(e.target.value)}
    >
        <option value="">{label}</option>
        
        {options.map((option) => (
            <option key={option.value} value={option.value}>
                {option.label}
            </option>
        ))}
    </select>
    )
}

export default Dropdown;
