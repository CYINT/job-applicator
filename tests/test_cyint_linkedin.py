from src.cyint_linkedin import initialize_webdriver, open_homepage, sign_in, job_search
import selenium

driver = None

def test_initialize_webdriver():    
    global driver
    driver = initialize_webdriver()
    assert type(driver) == selenium.webdriver.chrome.webdriver.WebDriver

def test_open_homepage():
    global driver
    open_homepage(driver)
    assert (driver.title == "LinkedIn: Log In or Sign Up" or driver.title == "LinkedIn")

def test_sign_in():
    global driver
    open_homepage(driver)
    sign_in(driver)
    assert driver.title != "LinkedIn: Log In or Sign Up"

def test_job_search():
    global driver
    results = job_search(driver, "machine learning engineer")
    assert "machine learning engineer" in driver.title
    assert type(results["result_count"]) == int    
    assert len(results["jobs"]) >= 0
    