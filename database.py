import pymongo
import certifi
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://erthirukumaran_db_user:Thiru1234@cluster0.l358pfx.mongodb.net/MentionFlowDB?retryWrites=true&w=majority")

db = None
posts_collection = None

try:
    print("--- Connecting to MongoDB Atlas ---")
    
    
    client = pymongo.MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000 
    )
    
    
    client.admin.command('ping')
    
   
    db = client['MentionFlowDB']
    posts_collection = db['mentions']
    
    print("SUCCESS: Database connection established.")

except Exception as e:
    
    print(f"CRITICAL ERROR: Could not connect to MongoDB. Details: {e}")
    sys.exit(1)

def save_posts_to_db(posts, search_query):
    """
    Saves or updates LinkedIn posts in the database.
    Prevents duplicates by using the post URL as a unique key (Upsert).
    """
    if posts_collection is None:
        print("ERROR: Database not initialized. Cannot save data.")
        return

    count = 0
    for post in posts:
        
        post_data = {
            "title": post.get("title", "No Title"),
            "link": post.get("link"),
            "snippet": post.get("snippet", ""),
            "source": "LinkedIn",
            "keyword_used": search_query,
            "extracted_at": datetime.utcnow(),
            "status": "new"
        }
        
        
        if not post_data["link"]:
            continue

       
        try:
            result = posts_collection.update_one(
                {"link": post_data["link"]},
                {"$set": post_data},
                upsert=True
            )
            
            
            if result.upserted_id or result.modified_count > 0:
                count += 1
        except Exception as write_error:
            print(f"Minor Error saving post: {write_error}")
            
    print(f"DATABASE SYNC: {count} new or updated posts added for query: '{search_query}'")

if __name__ == "__main__":
    print("Database module test run...")
  