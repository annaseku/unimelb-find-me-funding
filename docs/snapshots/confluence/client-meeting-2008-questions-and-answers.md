# Client Meeting 20/08: Questions and Answers

> Snapshot of the Confluence page [Client Meeting 20/08: Questions and Answers](https://annaseku01.atlassian.net/wiki/spaces/Crawlers/pages/7733249), taken 23 October 2026. The live page needs an Atlassian login. The client is referred to by role, not by name.

‌

**Question:** What exactly do you mean by dynamic web crawling? Do you expect the system to discover completely new funding websites, or is regularly updating a broad collection of funding sources sufficient?   
  
Answer:  Data needs to be fresh and as global as possible

  
**Question:** How fresh do the funding results need to be? Would daily updates be sufficient, or do you expect near-real-time results?

Answer: Close to real time results

  
**Question:** How strict should eligibility matching be? If an opportunity appears highly relevant but one eligibility requirement cannot be verified, should it be excluded or shown as unknown? :

Answer: include it

strict bubble options, LLM handles complex projects

  
**Question:** Should opportunities that are likely ineligible ever be shown to the user, or should they be completely hidden?

Answer:  He once again said it’s tricky, but thats where an LLM might be useful

  
**Question:** Should Australian funding opportunities be prioritised over international opportunities, or should opportunities from anywhere in the world be treated equally?

Answer:  Not prioritised just within english and citizenship eligibilty.   
Jummana: can prioritise based on project description/country

‌

**Question:** What criteria is important to you when analyzing a source of funding? 

Answer: Didn’t ask I felt like its a vague question. 

  
**Question:** Do you still want users to be able to search using another researcher's profile rather than only their own? 

Answer: unimelb access too hard to verify. Therefore, unique profiles to save preferences etc. ideally, anyone can filiter using anyone's projects.

  
**Question:** If the crawler finds an opportunity but cannot determine its eligibility, funding amount, or deadline, should the system show it as unknown, exclude it, or try to find the information elsewhere?

Answer:  Ideally try to find information 

‌

Unanswered Questions:

**Question:** What should happen when the system cannot confidently determine whether a researcher is eligible for an opportunity? Should it be classified as unknown, excluded, or shown lower in the results?

If the same funding opportunity appears on multiple websites, should the system combine those into one result?

‌

What should happen when a funding webpage disappears or an opportunity closes? Should the system remove it immediately or retain it with a warning?

‌

What information would you expect to see for each funding opportunity before deciding whether to click through to the original website?

‌

Would you like the system to explain why an opportunity received its ranking, or are the four individual ratings enough?

‌

When a user asks for more than the top 10 results, should the system return the next results from the existing search or perform additional discovery/crawling?

‌

Should users be able to adjust individual search criteria after seeing their results without starting a completely new search?

‌

Would you prefer the system to return fewer opportunities with high confidence, or more opportunities where some information may be uncertain?

  
Looking at the GrantForward example, what parts of the search experience do you want our system to emulate?

  
Looking at the GrantForward example, is there anything about the search experience that you specifically do not want?

  
Are there particular types of funding organisations or websites that you consider especially important to include in the system's discovery?

‌

Should eligibility act as a hard filter, or should it simply have the highest weight in the ranking?

‌

How should eligibility, research match, funding value, and deadline be prioritised relative to each other?
