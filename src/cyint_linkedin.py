from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import pickle
from dotenv import load_dotenv
load_dotenv()

def initialize_webdriver():
    path_to_driver = os.environ["WEBDRIVER_PATH"]
    data_directory = os.environ["DATA_DIRECTORY"]
    service = Service(executable_path=path_to_driver)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir={data_directory}") 
    chrome_options.add_argument(f"window-size=2000,1000")
    driver = webdriver.Chrome(service=service, options=chrome_options) 
    cookies = []
    if os.path.exists("cookies.pkl"):
        cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    return driver

def open_homepage(driver):
    driver.get('https://linkedin.com')

def sign_in(driver):
    if driver.title != "LinkedIn: Log In or Sign Up":
        return

    username = os.environ["LINKEDIN_USER"]
    password = os.environ["LINKEDIN_PASSWORD"]
    
    username_field = driver.find_element(by=By.NAME, value="session_key")
    username_field.click()
    username_field.clear()
    username_field.send_keys(username)
    password_field = driver.find_element(by=By.NAME,value="session_password")
    password_field.click()
    password_field.clear()
    password_field.send_keys(password)    
    action = ActionChains(driver)  
    action.move_to_element(password_field)
    button = driver.find_element(by=By.CLASS_NAME, value="sign-in-form__submit-btn--full-width")
    button.click()

def job_search(driver, alert):
    driver.get('https://www.linkedin.com/jobs/jam/')
    driver.implicitly_wait(5)
    link = driver.find_element(by=By.XPATH, value=f"//a[text()='{alert}']")
    link.click()
    chevrons = driver.find_elements(by=By.XPATH, value=f"//li-icon[@type='chevron-down']")
    [chevron.click() for chevron in chevrons]
    date_posted = driver.find_element(by=By.XPATH, value=f"//button[text()='Date posted']")
    date_posted.click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='timePostedRange-r86400']"))).click()
    date_posted = driver.find_element(by=By.XPATH, value=f"//button[text()='Date posted']")
    date_posted.click()
    sleep(5)
    total_results = driver.find_element(by=By.CSS_SELECTOR, value=".jobs-search-results-list__title-heading small")
    result_count = int(total_results.text.split(' ')[0].replace(',',''))
    
    jobs = extract_jobs_from_page(driver)

    current_page = 2
    exception = None
    while len(jobs) < result_count:
        try:
            page_button = driver.find_element(by=By.XPATH, value=f"//li[@data-test-pagination-page-btn='{current_page}']")
            page_button.click()
            page_jobs = extract_jobs_from_page(driver)        
            jobs += page_jobs   
            current_page += 1
        except Exception as e:
            exception = e
            break
    return {
        "result_count": result_count,
        "jobs": jobs,
        "exception": exception
    }


def extract_jobs_from_page(driver, job_counter = 0):
    job_list = driver.find_elements(by=By.CSS_SELECTOR, value=".job-card-container")
    while len(job_list) > job_counter:
        job_counter = len(job_list)
        driver.execute_script("""
        var elements = document.querySelectorAll('.job-card-container');
        elements[elements.length-1].scrollIntoView();
    """)
        job_list = driver.find_elements(by=By.CSS_SELECTOR, value=".job-card-container")
        
    jobs = [parse_job_data(job) for job in job_list]
    jobs = [job for job in jobs if job['title'] != None]

    sleep(2)
    return jobs


def parse_job_data(job):
    try:
        job_id = job.get_attribute('data-job-id')
        title_container = job.find_element(by=By.CSS_SELECTOR, value=".job-card-list__title")
        title = title_container.text
        path = title_container.get_attribute('href')
        try:
            company = job.find_element(by=By.CSS_SELECTOR, value=".job-card-container__primary-description").text
        except:
            company = None
        return {
            "job_id": job_id,
            "title": title,
            "path": path,
            "company": company
        }
    except Exception as e:
        return {
            "job_id": None,
            "title": None,
            "path": None,
            "company": None,
            "exception": e
        }

def extract_description_from_url(driver, url):
    driver.get(url)
    driver.implicitly_wait(10)
    button = driver.find_element(by=By.XPATH, value="//span[text()='See more']")
    button.click()
    sleep(2)
    description_container = driver.find_element(by=By.CSS_SELECTOR, value=".jobs-description-content__text")
    return description_container.text

def extract_hiring_manager(driver):

    try:
        driver.implicitly_wait(2)
        manager =  driver.find_elements(
            by=By.CSS_SELECTOR, 
            value = '.jobs-poster__name'
        )
        return manager[0].text
    except Exception as e:
        print(e)
        return "Unknown"
            