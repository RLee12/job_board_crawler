import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import sys
import time

class HttpHelpers:
    """Helper class to download a webpage's content."""
    
    def __init__(self):
        self.session = requests.Session()

    def download_page(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except HTTPError as httpErr:
            print("Http error occurred: {httpErr}")
            return None
        except Exception as err:
            print("A generic error occurred: {err}")
            return None
        else:
            return response.content


class IndeedJobs:
    """Indeed crawler to scrape all jobs for a URL."""

    def __init__(self, url):
        self.url = url
        self.helpers = HttpHelpers()
        self.all_indeed_jobs = []

    def get_jobs(self):
        self.curr_page = self.helpers.download_page(self.url)
        self.indeed_jobs = self.parse_job_meta(self.curr_page)

        for job in self.indeed_jobs:
            job_content = self.helpers.download_page(job["href"])
            if job_content is None:
                continue
            parsed_details = self.parse_job_description(job_content)
            job["description"] = parsed_details

        self.all_indeed_jobs.extend(self.indeed_jobs)

        # Recursively get jobs from all pages.
        self.get_next_page_jobs()

    def get_next_page_jobs(self):
        # Pause for a second to be a courteous crawler.
        time.sleep(1)
        
        self.url = self.get_next_page_url(self.curr_page)

        # Check if next page exists. If not then all pages have been crawled and return all scraped jobs. 
        if len(self.url) > 0:
            self.get_jobs()
        else:
            return self.all_indeed_jobs
        
    def parse_job_meta(self, html_content):
        """Parse downloaded webpage to get job data."""

        soup = BeautifulSoup(html_content, 'lxml')
        jobs_container = soup.find(id='resultsCol')
        job_items = jobs_container.find_all(class_="jobsearch-SerpJobCard unifiedRow row result")
        
        curr_page_num = soup.find(attrs={"aria-current": "true"})["aria-label"]
        print(f"Crawling page {curr_page_num}")

        all_jobs = []

        for job_elem in job_items:
            url_elem = job_elem.find(attrs={"data-tn-element": "jobTitle"})
            href = url_elem.get('href')
            if href is None:
                href = ""

            title_elem = job_elem.find(attrs={"data-tn-element": "jobTitle"})
            if title_elem["title"] is None:
                title_text = ""
            else:
                title_text = title_elem["title"].strip()

            company_elem = job_elem.find(class_="company")
            if company_elem is None:
                company_text = ""
            else:
                company_text = company_elem.text.strip()

            loc_elem = job_elem.find(
                class_="location accessible-contrast-color-location")
            if loc_elem is None:
                loc_text = ""
            else:
                loc_text = loc_elem.text.strip()

            salary_elem = job_elem.find(class_="salaryText")
            if salary_elem is None:
                salary_text = ""
            else:
                salary_text = salary_elem.text.strip()

            date_elem = job_elem.find(class_="date")
            if date_elem is None:
                date_text = ""
            else:
                date_text = date_elem.text.strip()

            item = {
                "title": title_text,
                "company": company_text,
                "location": loc_text,
                "salary": salary_text,
                "date": date_text,
                "href": f'https://www.indeed.com{href}',
                "description": ""
            }

            all_jobs.append(item)

        return all_jobs

    def parse_job_description(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        description_element = soup.find(id='jobDescriptionText')
        description_text = description_element.text.strip()
        
        return description_text

    def get_next_page_url(self, html_content):
        soup = BeautifulSoup(html_content, "lxml")
        next_page_element = soup.find(attrs={"aria-label": "Next"})

        if next_page_element is not None:
            next_page_href = next_page_element["href"]
            next_page_url = f'https://www.indeed.com{next_page_href}'
        else:
            next_page_url = ""
        
        return next_page_url