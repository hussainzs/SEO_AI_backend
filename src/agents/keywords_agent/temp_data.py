from langchain_core.messages import AIMessage

query_generator_ai_message = [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'fRvBlnQ6B', 'function': {'name': 'web_search_tool', 'arguments': '{"query": "Michael Mann defamation case legal fees"}'}, 'index': 0}, {'id': 'TON9yA0tZ', 'function': {'name': 'web_search_tool', 'arguments': '{"query": "What are the latest updates on Michael Mann defamation case and legal fees"}'}, 'index': 1}]}, response_metadata={'token_usage': {'prompt_tokens': 1490, 'total_tokens': 1536, 'completion_tokens': 46}, 'model_name': 'mistral-medium-2505', 'model': 'mistral-medium-2505', 'finish_reason': 'tool_calls'}, id='run--03439be1-b718-4598-8fb4-d3c0356b7218-0', tool_calls=[{'name': 'web_search_tool', 'args': {'query': 'Michael Mann defamation case legal fees'}, 'id': 'fRvBlnQ6B', 'type': 'tool_call'}, {'name': 'web_search_tool', 'args': {'query': 'What are the latest updates on Michael Mann defamation case and legal fees'}, 'id': 'TON9yA0tZ', 'type': 'tool_call'}], usage_metadata={'input_tokens': 1490, 'output_tokens': 46, 'total_tokens': 1536})]

query_generator_search_queries = [
    "Undergrad Employment trends and AI impact on job market",
    "How is AI affecting job prospects for recent college graduates?"
]

query_generator_tool_call_count = 1

