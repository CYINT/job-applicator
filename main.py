from src.cyint_dynamodb import initiate_dynamo_resource, insert_records, get_items, get_unprocessed_opportunities
from src.cyint_linkedin import initialize_webdriver, open_homepage, sign_in, job_search
from src.cyint_jira import authenticate_jira, create_opportunities
from src.cyint_slack import talk_to_slack

def connect_to_linkedin():
    driver = initialize_webdriver()
    open_homepage(driver)
    sign_in(driver)
    job_object = job_search(driver, "machine learning engineer")
    return job_object["jobs"], job_object["exception"]

def save_jobs_to_database(jobs):
    resource = initiate_dynamo_resource()
    keys = []
    for job in jobs:
        keys.append(job["job_id"])
    duplicates = get_items(resource, keys)
    total_start = len(jobs)
    dupe_count = len(duplicates)
    for key in duplicates.keys():
        for index in range(len(jobs)):
            if jobs[index]["job_id"] == key:
                jobs.pop(index)
                break 

    total_end = len(jobs)

    for job in jobs:        
        job["jira"] = 0

    insert_records(resource, jobs)
    return [total_start, dupe_count, total_end]

def create_jira_opportunities():
    resource = initiate_dynamo_resource()
    unprocessed_jobs = get_unprocessed_opportunities(resource)
    jobs = []
    for job in unprocessed_jobs:
        jobs.append(unprocessed_jobs[job])
    jira = authenticate_jira()
    issues = create_opportunities(jira, jobs, "MAR")
    for job in jobs:
        job["jira"] = 1

    insert_records(resource, jobs)
    return issues

def shut_down():
    pass

def harvest_opportunities():
    try:
        talk_to_slack("Hello! LinkedIn Marketing Bot reporting for work. I'm going to try to harvest new opportunities.")
        jobs, exception = connect_to_linkedin()
        if exception != None:
            talk_to_slack(f"I had some trouble getting all of the pages of jobs, but I was able to get some. Here is the error I enountered trying to go through the pages: {str(exception)}")
        total_start, dupe_count, total_end = save_jobs_to_database(jobs)
        talk_to_slack(f"I found {total_start} opportunities, {dupe_count} were duplicates, and I saved {total_end} opportunities to the database.")
        issues = create_jira_opportunities()
        talk_to_slack(f"I've gone ahead and created {len(issues)} opportunities in JIRA. Whew! That was a lot of work.")
    except Exception as e:
        talk_to_slack(f"Oops! Something went wrong. Here is the exception I got: {str(e)}")    
        
    #shut_down()    


if __name__ == "__main__":
    harvest_opportunities()