from openai import OpenAI
from data import OPENAI_API_KEY

api_key = OPENAI_API_KEY

def sentiment_analysis(transcript: str) -> tuple:

    prompt = f'''
    
        You are a lead grader for Google LSA leads. Your job is to review call transcripts and grade them according to a strict schema. You will output exactly **one** of the bracketed options below and nothing else—no additional explanations, no punctuation outside the angle brackets, and no text before or after.

        **Permissible Output Options** (choose exactly one):
        ```
        <Very satisfied - Booked>
        <Very satisfied - Could convert to a booked client>
        <Very dissatisfied - Spam/Robocall>
        <Very dissatisfied - Employment/Sales Pitch>
        <Very dissatisfied - Wrong Number>
        <Neither satisfied nor dissatisfied>
        <Very dissatisfied - Outside service area>
        <Very dissatisfied - Service not offered>
        <Very satisfied - High value to the business>
        <Very dissatisfied - Other>
        <Not confident>
        ```

        ---
        **Company & Services Overview**  
        Use this information to better understand the context of calls:

        - **Company:** Advantage Heating & Air Conditioning, LLC  
        - Based in Salem, OR  
        - Known for residential HVAC services; customer reviews highlight professionalism and timeliness  

        - **Services Offered:**  
        - Heating: Installation, repair, and maintenance (including heat pumps and furnaces)  
        - Air Conditioning: Installation, repair, maintenance (including ductless mini splits, VIP maintenance plans)  
        - Indoor Air Quality: General improvement services  
        - Additional: Electrical and commercial HVAC services  

        - **Service Area:**  
        - Cities: Salem, Keizer, Beaverton, Hillsboro, Woodburn, Wilsonville  
        - Counties: Marion, Polk, Clackamas, Yamhill, parts of Washington County  
        - Note: Leads from outside these areas (e.g., Portland, Eugene) should be flagged as “Outside Service Area”

        - **Emergency Services:** Offers 24-hour emergency service; leads requesting immediate help are highly relevant  
        - **Irrelevant Leads:** Spam/robocalls, employment inquiries, and sales pitches must be flagged as such.

        ---
        **Grading Workflow**  
        Follow these steps in order:

        Follow the following grading workflow step by step:

            Step 1.	Booked or not Booked:
            •	Find out if the caller booked an appointment, a sales followup, or if the caller references a previously scheduled/completed appointment and is simply following up (e.g., requesting an invoice, inquiring about status), mark as <Very satisfied - Booked>
            •	If they booked, immediately skip all following steps and mark lead as <Very satisfied - Booked>
            •	If they didn't book, move onto Step 2.
        Step 2. Booking Obstacles
            •	If the caller decided not to book specifically because: a) There wasn’t enough availability or the scheduling wait was too long; or b) The price was higher than they wanted to pay, and that’s why they declined; Then mark the lead as <Very Satisfied - Could convert to a booked client>.
        Important: If the caller is unhappy or disappointed because they cannot be scheduled soon enough or the price is too high, this still qualifies as <Very Satisfied - Could convert to a booked client>
            Step 3.	Caller Intent:
            •	Spam/robocalls or hang-ups should be marked as "Very dissatisfied" and “Spam/Robocall.”
            •	Employment inquiries or sales pitches should be marked as "Very dissatisfied" and “Employment/Sales Pitch”
            •	Wrong number dials should be marked as "Very dissatisfied" and "Wrong Number"
            •	If it is a missed call with no followup, mark as "Neither satisfied nor dissatisfied".
            •	If calling about HVAC services, continue to Step 4.
            •	Mark any other unique cases as "Other" with a short explanation.
            Step 4.	Location Check:
            •	Verify if the caller’s location is in Advantage's service area.
            •	If not (e.g., Portland, Eugene), mark lead as “Very dissatisfied” and “Outside service area”
            •	If it is in our service area, move to Step 5.
            Step 5.	Service Relevance:
            •	Confirm the caller requests HVAC services (heating, AC, or indoor air quality).
            •	Requests for services not offered (e.g., plumbing) should be marked as “Very dissatisfied” and “Service not offered”.
            •	If the caller is requesting services we offer but doesn't book, mark as "Very satisfied" and "could convert to a booked client".
        VERY IMPORTANT: If the caller is requesting specifically Installation services (not repair, electrical, etc), mark as "Very satisfied" and "High value to the business".

        If you cannot confidently determine one of these categories, output `<Not confident>`.

        ---

        **Important**:
        - **Your final output must be exactly one of the bracketed options above.**  
        - **Do not add any text, explanation, or punctuation beyond the single bracketed label.**  


        Use this transcript:
        {transcript}'''

    # Initialize the client
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="o3-mini", #"gpt-3.5-turbo", #"o3-mini-2025-01-31",
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
    return output

#if __name__ == "__main__":

    # test = '''
    # (971) 998-9211 • 0:00
    # The person you're trying to reach is not available. At the tone, please record your message. When you have finished recording you may hang up.

    # Krystal • 0:08
    # Hi, this is Crystal with Advantage Heating and Electrical. This message is for Claudia. I was calling to confirm your appointment with us for tomorrow with an arrival window of 120 p.m. to 3 p.m. If you need to cancel or reschedule this, please give us a call back at 503-393-5315. Otherwise we look forward to seeing you tomorrow between 12 and 30 p.m. Thank you so much and have a great day.
    # '''

    # d=sentiment_analysis(test)
    # print(d)

    # test_transcripts = 

    # customers=
    # i=0
    # for transcript in test_transcripts:
    #     d = sentiment_analysis(transcript)
    #     print(customers[i], d)
    #     i+=1
        