router_web_search_results_accumulated = "\n\nSearch Query: Undergrad Employment trends and AI impact on job market\n[{'url': 'https://www.cnbc.com/2025/05/16/how-college-grads-can-find-a-job-in-a-tough-market.html', 'title': \"College grads face a 'tough and competitive' job market this year, expert says - CNBC\", 'score': 0.2830381, 'published_date': 'Fri, 16 May 2025 10:40:01 GMT', 'highlights': 'A majority, 62%, of the Class of 2025 are concerned about what AI will mean for their jobs, compared to 44% two years ago, according to a survey by Handshake.'}, {'url': 'https://www.hrdive.com/news/2025-raises-lower-than-expected/747142/', 'title': '2025 raises fell short of employers’ recent projections, Mercer finds - HR Dive', 'score': 0.19355896, 'published_date': 'Mon, 05 May 2025 21:00:53 GMT', 'highlights': 'Pay expectations for recent graduates aren’t being met either, according to an April ZipRecruiter report. About 42% of recent graduates said they didn’t get the pay they wanted in their job search.'}, {'url': 'https://www.post-gazette.com/news/education/2025/05/13/penn-state-campus-closures-fayette-new-kensington-shenango/stories/202505130066', 'title': 'Penn State proposes 7 campus closures, including 3 in Pittsburgh region - Pittsburgh Post-Gazette', 'score': 0.12024263, 'published_date': 'Tue, 13 May 2025 20:21:41 GMT', 'highlights': 'Enrollment drops at the commonwealth campuses have been a yearslong struggle. At Western Pennsylvania campuses between fall 2020 and fall 2024, student declines have varied from 7% (Penn State Behrend in Erie) to 29% (Penn State Fayette).'}, {'url': 'https://www.post-gazette.com/sports/paul-zeise/2025/05/12/aaron-rodgers-nevillewood-steelers-offseason/stories/202505120061', 'title': 'Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining - Pittsburgh Post-Gazette', 'score': 0.094719745, 'published_date': 'Mon, 12 May 2025 23:38:05 GMT', 'highlights': '1 news Penn State pushes back against report detailing possible campus closures Mon, May 12, 2025, 11:50pm Megan Tomasic 2 sports Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining Mon, May 12, 2025, 11:38pm Paul Zeise 3 sports Instant analysis: Pirates lose to Mets on Pete Alonso sacrifice fly Tue, May 13, 2025, 2:14am Colin Beazley 4 business Student debt will follow him to the grave — and he still makes payments Mon, May 12.'}, {'url': 'https://www.post-gazette.com/sports/pirates/2025/05/14/pirates-mets-bryan-reynolds-mitch-keller-loss/stories/202505130046', 'title': '3 takeaways: Pirates have a Bryan Reynolds problem right now - Pittsburgh Post-Gazette', 'score': 0.08716692, 'published_date': 'Wed, 14 May 2025 04:19:22 GMT', 'highlights': \"1 news Pittsburgh International Airport's new terminal is nearly complete Wed, May 14, 2025, 12:33am.\"}]\n\nSearch Query: How is AI affecting job prospects for recent college graduates?\n[{'url': 'https://www.cnbc.com/2025/05/16/how-college-grads-can-find-a-job-in-a-tough-market.html', 'title': \"College grads face a 'tough and competitive' job market this year, expert says - CNBC\", 'score': 0.2830381, 'published_date': 'Fri, 16 May 2025 10:40:01 GMT', 'highlights': 'A majority, 62%, of the Class of 2025 are concerned about what AI will mean for their jobs, compared to 44% two years ago, according to a survey by Handshake.'}, {'url': 'https://www.hrdive.com/news/2025-raises-lower-than-expected/747142/', 'title': '2025 raises fell short of employers’ recent projections, Mercer finds - HR Dive', 'score': 0.19355896, 'published_date': 'Mon, 05 May 2025 21:00:53 GMT', 'highlights': 'Pay expectations for recent graduates aren’t being met either, according to an April ZipRecruiter report. About 42% of recent graduates said they didn’t get the pay they wanted in their job search.'}, {'url': 'https://www.post-gazette.com/news/education/2025/05/13/penn-state-campus-closures-fayette-new-kensington-shenango/stories/202505130066', 'title': 'Penn State proposes 7 campus closures, including 3 in Pittsburgh region - Pittsburgh Post-Gazette', 'score': 0.12024263, 'published_date': 'Tue, 13 May 2025 20:21:41 GMT', 'highlights': 'Enrollment drops at the commonwealth campuses have been a yearslong struggle. At Western Pennsylvania campuses between fall 2020 and fall 2024, student declines have varied from 7% (Penn State Behrend in Erie) to 29% (Penn State Fayette).'}, {'url': 'https://www.post-gazette.com/sports/paul-zeise/2025/05/12/aaron-rodgers-nevillewood-steelers-offseason/stories/202505120061', 'title': 'Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining - Pittsburgh Post-Gazette', 'score': 0.094719745, 'published_date': 'Mon, 12 May 2025 23:38:05 GMT', 'highlights': '1 news Penn State pushes back against report detailing possible campus closures Mon, May 12, 2025, 11:50pm Megan Tomasic 2 sports Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining Mon, May 12, 2025, 11:38pm Paul Zeise 3 sports Instant analysis: Pirates lose to Mets on Pete Alonso sacrifice fly Tue, May 13, 2025, 2:14am Colin Beazley 4 business Student debt will follow him to the grave — and he still makes payments Mon, May 12.'}, {'url': 'https://www.post-gazette.com/sports/pirates/2025/05/14/pirates-mets-bryan-reynolds-mitch-keller-loss/stories/202505130046', 'title': '3 takeaways: Pirates have a Bryan Reynolds problem right now - Pittsburgh Post-Gazette', 'score': 0.08716692, 'published_date': 'Wed, 14 May 2025 04:19:22 GMT', 'highlights': \"1 news Pittsburgh International Airport's new terminal is nearly complete Wed, May 14, 2025, 12:33am.\"}]"

