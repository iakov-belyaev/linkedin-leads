import time
from duckduckgo_search import DDGS
from config import SEARCH_QUERIES
from db import init_db, insert_lead

def run_scraper(max_results_per_query=50):
    init_db()
    print("[Db] Database initialized.")
    
    total_added = 0
    with DDGS() as ddgs:
        for query in SEARCH_QUERIES:
            print(f"\n[Scraper] Executing search: {query}")
            
            # Tag role focus based on search string
            role_tag = "Procurement" if ("Procurement" in query or "Закупки" in query) else "HR"
            
            try:
                results = ddgs.text(query, max_results=max_results_per_query)
                added_count = 0
                for res in results:
                    url = res.get('href', '')
                    title = res.get('title', '')
                    body = res.get('body', '')
                    
                    if url and insert_lead(url, title, body, target_role=role_tag):
                        added_count += 1
                
                total_added += added_count
                print(f"[Scraper] Added {added_count} new leads.")
            except Exception as e:
                print(f"[Scraper] Error during query execution: {e}")
            
            time.sleep(2)  # Respect rate limits

    print(f"\n[Scraper] Complete. Total new leads inserted: {total_added}")

if __name__ == "__main__":
    run_scraper()