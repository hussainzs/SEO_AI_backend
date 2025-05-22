"""
Write all of the prompts for keywords agent here.
Don't use any explicit system prompts since some models we use don't support them. 
Instead create one prompt which has system instructions and input variables for user input and any other variables.
"""
ENTITY_EXTRACTOR_PROMPT = """
You are an expert in SEO and keyword research. You are given a draft of a news article.
Your job is to extract the most important and representative entities from the article.

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
You are an expert in SEO and keyword research. You are given a draft of a news article.
Your job is to use the provided entities which are derived from the article and content of the article to come up with two targeted search queries and generate a tool call optimized to retrieve high-ranking articles closely related to the article's content and topic.

While generating the search queries, please consider the following:
1. the search queries you extract will be used to find competitor articles written about the same topic. Keep this purpose in mind. The search queries will be executed using tool provided to you. Thus you should output a tool call with the search query. 
2. your search queries should be able to identify competitor's articles covering general topic of our user article and specific nuances of the topics as well.
3. make sure two distinct search intent queries are generated. (a) Statement based Broad/Entity Focused Search Query: Use retrieved entities to generate this type of query.
(b) Question based Google Search Query: Formulate common question user might ask related to the topic.
4. your search queries should be consisting of a couple of words (concise and under 400 characters). 
5. The goal is to conduct competitor analysis for our user article and conduct high performing keyword search. Keep all of these purposes of the search queries in mind to determine the best search queries.
6. YOU MUST ALWAYS generate TWO tool calls in your response each with a each type of search query you came up with.

IMPORTANT: 
If you are provided below a history of previous tool calls and their responses, you MUST use the information from the previous tool calls to analyze what was missing in the previous search queries and generate NEW search queries (again of two types but new) to get better results. In this case, take a hollistic view of our user article, the entities, and the previous tool calls and their responses to generate new search queries. Again respond with two tool calls.

IMPORTANT:
YOU MUST ALWAYS RESPOND WITH TWO TOOL CALLS FILLED WITH EACH TYPE OF SEARCH QUERIES you came up with. No other text or explanation is needed. Correctly format tool calls for the tool provided to you.
The only exception is that if you are not provided any tool at all, please respond exactly with "I dont have a tool" and nothing else.

Here are the extracted entities from the article:
{entities}

Here is our user article:
{user_article}

\nHistory of previous tool calls and their responses:
{web_search_results}
"""

ROUTE_QUERY_OR_ANALYSIS_PROMPT = """
You are an SEO expert in keyword research and competitor analysis. You will recieve a user_article, a list of entities and a history of web queries that were executed to find competitors. Your task is to determine whether to generate new search queries or to conduct a competitor analysis based on the provided information.

NOTE: Take a critical look at the web search results and the user article. If you think the web results (titles, urls, content) are good competitors and relevant to the user article then you should route to the competitor analysis node. If you think they are not sufficient for SEO competitor analysis, then you should route to the query generator node that tries to find new competitors.

KEEP IN MIND: You may get 5-10 results for 1-2 search queries. If 8 out of 10 results are good competitors then you should route to the competitor analysis node. Otherwise, you should route to the query generator node.

Here is the user article:
{user_article}

Here are the extracted entities:
{entities}

Here is the history of previous web queries and their responses:
{web_search_results}

"""