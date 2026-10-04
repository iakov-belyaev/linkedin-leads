import time
from ddgs import DDGS
from config import SEARCH_QUERIES
from db import init_db, insert_lead

# URL path segments that indicate a non-personal LinkedIn page.
INVALID_URL_MARKERS = ("/jobs/", "/company/", "/posts/", "/dir/")

def is_valid_profile_url(url: str) -> bool:
    """Return True only for personal LinkedIn profile URLs (contain '/in/')."""
    if not url:
        return False
    lowered = url.lower()
    if "/in/" not in lowered:
        return False
    if any(marker in lowered for marker in INVALID_URL_MARKERS):
        return False
    return True

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
                results = list(ddgs.text(query, max_results=max_results_per_query))
                raw_count = len(results)
                added_count = 0
                valid_count = 0
                for res in results:
                    url = res.get('href', '')
                    title = res.get('title', '')
                    body = res.get('body', '')
                    
                    if not is_valid_profile_url(url):
                        continue

                    valid_count += 1
                    if insert_lead(url, title, body, target_role=role_tag):
                        added_count += 1
                
                total_added += added_count
                print(f"[Scraper] Raw hits: {raw_count}, passed validation: {valid_count}, new leads inserted: {added_count}.")
            except Exception as e:
                print(f"[Scraper] Error during query execution: {e}")
            
            time.sleep(2)  # Respect rate limits

    print(f"\n[Scraper] Complete. Total new leads inserted: {total_added}")

if __name__ == "__main__":
    run_scraper()
