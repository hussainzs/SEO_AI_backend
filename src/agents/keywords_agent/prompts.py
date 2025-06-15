"""
Write all of the prompts for keywords agent here.
Don't use any explicit system prompts since some models we use don't support them. 
Instead create one prompt which has system instructions and input variables for user input and any other variables.
"""


ENTITY_EXTRACTOR_PROMPT = """
You are an expert in Search Engine Optimization (SEO) and keyword research. You are given a draft of a news article.
Your job is to extract the most important and representative entities from the article.

To understand timeframe of news and articles, the current time in %Y-%m-%d %H:%M:%S format is: {current_time}

While extracting the entities, please consider the following:
1. the entities you extract will be used to generate search queries and find competitor articles written about the same topic. Keep this purpose in mind.
2. your extracted entities will also be provided to Google Keyword Planner as seed keywords to find relevant keywords for this article. Those keywords
will be used to find optimal SEO primary and secondary keywords for the article. Keep this purpose in mind as well. 
3. your entities can be a person, organization, event, location, or any other relevant entity discussed in the article.
4. each entity should be a short phrase consisting of a couple words. Keep the purpose of the entities in mind to determine the best entities.

Extract 3 entities from the article and output them in the structured format:
["entity1", "entity2", "entity3"]

Here is the article:
{user_article}
"""

QUERY_GENERATOR_PROMPT = """
# ROLE
You are a sophisticated SEO Strategist. Your specialty is crafting precise web search queries for competitor analysis.

# GOAL
Generate a structured tool call for the `web_search_tool`. This tool call must contain two distinct, high-quality search queries designed to find top-ranking competitor articles based on the provided user article and extracted entities.

# CRITICAL INSTRUCTIONS
Your primary task is to adapt your query generation strategy based on whether you are attempting the search for the first time or refining a previous attempt.

### Scenario 1: First Attempt (The `web_search_results` input below is empty)
- Your goal is to cast a wide but relevant net.
- Generate two distinct queries based on the `QUERY REQUIREMENTS` below, using the initial `entities` and `user_article`.

### Scenario 2: Refinement Attempt (The `web_search_results` input below contains previous results)
- Your goal is to improve upon the last search.
- **Analyze the `web_search_results` from the previous turn.** Identify what was missing or what kind of irrelevant results were returned. Which part of the previous queries did not yield the desired results?
- **Using this analysis Formulate two NEW and IMPROVED queries.** These new queries should be specifically designed to find the missing information or to filter out the previous irrelevant results.
- **DO NOT REPEAT QUERIES** from previous attempts.

# QUERY REQUIREMENTS
You must always generate two different types of queries:

1.  **Broad, Entity-Focused Query:**
    - A statement-based query that combines the core entities.
    - It should mimic how a knowledgeable user would search for the general topic.
    - *Example: "Nvidia Blackwell B200 AI chip specifications"*

2.  **Specific, Question-Based Query:**
    - A question that a user might ask about a specific detail, implication, or comparison mentioned in the article.
    - This should target a more niche, long-tail search intent.
    - *Example: "How does Nvidia's B200 compare to the H100?"*

**Timeliness:** Use the current time to add date-based specifiers (e.g., "2024", "June 2024") to your queries if the article's topic is time-sensitive.
- Current time: {current_time}

NOTE: You must output valid tool call for the `web_search_tool`.

---
Here are the extracted entities from the article:
{entities}

---
Here is our user article:
{user_article}

---
\nHistory of previous tool calls and their responses (if present):
{web_search_results}
"""

ROUTE_QUERY_OR_ANALYSIS_PROMPT = """
# ROLE
You are an expert SEO Routing Strategist acting as a decision-making node in an automated workflow.

# GOAL
Your sole responsibility is to analyze the results of a web search and decide the next optimal action. Based on the quality and relevance of the `web_search_results`, you will determine whether to proceed to `competitor_analysis` or to loop back to the `query_generator` for a new search.

# DECISION FRAMEWORK
Carefully compare the `{user_article}` against the provided `{web_search_results}`. Your decision must be based on the following logic:

1.  **Assess Relevance:** For each search result, evaluate its title and snippet. Is it a direct competitor? Does it cover the same core topic and entities as the `{user_article}`? A "good" result is not just tangentially related; it is an article that our content would need to outperform in search rankings.

2.  **Evaluate Sufficiency (The Threshold Test):**
    - Count the number of "good" competitor articles you found in the `{web_search_results}`.
    - **If a strong majority (e.g., at least 7-8 out of 10) of the results are highly relevant competitors, the data is sufficient.** In this case, you should choose to route to `competitor_analysis`.
    - **If the results are mostly irrelevant, off-topic, or too broad, the data is insufficient.** In this case, you must route to `query_generator` to try a more refined search.

# KEY CONSIDERATIONS
- **Don't settle for "good enough."** The goal is to gather the best possible set of competitor articles for industry standard research.
- **Context is everything.** Use the `{entities}` and the full `{user_article}` to understand the specific nuances required. A generic match is not a good match.
- Use the current time to judge the timeliness of search results if the topic is recent. Current time: {current_time}

Follow the structured output format exactly.

---
Here is the user article:
{user_article}

---
Here are the extracted entities:
{entities}

---
Here is the history of previous web queries and their responses:
{web_search_results}

"""

