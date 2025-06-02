from data import Customer, USERNAME, PASSWORD

from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4.1") #gpt-4o

# (215) 804-8145 GRADED
# (503) 334-5574
#graded_customer = Customer(phone='(215) 804-8145', grade='Very satisfied', grade_secondary='Booked')

customers_to_grade = [
    Customer(phone='(215) 804-8145', grade='Very satisfied', grade_secondary='Booked'),
    Customer(phone='(503) 334-5574', grade='Neither satisfied nor dissatisfied', grade_secondary=''),
]

def generate_grading_steps(grade, grade_secondary):
    """Generate grading steps based on grade and grade_secondary"""
    if grade == 'Neither satisfied nor dissatisfied':
        return f'''
        12. Select {grade}
        13. Select "Archive"
        '''
    elif grade == 'Very satisfied' and grade_secondary == 'Booked':
        return f'''
        12. Select {grade}
        13. Select "It converted into a booked customer or client"
        14. Select "Done"
        15. Select "Mark Booked"
        16. Select "Save"
        '''
    elif grade == 'Very satisfied' and grade_secondary != 'Booked':
        return f'''
        12. Select {grade}
        13. Select {grade_secondary}
        14. Select "Archive"
        '''
    elif grade == 'Very dissatisfied':
        return f'''
        12. Select {grade}
        13. Select {grade_secondary}
        14. Select "Archive"
        '''
    else:
        raise ValueError(f"Invalid grade: {grade}")

async def main():
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
        grading_steps = generate_grading_steps(grade, grade_secondary)
        
        customer_steps = f'''
        {step_counter}. Locate number: "{phone}"
            - Might be located on a different page. Use pagination buttons located at the bottom of the table to navigate. Be sure to thoroughly scroll each new page you are searching. don't just search within the current view window
            - If number not found, try searching for number one more time before moving to the next page.
        {step_counter + 1}. Select "{phone}" row when located.
        {step_counter + 2}. Select "Rate this lead"
        {step_counter + 3}. Wait 1 second
        {grading_steps}
        '''
        
        # If not the last customer, add step to return to main table
        if i < len(customers_to_grade) - 1:
            customer_steps += f'''
        {step_counter + 4}. Return to the main leads table to process the next customer
        {step_counter + 5}. Wait 1 second
        '''
            step_counter += 6
        else:
            step_counter += 4
        
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

    # prompt = f'''
    # 1. Login using g_username & g_password for their respective sections.
    # 2. Wait 1 second
    # 3. Select Advantage Heating & Air Conditioning
    # 4. Wait 1 second
    # 5. Filter the table by selecting "Any lead type" dropdown menu & use up down arrows to highlight "Phone leads" and select using enter. No need to scroll 
    # 6. Wait 1 second
    # 7. Filter the table by selecting "Any charge status" dropdown menu & use up down arrows to highlight "Charged leads" and select using enter. No need to scroll
    # 8. Locate number: "{phone}"
    #     - Might be located on a different page. Use pagnation buttons located at the bottom of the table to navigate. Be sure to thoroughly scroll each new page you are searching. don't just search within the current view window
    #     - If number not found, try searching for number one more time before moving to the next page.
    # 9. Select "{phone}" row when located.
    # 10. Select "Rate this lead"
    # 11. Wait 1 second
    # {grading_steps}
    # 15. STOP ALL ACTIONS
    # '''    
    #-Hit "All time" dropdown menu & select Last month

    initial_actions = [
        {'open_tab': {'url': 'https://ads.google.com/localservices/'}},
    ]

    sensitive_data = {'g_username': USERNAME, 'g_password': PASSWORD}

    agent = Agent(
        task=prompt,
        llm=llm,
        initial_actions=initial_actions,
        sensitive_data=sensitive_data
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
