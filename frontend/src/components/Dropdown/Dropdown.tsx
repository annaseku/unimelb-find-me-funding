import styles from './Dropdown.module.css';
import type { FilterOption } from '../../data/filterOptions';

interface DropdownProps {
  label: string;
  options: FilterOption[];
  value: string;
  onChange: (value: string) => void;
}

export default function Dropdown({ label, options, value, onChange }: DropdownProps) {
  return <select className={styles.dropdown} aria-label={label} value={value}
    onChange={(event) => onChange(event.target.value)}>
    <option value="">{label} ? Any</option>
    {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
  </select>;
}
