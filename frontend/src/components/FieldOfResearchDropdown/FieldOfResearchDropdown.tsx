import { useEffect, useRef, useState } from 'react';
import { fieldOfResearchOptions } from '../../data/fieldOfResearchOptions';
import styles from './FieldOfResearchDropdown.module.css';

interface FieldOfResearchDropdownProps {
    value: string[];
    onChange: (value: string[]) => void;
}

export default function FieldOfResearchDropdown({
    value,
    onChange,
}: FieldOfResearchDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [search, setSearch] = useState('');
    const [expandedDivision, setExpandedDivision] = useState<string | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                containerRef.current &&
                !containerRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const searchTerm = search.trim().toLowerCase();

    const selectedOptions = fieldOfResearchOptions
        .flatMap((division) => [
            { value: division.value, label: division.label },
            ...division.groups,
        ])
        .filter((option) => value.includes(option.value));

    const triggerLabel = selectedOptions.length === 0
        ? 'Field of Research – Any'
        : selectedOptions.length === 1
            ? selectedOptions[0].label
            : `${selectedOptions.length} fields selected`;

    const filteredDivisions = fieldOfResearchOptions
        .map((division) => {
            if (!searchTerm) {
                return division;
            }

            const divisionMatches =
                division.label.toLowerCase().includes(searchTerm) ||
                division.value.includes(searchTerm);

            const matchingGroups = division.groups.filter(
                (group) =>
                    group.label.toLowerCase().includes(searchTerm) ||
                    group.value.includes(searchTerm)
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
        setExpandedDivision((current) =>
            current === divisionValue ? null : divisionValue
        );
    };

    const handleSelect = (selectedValue: string) => {
        onChange(
            value.includes(selectedValue)
                ? value.filter((selected) => selected !== selectedValue)
                : [...value, selectedValue]
        );
    };

    const handleClear = () => {
        onChange([]);
    };

    return (
        <div ref={containerRef} className={styles.dropdownWrapper}>
            <span className={styles.label}>Field of Research</span>
            <button
                type="button"
                className={styles.trigger}
                onClick={() => setIsOpen((current) => !current)}
                aria-expanded={isOpen}
            >
                <span className={styles.triggerLabel}>
                    {triggerLabel}
                </span>

                <span className={styles.triggerArrow}>
                    <span
                        data-icon="chevron-bottom"
                        data-size="sm"
                        data-hide-label="true"
                    />
                </span>
            </button>
            {isOpen && (
                <div className={styles.menu}>
                    <input
                        type="text"
                        className={styles.search}
                        placeholder="Search field of research..."
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />

                    <button
                        type="button"
                        className={styles.anyOption}
                        onClick={handleClear}
                    >
                        Any
                    </button>

                    <div className={styles.options}>
                        {filteredDivisions.map((division) => {
                            const isExpanded =
                                expandedDivision === division.value;

                            const showGroups =
                                isExpanded || searchTerm.length > 0;

                            return (
                                <div
                                    key={division.value}
                                    className={styles.division}
                                >
                                    <div className={styles.divisionRow}>
                                        <button
                                            type="button"
                                            className={styles.expandButton}
                                            onClick={() =>
                                                toggleDivision(division.value)
                                            }
                                            aria-label={`${
                                                isExpanded
                                                    ? 'Collapse'
                                                    : 'Expand'
                                            } ${division.label}`}
                                        >
                                            {isExpanded ? '▼' : '▶'}
                                        </button>

                                        <div
                                            className={`${styles.divisionOption} ${
                                                value.includes(division.value) ? styles.selectedOption : ''
                                            }`}
                                        >
                                            <input
                                                type="checkbox"
                                                id={`for-${division.value}`}
                                                className="checkbox"
                                                checked={value.includes(division.value)}
                                                onChange={() => handleSelect(division.value)}
                                            />
                                            <label htmlFor={`for-${division.value}`}>
                                                <span className={styles.code}>{division.value}</span>
                                                {division.label}
                                            </label>
                                        </div>
                                    </div>

                                    {showGroups && (
                                        <div className={styles.groups}>
                                            {division.groups.map((group) => (
                                                <div
                                                    key={group.value}
                                                    className={`${styles.groupOption} ${
                                                        value.includes(group.value) ? styles.selectedOption : ''
                                                    }`}
                                                >
                                                    <input
                                                        type="checkbox"
                                                        id={`for-${group.value}`}
                                                        className="checkbox"
                                                        checked={value.includes(group.value)}
                                                        onChange={() => handleSelect(group.value)}
                                                    />
                                                    <label htmlFor={`for-${group.value}`}>
                                                        <span className={styles.code}>{group.value}</span>
                                                        {group.label}
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            );
                        })}

                        {filteredDivisions.length === 0 && (
                            <p className={styles.noResults}>
                                No fields of research found.
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}