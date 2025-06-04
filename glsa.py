from data import Customer, convert_grade_secondary_to_full, USERNAME, PASSWORD
import sys
import os

from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserSession
from dotenv import load_dotenv
load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4.1") #gpt-4o


def process_args(args):
    # Parse customers from command line arguments
    customers_to_grade = []
    for arg in args:
        try:
            parts = arg.split(',')
            if len(parts) != 3:
                print(f"Error: Invalid format for '{arg}'. Expected format: 'phone,grade,grade_secondary'")
                #return
            
            phone = parts[0].strip()
            grade = parts[1].strip()
            grade_secondary = parts[2].strip()
            
            # Create Customer object
            customer = Customer(phone=phone, grade=grade, grade_secondary=grade_secondary)
            customers_to_grade.append(customer)
            
        except Exception as e:
            print(f"Error parsing argument '{arg}': {e}")
            
    return customers_to_grade


def generate_grading_steps(grade, grade_secondary_short, start_step):
    """Generate grading steps based on grade and grade_secondary with dynamic step numbers"""
    grade_secondary = convert_grade_secondary_to_full(grade_secondary_short)

    if grade == 'Neither satisfied nor dissatisfied':
        return f'''
        {start_step}. Select {grade}
        {start_step + 1}. Select "Archive"
        '''
    elif grade == 'Very satisfied' and grade_secondary == 'Booked':
        return f'''
        {start_step}. Select {grade}
        {start_step + 1}. Select "It converted into a booked customer or client"
        {start_step + 2}. Select "Done"
        {start_step + 3}. Select "Mark Booked"
        {start_step + 4}. Select "Save"
        '''
    elif grade == 'Very satisfied' and grade_secondary != 'Booked':
        return f'''
        {start_step}. Select {grade}
        {start_step + 1}. Select {grade_secondary}
        {start_step + 2}. Select "Archive"
        '''
    elif grade == 'Very dissatisfied':
        return f'''
        {start_step}. Select {grade}
        {start_step + 1}. Select {grade_secondary}
        {start_step + 2}. Select "Archive"
        '''
    else:
        raise ValueError(f"Invalid grade: {grade}")


async def main():
    customers_to_grade = process_args(sys.argv[1:])

    # (215) 804-8145 GRADED: satisfied -> booked
    # (503) 334-5574
    # (971) 218-7149

    # customers_to_grade = [
    #     Customer(phone='(503) 334-5574', grade='Neither satisfied nor dissatisfied', grade_secondary=''),
    #     Customer(phone='(971) 218-7149', grade='Very satisfied', grade_secondary='Booked'),
    # ]

    prompt_parts = [
    '''
    1. Login using g_username & g_password for their respective sections.
    2. Wait 1 second
    3. Select Advantage Heating & Air Conditioning
    4. Wait 1 second
    5. Filter the table by selecting "Any lead type" dropdown menu & use up down arrows to highlight "Phone leads" and select using enter. No need to scroll 
    6. Wait 1 second
    7. Filter the table by selecting "Any charge status" dropdown menu & use up down arrows to highlight "Charged leads" and select using enter. No need to scroll
    '''
    ]

    # Add steps for each customer
    step_counter = 8
    for i, customer in enumerate(customers_to_grade):
        phone = customer.get_phone()
        grade, grade_secondary = customer.get_grades()
        grading_steps = generate_grading_steps(grade, grade_secondary, step_counter + 4)
        
        customer_steps = f'''
        {step_counter}. Locate number: "{phone}"
            - Might be located on a different page. Use pagination buttons located at the bottom of the table to navigate. Be sure to thoroughly scroll each new page you are searching. don't just search within the current view window
            - If number not found, try searching for number one more time before moving to the next page.
        {step_counter + 1}. Select "{phone}" row when located.
        {step_counter + 2}. Select "Rate this lead"
        {step_counter + 3}. Wait 1 second
        {grading_steps}
        '''
        
        # Calculate how many steps the grading process takes
        if grade == 'Neither satisfied nor dissatisfied':
            grading_step_count = 2
        elif grade == 'Very satisfied' and grade_secondary == 'Booked':
            grading_step_count = 5
        else:  # 'Very satisfied' (non-booked) or 'Very dissatisfied'
            grading_step_count = 3
        
        # If not the last customer, add step to return to main table
        if i < len(customers_to_grade) - 1:
            return_step = step_counter + 4 + grading_step_count
            customer_steps += f'''
        {return_step}. Return to table by clicking the arrow on top left of the screen.
        {return_step + 1}. Wait 1 second
        '''
            step_counter = return_step + 2
        else:
            step_counter = step_counter + 4 + grading_step_count
        
        prompt_parts.append(customer_steps)

    # Add final stop instruction
    prompt_parts.append(f'''
    {step_counter}. STOP ALL ACTIONS
    ''')

    # Combine all parts
    prompt = ''.join(prompt_parts)

    # print(f"Processing {len(customers_to_grade)} customers:")
    # for customer in customers_to_grade:
    #     phone = customer.get_phone()
    #     grade, grade_secondary = customer.get_grades()
    #     print(f"  - {phone}: {grade} -> {grade_secondary}")
    # print()

    initial_actions = [
        {'open_tab': {'url': 'https://ads.google.com/localservices/'}},
    ]

    sensitive_data = {'g_username': USERNAME, 'g_password': PASSWORD}

    # Configure browser session for Replit
    if 'REPL_ID' in os.environ:
        # For Replit - use system chromium and disable headless for VNC
        browser_session = BrowserSession(
            headless=False,  # Enable VNC display
            browser_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--remote-debugging-port=9222",
                "--display=:0"  # Use VNC display
            ],
            executable_path=os.getenv('CHROME_BIN', '/nix/store/*/chromium/bin/chromium')
        )
    else:
        browser_session = BrowserSession(headless=False)


    agent = Agent(
        task=prompt,
        llm=llm,
        initial_actions=initial_actions,
        sensitive_data=sensitive_data,
        browser_session=browser_session
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
