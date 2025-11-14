from app.models.prompt import SystemPrompt
from openai import OpenAI
from flask import current_app

# preprocess data returned from llm calls
def clean_response(response:str) -> tuple:
    '''
    args:
        input_string (str): "<grade - grade_secondary>"
        
    returns:
        tuple: (grade, grade_secondary)
    '''
    cleaned = response.strip()[1:-1].strip() # remove the angle brackets
    parts = cleaned.split(" - ") # split by the delimiter " - "
    
    if len(parts) >= 2:
        grade, grade_secondary = parts[0].strip(), parts[1].strip()
    else: # if response = <Not confident>  
        grade, grade_secondary = cleaned, ""
        
    if grade_secondary == 'Wrong Number': grade_secondary = 'Service not offered'

    return grade, grade_secondary

def analyze_sentiment(transcript: str) -> tuple:

    prompt_obj = SystemPrompt.query.first()
    base_prompt = prompt_obj.prompt_text if prompt_obj else current_app.config['DEFAULT_SYSTEM_PROMPT']
    
    prompt = f"{base_prompt}\n\nUse this transcript:\n{transcript}"

    # Initialize the client
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'], timeout=120.0)
    
    response = client.chat.completions.create(
        model="o3-mini", #o3-2025-04-16, #"gpt-3.5-turbo", #"o3-mini-2025-01-31",
        messages=[
            {"role": "user", "content": prompt}
        ],
        #temperature=0.7, #gpt-3.5-turbo
        #max_tokens=200 #gpt-3.5-turbo
        #max_completion_tokens=200 #o3-mini-2025-01-31
    )

    output = response.choices[0].message.content.strip()
    
    # Extract only the text after "Output:"
    #if "Output:" in output:
    #    output = output.split("Output:")[1].strip()
    
    #output_list = output.split(",")
    #grade = output_list[0]
    #grade_secondary = output_list[1]
    return clean_response(output)
