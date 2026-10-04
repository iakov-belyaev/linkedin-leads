import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DB_PATH = "cyprus_leads.db"

# X-Ray queries targeting Cyprus decision-makers
SEARCH_QUERIES = [
    'site:cy.linkedin.com/in "Cyprus" ("HR" OR "Human Resources" OR "Head of People")',
    'site:cy.linkedin.com/in "Cyprus" ("Procurement" OR "Purchasing" OR "Отдел Закупок" OR "Закупки")',
    'site:cy.linkedin.com/in "Limassol" ("HR" OR "Human Resources" OR "Head of People")',
    'site:cy.linkedin.com/in "Limassol" ("Procurement" OR "Purchasing" OR "Отдел Закупок" OR "Закупки")'
]