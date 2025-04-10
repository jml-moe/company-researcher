from pydantic import BaseModel
from core.prompt_manager import PromptManager
from researcher.prompts import QUERY_GENERATOR_PROMPT, BUSINESS_PROFILE_PROMPT
from researcher.utils import tavily_client

class Queries(BaseModel):
    category: str
    queries: list[str]

def generate_query(category, company_name):
    pm = PromptManager()
    pm.add_message("system", QUERY_GENERATOR_PROMPT.format(category=category, company_name=company_name))
    pm.add_message("user", f"Generate a query for a {category} about {company_name}")
    return pm.generate_structured(Queries)

def research(query):
    response = tavily_client.qna_search(query=query)
    return response

def generate_business_profile(context):
    pm = PromptManager()
    pm.add_message("system", BUSINESS_PROFILE_PROMPT)
    pm.add_message("user", f"Generate a business profile for a company based on the following context: {context}")
    return pm.generate()