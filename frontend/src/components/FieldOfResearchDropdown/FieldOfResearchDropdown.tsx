import { useId, useRef, useState } from 'react';
import { fieldOfResearchOptions } from '../../data/fieldOfResearchOptions';
import { useDismiss } from '../../hooks/useDismiss';
import menuStyles from '../../styles/menuDropdown.module.css';
import styles from './FieldOfResearchDropdown.module.css';

interface FieldOfResearchDropdownProps {
  value: string[];
  onChange: (value: string[]) => void;
}

export default function FieldOfResearchDropdown({ value, onChange }: FieldOfResearchDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedDivision, setExpandedDivision] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const id = useId();
  const menuId = `${id}-menu`;
  useDismiss({ open: isOpen, onDismiss: () => setIsOpen(false), containerRef, triggerRef });

  const searchTerm = search.trim().toLowerCase();

  const selectedOption = fieldOfResearchOptions
    .flatMap((division) => [{ value: division.value, label: division.label }, ...division.groups])
    .find((option) => option.value === value[0]);

  const filteredDivisions = fieldOfResearchOptions
    .map((division) => {
      if (!searchTerm) {
        return division;
      }

      const divisionMatches =
        division.label.toLowerCase().includes(searchTerm) || division.value.includes(searchTerm);

      const matchingGroups = division.groups.filter(
        (group) =>
          group.label.toLowerCase().includes(searchTerm) || group.value.includes(searchTerm),
      );

      if (divisionMatches) {
        return division;
      }

      if (matchingGroups.length > 0) {
        return {
          ...division,
          groups: matchingGroups,
        };
      }

      return null;
    })
    .filter((division) => division !== null);

  const toggleDivision = (divisionValue: string) => {
    setExpandedDivision((current) => (current === divisionValue ? null : divisionValue));
  };

  const handleToggleField = (code: string) => {
    if (value.includes(code)) {
      onChange(value.filter((selected) => selected !== code));
    } else {
      onChange([...value, code]);
    }
  };

  const getDisplayLabel = () => {
    if (value.length === 0) {
      return 'Field of Research – Any';
    }

    if (value.length === 1) {
      return selectedOption?.label ?? 'Field of Research';
    }

    return `${value.length} fields selected`;
  };

  return (
    <div ref={containerRef} className={menuStyles.dropdownWrapper}>
      <span id={`${id}-label`} className={menuStyles.label}>
        Field of Research
      </span>
      <button
        ref={triggerRef}
        type="button"
        className={menuStyles.trigger}
        onClick={() => setIsOpen((current) => !current)}
        aria-expanded={isOpen}
        aria-controls={isOpen ? menuId : undefined}
        aria-labelledby={value.length > 0 ? `${id}-label ${id}-value` : `${id}-value`}
      >
        <span id={`${id}-value`} className={menuStyles.triggerLabel}>
          {getDisplayLabel()}
        </span>

        <span className={menuStyles.triggerArrow}>
          <span data-icon="chevron-bottom" data-size="sm" data-hide-label="true" />
        </span>
      </button>
      {isOpen && (
        <div id={menuId} className={menuStyles.menu}>
          <input
            type="text"
            className={menuStyles.search}
            placeholder="Search field of research..."
            aria-label="Search fields of research"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <button type="button" className={styles.anyOption} onClick={() => onChange([])}>
            Any
          </button>

          <div className={menuStyles.options}>
            {filteredDivisions.map((division) => {
              const isExpanded = expandedDivision === division.value;

              const showGroups = isExpanded || searchTerm.length > 0;
              const groupsId = `${menuId}-${division.value}`;

              return (
                <div key={division.value} className={styles.division}>
                  <div className={styles.divisionRow}>
                    <button
                      type="button"
                      className={styles.expandButton}
                      onClick={() => toggleDivision(division.value)}
                      aria-label={`${division.label} groups`}
                      aria-expanded={showGroups}
                      aria-controls={showGroups ? groupsId : undefined}
                    >
                      {isExpanded ? '▼' : '▶'}
                    </button>

                    <div className={styles.divisionOption}>
                      <input
                        type="checkbox"
                        id={`${id}-${division.value}`}
                        className="checkbox"
                        checked={value.includes(division.value)}
                        onChange={() => handleToggleField(division.value)}
                      />
                      <label htmlFor={`${id}-${division.value}`}>
                        <span>
                          <span className={styles.code}>{division.value}</span>
                          {division.label}
                        </span>
                      </label>
                    </div>
                  </div>

                  {showGroups && (
                    <div id={groupsId} className={styles.groups}>
                      {division.groups.map((group) => (
                        <div key={group.value} className={styles.groupOption}>
                          <input
                            type="checkbox"
                            id={`${id}-${group.value}`}
                            className="checkbox"
                            checked={value.includes(group.value)}
                            onChange={() => handleToggleField(group.value)}
                          />
                          <label htmlFor={`${id}-${group.value}`}>
                            <span>
                              <span className={styles.code}>{group.value}</span>
                              {group.label}
                            </span>
                          </label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}

            {filteredDivisions.length === 0 && (
              <p className={styles.noResults}>No fields of research found.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
