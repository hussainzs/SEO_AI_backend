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

MASTERLIST_AND_PRIMARY_KEYWORD_GENERATOR_PROMPT = """
You are an expert in SEO and keyword research. You are given a draft of a news article in user input, entities, and google keyword planner data which contains keywords and their metrics related to their monthly_search_volumes.
Your job is to use the provided entities which are derived from the article and content of the article in user input, and competitive analysis, in order to analyze the keywords given in google keyword planner data to evaluate relevance of each keyword. 
Now, after evaluating relevance to content of article and competitiveness of each keyword based on the monthly_search_volumes, you will generate a masterlist of upto 20 keywords.
While generating the keywords, please consider the following:
1. masterlist of keywords you extract will be used to find the primary and secondary keywords for the article. keep this purpose in mind.
2. Make sure you look at the metrics of each keyword.
3. Make sure you also consider the relevance of each keyword to the content of the article, and in context of competitive analysis.
4. Pick up to 20 keywords for the masterlist based on the above two points.
5. Make sure there are no duplicates in the masterlist.
6. The keywords in the masterlist should be sorted in descending order based on their monthly_search_volumes.

Generate a masterlist of keywords and output them in the structured format:
[{"keyword1": "monthly_search_volumes", "keyword2": "monthly_search_volumes" "keyword3":"monthly_search_volumes", ...}]

7. Then, pick 3-5 primary keywords from the masterlist. 
Please consider the following for choosing primary keywords:
1. Primary keywords are those keywords for which we want our article to rank for. 
2. They should have a balanced search volume and relevance to the content of the article.
3. Each primary keyword should ideally target a significant facet of the article.
4. Reasoning should be provided for each secondary keyword as well. It should be based on the relevance to the article, google planner data , and competitive analysis.

Generate a list of primary keywords and output them in the structured format by giving keyword and reasoning:
["primary_keyword1": "reasoning", "primary_keyword2":"reasoning", "primary_keyword3":"reasoning", ...]

8. Then, pick 3-5 secondary keywords from the masterlist.
Please consider the following for choosing secondary keywords:
1. These are variations, long-tail versions, synonyms, or related sub-topics to your primary keywords.
2. They help build topical authority and capture more specific searches.
3. They generally have lower volume but can be less competitive and highly relevant.
4. Each will be judged based on its own google planner data metrics.
5. Reasoning should be provided for each secondary keyword as well. It should be based on the relevance to the article, google planner data , and competitive analysis.

Generate a list of secondary keywords and reasoning output them in the structured format:
["secondary_keyword1":"reasoning", "secondary_keyword2":"reasoning", "secondary_keyword3":"reasoning", ...]

Here is the article:
{user_article}
Here are the entities:
{entities}
Here is the google planner data:
{gkp_data}
Here is the competitive analysis:
{competitive_analysis}
"""

SUGGESTION_GENERATOR_PROMPT = """
You are an expert in SEO and have expertise in generating Keyword-rich url slugs, article titles, and in suggesting revised sentences with incorporation of 
primary & secondary keywords, all these things with the goal of SEO Optimization. You are given a draft of a news article in user input, competitor information which includes competitor URLs and their titles, 
primary_keywords and secondary_keywords which contains keywords and their reasoning related to the article. Using this information, you will generate the following:

1. SEO-optimized URL slug:
consider the following for generating the keyword-rich url slug:
1. The URL slug should be concise, keyword-rich optimzied for search engines, for this you can refer to primary keywords.
2. It should be relevant to the content of the article.
3. Use the competitors URLs for generating the URL slug.

Generate the output for this in the structured format:
"url_slug": "keyword-rich-url-slug"

2. SEO-optimized keyword-rich article titles:
consider the following for generating the keyword-rich article titles:
1. Generate 2 distinct article title options incorporating primary keywords and secondary keywords to maximize Click Through Rate.
2. As reference article titles, you can refer to the titles of the competitor articles. 
3. Make sure the titles are rlevant to the content of the article.

Generate the ourput for this in the structured format:
["article_title1", "article_title2"]

3. Suggest revised sentences with incorporation of primary & secondary keywords:
consider the following for generating the revised sentences:
1. You need to identify & provide specific places (at least 1 or 2) at the sentence level in the user input where keywords can be inserted. You need to do this for each of the keyword present in the primary & secondary keywords.
2. Make sure you identify the most relevant sentences in the article where the keywords can be inserted. 
3. Make sure you do not miss any keyword in the primary & secondary keywords.
4. When you insert the keyword in the sentence you need to make sure you do not change the meaning of the original sentence. You insert the keyword with the minimal change in the tone & style of the original sentence. Just make sure then sentence is clear and conveys the same meaning and makes sense.
5. For each revised sentence,  you need to classify them as either Critical SEO Boost (High Impact) or Minor Enhancement (Low Impact).

Generate the output for this in the structured format:
Original sentence: "Existing sentence from the user input"
Revised sentence with keyword: "Revised sentence with keyword inserted"

Here is the article:
{user_article}
Here is the competitor information:
{competitor_information}
Here are the primary keywords:
{primary_keywords}
Here are the secondary keywords:
{secondary_keywords}
"""
