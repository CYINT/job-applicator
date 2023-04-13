import json
import re
import base64
from src.cyint_resume import get_resume_data, build_resume
from src.cyint_openai import gpt_generate_coverletter, gpt_choose_best_title, gpt_rewrite_pitch, gpt_rewrite_work_history, gpt_evaluate_work_history_entry

def build(event, context):

    payload = json.loads(event["body"])
    job_title = payload['title']
    summary = payload['summary']    

    first_name, last_name, address, phone, email, calendly,\
    linkedin, titles, headline, pitch, technical_skills, work_history,\
    education, certifications = get_resume_data()
    
    experience = f"""
Applicant's Name:{first_name} {last_name}, 
Applicant's Address: {address}, 
Applicant's phone: {phone}, 
Applicant's Email: {email}, 
Applicant's Calendly: {calendly}, 
Applicant's LinkedIn: {linkedin}, 
Applicant's Background: {summary}
"""
 
    job_info = f"{job_title}: {summary}"
    
    cover_letter = gpt_generate_coverletter(job_info, experience)
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

        work['description'] = new_description

    filename = f"{first_name} {last_name} - {title}"
    filename = f"{_get_valid_filename(filename)}.docx"
    
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

    resume = open(filename, 'rb')
    body = base64.b64encode(resume.read()).decode('utf-8')

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        },
        "body":body,
        "isBase64Encoded": True
    }

def _get_valid_filename(s): 
    s = str(s).strip().replace(' ', '_') 
    return re.sub(r'(?u)[^-\w.]', '', s) 
