export interface FilterOption { value: string; label: string }

export const filterOptions = {
  fieldOfResearch: [
    { value: '31', label: 'Biological Sciences' },
    { value: '3103', label: 'Ecology' },
    { value: '3708', label: 'Oceanography' },
  ],
  typeOfActivity: [
    { value: '1', label: 'Pure basic research' },
    { value: '2', label: 'Strategic basic research' },
    { value: '3', label: 'Applied research' },
    { value: '4', label: 'Experimental development' },
  ],
  citizenship: [
    { value: 'AU', label: 'Australia' },
    { value: 'NZ', label: 'New Zealand' },
    { value: 'GB', label: 'United Kingdom' },
    { value: 'US', label: 'United States' },
    { value: 'CN', label: 'China' },
    { value: 'IN', label: 'India' },
  ],
  employerType: [
    { value: 'university', label: 'University' },
    { value: 'research_institute', label: 'Research Institute' },
    { value: 'industry', label: 'Industry' },
    { value: 'philanthropic', label: 'Philanthropic organisation' },
  ],
  careerStage: [
    { value: 'undergraduate', label: 'Undergraduate' },
    { value: 'graduate_student', label: 'Graduate Student' },
    { value: 'postdoc_0_2', label: 'Postdoctoral (0-2 years)' },
    { value: 'postdoc_2_5', label: 'Postdoctoral (2-5 years)' },
    { value: 'postdoc_5_10', label: 'Postdoctoral (5-10 years)' },
    { value: 'postdoc_10_plus', label: 'Postdoctoral (10+ years)' },
  ],
  fundingType: [
    { value: 'salary', label: 'Salary' },
    { value: 'consumables', label: 'Consumables' },
    { value: 'equipment', label: 'Equipment' },
    { value: 'all', label: 'All categories' },
    { value: 'any', label: 'Any category' },
  ],
} satisfies Record<string, FilterOption[]>;

export const defaultFilterValues = {
  fieldOfResearch: '',
  typeOfActivity: '',
  citizenship: '',
  employerType: '',
  careerStage: '',
  fundingType: '',
};
export type FilterKey = keyof typeof defaultFilterValues;
export type FilterValues = typeof defaultFilterValues;
