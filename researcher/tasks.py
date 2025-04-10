from core.methods import send_notification
from huey.contrib.djhuey import task
from researcher.methods import generate_business_profile, generate_query, research
import markdown2

@task()
def process_research(company_name):
    queries = []

    send_notification("notification","Generating financial queries...")
    financial_queries = generate_query("Financial", company_name)

    send_notification("notification","Generating leadership queries...")
    leadership_queries = generate_query("Leadership", company_name)

    send_notification("notification","Generating operations queries...")
    operations_queries = generate_query("Operations", company_name)

    send_notification("notification","Generating corporate history queries...")
    corporate_history_queries = generate_query("Corporate History", company_name)


    queries.extend(financial_queries.get("queries"))
    queries.extend(leadership_queries.get("queries"))
    queries.extend(operations_queries.get("queries"))
    queries.extend(corporate_history_queries.get("queries"))

    context = ""

    for query in queries:
        send_notification("notification", f"Processing query: {query}")
        response = research(query)
        context += f"Query: {query}\nResponse: {response}\n\n"

    send_notification("notification", "Generating business profile...")

    business_profile = generate_business_profile(context)
    html = markdown2.markdown(business_profile)
    send_notification("business_profile", html)