competitor_information = [
    {
      "rank": 1,
      "url": "https://www.cnbc.com/2025/05/16/how-college-grads-can-find-a-job-in-a-tough-market.html",
      "title": "College grads face a 'tough and competitive' job market this year, expert says - CNBC",
      "published_date": "Fri, 16 May 2025 10:40:01 GMT",
      "highlights": "A majority, 62%, of the Class of 2025 are concerned about what AI will mean for their jobs, compared to 44% two years ago, according to a survey by Handshake."
    },
    {
      "rank": 2,
      "url": "https://www.hrdive.com/news/2025-raises-lower-than-expected/747142/",
      "title": "2025 raises fell short of employers’ recent projections, Mercer finds - HR Dive",
      "published_date": "Mon, 05 May 2025 21:00:53 GMT",
      "highlights": "Pay expectations for recent graduates aren’t being met either, according to an April ZipRecruiter report. About 42% of recent graduates said they didn’t get the pay they wanted in their job search."
    },
    {
      "rank": 3,
      "url": "https://www.post-gazette.com/news/education/2025/05/13/penn-state-campus-closures-fayette-new-kensington-shenango/stories/202505130066",
      "title": "Penn State proposes 7 campus closures, including 3 in Pittsburgh region - Pittsburgh Post-Gazette",
      "published_date": "Tue, 13 May 2025 20:21:41 GMT",
      "highlights": "Enrollment drops at the commonwealth campuses have been a yearslong struggle. At Western Pennsylvania campuses between fall 2020 and fall 2024, student declines have varied from 7% (Penn State Behrend in Erie) to 29% (Penn State Fayette)."
    },
    {
      "rank": 4,
      "url": "https://www.post-gazette.com/sports/paul-zeise/2025/05/12/aaron-rodgers-nevillewood-steelers-offseason/stories/202505120061",
      "title": "Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining - Pittsburgh Post-Gazette",
      "published_date": "Mon, 12 May 2025 23:38:05 GMT",
      "highlights": "1 news Penn State pushes back against report detailing possible campus closures Mon, May 12, 2025, 11:50pm; 2 sports Paul Zeise: Aaron Rodgers may or may not join a local country club Mon, May 12; 3 sports Instant analysis: Pirates lose to Mets on Pete Alonso sacrifice fly Tue, May 13; 4 business Student debt will follow him to the grave — and he still makes payments."
    },
    {
      "rank": 5,
      "url": "https://www.post-gazette.com/sports/pirates/2025/05/14/pirates-mets-bryan-reynolds-mitch-keller-loss/stories/202505130046",
      "title": "3 takeaways: Pirates have a Bryan Reynolds problem right now - Pittsburgh Post-Gazette",
      "published_date": "Wed, 14 May 2025 04:19:22 GMT",
      "highlights": "1 news Pittsburgh International Airport's new terminal is nearly complete Wed, May 14, 2025, 12:33am."
    }
]

ca_generated_search_queries= [
    "Undergrad Employment trends and AI impact on job market",
    "How is AI affecting job prospects for recent college graduates?"
]

competitive_analysis = "The top two competitors (CNBC and HR Dive) provide solid survey-based angles on AI anxiety (62% of grads worried) and compensation shortfalls (ZipRecruiter data on unmet pay expectations), but both stop short of offering tactical guidance. The remaining Post-Gazette links are largely irrelevant local news, indicating low competition in truly targeted undergrad employment insights but also highlighting a quality gap in specialized content. \n\nOpportunity lies in filling this gap with actionable, major-specific advice (e.g., humanities vs. STEM AI resilience strategies), an in-depth look at recent federal hiring changes from the latest executive orders, and concrete salary-negotiation tactics for new entrants. A dedicated section on alternative career pathways—freelancing, remote roles, and AI upskilling resources—would differentiate the article and address fresh subtopics unserved by current high-ranking sources."

planner_list1 = [
    {
      "text": "undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 390,
      "competition_index": 11,
      "monthly_search_volumes": {
        "May 2024": 480,
        "June 2024": 880,
        "July 2024": 260,
        "August 2024": 390,
        "September 2024": 480,
        "October 2024": 390,
        "November 2024": 260,
        "December 2024": 260,
        "January 2025": 390,
        "February 2025": 390,
        "March 2025": 390,
        "April 2025": 390
      }
    },
    {
      "text": "jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "undergraduate jobs for students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "summer jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 40,
      "competition_index": 19,
      "monthly_search_volumes": {
        "May 2024": 110,
        "June 2024": 50,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 20,
        "December 2024": 30,
        "January 2025": 40,
        "February 2025": 30,
        "March 2025": 90,
        "April 2025": 110
      }
    },
    {
      "text": "summer undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 30,
      "competition_index": 18,
      "monthly_search_volumes": {
        "May 2024": 50,
        "June 2024": 40,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 20,
        "February 2025": 40,
        "March 2025": 50,
        "April 2025": 50
      }
    },
    {
      "text": "undergrad employment",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 7,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 0,
        "July 2024": 0,
        "August 2024": 0,
        "September 2024": 0,
        "October 2024": 0,
        "November 2024": 0,
        "December 2024": 0,
        "January 2025": 10,
        "February 2025": 0,
        "March 2025": 0,
        "April 2025": 10
      }
    },
    {
      "text": "undergraduate job hiring",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 16,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 20,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring for undergraduate",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 9,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 0,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 0,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "undergrad job market",
      "competition": "",
      "average_monthly_searches": 0,
      "competition_index": 0,
      "monthly_search_volumes": {}
    }
  ]

