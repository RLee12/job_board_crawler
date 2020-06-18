from urllib.parse import urlencode
from indeed_scraper import *

indeed_url = "https://www.indeed.com/jobs?"
query_param = {
    "q": "data",
    "l": "Los Angeles, CA",
    "radius": "50",
    "jt": "fulltime"
}
encoded_query = urlencode(query_param)
indeed_query = f"https://www.indeed.com/jobs?{encoded_query}"

######### Testing block #########
# query_response = HttpHelpers().download_page(indeed_query)
# soup = BeautifulSoup(query_response, 'lxml')

# # soup.find(class_="pagination-list")
# soup.find(attrs={"aria-label": "Next"})["href"]
# soup.find(attrs={"aria-current": "true"})["aria-label"]
######### Testing block #########

# The crawler will run until all pages have been scraped. 
# Next step is to add a trigger to stop the crawler.
indeed = IndeedJobs(indeed_query)
indeed.get_jobs()
indeed_jobs = indeed.all_indeed_jobs

for job in indeed_jobs:
    print((job['title'], job['company'], job['location'], job['salary'], job['date']))