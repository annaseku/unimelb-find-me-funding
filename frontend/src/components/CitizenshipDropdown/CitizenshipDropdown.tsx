import { useId, useRef, useState } from 'react';
import { filterOptions } from '../../data/filterOptions';
import { useDismiss } from '../../hooks/useDismiss';
import styles from './CitizenshipDropdown.module.css';

interface CitizenshipDropdownProps {
  value: string[];
  onChange: (value: string[]) => void;
}

export default function CitizenshipDropdown({ value, onChange }: CitizenshipDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuId = useId();
  useDismiss({ open: isOpen, onDismiss: () => setIsOpen(false), containerRef, triggerRef });

  const searchTerm = search.trim().toLowerCase();

  const filteredCountries = filterOptions.citizenship.filter(
    (country) =>
      country.label.toLowerCase().includes(searchTerm) ||
      country.value.toLowerCase().includes(searchTerm),
  );

  const handleToggleCountry = (countryCode: string) => {
    if (value.includes(countryCode)) {
      onChange(value.filter((code) => code !== countryCode));
    } else {
      onChange([...value, countryCode]);
    }
  };

  const handleClear = () => {
    onChange([]);
  };

  const getDisplayLabel = () => {
    if (value.length === 0) {
      return 'Citizenship – Any';
    }

    if (value.length === 1) {
      const selectedCountry = filterOptions.citizenship.find(
        (country) => country.value === value[0],
      );

      return selectedCountry?.label ?? 'Citizenship';
    }

    return `${value.length} citizenships selected`;
  };

  return (
    <div ref={containerRef} className={styles.dropdownWrapper}>
      <span className={styles.label}>Citizenship</span>
      <button
        ref={triggerRef}
        type="button"
        className={styles.trigger}
        onClick={() => setIsOpen((current) => !current)}
        aria-expanded={isOpen}
        aria-controls={isOpen ? menuId : undefined}
      >
        <span className={styles.triggerLabel}>{getDisplayLabel()}</span>

        <span className={styles.triggerArrow}>
          <span data-icon="chevron-bottom" data-size="sm" data-hide-label="true" />
        </span>
      </button>

      {isOpen && (
        <div id={menuId} className={styles.menu}>
          <input
            type="text"
            className={styles.search}
            placeholder="Search citizenship..."
            aria-label="Search citizenships"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <button type="button" className={styles.anyOption} onClick={handleClear}>
            Any
          </button>

          <div className={styles.options}>
            {filteredCountries.map((country) => {
              const checkboxId = `citizenship-${country.value}`;

              return (
                <div
                  key={country.value}
                  className={`${styles.countryOption} ${
                    value.includes(country.value) ? styles.selectedCountry : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    id={checkboxId}
                    className="checkbox"
                    checked={value.includes(country.value)}
                    onChange={() => handleToggleCountry(country.value)}
                  />

                  <label htmlFor={checkboxId}>
                    <span>{country.label}</span>
                  </label>
                </div>
              );
            })}

            {filteredCountries.length === 0 && (
              <p className={styles.noResults}>No countries found.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