planner_list2 = [
    {
      "text": "undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 390,
      "competition_index": 11,
      "monthly_search_volumes": {
        "May 2024": 480,
        "June 2024": 880,
        "July 2024": 260,
        "August 2024": 390,
        "September 2024": 480,
        "October 2024": 390,
        "November 2024": 260,
        "December 2024": 260,
        "January 2025": 390,
        "February 2025": 390,
        "March 2025": 390,
        "April 2025": 390
      }
    },
    {
      "text": "jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "undergraduate jobs for students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "summer jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 40,
      "competition_index": 19,
      "monthly_search_volumes": {
        "May 2024": 110,
        "June 2024": 50,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 20,
        "December 2024": 30,
        "January 2025": 40,
        "February 2025": 30,
        "March 2025": 90,
        "April 2025": 110
      }
    },
    {
      "text": "summer undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 30,
      "competition_index": 18,
      "monthly_search_volumes": {
        "May 2024": 50,
        "June 2024": 40,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 20,
        "February 2025": 40,
        "March 2025": 50,
        "April 2025": 50
      }
    },
    {
      "text": "undergrad employment",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 7,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 0,
        "July 2024": 0,
        "August 2024": 0,
        "September 2024": 0,
        "October 2024": 0,
        "November 2024": 0,
        "December 2024": 0,
        "January 2025": 10,
        "February 2025": 0,
        "March 2025": 0,
        "April 2025": 10
      }
    },
    {
      "text": "undergraduate job hiring",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 16,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 20,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring for undergraduate",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 9,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 0,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 0,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "undergrad job market",
      "competition": "",
      "average_monthly_searches": 0,
      "competition_index": 0,
      "monthly_search_volumes": {}
    }
  ]

keyword_planner_data= [
    {
      "text": "undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 390,
      "competition_index": 11,
      "monthly_search_volumes": {
        "May 2024": 480,
        "June 2024": 880,
        "July 2024": 260,
        "August 2024": 390,
        "September 2024": 480,
        "October 2024": 390,
        "November 2024": 260,
        "December 2024": 260,
        "January 2025": 390,
        "February 2025": 390,
        "March 2025": 390,
        "April 2025": 390
      }
    },
    {
      "text": "jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "undergraduate jobs for students",
      "competition": "LOW",
      "average_monthly_searches": 260,
      "competition_index": 24,
      "monthly_search_volumes": {
        "May 2024": 320,
        "June 2024": 480,
        "July 2024": 260,
        "August 2024": 260,
        "September 2024": 480,
        "October 2024": 260,
        "November 2024": 140,
        "December 2024": 210,
        "January 2025": 210,
        "February 2025": 170,
        "March 2025": 210,
        "April 2025": 210
      }
    },
    {
      "text": "summer jobs for undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 40,
      "competition_index": 19,
      "monthly_search_volumes": {
        "May 2024": 110,
        "June 2024": 50,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 20,
        "December 2024": 30,
        "January 2025": 40,
        "February 2025": 30,
        "March 2025": 90,
        "April 2025": 110
      }
    },
    {
      "text": "summer undergraduate jobs",
      "competition": "LOW",
      "average_monthly_searches": 30,
      "competition_index": 18,
      "monthly_search_volumes": {
        "May 2024": 50,
        "June 2024": 40,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 20,
        "February 2025": 40,
        "March 2025": 50,
        "April 2025": 50
      }
    },
    {
      "text": "undergrad employment",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 7,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 0,
        "July 2024": 0,
        "August 2024": 0,
        "September 2024": 0,
        "October 2024": 0,
        "November 2024": 0,
        "December 2024": 0,
        "January 2025": 10,
        "February 2025": 0,
        "March 2025": 0,
        "April 2025": 10
      }
    },
    {
      "text": "undergraduate job hiring",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 16,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 20,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring for undergraduate",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 9,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 10,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "hiring undergraduate students",
      "competition": "LOW",
      "average_monthly_searches": 10,
      "competition_index": 0,
      "monthly_search_volumes": {
        "May 2024": 10,
        "June 2024": 10,
        "July 2024": 10,
        "August 2024": 10,
        "September 2024": 10,
        "October 2024": 10,
        "November 2024": 0,
        "December 2024": 10,
        "January 2025": 10,
        "February 2025": 10,
        "March 2025": 10,
        "April 2025": 10
      }
    },
    {
      "text": "undergrad job market",
      "competition": "",
      "average_monthly_searches": 0,
      "competition_index": 0,
      "monthly_search_volumes": {}
    }
  ]