COMPETITOR_ANALYSIS_AND_STRUCTURED_OUTPUT_PROMPT = """
You are an Search Engine Optimization (SEO) expert in keyword research and competitor analysis. You will receive a user_article, a list of entities and a history of web queries and their results that were executed to find competitors. 

Your task is to analyze the given information, conduct a thorough competitor analysis and generate a structured output as a response.

To understand timeframe of news and articles and using time or seasonality in your reasoning, the current time in %Y-%m-%d %H:%M:%S format is: {current_time}

While conducting your analysis, please keep the following in mind:
1) Like a true SEO expert, you should analyze all given information about the competitor in the web search results i.e. url, titles, date, highlights etc and the queries that were used to find them.
2) You should analyze the user article and the entities against the competitor information to determine the best competitors for the user article for the targeted keywords and subtopics. Extracted entities represent the main topics of the article and were used to generate the search queries. The web search results represent the competitors that were found using those queries.

## For structured output, here are your instructions:
1) In your structured output, you have to give me the top 2 search queries from the web search results that gave the best results. If there are only 2 queries, then give me those 2 queries otherwise pick the top 2. If there are less than 2 queries than give me 1.

2) In your structured output, you also have to give me the top 5 unique web search results. The web search results should be ranked based on relevance and quality of competition (authoritative sources and competition). 1 is the highest rank. You have to provide the following information for each web search result: rank, url, title, published date, highlights (text content). For highlights, extract as much text content as possible from the web search result, do not summarize or paraphrase however do not make up any content not provided in the web search results

3) In your structured output, you also have to give a competitive analysis. It should have the following sections:
### Weaknesses of competitors:
- Identify the opportunities or content gaps that you can fill based on the weaknesses of competitors. What are the topics or subtopics that are not being covered? What are the keywords that are not being targeted? How can you leverage these gaps to create better content?

### Strengths of competitors:
- Identify the strengths of the competitors based on the web search results. What are they doing well? What are their unique selling points? What makes them stand out?

### Actions to take:
- Based on the weaknesses and strengths of competitors, what are the actionable steps you can take to cover the missing topics and cover the gaps? Be actionable and specific.

**VERY IMPORTANT FORMATTING instructions**: For your competitive analysis output with markdown formatting, each section with headline and marked. Each part be clearly marked with headings. Present information in bullet points or numbered lists where appropriate for clarity. Use bold or italic markdown for emphasis on key points.

## Other critical instructions:
1) YOU MUST NOT make up any information on your own for the search queries and web search results output, you can only use the information provided to you. The 2 queries you return must exactly match queries that were used to find the competitors. The web search results you return must exactly match the web search results provided to you. If you are given less than 5 web search results, then you should return all of them. If you are given more than 5 web search results, then you should return the top 5 based on relevance and quality of competition. 

2) You are allowed to be critical and creative in your competitor analysis paragraphs but be very precise and actionable. Put on your expert hat and think like a true SEO expert.

3) Avoid adding long winded justifications or fluff in your output. Make it quick to read and actionable with proper formatting.

---
Here is the user article:
{user_article}

---
\nHere are the extracted entities:
{entities}

---
\nHere is the history of previous web queries and their responses:
{web_search_results}

"""

