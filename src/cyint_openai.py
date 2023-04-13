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
            sleep(1)
            return result
        except RateLimitError as ex:
            sleep(60)
            max_tries -= 1
def gpt_parse_summary(description = ''):

    prompt = 'Summarize the job description provided by the user. Include salary range/hourly rate or "Unknown", qualifications or "Unknown", the hiring managers name or "Hiring manager", and a brief synopsis of the description.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": description[:(3000-len(prompt))]}
    ]

    result = chat_completion(messages)    
    return result.choices[0].message.content 


def gpt_generate_coverletter(summary = '', experience = '', additions = []):
    prompt = f"Generate a cover letter for the job summary provided by the user. Add a sentance about scheduling time for an interview via Calendly. Do not include placeholders. {experience}."

    messages = [{"role":"system", "content": prompt}, 
        {"role": "user", "content": summary}
    ] + additions

    result = chat_completion(messages, max_tokens=1000, temperature=0)    
    return result.choices[0].message.content 

def gpt_parse_skills():
    return []

def gpt_choose_best_title(summary = '', titles = []):

    prompt = f'Select one best match from the following: {". ".join(titles)}.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": 'The job is for a remote Principal Software Engineer for a ground travel search startup in North America. The salary range for the position is $160,000 - $200,000 per year. The company is looking for a technical leader to develop their technical roadmap and ensure that their teams are building the best platform for their travel marketplace. The candidate should have experience in driving architecture discussions, collaborating with stakeholders, and driving large transformation projects. The company values diversity and is fully remote, and the candidate should be dri,ven, solutions-focused, and passionate about their work. Qualifications are not mentioned in the job description.'},
        {"role": "assistant", "content": "Software Engineer"},
        {"role": "user", "content": summary[:3000]}
    ]

    result = chat_completion(messages, max_tokens=100, temperature=1, top_p=0.25)    
    return result.choices[0].message.content 

def gpt_rewrite_pitch(summary = '', pitch = '', additions = []):

    prompt = f'Rewrite the following resume summary for the job description as a single paragraph: {pitch}.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": f"Job Description: {summary[:3000]}."}
    ] + additions

    result = chat_completion(messages, max_tokens=500)    
    return result.choices[0].message.content 


def gpt_rewrite_work_history(summary = '', skills = '', results = '', company = '', position = '', additions = []):

    prompt = f'Skills: {skills}\nResults: {results}\nCompany: {company}\nTitle: {position}\n.Use the information above to write a resume experience entry and how each relates to the job posting. Use only a single paragraph without bullets.'

    messages = [
        {"role":"system", "content": prompt}, 
        {"role": "user", "content": f"My job posting is: {summary[:3000]}."},
    ] + additions

    result = chat_completion(messages, max_tokens=250)    
    return result.choices[0].message.content 

def gpt_evaluate_model_output(entry):

    prompt = f'Review the users message. If it contains any spelling errors or is incomplete, or mentions degrees in anything other than Computer Science, Quantum Computing, or Intelligence, return false. If it is complete and has no spelling errors, return true. Generate instructions to add to a GPT-4 prompt to correct the output. I am currently pursuing a PhD in Quantum Computing, have a Bachelor\'s in Intelligence Management, and have only completed coursework for a Master\'s in Computer Science, Cybersecurity, Intelligence Management, and Research Methods. I\'m only interested in remote roles and not willing to travel.'

    messages = [
        {"role":"system", "content": prompt},
        {"role": "user", "content": "With my PhD in Economics I am a good fit for this role."},
        {"role": "assistant", "content": "False. Try again without the false degree."},
        {"role": "user", "content": "Because I am currently pursuing a PhD in Quantum Computing, have a bachelor's in Intelligence Management, and have completed Masters coursework in Cybersecurity, Computer Science, Intelligence, and Research Methods, I am a good fit for this role."},
        {"role": "assistant", "content": "True"},
        {"role": "user", "content": "I have a Bachelor\'s in Computer Science."},
        {"role": "assistant", "content": "False. Rewrite to indicate that I have completed coursework towards a Master\'s in Computer Science."},
        {"role": "user", "content": "I am willing to travel."},
        {"role": "assistant", "content": "False. Rewrite and exclude mention of travel."},

        {"role": "user", "content": entry}
    ]

    result = chat_completion(messages, max_tokens=100, temperature=0)    
    return result.choices[0].message.content 

def optimized_gpt_call(gpt_model, retries=3, **kwargs):

    additions = []

    for i in range(retries):
        output = gpt_model(**kwargs, additions=additions)
        evaluation = gpt_evaluate_model_output(output)
        if evaluation[:5].lower() == "true":
            return output
        
        additions = [
            {"role": "assistant", "content": output},
            {"role": "user", "content": evaluation[6:]}
        ]

    raise Exception(f"Could not generate quality output from GPT model {gpt_model.__name__}")