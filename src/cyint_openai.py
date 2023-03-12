import openai
import os
from dotenv import load_dotenv
load_dotenv()


def initialize_openai():
    API_KEY = os.environ['OPENAI_API_KEY']
    openai.api_key = API_KEY

def chat_completion(messages, max_tokens = 1000, temperature = 0.7):
    result = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return result

def gpt_parse_summary(description):

    prompt = 'Summarize the job description provided by the user. Include salary range or "Unknown", qualifications or "Unknown", and a brief synopsis of the description.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": description[:(3000-len(prompt))]}
    ]

    result = chat_completion(messages)    
    return result.choices[0].message.content 

def gpt_parse_skills():
    return []

def gpt_parse_salary(summary):
    prompt = 'Extract the minimum and maximum salary range from a summary of the job description. If the minimum or maximum salary range is not present, substitute "Uknown"'


    messages = [{"role":"system", "content": prompt}, 
        {"role": "user", "content": 'The job is for a remote Principal Software Engineer for a ground travel search startup in North America. The salary range for the position is $160,000 - $200,000 per year. The company is looking for a technical leader to develop their technical roadmap and ensure that their teams are building the best platform for their travel marketplace. The candidate should have experience in driving architecture discussions, collaborating with stakeholders, and driving large transformation projects. The company values diversity and is fully remote, and the candidate should be dri,ven, solutions-focused, and passionate about their work. Qualifications are not mentioned in the job description.'},
        {"role": "assistant", "content": "160000;20000"},
        {"role": "user", "content": summary}
    ]

    result = chat_completion(messages, max_tokens=30, temperature=0)    
    return result.choices[0].message.content 
