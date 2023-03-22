import openai
import os
from dotenv import load_dotenv
from time import sleep
from openai.error import RateLimitError
load_dotenv()


def initialize_openai():
    API_KEY = os.environ['OPENAI_API_KEY']
    openai.api_key = API_KEY

def chat_completion(messages, max_tokens = 1000, temperature = 0.7, top_p=1, frequency_penalty=0, presence_penalty=0):

    trying = True    
    max_tries = 3
    while trying and max_tries > 0:
    
        try:
            result = openai.ChatCompletion.create(
                model = 'gpt-4',
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )

            return result
        except RateLimitError as ex:
            sleep(60)
            max_tries -= 1
def gpt_parse_summary(description):

    prompt = 'Summarize the job description provided by the user. Include salary range/hourly rate or "Unknown", qualifications or "Unknown", the hiring managers name or "Hiring manager", and a brief synopsis of the description.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": description[:(3000-len(prompt))]}
    ]

    result = chat_completion(messages)    
    return result.choices[0].message.content 


def gpt_generate_coverletter(summary, experience):
    prompt = f"Generate a cover letter for the job summary provided by the user. Add a sentance about scheduling time for an interview via Calendly. {experience}."

    messages = [{"role":"system", "content": prompt}, 
        {"role": "user", "content": summary}
    ]

    result = chat_completion(messages, max_tokens=1000, temperature=0)    
    return result.choices[0].message.content 

def gpt_parse_skills():
    return []

def gpt_parse_salary(summary):
    prompt = 'Extract the minimum and maximum salary range from a summary of the job description. If the minimum or maximum salary range is not present, substitute "Uknown". If the range is listed as an hourly rate, calculate the yearly salary based on 40 hour weeks and return the total.'


    messages = [{"role":"system", "content": prompt}, 
        {"role": "user", "content": 'The job is for a remote Principal Software Engineer for a ground travel search startup in North America. The salary range for the position is $160,000 - $200,000 per year. The company is looking for a technical leader to develop their technical roadmap and ensure that their teams are building the best platform for their travel marketplace. The candidate should have experience in driving architecture discussions, collaborating with stakeholders, and driving large transformation projects. The company values diversity and is fully remote, and the candidate should be dri,ven, solutions-focused, and passionate about their work. Qualifications are not mentioned in the job description.'},
        {"role": "assistant", "content": "160000;20000"},
        {"role": "user", "content": "We are looking for an experienced machine learning engineer."},
        {"role": "assistant", "content": "unknown;unknown"},
        {"role": "user", "content": "If you are a front end engineer please apply! The maximum salary range for this position is $150k"},
        {"role": "assistant", "content": "unknown;150000"},
        {"role": "user", "content": "Seeking Data Engineer. Hourly rate $75 - $100 an hour."},
        {"role": "assistant", "content": "156000;208000"},
        {"role": "user", "content": summary}
    ]

    result = chat_completion(messages, max_tokens=30, temperature=0)    
    return result.choices[0].message.content 

def gpt_choose_best_title(job_info, titles, headline):

    prompt = f'Select one best match from the following: {". ".join(titles)}.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": 'The job is for a remote Principal Software Engineer for a ground travel search startup in North America. The salary range for the position is $160,000 - $200,000 per year. The company is looking for a technical leader to develop their technical roadmap and ensure that their teams are building the best platform for their travel marketplace. The candidate should have experience in driving architecture discussions, collaborating with stakeholders, and driving large transformation projects. The company values diversity and is fully remote, and the candidate should be dri,ven, solutions-focused, and passionate about their work. Qualifications are not mentioned in the job description.'},
        {"role": "assistant", "content": "Software Engineer"},
        {"role": "user", "content": job_info[:3000]}
    ]

    result = chat_completion(messages, max_tokens=100, temperature=1, top_p=0.25)    
    return result.choices[0].message.content 

def gpt_rewrite_pitch(job_info, pitch):

    prompt = f'Rewrite the following resume summary pitch to be a better fit for the user provided job description: {pitch}.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": job_info[:3000]}
    ]

    result = chat_completion(messages, max_tokens=250)    
    return result.choices[0].message.content 


def gpt_rewrite_work_history(job_info, skills, results, company, position):

    prompt = f'Skills: {skills}\nResults: {results}\nCompany: {company}\nTitle: {position}\n.Use the information above to write a resume experience entry and how each relates to the job posting. Response must fit in 200 tokens.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": f"My job posting is: {job_info[:3000]}"}
    ]

    result = chat_completion(messages, max_tokens=250)    
    return result.choices[0].message.content 

def gpt_evaluate_work_history_entry(entry):

    prompt = f'Review the users message. If it contains any spelling errors or is incomplete, or mentions degrees in anything other than Computer Science, Quantum Computing, or Intelligence, return false. If it is complete and has no spelling errors, return true.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": entry}
    ]

    result = chat_completion(messages, max_tokens=5, temperature=0)    
    return result.choices[0].message.content 
