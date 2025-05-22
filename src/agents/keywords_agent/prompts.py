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

COMPETITOR_ANALYST_PROMPT = """
You are an expert in SEO and keyword research. You are given a draft of a news article.
Your job is to use the provided entities which are derived from the article and content of the article to come up with two targeted search queries optimized to retrieve
high-ranking articles closely related to the article's content and topic.

While generating the search queries, please consider the following:
1. the search queries you extract will be used to find competitor articles written about the same topic. Keep this purpose in mind.
2. your search queries should be able to identify competitor's articles covering general topic our article is covering & those articles address similar specific nauances.  
3.make sure two distinct search intent queries are generated. (a) Statement based Broad/Entity Focused Search Query: Use retrieved entities to generate this type of query. 
(b) Question based Google Search Query: Formulate common question user might ask related to the topic.
4. your search queries should be consisting of a couple of words. Keep the purpose of the search queries in mind to determine the best search queries.

Generate 2 search queries for the article and output them in the structured format:
["search_query1", "search_query2"]

Here are the entities:
{entities}
Here is the article:
{user_article}

"""