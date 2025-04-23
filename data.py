import pandas as pd
import json
import os

# input
#phone_num = 9719989211 #(971) 998-9211
#phone_num = 5096375941 #(509) 637-5941
#phone_nums_example = ['(971) 998-9211', '(509) 637-5941']
PHONES_EXAMPLES = ['(317) 956-0147', '(314) 215-9742', '(440) 864-5454', '(503) 857-3235', '(971) 451-4080', '(503) 339-6510', '17373005221', '(360) 887-8033', '(503) 719-0085']

# fetch grade options
with open("options.json", "r") as f:
    grades_json = json.load(f)
GRADES = grades_json["GRADES"]
GRADE_SECONDARY_POS = grades_json["GRADE_SECONDARY_POS"]
GRADE_SECONDARY_NEG = grades_json["GRADE_SECONDARY_NEG"]

# try enviornment variables (replit, render, railway, etc)
try:
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    API_KEY = os.environ.get("API_KEY")
except Exception as e:
    # try loading secrets through Docker (defined in docker-compose)
    # if fail, load secrets locally
    try:
        # try docker
        docker_path = '/run/secrets/stash'
        if os.path.exists(docker_path):
            with open(docker_path, 'r') as secret_file:
                    will_explode = secret_file.read().strip().split('\n')
        # fall back to local path if Docker secrets not available
        with open('secrets.txt', 'r') as secret_file:
                will_explode = secret_file.read().strip().split('\n')
        USERNAME = will_explode[0]
        PASSWORD = will_explode[1]
        API_KEY = will_explode[2]    
    except Exception as e:
        print(f"Error reading secrets: {str(e)}")

# preprocess data returned from llm calls
def clean_response(response:str) -> tuple:
    """
    Args:
        input_string (str): "<grade - grade_secondary>"
        
    Returns:
        tuple: (grade, grade_secondary)
    """
    cleaned = response.strip()[1:-1].strip() # remove the angle brackets
    parts = cleaned.split(" - ") # split by the delimiter " - "
    
    if len(parts) >= 2:
        grade, grade_secondary = parts[0].strip(), parts[1].strip()
    else: # if response = <Not confident>  
        grade, grade_secondary = cleaned, ""
        
    if grade_secondary == 'Wrong Number': grade_secondary = 'Service not offered'

    return grade, grade_secondary

def load_charged_leads(path: str):
    # read the leads-inbox CSV file with headers, preserving empty spaces and handling trailing commas
    df = pd.read_csv(path, 
                    header=0, 
                    keep_default_na=False, 
                    na_filter=False,
                    usecols=['Customer', 'Job type', 'Location', 'Lead type', 'Charge status', 'Lead received', 'Last activity'])
    
    # filter for charged leads
    #charged_df = df[df['Charge status'] == 'Charged']
    charged_df = df[(df['Charge status'] == 'Charged') & (df['Lead type'] == 'Phone call')]
    non_empty_customers = charged_df[charged_df['Customer'] != '']
    #print(f"\nNumber of charged leads found: {len(charged_df)}")
    
    return non_empty_customers

def get_customer_names(df):
    """
    Extract just the customer names/phone numbers into a list.
    """
    return df['Customer'].tolist()

def load_customer_data(path: str):
    charged_leads = load_charged_leads(path)
    customer_names = get_customer_names(charged_leads)
    return customer_names

if __name__ == '__main__':
    charged_leads = load_charged_leads('sample_data/leads-inbox.csv')
    
    # get customer names
    customer_names = get_customer_names(charged_leads)
    print("\nAll customer names:")
    print(customer_names)
    print(len(customer_names))
