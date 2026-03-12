import requests
import json
import os
import sys
from datetime import datetime

from database import save_posts_to_db 


if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


API_KEY = os.getenv("SERPER_API_KEY", "60cdc13e66b32a43b6e4318bc59dc18a1cadb56c")
URL = "https://google.serper.dev/search"

def wipe_data():
    """Deletes old local JSON results to keep workspace clean."""
    count = 0
    for f in os.listdir('.'):
        if f.startswith('results_') and f.endswith('.json'):
            try:
                os.remove(f)
                count += 1
            except:
                pass
    if count > 0:
        print(f"--- Cleaned up {count} old local result files ---")

def run_search(query):
    """Hits the Serper API to find LinkedIn mentions from the last 6 months."""
    headers = {
        'X-API-KEY': API_KEY.strip(),
        'Content-Type': 'application/json'
    }
    payload = {
        "q": f"{query} site:linkedin.com/posts/",
        "tbs": "qdr:m6" 
    }
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get('organic', [])
        else:
            print(f"API ERROR {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return []

def main():
    print("--- MentionFlow Scraper Started ---")
    wipe_data()
    
    queries = [
        "Shayak Mazumder", 
        "Adya", 
        "Adya AI", 
        "Adya.ai ONDC LinkedIn",
        "Shayak Mazumder CEO Adya", 
        "Adya.ai social commerce",
        "Shayak Mazumder social commerce", 
        "CEO of Adya Shayak Mazumder"
    ]
    
    
    all_posts = []
    
    for q in queries:
        data = run_search(q)
        if data:
            all_posts.extend(data)
            print(f"SUCCESS: Found {len(data)} results for {q}")
            
           
            timestamp = datetime.now().strftime("%H%M%S")
            with open(f"results_{timestamp}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        else:
            print(f"INFO: No results found for {q}")
        
    print(f"--- Process Complete. Total unique posts collected: {len(all_posts)} ---")

    
    if all_posts:
        print("📤 Connecting to MongoDB Atlas for sync...")
        save_posts_to_db(all_posts, "Shayak Mazumder & Adya AI")
    else:
        print("⚠️ No data found to save to database.")

if __name__ == "__main__":
    main()