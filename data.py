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
GRADE_SECONDARY_POS_FULL = grades_json["GRADE_SECONDARY_POS_FULL"]
GRADE_SECONDARY_NEG_FULL = grades_json["GRADE_SECONDARY_NEG_FULL"]


class TwoFactCode:
    def __init__(self, code):
        """Initialize with a code."""
        self.code = code

    def get_code(self):
        """Return the stored code."""
        return self.code
    
    def update_code(self, new_code):
        self.code = new_code
        with open("2fa_code.json", "w") as f:
            json.dump({"code": self.code}, f)  # Save to a file



class Customer:
    def __init__(self, phone: str, grade: str = "Not Graded", grade_secondary: str = "Not Graded", transcript: str = "Not Fetched"):
        self.phone = phone
        self.grade = grade
        self.grade_secondary = grade_secondary
        self.transcript = transcript
    
    def get_phone(self):
        return self.phone
    
    def get_grades(self):
        return (self.grade, self.grade_secondary)


class Customers:
    def __init__(self, customers: list[Customer]):
        self.customers = customers
    
    def get_customers(self):
        """
        Returns list of ONLY customer phone numbers
        """
        return [customer.get_phone() for customer in self.customers]
    
    def get_len_customers(self):
        return len(self.customers)
    
    def add_customer(self, phone: str, grade: str = "Not Graded", grade_secondary: str = "Not Graded", transcript: str = "Not Fetched"):
        self.customers.append(Customer(phone, grade, grade_secondary, transcript))


class DateRange:
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
    
    def set_start(self, start_date: str):
        self.start_date = start_date

    def get_start(self):
        return self.start_date
    
    def set_end(self, end_date: str):
        self.end_date = end_date

    def get_end(self):
        return self.end_date




# try enviornment variables (replit, render, railway, etc)
try:
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
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
        OPENAI_API_KEY = will_explode[2]    
    except Exception as e:
        print(f"Error reading secrets: {str(e)}")


def convert_grade_secondary_to_full(grade_secondary: str) -> str:
    """
    Convert a short grade_secondary value to its full description.
    
    Args:
        grade_secondary (str): The short grade secondary value
        
    Returns:
        str: The full description of the grade secondary, or the original value if not found
    """
    # Check if it's in the positive list
    if grade_secondary in GRADE_SECONDARY_POS:
        index = GRADE_SECONDARY_POS.index(grade_secondary)
        return GRADE_SECONDARY_POS_FULL[index]
    
    # Check if it's in the negative list
    elif grade_secondary in GRADE_SECONDARY_NEG:
        index = GRADE_SECONDARY_NEG.index(grade_secondary)
        return GRADE_SECONDARY_NEG_FULL[index]
    
    # If not found in either list, return the original value
    else:
        return grade_secondary
    

def convert_grade_secondary_to_index(grade_secondary: str, sentiment: str) -> int:
    """
    Convert a short grade_secondary value to its index.
    
    Args:
        grade_secondary (str): The short grade secondary value
        
    Returns:
        int: The index of the grade secondary, -1 if not found
    """
    # Check if it's in the positive list
    if grade_secondary in GRADE_SECONDARY_POS:
        return GRADE_SECONDARY_POS.index(grade_secondary) + 1
    
    # Check if it's in the negative list
    elif grade_secondary in GRADE_SECONDARY_NEG:
        return GRADE_SECONDARY_NEG.index(grade_secondary) + 1
    
    # If not found in either list, return -1
    else:
        return -1
    

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

# if __name__ == '__main__':
#     charged_leads = load_charged_leads('sample_data/leads-inbox.csv')
    
#     # get customer names
#     customer_names = get_customer_names(charged_leads)
#     print("\nAll customer names:")
#     print(customer_names)
#     print(len(customer_names))
