from openai import OpenAI
from config import DEEPSEEK_API_KEY

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY missing from environment/.env file.")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def generate_pitch(title_snippet: str, body_snippet: str, target_role: str = "HR") -> str:
    prompt = f"""
You are an expert B2B corporate event organiser based in Cyprus.
Review the following search engine snippet for a LinkedIn profile.

Target Department Focus: {target_role}
Profile Title/Name: {title_snippet}
Profile Snippet: {body_snippet}

Task:
1. Identify their company and exact role in Cyprus if possible.
2. Write a short, highly personalized 2-3 sentence LinkedIn connection request pitch (STRICTLY under 300 characters).
3. Tailor the offer to their department:
   - For HR / Head of People: Focus on corporate team building, summer parties, employer branding offsites, and holiday galas.
   - For Procurement / Отдел Закупок: Focus on reliable vendor partner execution, transparent pricing, and turnkey corporate event logistics.
4. Match the primary language of the profile snippet (write in Russian if the snippet is primarily Russian, otherwise write in English).

Output ONLY the raw pitch text with no quotes, greetings, or meta commentary.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a concise, sharp B2B outreach copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating pitch: {str(e)}"