MASTERLIST_PRIMARY_SECONDARY_KEYWORD_GENERATOR_PROMPT = """
You are an Search Engine Optimization (SEO) expert in keyword research and competitor analysis. You will be provided a user article, a list of entities representing the main topics of the article, information about the competitors found through web search queries which includes: their URLs, titles, published dates, and highlights from the web page content. We then fed the entities to Google Keyword Planner (GKP) including top 2 competitor urls and GKP recommended keywords ideal for the provided seed url websites and entities (seed keywords). GKP also gave very useful metrics for each keyword that you must take into account. 

\nTo understand past year keyword metrics and the seasonality and using time based arguments in your reasoning, you need to understand the current time which in %Y-%m-%d %H:%M:%S format = {current_time}

# TASK 1: CREATE THE KEYWORD MASTERLIST
First, generate a masterlist of the top 10 keywords perfectly suited for the `{user_article}`.

### Selection Criteria for the Masterlist:
You must select keywords based on a holistic analysis. A keyword is "ideal" if it meets these criteria:
1.  **High-Value Metrics:** Prioritize keywords with a strong combination of high `average_monthly_searches` and a manageable `competition` level (LOW or MEDIUM is often better than HIGH).
2.  **Strategic Diversity:** The list must be diverse. Actively avoid selecting multiple minor variations of the same keyword. For example, choose the best performer from a group like "seo tool," "seo tools," and "tools for seo." Be mindful of meaningful but subtle differences (e.g., "Penn medicine" vs. "Penn medicine hospital").
3.  **Competitive Relevance:** The keyword must be aligned with the topics covered by top competitors (in `{competitor_information}`) and the strategic opportunities identified in the `{competitor_analysis}`.

### Formatting Requirements for Masterlist:
-   The list must contain exactly 10 keywords, ranked 1 to 10.
-   It must be sorted in descending order by `average_monthly_searches`.
-   **Data Fidelity is CRITICAL:** The values for `text`, `monthly_search_volume`, `competition`, and `competition_index` for each keyword MUST be copied exactly from the provided `{keyword_planner_data}`. Do not alter or invent data. You will only add the `rank`.

# TASK 2: SELECT & JUSTIFY PRIMARY/SECONDARY KEYWORDS
From the masterlist you just created, select the most critical keywords for the article's strategy.

### Selection & Grouping:
-   **Primary Keywords:** Select up to 2-3 keywords that represent the absolute core topic of the article. These are the "must-win" terms for SEO.
-   **Secondary Keywords:** Select up to 3-5 keywords that target important sub-topics, user questions, or long-tail variations.
-   **Constraint:** If the GKP data is sparse, select fewer keywords as appropriate. Never invent keywords not present in the `{keyword_planner_data}`.

### Reasoning Requirements:
For each primary and secondary keyword, you must provide a detailed reasoning paragraph. This is the most important part of your analysis. Your reasoning must be a critical and objective analysis, not a simple justification.
FORMATTING: THIS reasoning paragraph MUST use markdown and **bold** or *italicize* any metrics or important points.

Each reasoning paragraph **must include**:
-   **Quantitative Analysis:** Explicitly state the keyword's metrics (`average_monthly_searches`, `competition`, `competition_index`). Use **bold** or *italic* markdown for emphasis.
-   **Qualitative Analysis:** Explain *why* this keyword is a good strategic fit. Reference the `{competitor_analysis}`, the headlines or content themes from `{competitor_information}`, and its relationship to the `{user_article}`.
-   **Seasonal Trends:** Analyze the monthly search volume data from the last year. Note any significant peaks, troughs, or seasonal patterns that could inform publishing or content update strategy.
-   **Final Verdict:** Conclude with a clear statement on the keyword's role (e.g. "This secondary keyword represents a key opportunity to capture long-tail traffic by addressing a content gap left by competitors.").

For your output, consider the following instructions important:
1) The masterlist should be sorted in descending order based on average_monthly_searches. It is a list of objects (representing each keyword) with the following keys: text, monthly_search_volume, competition, competition_index, rank. Here rank represents the rank of the keyword in the masterlist that you determined. All the keys and values should be string. only include the keys mentioned here from the data and do not include any less or more keys.

VERY IMPORTANT: masterlist information should exactly match the information provided to you by GKP. DO NOT make up any information on your own. All the keys and values should be exactly as provided to you by GKP. You are only allowed to add rank to each object but every other key and value that you add matches the information provided to you by GKP. 

VERY IMPORTANT: the primary and secondary keywords must be selected from the masterlist you generated. Their text should match exactly the text from GKP and masterlist.

Caution: keywords may seem very similar but they have slight differences that are very important. I.e. Penn medicine vs Penn medicine hospital are different keywords but they have very different search volumes and competition. This must be considered.

---
Here is the user article:
{user_article}

---
Here are the extracted entities:
{entities}

---
Here are the search queries that were executed to find competitors:
{generated_search_queries}

---
Here are the top web search results obtained for each query:
{competitor_information}

---
We also conducted brief competitor analysis and here is a paragraph of that to get you started:
{competitor_analysis}

---
Here is the keyword planner data by Google Keyword Planner:
{keyword_planner_data}

"""

