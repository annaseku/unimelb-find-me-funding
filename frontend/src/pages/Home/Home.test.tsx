import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Home from './Home';
import { defaultFilterValues } from '../../data/filterOptions';

const dropdownLabels = [
  'Field of Research',
  'Type of Activity',
  'Citizenship',
  'Employer Type',
  'Career Stage',
  'Funding Type',
];

const searchPlaceholder = 'What kind of research are you searching for funding for?';

function LocationProbe() {
  const location = useLocation();
  return <pre data-testid="state">{JSON.stringify(location.state)}</pre>;
}

function renderHome() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

function readNavigatedState() {
  return JSON.parse(screen.getByTestId('state').textContent ?? 'null');
}

describe('Home', () => {
  it('renders the six filter dropdowns and the search input', () => {
    renderHome();

    dropdownLabels.forEach((label) => {
      expect(screen.getByText(`${label} – Any`)).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText(searchPlaceholder)).toBeInTheDocument();
  });

  it('labels the submit button "Search funding" for assistive tech', () => {
    renderHome();

    expect(screen.getByRole('button', { name: 'Search funding' })).toHaveTextContent('Search');
  });

  it('navigates to /results with the typed search and default filters when nothing is picked', async () => {
    const user = userEvent.setup();
    renderHome();

    await user.type(screen.getByPlaceholderText(searchPlaceholder), 'coral reefs');
    await user.click(screen.getByRole('button', { name: 'Search funding' }));

    expect(readNavigatedState()).toEqual({
      search: 'coral reefs',
      filters: defaultFilterValues,
    });
  });

  it('carries picked filter values in state and leaves the rest default', async () => {
    const user = userEvent.setup();
    renderHome();

    await user.click(screen.getByText('Field of Research – Any'));
    //await user.click(screen.getByRole('radio', { name: 'Ecology' }));
    await user.click(screen.getByRole('radio', { name: 'Biological Sciences' }));
    await user.click(screen.getByText('Career Stage – Any'));
    await user.click(screen.getByRole('radio', { name: 'Postdoctoral (2-5 years)' }));

    await user.click(screen.getByRole('button', { name: 'Search funding' }));

    const state = readNavigatedState();
    expect(state.filters).toEqual({
      ...defaultFilterValues,
      fieldOfResearch: '31',
      careerStage: 'postdoc_2_5',
    });
  });
});
