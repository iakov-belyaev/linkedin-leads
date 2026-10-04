the repo layout for AI reference
cyprus-event-leads/
├── .env.example          # Template for environment variables
├── .gitignore            # Ignores .env, *.db, __pycache__, venv
├── requirements.txt      # Python package dependencies
├── config.py             # Centralized settings & search query parameters
├── db.py                 # SQLite CRUD operations & schema initialization
├── scraper.py            # DuckDuckGo X-Ray search engine ingestion
├── enricher.py           # DeepSeek API integration & prompt engineering
├── app.py                # Tkinter desktop review UI & clipboard runner
└── README.md             # Complete system blueprint for Aider