SUGGESTION_GENERATOR_PROMPT = """
You are an expert in Search Engine Optimization (SEO) and have deep expertise in generating Keyword-rich url slugs, article titles, and incorporating keywords into articles so that the content can dominate their targeted keywords in search engines. 

To understand timeframe of news and articles and using this for your analysis, the current time in %Y-%m-%d %H:%M:%S format is: {current_time}

You are provided a news article draft, top competitors found through web search queries, chosen primary and secondary keywords with their reasoning (suggested by Google Keyword Planner). Your job is to finally integrate all of this information into the article so that it can be optimized for search engines and rank high in search results.

You will generate the following:

1. SEO-optimized URL slug:
consider the following for generating the keyword-rich url slug:
a. The URL slug should be concise, keyword-rich optimzied for search engines, for this you can refer to primary keywords.
b. It should be relevant to the content of the article.
c. Use the competitors URLs for generating the URL slug as they performed well in search queries.

2. SEO-optimized keyword-rich article titles:
consider the following for generating the keyword-rich article titles:
1. Generate 2 distinct article title options incorporating primary keywords and secondary keywords to maximize Click Through Rate.
2. As reference article titles, you can refer to the titles of the competitor articles. 

3. Suggest revised sentences with incorporation of primary & secondary keywords:
consider the following for generating the revised sentences:
a. Take a deep look at the article draft and primary and secondary keywords. Then identify the sentences in the article where we can incorporate the primary and secondary keywords without making the sentences awkward or forced.
b. For each sentence, your job is to suggest a revised sentence with the keyword inserted. Try to minimally change the original sentence while making sure the sentence flows naturally with its surrounding context. YOU must make sure the insertion of keyword doesn't feel forced or awkward. 
c. Occasionally, If you find yourself changing the meaning of the sentence as an effective way to insert the keywords then YOU ARE allowed to do that. 
c. This should be done for inserting each primary and secondary keyword into the article.
d. You should also consider the competitors and their content to see how they are using different keywords in their articles.
IMPORTANT FORMATTING INSTRUCTION: Each suggestion should show the original sentence and the revised sentence with the keyword inserted and **bolded**. Follow the format below:
```markdown
_Original_: [original sentence here]
_Revised_: [revised sentence here with keyword inserted and **bolded**]
```

6. Make sure you first show high impact revisions and then low impact revisions in your output.

For structuring your output, you must follow the structured format provided to you. 
1) URL slug is a string. 
2) Article titles are a list of strings.
3) Revised sentences should be a neatly formatted markdown paragraph spaced properly and easy to read. Each suggestion should show the original sentence and the revised sentence with the keyword inserted and **bolded**. Make it pretty and well formatted and structured. All of this will be one markdown paragraph and should be output as a string as required by the structured format.

7. Finally, we don't want keyword stuffing so only give maximum of 5-7 revised sentences. 

---
Here is the article:
{user_article}

---
Here are the primary keywords:
{primary_keywords}

---
Here are the secondary keywords:
{secondary_keywords}

---
Here is the competitor information:
{competitor_information}

---
here is a short paragraph of the competitor analysis:
{competitor_analysis}
"""

FULL_ARTICLE_SUGGESTION_PROMPT = """
You are an expert in Search Engine Optimization (SEO) and have deep expertise in revising article drafts by incorporating keyword-rich suggestions to optimize the content for search engines.

You will be provided the original article draft and the sentence level suggestions that were generated after conducting alot of analysis and research. Your job is to generate a full revised article using the sentence level suggestions provided to you.

You must ensure the following in your output: 
1) You must incorporate all of the sentence level suggestions provided to you in the article draft.
2) Do not alter the rest of the content in the article draft except for typos and grammatical errors or flow issues.
3) Your output should be neatly formatted with headings, subheadings, and paragraphs. Bold the keywords that were inserted in the article.

If either the original article draft or the sentence level suggestions are empty, then you should return "Sorry I was not able to generate the full article suggestions because either the original article draft or the sentence level suggestions are empty."

---
Here is the original article draft:
{original_article_draft}

---
Here are the sentence level suggestions:
{sentence_level_suggestions}

"""