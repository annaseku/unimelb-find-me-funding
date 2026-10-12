import styles from './Dropdown.module.css';
import { useId, useRef } from 'react';
import type { FilterOption } from '../../data/filterOptions';

interface DropdownProps {
  label: string;
  options: FilterOption[];
  value: string;
  onChange: (value: string) => void;
}

export default function Dropdown({ label, options, value, onChange }: DropdownProps) {
  const dropdownId = useId();
  const dropdownRef = useRef<HTMLDetailsElement>(null);
  const selectedOption = options.find((option) => option.value === value);

  const selectOption = (nextValue: string) => {
    onChange(nextValue);
    if (dropdownRef.current) dropdownRef.current.open = false;
  };

  return <div className={styles.dropdownWrapper}>
    <span className={styles.label} id={`${dropdownId}-label`}>{label}</span>
    <details ref={dropdownRef} className={`dropdown ${styles.dropdown}`} aria-labelledby={`${dropdownId}-label`}>
      <summary>{selectedOption?.label ?? `${label} – Any`}</summary>
      <div className="dropdown__panel">
        <fieldset>
          <legend className="screenreaders-only">{label}</legend>
          <div className="inline">
            <input
              id={`${dropdownId}-any`}
              className="radio"
              type="radio"
              name={dropdownId}
              value=""
              checked={value === ''}
              onChange={() => selectOption('')}
            />
            <label htmlFor={`${dropdownId}-any`}><span>Any</span></label>
          </div>
          {options.map((option) => {
            const optionId = `${dropdownId}-${option.value}`;
            return <div className="inline" key={option.value}>
              <input
                id={optionId}
                className="radio"
                type="radio"
                name={dropdownId}
                value={option.value}
                checked={value === option.value}
                onChange={() => selectOption(option.value)}
              />
              <label htmlFor={optionId}><span>{option.label}</span></label>
            </div>;
          })}
        </fieldset>
      </div>
    </details>
  </div>;
}