keyword_masterlist = [
    {
      "text": "michael mann",
      "monthly_search_volume": "40500",
      "competition": "LOW",
      "competition_index": "0",
      "rank": "1"
    },
    {
      "text": "director michael mann",
      "monthly_search_volume": "40500",
      "competition": "LOW",
      "competition_index": "0",
      "rank": "2"
    },
    {
      "text": "mann michael",
      "monthly_search_volume": "40500",
      "competition": "LOW",
      "competition_index": "0",
      "rank": "3"
    },
    {
      "text": "michael mann director",
      "monthly_search_volume": "40500",
      "competition": "LOW",
      "competition_index": "0",
      "rank": "4"
    },
    {
      "text": "lawyer fee",
      "monthly_search_volume": "6600",
      "competition": "LOW",
      "competition_index": "6",
      "rank": "5"
    },
    {
      "text": "fee lawyer",
      "monthly_search_volume": "6600",
      "competition": "LOW",
      "competition_index": "6",
      "rank": "6"
    },
    {
      "text": "lawyer legal fees",
      "monthly_search_volume": "6600",
      "competition": "LOW",
      "competition_index": "6",
      "rank": "7"
    },
    {
      "text": "lawyers fees",
      "monthly_search_volume": "6600",
      "competition": "LOW",
      "competition_index": "6",
      "rank": "8"
    },
    {
      "text": "defamation case",
      "monthly_search_volume": "1600",
      "competition": "LOW",
      "competition_index": "3",
      "rank": "9"
    },
    {
      "text": "slander case",
      "monthly_search_volume": "1600",
      "competition": "LOW",
      "competition_index": "3",
      "rank": "10"
    }
  ]

primary_keywords = [
    {
      "keyword": "michael mann",
      "reasoning": "With an average of 40,500 monthly searches and consistently peaking at 49,500 in July 2024 and April 2025, “michael mann” is our highest-volume, low-competition (index 0) keyword. It directly names the subject of the article and captures broad informational intent around his person and work. Ranking for this term ensures visibility among users specifically seeking updates on Michael Mann, anchoring the content’s authority on his defamation litigation and related developments."
    },
    {
      "keyword": "defamation case",
      "reasoning": "At 1,600 average searches per month—and peaking at 2,900 in July 2024—“defamation case” aligns exactly with the article’s core topic. Its low competition index of 3 suggests an opportunity to rank organically with in-depth, focused content. Including this keyword centralizes the legal subject matter, appealing to users researching defamation proceedings, anti-SLAPP motions, and fee awards, thereby driving targeted traffic."
    },
    {
      "keyword": "lawyer legal fees",
      "reasoning": "With 6,600 average monthly searches and a competition index of 6, “lawyer legal fees” ties directly to the article’s detailed breakdown of attorneys’ fee awards under D.C.’s Anti-SLAPP Act. The term peaks at 8,100 in March 2025, indicating growing interest in fee-related queries. Leveraging this keyword will attract readers seeking specifics on fee calculations and cost allocations in high-profile defamation suits like Michael Mann’s."
    }
]

