import os
import sys

# Windows console encoding fix for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import asyncio
from config import Config
from services.openai_service import AIService
from services.weather_service import WeatherService
from dotenv import load_dotenv

load_dotenv()

async def test_all():
    ai = AIService()
    weather = WeatherService()
    
    # Test weather first since AI was crashing
    try:
        print("Testing Weather...")
        w_res = await weather.get_weather("Delhi")
        print("Weather result:", w_res)
    except Exception as e:
        print("Weather error:", e)

    # Test summarize
    try:
        print("\nTesting Summarize...")
        text = "Artificial Intelligence (AI) is the simulation of human intelligence by computer systems. It involves developing algorithms to mimic cognitive functions."
        res = await ai.summarize(text)
        print("Summarize result:", res)
    except Exception as e:
        print("Summarize error:", e)
    
    # Test chat fallback
    try:
        print("\nTesting Chat...")
        c_res = await ai.chat("user123", "hi")
        print("Chat result:", c_res)
    except Exception as e:
        print("Chat error:", e)

if __name__ == "__main__":
    asyncio.run(test_all())
