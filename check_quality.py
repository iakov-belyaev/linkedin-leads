import sqlite3

conn = sqlite3.connect('cyprus_leads.db')
cursor = conn.cursor()

# Pull 5 sample leads across HR and Procurement
cursor.execute("SELECT id, target_role, linkedin_url, title_snippet, body_snippet FROM leads LIMIT 5")
leads = cursor.fetchall()

print("="*80)
print("LEAD QUALITY SAMPLE CHECK")
print("="*80)

for lead in leads:
    lead_id, role, url, title, body = lead
    print(f"\n[ID {lead_id}] Role Focus: {role}")
    print(f"URL: {url}")
    print(f"Title: {title}")
    print(f"Snippet: {body}")
    print("-" * 80)

conn.close()