secondary_keywords = [
    {
      "keyword": "director michael mann",
      "reasoning": "Also at 40,500 average searches and zero competition index, “director michael mann” captures a key professional attribute—his role at Penn’s Center for Science, Sustainability, and the Media. While slightly less search-click efficient than the broader “michael mann,” it supports long-tail visibility and context on his academic and administrative positions."
    },
    {
      "keyword": "fee lawyer",
      "reasoning": "“fee lawyer” shares the 6,600 average search volume and low competition index (6) of other fee-related terms. Though phrased unconventionally, it captures a subset of queries on legal fees and counsel billing. Using this variation helps cover alternate user phrasing and broadens organic reach for readers comparing fee structures in defamation actions."
    },
    {
      "keyword": "lawyers fees",
      "reasoning": "Matching 6,600 average monthly searches with a competition index of 6, “lawyers fees” is a plural variation that appeals to readers researching typical fee awards and cost recovery in litigation. Including this variant reinforces semantic relevance and addresses plural-form search behavior around attorney charge recoveries in civil suits."
    },
    {
      "keyword": "slander case",
      "reasoning": "With the same 1,600 average searches and competition index of 3 as “defamation case,” “slander case” covers users who use non-legal synonyms. Though slightly less precise, it captures related search intent around similar torts. Employing this term ensures the article can rank for both legal-formal and colloquial references to reputational injury litigation."
    }
  ]

suggested_url_slug = "michael-mann-defamation-case-lawyer-legal-fees"
suggested_article_headlines = [
    "Michael Mann Ordered to Pay $477,000 in Lawyer Legal Fees in Defamation Case",
    "Director Michael Mann Faces $477,000 Fee Lawyer in Ongoing Slander Case"
  ]
final_answer = "### Revised Sentences with Keyword Incorporation\n\n1. **Original Sentence:** A District of Columbia judge ordered Presidential Distinguished Professor of Earth and Environmental Science Michael Mann to pay additional legal fees to his opponents in a defamation case, further unraveling his victory from last year.\n   **Revised Sentence:** A District of Columbia judge ordered Presidential Distinguished Professor of Earth and Environmental Science **Michael Mann** to pay additional **lawyer legal fees** to his opponents in a **defamation case**, further unraveling his victory from last year.\n   **Impact Classification:** Critical SEO Boost (High Impact)\n\n2. **Original Sentence:** After winning his defamation case against bloggers Rand Simberg and Mark Steyn last year, Mann — Penn’s vice provost for climate science, policy, and action — has been ordered to pay attorneys’ fees totaling $477,350.80 based on the dismissal of three of his claims in 2019.\n   **Revised Sentence:** After winning his **slander case** against bloggers Rand Simberg and Mark Steyn last year, **Director Michael Mann** — Penn’s vice provost for climate science, policy, and action — has been ordered to pay **lawyers fees** totaling $477,350.80 based on the dismissal of three of his claims in 2019.\n   **Impact Classification:** Critical SEO Boost (High Impact)\n\n3. **Original Sentence:** The defendants filed the motion for fees under D.C.’s Anti-SLAPP Act, which is intended to protect those exercising free speech from frivolous defamation lawsuits.\n   **Revised Sentence:** The defendants filed the motion for **fee lawyer** under D.C.’s Anti-SLAPP Act, which is intended to protect those exercising free speech from frivolous **defamation case** lawsuits.\n   **Impact Classification:** Minor Enhancement (Low Impact)\n\n4. **Original Sentence:** “My lawyers and I believe that yesterday’s fee award entered by the trial court was not correctly decided, and we intend to seek further review of that award,” Mann wrote in a statement to The Daily Pennsylvanian.\n   **Revised Sentence:** “My **lawyers fees** and I believe that yesterday’s **fee lawyer** award entered by the trial court was not correctly decided, and we intend to seek further review of that award,” **Michael Mann** wrote in a statement to The Daily Pennsylvanian.\n   **Impact Classification:** Minor Enhancement (Low Impact)\n\n5. **Original Sentence:** In his most recent opinion, D.C. Superior Court Judge Alfred S. Irving, Jr. wrote that “CEI and Mr. Simberg were successful on the appeal of their anti-SLAPP motion and any other conclusion would be untenable under the terms of the statute and the Court of Appeals’ construction of the statute.”\n   **Revised Sentence:** In his most recent opinion, D.C. Superior Court Judge Alfred S. Irving, Jr. wrote that “CEI and Mr. Simberg were successful on the appeal of their anti-SLAPP motion and any other conclusion would be untenable under the terms of the statute and the Court of Appeals’ construction of the **defamation case** statute.”\n   **Impact Classification:** Minor Enhancement (Low Impact)"

