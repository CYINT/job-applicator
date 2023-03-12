from src.cyint_jira import get_new_opportunities, authenticate_jira
from src.cyint_slack import talk_to_slack
from src.cyint_linkedin import extract_description_from_url, initialize_webdriver
from time import sleep

def get_job_descriptions():
    jira = authenticate_jira()

    opportunities = []

    new_opportunities = get_new_opportunities(jira, 0)
    opportunities += new_opportunities
    while len(new_opportunities) > 0:
        new_opportunities = get_new_opportunities(jira, len(opportunities))
        opportunities += new_opportunities
        sleep(1)

    driver = initialize_webdriver()
    success = 0
    failure = 0
    for opportunity in opportunities:
        try:
            url = opportunity.get_field('customfield_10158')
            description = extract_description_from_url(driver, url)
            opportunity.update({'description': description})
            jira.transition_issue(opportunity, transition='Captured Job Description')
            success += 1
            if success % 25 == 0:
                sleep(2)
        except Exception as ex:
            talk_to_slack(f"I encountered a problem with opportunity {opportunity.key}. Error: {str(ex)}")
            failure += 1

    return [success, failure]

if __name__ == "__main__":
    talk_to_slack("Im going to process some of these new opportunities.")
    success, failure = get_job_descriptions()
    talk_to_slack(f"I added descriptions to {success} opportunities, and encountered {failure} problems.")