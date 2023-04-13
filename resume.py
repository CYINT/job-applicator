from src.cyint_slack import talk_to_slack, error_to_slack
from src.cyint_jira import authenticate_jira, get_prepared_opportunities
from src.cyint_openai import gpt_parse_summary, initialize_openai, gpt_generate_coverletter, gpt_choose_best_title, gpt_rewrite_pitch, gpt_rewrite_work_history, gpt_evaluate_work_history_entry
from src.cyint_resume import get_resume_data, build_resume
from time import sleep
import os
import re

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
            
            first_name, last_name, address, phone, email, calendly,\
            linkedin, titles, headline, pitch, technical_skills, work_history,\
            education, certifications = get_resume_data()
            

            experience = f"Applicant's Name:{first_name} {last_name}, Applicant's Address: {address}, Applicant's phone: {phone}, Applicant's Email: {email}, Applicant's Calendly: {calendly}, Applicant's LinkedIn: {linkedin}, Applicant's Background: {summary}"
            
            job_info = f"{opportunity.fields.summary}: {summary}"
            
            cover_letter = gpt_generate_coverletter(job_info, experience)
            cover_letter = re.sub(r'\[.*?\]\n?', '', cover_letter)
            title = gpt_choose_best_title(job_info, titles, headline)
            new_headline = f"Expert {title}"
            pitch = gpt_rewrite_pitch(summary, pitch)

            for work in work_history:
                skills = str(work['skills'])
                results = str(work['results'])
                valid = False
                max_tries = 3
                while not valid:
                    if max_tries < 1:
                        raise Exception('Could not generate a valid work history entry in three tries.')                    
                    new_description = gpt_rewrite_work_history(job_info, skills, results, work['company'], work['title'])
                    valid = bool(gpt_evaluate_work_history_entry(new_description))
                    max_tries -= 1
                    sleep(1)

                work['description'] = new_description

            filename = f"Daniel Fredriksen - {title}"
            filename = f"{get_valid_filename(filename)}.docx"
            
            build_resume(
                cover_letter,
                first_name, 
                last_name, 
                address, 
                phone, 
                email, 
                calendly,
                linkedin, 
                title, 
                new_headline,
                pitch, 
                technical_skills, 
                work_history,
                education, 
                certifications,
                filename
            )
            
            with open(filename, 'rb') as f:
                jira.add_attachment(issue=opportunity, attachment=f)
            jira.transition_issue(opportunity, 'GPT Preprocess Description')
            os.remove(filename)
            success += 1
        except Exception as ex:
            failure += 1
            error_to_slack(f"I encountered a problem with preprocessing opportunity {opportunity.key}. Error: {str(ex)}")

    return [success, failure, cancel]

def get_valid_filename(s): 
    s = str(s).strip().replace(' ', '_') 
    return re.sub(r'(?u)[^-\w.]', '', s) 

if __name__ == "__main__":
    talk_to_slack(f"I'm going to write some optimized resumes for opportunities in the backlog.")
    success, failure, cancel = generate_resumes_for_opportunities()
    talk_to_slack(f"I successfully prepared {success} opportunities with summary and salary information, and wrote a custom resume for each. I cancelled {cancel} opportunites as not qualified due to detected salary range, and I had problems processing {failure} opportunities.")