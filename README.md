# Cyprus B2B Event Outreach Lead Sandbox

An offline, zero-cost lead generation pipeline designed to find, parse, and draft personalized outreach pitches for decision-makers in Cyprus (HR, Head of People, Procurement / Отдел Закупок). 

It uses DuckDuckGo X-Ray searches to bypass LinkedIn scraping protections, stores raw profile snippets in a local SQLite database, enriches profiles with DeepSeek AI pitches, and presents them in a local Tkinter desktop GUI for human approval.

---

## 1. System Architecture & Workflow
[ DuckDuckGo Search ] ──> (scraper.py) ──> [ SQLite Database ] (cyprus_leads.db)
│
▼
[ DeepSeek API ] <── (enricher.py) <─── (app.py: Tkinter GUI)
│                                       │
└────── Drafted Pitch ──────────────────┴─> [ Human Review ] ──> Clipboard

1. **Ingestion (`scraper.py`)**: Runs targeted X-Ray queries against search engine indexes for Cyprus profiles. Deduplicates and writes raw snippet data to `cyprus_leads.db`.
2. **Database Abstraction (`db.py`)**: Handles table schema, connection pooling, and atomic state updates (`New`, `Processed`, `Skipped`).
3. **AI Generation (`enricher.py`)**: Sends snippet context to DeepSeek (`deepseek-chat`) via the OpenAI SDK format to craft 2-3 sentence (< 300 character) connection pitches in English or Russian.
4. **Human Circuit-Breaker (`app.py`)**: Tkinter GUI displays raw snippet alongside the AI draft. On "Approve & Copy", marks lead as processed and copies pitch to system clipboard.

---

## 2. File Specifications & Modules

### `config.py`
Centralized configuration module. Loads `.env` using `python-dotenv`.
- **`DEEPSEEK_API_KEY`**: DeepSeek API key fetched strictly from `.env`.
- **`DB_PATH`**: Path to local SQLite file (`cyprus_leads.db`).
- **`SEARCH_QUERIES`**: List of targeted search operators targeting Cyprus HR and Procurement:
  - `site:cy.linkedin.com/in "Cyprus" ("HR" OR "Human Resources" OR "Head of People")`
  - `site:cy.linkedin.com/in "Cyprus" ("Procurement" OR "Purchasing" OR "Отдел Закупок" OR "Закупки")`

### `db.py`
Encapsulates all SQLite operations.
- **Table Schema (`leads`)**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `linkedin_url`: TEXT UNIQUE
  - `title_snippet`: TEXT
  - `body_snippet`: TEXT
  - `target_role`: TEXT (e.g., 'HR' or 'Procurement')
  - `status`: TEXT DEFAULT 'New' ('New', 'Processed', 'Skipped')
  - `ai_draft_pitch`: TEXT
  - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Functions**: `init_db()`, `insert_lead()`, `get_next_new_lead()`, `update_lead_status()`.

### `scraper.py`
Scrapes search results using `duckduckgo-search` and populates the database.
- Features rate limiting (`time.sleep`) between query batches.
- Handles duplicate URL collisions via SQL `IGNORE` or python exception handling.

### `enricher.py`
Wrapper for the DeepSeek API using `openai.OpenAI(base_url="https://api.deepseek.com")`.
- Accepts `title_snippet` and `body_snippet`.
- System Prompt: B2B corporate event specialist based in Cyprus.
- Outputs strict 2-3 sentence pitch (<300 chars) offering event management, offsites, or team-building. Auto-detects language (English vs Russian).

### `app.py`
Tkinter desktop UI.
- Displays lead URL, raw text snippet, and editable DeepSeek pitch text box.
- Actions:
  - **Approve & Copy**: Copies active pitch to clipboard, marks lead `Processed` in DB, auto-loads next lead.
  - **Skip**: Marks lead `Skipped` in DB, auto-loads next lead.
  - **Regenerate**: Calls `enricher.py` to draft a new pitch with higher temperature if the user wants another attempt.

---

## 3. Environment Setup & Installation

1. **Clone & Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

   Install Dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory (do not commit this file):

Code snippet
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
4. Execution Order
To run the pipeline manually:

Populate Database:

Bash
python scraper.py
Launch Review Dashboard:

Bash
python app.py
5. Tasks for Aider (Roadmap / Refinement Prompt)
When running Aider on this repository, focus on these enhancement priorities:

[ ] Error Handling in enricher.py: Add graceful retry logic and timeout handling for DeepSeek API calls.

[ ] UI Polish in app.py: Add a counter showing total remaining leads (New status count), clickable hyperlink opening for linkedin_url, and an inline text length counter for the draft pitch (warning if > 300 characters).

[ ] Data Cleaning in scraper.py: Add regex filters to remove non-person URLs (e.g., jobs pages, company posts) before inserting into SQLite.

[ ] Editable Pitch Sync: Ensure that if the user manually edits the draft pitch text inside the Tkinter UI before clicking "Approve", the edited version is saved to ai_draft_pitch in SQLite.


---

### Supporting Configuration Files

#### `.env.example`
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
.gitignore
Plaintext
# Environment & Secrets
.env

# Database
*.db

# Python runtime
__pycache__/
*.py[cod]
*$py.class
venv/
.venv/

# IDE / Editors
.vscode/
.idea/
requirements.txt
Plaintext
duckduckgo-search>=6.0.0
openai>=1.0.0
python-dotenv>=1.0.0
How to Feed This to Aider
Once you create these files in your directory, you can kick off Aider in your terminal with:

Bash
aider --model deepseek/deepseek-chat config.py db.py scraper.py enricher.py app.py README.md
You can then pass Aider simple execution directives like:

"Read README.md and implement config.py, db.py, scraper.py, and enricher.py according to the module specs."