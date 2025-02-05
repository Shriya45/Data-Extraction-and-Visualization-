import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import nest_asyncio
import re

nest_asyncio.apply()

def clean_text(text):
    return re.sub(r'[^A-Za-z0-9\s]', '', text)  
async def scrape_indeed_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set user agent to avoid bot detection
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        # URL for Indeed job search in Pune, Maharashtra
        await page.goto("https://in.indeed.com/jobs?q=&l=Maharashtra&from=searchOnDesktopSerp&vjk=1fee8c4e8b54bf2d")

        jobData = []

        for i in range(50):
            try:
            
                await page.wait_for_selector('div.job_seen_beacon', timeout=60000)  # Wait up to 60 seconds
            except Exception as e:
                print(f"Timeout or error: {e}")
                break

       
            dContent = await page.content()
            soup = BeautifulSoup(dContent, 'html.parser')

         
            for job_card in soup.find_all('div', class_='job_seen_beacon'):
             
                title_tag = job_card.find('h2', class_='jobTitle')
                title = title_tag.get_text(strip=True) if title_tag else 'N/A'

               
                company_tag = job_card.find('span', class_='companyName')
                company = company_tag.get_text(strip=True) if company_tag else 'N/A'

              
                location_tag = job_card.find('div', class_='companyLocation')
                location = location_tag.get_text(strip=True) if location_tag else 'N/A'

               
                salary_tag = job_card.find('div', class_='salary-snippet')
                salary = salary_tag.get_text(strip=True) if salary_tag else 'N/A'
                salary = clean_text(salary)

              
                summary_tag = job_card.find('div', class_='job-snippet')
                summary = summary_tag.get_text(strip=True) if summary_tag else 'N/A'

                
                job_link_tag = job_card.find('a', href=True)
                job_link = "https://in.indeed.com" + job_link_tag['href'] if job_link_tag else 'N/A'

               
                jobData.append({
                    'Job Title': title,
                    'Company': company,
                    'Location': location,
                    'Salary': salary,
                    'Summary': summary,
                    'Apply Link': job_link
                })

            next_button = await page.query_selector('a[aria-label="Next Page"]')
            if next_button:
                await next_button.click()
                await page.wait_for_timeout(2000) 
            else:
                print("No next page. Exiting...")
                break

    
        await browser.close()

    
        return pd.DataFrame(jobData)

async def main():
  
    indeed_jobs_df = await scrape_indeed_jobs()

   
    indeed_jobs_df.to_csv('Maharashtra_jobs.csv', index=False)

   
    indeed_jobs_df.to_excel('Maharashtra_jobs.xlsx', index=False)


    print(indeed_jobs_df)


asyncio.run(main())
