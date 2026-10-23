import CitizenshipDropdown from '../CitizenshipDropdown/CitizenshipDropdown';
import Dropdown from '../Dropdown/Dropdown';
import FieldOfResearchDropdown from '../FieldOfResearchDropdown/FieldOfResearchDropdown';
import { filterOptions, type FilterKey, type FilterValues } from '../../data/filterOptions';
import styles from './FilterPanel.module.css';

interface FilterPanelProps {
  filters: FilterValues;
  onChange: (filters: FilterValues) => void;
}

export default function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const set = <K extends FilterKey>(key: K, value: FilterValues[K]) =>
    onChange({ ...filters, [key]: value });

  return (
    <div className={styles.panel}>
      <FieldOfResearchDropdown
        value={filters.fieldOfResearch}
        onChange={(value) => set('fieldOfResearch', value)}
      />
      <Dropdown
        label="Type of Activity"
        options={filterOptions.typeOfActivity}
        value={filters.typeOfActivity}
        onChange={(value) => set('typeOfActivity', value)}
      />
      <CitizenshipDropdown
        value={filters.citizenship}
        onChange={(value) => set('citizenship', value)}
      />
      <Dropdown
        label="Employer Type"
        options={filterOptions.employerType}
        value={filters.employerType}
        onChange={(value) => set('employerType', value)}
      />
      <Dropdown
        label="Career Stage"
        options={filterOptions.careerStage}
        value={filters.careerStage}
        onChange={(value) => set('careerStage', value)}
      />
      <Dropdown
        label="Funding Type"
        options={filterOptions.fundingType}
        value={filters.fundingType}
        onChange={(value) => set('fundingType', value)}
      />
    </div>
  );
}
