export interface FilterOption { value: string; label: string }

export const filterOptions = {
  fieldOfResearch: [
    // ANZSRC 2020 FoR divisions (ABS anzsrc2020_for.xlsx)
    { value: '30', label: 'Agricultural, Veterinary and Food Sciences' },
    { value: '31', label: 'Biological Sciences' },
    { value: '32', label: 'Biomedical and Clinical Sciences' },
    { value: '33', label: 'Built Environment and Design' },
    { value: '34', label: 'Chemical Sciences' },
    { value: '35', label: 'Commerce, Management, Tourism and Services' },
    { value: '36', label: 'Creative Arts and Writing' },
    { value: '37', label: 'Earth Sciences' },
    { value: '38', label: 'Economics' },
    { value: '39', label: 'Education' },
    { value: '40', label: 'Engineering' },
    { value: '41', label: 'Environmental Sciences' },
    { value: '42', label: 'Health Sciences' },
    { value: '43', label: 'History, Heritage and Archaeology' },
    { value: '44', label: 'Human Society' },
    { value: '45', label: 'Indigenous Studies' },
    { value: '46', label: 'Information and Computing Sciences' },
    { value: '47', label: 'Language, Communication and Culture' },
    { value: '48', label: 'Law and Legal Studies' },
    { value: '49', label: 'Mathematical Sciences' },
    { value: '50', label: 'Philosophy and Religious Studies' },
    { value: '51', label: 'Physical Sciences' },
    { value: '52', label: 'Psychology' },
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
