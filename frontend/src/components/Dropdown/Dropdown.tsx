import { useState } from 'react';
import styles from './Dropdown.module.css';

interface DropdownProps {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
}

function Dropdown({ label, options, value, onChange }: DropdownProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className={styles.dropdownWrapper}>
      <button
        type="button"
        className={styles.dropdown}
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
      >
        <span>{value || label}</span>
        <span data-icon="sort-down" data-size="sm" data-hide-label="true"></span>
      </button>

      {open && (
        <div className={styles.menu}>
          <button type="button" className={styles.menuOption} onClick={() => { onChange(''); setOpen(false); }}>
            Any
          </button>
          {options.map((option) => (
            <button
              key={option}
              type="button"
              className={styles.menuOption}
              onClick={() => {
                onChange(option);
                setOpen(false);
              }}
            >
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dropdown;