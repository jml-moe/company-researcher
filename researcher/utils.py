from tavily import TavilyClient
from dotenv import load_dotenv
import os
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
