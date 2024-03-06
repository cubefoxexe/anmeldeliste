from dotenv import load_dotenv
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

load_dotenv()

username = os.getenv('myusername')
password = os.getenv('mypassword')
api = os.getenv('api')

async def login(page):
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('.submit')

async def start():
    async with async_playwright() as p:
        browser_context = await p.chromium.launch_persistent_context(user_data_dir='./userdata', headless=False)
        page = await browser_context.new_page()
        await page.goto(api)
        if page.url != api:
            await login(page)
        await page.goto(api)
        content = await page.content()
        await page.close()
        await browser_context.close()
        return content

async def weeks():
    content = await start()
    soup = BeautifulSoup(content, 'html.parser')
    json_content = soup.find('pre', style='word-wrap: break-word; white-space: pre-wrap;').text
    parsed = json.loads(json_content)

    info = {}
    for week in parsed['weeks']:
        name = week['name'].split(':')[0].strip()
        has_slot = any(day['slots'] for day in week['days'])
        info[name] = has_slot

    return info

async def new_week(info1, info2):
    for key, value in info1.items():
        if info2[key] != value:
            return key
    
    return None
        

