from src.cyint_slack import talk_to_slack
from src.cyint_jira import authenticate_jira, get_prepared_opportunities
from src.cyint_openai import gpt_parse_summary, gpt_parse_salary, initialize_openai
from time import sleep


def generate_resumes_for_opportunities():
    jira = authenticate_jira()
    opportunities = get_prepared_opportunities(jira)
    initialize_openai()
    success = 0
    failure = 0
    cancel = 0
    for opportunity in opportunities:
        try:
            description = opportunity.fields.description
            summary = gpt_parse_summary(description)
            salary = gpt_parse_salary(summary)
            salaries = salary.split(";")
            try:
                min_salary = salaries[0] if salaries[0].lower() != 'unknown'else None
                max_salary = salaries[1] if salaries[1].lower() != 'unknown'else None
            except:
                min_salary = None
                max_salary = None
            fields = {}
            
            if min_salary != None:
                fields['customfield_10207'] = int(min_salary)
            if max_salary != None:
                fields['customfield_10208'] = int(max_salary)
            
            fields['customfield_10209'] = summary

            opportunity.update(fields)

            if max_salary is not None and int(max_salary) < 150000:
                cancel += 1
                jira.transition_issue(opportunity, 'Canceled')
                continue
            
            jira.transition_issue(opportunity, 'GPT Preprocess Description')
            success += 1
        except Exception as ex:
            failure += 1
            talk_to_slack(f"I encountered a problem with preprocessing opportunity {opportunity.key}. Error: {str(ex)}")
    return [success, failure, cancel]
if __name__ == "__main__":
    talk_to_slack(f"I'm going to preprocess some opportunities for automatic resume generation.")
    success, failure, cancel = generate_resumes_for_opportunities()
    talk_to_slack(f"I successfully prepared {success} opportunities with summary and salary information. I cancelled {cancel} opportunites as not qualified due to detected salary range, and I had problems processing {failure} opportunities.")