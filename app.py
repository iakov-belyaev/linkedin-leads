import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load the environment variables strictly from the local .env file
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("Missing DEEPSEEK_API_KEY. Please ensure it is set inside your .env file.")

# 2. Initialize DeepSeek Client
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

# Connect to the SQLite Database from Phase 1
conn = sqlite3.connect('cyprus_leads.db')
cursor = conn.cursor()

def get_next_lead():
    """Fetches the next unprocessed lead from the database."""
    cursor.execute("SELECT id, linkedin_url, title_snippet, body_snippet FROM leads WHERE status='New' LIMIT 1")
    return cursor.fetchone()

def generate_pitch(title, body):
    """Uses DeepSeek API to parse the search snippet and write a pitch."""
    prompt = f"""
    You are an expert B2B event organiser based in Cyprus. 
    Review the following search engine snippet for a LinkedIn profile.
    
    Profile Title/Name: {title}
    Profile Bio/Snippet: {body}
    
    Task:
    1. Identify their company and role if possible.
    2. Write a short, highly personalized 2-3 sentence LinkedIn connection request message (max 300 characters). 
    3. The pitch should offer high-end corporate event organization, team-building, or offsites.
    4. Write it in English unless the profile is exclusively in Russian.
    
    Output ONLY the pitch text, with no introductory or concluding remarks.
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a concise, professional B2B copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating pitch: {str(e)}"

def load_lead_into_ui():
    """Loads the next lead and generates the draft for the UI."""
    global current_lead_id, current_url
    
    lead = get_next_lead()
    if not lead:
        messagebox.showinfo("Done", "No more new leads in the database!")
        root.quit()
        return
        
    current_lead_id, url, title, body = lead
    current_url = url
    
    # Update UI with raw data
    url_label.config(text=f"URL: {url}")
    raw_data_text.delete("1.0", tk.END)
    raw_data_text.insert(tk.END, f"TITLE:\n{title}\n\nSNIPPET:\n{body}")
    
    # Generate and display DeepSeek pitch
    draft_text.delete("1.0", tk.END)
    draft_text.insert(tk.END, "DeepSeek is generating a personalized pitch...")
    root.update()
    
    pitch = generate_pitch(title, body)
    
    draft_text.delete("1.0", tk.END)
    draft_text.insert(tk.END, pitch)

def approve_and_copy():
    """Copies the pitch to clipboard and marks the lead as processed."""
    pitch = draft_text.get("1.0", tk.END).strip()
    
    # Copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(pitch)
    
    # Update Database
    cursor.execute("UPDATE leads SET status='Processed', ai_draft_pitch=? WHERE id=?", (pitch, current_lead_id))
    conn.commit()
    
    # Move to next
    load_lead_into_ui()

def skip_lead():
    """Marks the lead as skipped if it's irrelevant or low quality."""
    cursor.execute("UPDATE leads SET status='Skipped' WHERE id=?", (current_lead_id,))
    conn.commit()
    load_lead_into_ui()

# --- Build Tkinter GUI ---
root = tk.Tk()
root.title("DeepSeek Lead Sandbox - Cyprus Events")
root.geometry("700x550")
root.configure(padx=20, pady=20)

current_lead_id = None
current_url = None

tk.Label(root, text="Raw Search Snippet", font=("Arial", 12, "bold")).pack(anchor="w")
url_label = tk.Label(root, text="URL: ", fg="blue", cursor="hand2")
url_label.pack(anchor="w", pady=(0, 5))

raw_data_text = tk.Text(root, height=6, wrap=tk.WORD, bg="#f0f0f0")
raw_data_text.pack(fill="x", pady=(0, 15))

tk.Label(root, text="DeepSeek Draft Pitch", font=("Arial", 12, "bold")).pack(anchor="w")
draft_text = tk.Text(root, height=6, wrap=tk.WORD, font=("Arial", 11))
draft_text.pack(fill="x", pady=(0, 20))

btn_frame = tk.Frame(root)
btn_frame.pack(fill="x")

tk.Button(btn_frame, text="Reject / Skip", command=skip_lead, bg="#ffcccb", width=15, height=2).pack(side="left", padx=10)
tk.Button(btn_frame, text="Approve & Copy", command=approve_and_copy, bg="#90ee90", font=("Arial", 10, "bold"), width=20, height=2).pack(side="right", padx=10)

# Start the loop
load_lead_into_ui()
root.mainloop()

# Close DB when UI closes
conn.close()