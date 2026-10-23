# Frontend - Mock search flow and interactive elements

> Snapshot of the Confluence page [Frontend - Mock search flow and interactive elements](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/21921793), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

## Overview

 

Added a frontend mock search flow designed to simulate how the application would behave once a backend is available. The purpose of this implementation is to allow the user interface to be developed and tested before the backend is fully connected.

 

The mock flow is intentionally lightweight and does not replace the real backend. It mirrors the expected data contract and user journey so that the frontend can demonstrate how search, filtering, and results rendering would work in practice.

 

## This mock layer was created to:

 

* simulate how results would be returned from a backend

* allow the user to test the UI flow

* define the frontend contract around known crawler data

* keep the UI logic separate from the mock data source so it can later be replaced with a real API call

 

This approach helps maintain a clean handoff between frontend and backend work while the backend is still being developed.

 

 

## Technologies used

‌

The mock search flow is built using the existing frontend stack:

 

* React for the user interface

* TypeScript for typed data structures and safer state management

* React Router for routing between the search and results screens

* CSS modules for component styling

* A lightweight local mock service to simulate backend responses

 

This keeps the project consistent with the current stack while allowing a realistic demo flow to be built without introducing additional frameworks or dependencies.

 

##  Application flow

The mock search flow follows:

1. The user selects filters on the search page.

2. The user enters a keyword or leaves the search blank.

3. The search triggers navigation to a results page.

4. The results page reads the selected filters and keyword.

5. A mock service returns a list of results in the shape expected by the frontend.

6. The results are rendered as cards with key information such as title, funding amount, deadline, and eligibility context.

 

This mirrors the expected product behaviour of a real search experience while remaining intentionally decoupled from backend implementation details.

 

## Data model

 

The mock results are shaped to match the data produced by the crawler. This includes:

 

* opportunity title

* source URL

* raw page text

* deadline raw text

* parsed deadline

* funding amount

* eligibility snippet

* source query

 

This ensures the frontend is aligned with the data structure already being produced by the crawler, rather than inventing a separate schema that would later need to be reworked.

‌

## Components and responsibilities

 

The implementation is split into separate concerns:

 

Search page:

* displays the filter controls

* captures user-selected values

* collects the text search

* submits the request to the results view

 

Results page:

* reads the selected search criteria

* triggers a fresh mock search

* displays the returned results

* allows the user to refine the search again

 

Dropdown component:

* provides reusable filtering UI

* shows available option values

* stores the selected choice in local state

 

Mock service:

* acts as a stand-in for backend API logic

* returns dummy funding opportunity data

* applies simple filtering logic based on search text and selected values

 

## Filtering behaviour

 

The filtering in the mock layer is intentionally simple. It filters results based on:

 

* keyword presence in opportunity title or body text

* selected search criteria such as research area, funding type, and career stage

 

This is not a production-ranking system. It is a temporary UI-level approximation designed to demonstrate how search and filtering would behave when the real API becomes available.

 

## Limitations

This implementation should be treated as a demonstration layer, not a final product backend.

Current limitations include:

* data is static and locally mocked

* filtering is rule-based and simplified

* no real backend endpoint is involved

* the set of valid options is demo-only and not verified against a final API contract

* no persistence or live search indexing is implemented

 

These limitations are intentional, as the goal is to simulate the search experience without overcommitting to backend design decisions.

 

## Future integration path

 

Once the backend is ready, the mock service can be replaced with a real API call while the rest of the interface remains the same. This is the main benefit of the current approach: the UI is already structured around a defined data contract, so switching to real data should only require replacing the service implementation rather than redesigning the screens.

‌
