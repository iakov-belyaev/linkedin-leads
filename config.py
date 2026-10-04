import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DB_PATH = "cyprus_leads.db"

# X-Ray queries targeting Cyprus decision-makers
SEARCH_QUERIES = [
    'site:linkedin.com/in "Cyprus" "HR Manager"',
    'site:linkedin.com/in "Limassol" "HR"',
    'site:linkedin.com/in "Limassol" "Head of People"',
    'site:linkedin.com/in "Cyprus" "Procurement"',
    'site:linkedin.com/in "Limassol" "Purchasing"',
    'site:linkedin.com/in "Cyprus" "Отдел Закупок"'
]
