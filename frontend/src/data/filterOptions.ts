export const filterOptions = {
  fieldOfResearch: [
    'Marine Biology',
    'Climate Science',
    'Biotechnology',
    'Computer Science',
    'Physics',
  ],
  typeOfActivity: [
    'Experimental Research',
    'Fieldwork',
    'Computational Research',
    'Equipment Purchase',
    'Travel',
  ],
  citizenship: ['Australian', 'International', 'Any'],
  employerType: ['University', 'Industry', 'Hospital', 'Any'],
  careerStage: ['Undergraduate', 'Graduate Student', 'Postdoc 0-2', 'Postdoc 2-5', 'Postdoc 5-10'],
  fundingType: ['Equipment', 'Salary', 'Consumables', 'Any'],
};

export const defaultFilterValues = {
  fieldOfResearch: '',
  typeOfActivity: '',
  citizenship: '',
  employerType: '',
  careerStage: '',
  fundingType: '',
};

export type FilterKey = keyof typeof defaultFilterValues;
