# Frontend - Mockups and Initial Project Structure

> Snapshot of the Confluence page [Frontend - Mockups and Initial Project Structure](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/15597569), taken 25 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

### 1. Overview 

This page documents the initial frontend design and implementation of the Find Me Funding web application. The frontend is being developed using React and TypeScript. The initial work has focused on establishing design decisions through Figma mockups, the project structure and implementation of the basic layout of the home page.

### 2. Technologies

React - Frontend Framework 

TypeScript - Type-safe JavaScript 

CSS Modules - Component specific styling

Git/Github - Version control 

Figma - UX/UI 

### 3. Design Mockup

_(Image not included in this snapshot; see the live Confluence page.)_
_(Image not included in this snapshot; see the live Confluence page.)_
Used Figma to create a detailed Mockup of pages in focus in Sprint 2:

**Home Page** is the main interface where a user will conduct a search. They interact with drop down menus which display a list of selection criteria. There is also an expandable description box for the user to add extra details which they feels aren’t encompassed by the drop down selections.

**Search Page** displays search results and clearly shows the selected criteria and the results the user is most eligible for.

* To Discuss: develop Figma Mockup into prototype to import into react project OR use Mockup to inform implementation in React

### 4. Project Structure 

src/  
├── assets/  
│  
├── components/  
│   ├── Dropdown/  
│   │   ├── Dropdown.tsx  
│   │   └── Dropdown.module.css  
│   │  
│   ├── Navbar/  
│    │ ├── Navbar.tsx  
│    │  └── Navbar.module.css

│    └── Result/

│    │ ├── Result.tsx  
│    │  └── Result.module.css  
│  
├── pages/  
│   └── Home/  
│       ├── Home.tsx  
│       └── Home.module.css

│   └── Results/  
│       ├── Results.tsx  
│       └── Results.module.css  
│  
├── App.tsx

├── App.css  
├── main.tsx  
└── index.css

**Assets** contains relevant assets for the project. At this stage empty.

**Components** are separated into their own directories to allow them to be reused throughout the application. So far two components have been created, the dropdown component and the navbar component, each implementing their own CSS Modules.

**CSS Modules** are used to prevent component-specific styles from conflicting with other components. Global styles such as the page background and font are kept in `index.css`.

**Pages** are separated into their own directories and implement different components to construct the user interface.

### 5. Dropdown Component

A dropdown is a react component that accepts a “label” as a prop to describe the contents of the dropdown menu.

_(Image not included in this snapshot; see the live Confluence page.)_Dropdown with label; Citizenship
* To implement: dropdown to display selection criteria upon user click. 

### 6. Navbar Component

The navigation header was initially implemented using custom styling. During development, this was revised to align with the University of Melbourne Design System. The current implementation uses the UoM design system's styling and conventions.

*  https://designsystem.web.unimelb.edu.au/getting-started/ 

### 7. Home Page

Purpose: The Home page provides the initial search interface for users looking for research funding opportunities.

The page currently contains:

* Navigation Bar
* Field of Research dropdown
* Type of Activity dropdown
* Citizenship dropdown
* Employer Type dropdown
* Career Stage dropdown
* Funding Type dropdown
* Free-text research description field
* Search icon

_(Image not included in this snapshot; see the live Confluence page.)_Home Page
### 8. Results Page

Purpose: The Results Page displays relevant search results to the user with important information.

The page currently contains:

* Navigation Bar
* Field of Research dropdown
* Type of Activity dropdown
* Citizenship dropdown
* Employer Type dropdown
* Career Stage dropdown
* Funding Type dropdown
* Indication of how many results returned to user
* Search result: 

    * Result title 
    * Result description
    * Relevant selection criteria identified (TO BE IMPLEMENTED)
    * Eligibility ranking (TO BE IMPLEMENTED)
    

_(Image not included in this snapshot; see the live Confluence page.)_
### 9. Styling 

For consistency and to support extended feature of integration of current UoM websites with our application, we have chosen to adhere closely to the University of Melbourne Gen 3 Design System Style Guide: https://designsystem.web.unimelb.edu.au/style-guide/ 

The University of Melbourne Design System is included globally through `index.html`:

```html
<link rel="stylesheet" href="https://dds-gen3.web.unimelb.edu.au/v15.14.0/uom.css" />
<script src="https://dds-gen3.web.unimelb.edu.au/v15.14.0/uom.js"></script>
```

The UoM Design System provides the project's typography, colours and icon system.

**Icons:** The UoM icon system uses `data-icon` attributes:

```html
<span data-icon="search"></span>
```

The UoM stylesheet applies global styling to elements such as `<input>` and `<p>`. Some component-specific styles therefore need to override the design system's defaults.

**Known issue – UoM icons and React routing** UoM icons are initialised by `uom.js` when the DOM is initially loaded. Since React Router performs client-side navigation without reloading the page, newly rendered `data-icon` elements may not automatically be processed by the UoM icon system. Consequently, icons can appear after a full page refresh but not immediately following client-side navigation.

The solution is to explicitly initialise the relevant UoM components after React renders the new page.

### 10. Current Status

**In development**

The initial layout implementation of the Find Me Funding frontend has been completed for the Home and Search pages. The pages have been implemented in React and styled according to the University of Melbourne Design System and the team's Figma prototype.

The home page currently includes reusable dropdown components, a free-text search field, UoM Design System icons, and navigation to the search results page when a valid search is submitted.

The frontend structure and styling are still subject to refinement as development progresses and the frontend is integrated with the backend API.

### 11. Next Steps

- [ ] Refine results page layout
- [ ] Add interactive states to components 
- [ ] Dropdowns activating selection criteria 
- [ ] Selected criteria displayed in dropdown position


- [ ] **Create API Agreement** to define how data is communicated between front and backend
- [ ] Create mockup data to display with search results page

‌
