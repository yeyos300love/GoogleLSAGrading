from browser_use import Agent, BrowserSession
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
import os


async def run_agent(start_date, end_date):
    """Run the browser-use agent"""
    llm = ChatOpenAI(model="gpt-4.1")

    prompt = f'''
    1. You are setting the custom date range from {start_date} to {end_date}. The calendar popup is already open
    2. Set start date first to: {start_date} by:
        - Set correct month, use pagnation buttons of calendar popup to navigate to the correct month if necessary.
        - Click on the correct day
    3. Next, set end date to: {end_date} by:
        - Set correct month, use pagnation buttons of calendar popup to navigate to the correct month if necessary.
        - Click on the correct day
    4. STOP ALL ACTIONS
    '''
    
    # Configure browser session to connect to existing browser
    if 'REPL_ID' in os.environ:
        os.environ['CHROMIUM_FLAGS'] = '--no-sandbox --disable-setuid-sandbox --disable-seccomp-filter-sandbox'
        browser_session = BrowserSession(
            headless=False,
            debug_port=9223,
            cdp_url="http://localhost:9223",
            connect_to_existing_browser=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox", 
                "--disable-seccomp-filter-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--remote-debugging-port=9223",
                "--display=:0"
            ],
            executable_path=os.getenv('CHROME_BIN', '/nix/store/*/chromium/bin/chromium')
        )

    agent = Agent(
        task=prompt,
        llm=llm,
        browser_session=browser_session
    )

    result = await agent.run()
    return result

#import asyncio
#if __name__ == '__main__':
#    asyncio.run(run_agent())
