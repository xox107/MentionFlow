import pymongo
import certifi
import sys
from datetime import datetime
MONGO_URI = "mongodb://erthirukumaran_db_user:Thiru1234@ac-fmw4blu-shard-00-00.l358pfx.mongodb.net:27017/MentionFlow?ssl=true&authSource=admin&directConnection=true"
db = None
posts_collection = None

try:
    print("Connecting to MongoDB Atlas...")
    
   
    client = pymongo.MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000 
    )
    
    
    client.admin.command('ping')
    
    db = client['MentionFlowDB']
    posts_collection = db['mentions']
    
    print("✅ Connection Successful!")

except Exception as e:
    print(f"❌ Still failing: {e}")
    print("\n💡 Troubleshooting Tip: Check if your IP is whitelisted and if your password is correct.")
    sys.exit(1)

def save_posts_to_db(posts, search_query):
    """
    Saves or updates LinkedIn posts in the database.
    Prevents duplicates by using the post URL as a unique key.
    """
    if posts_collection is None:
        print("❌ Database not initialized. Cannot save.")
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

        
        result = posts_collection.update_one(
            {"link": post_data["link"]},
            {"$set": post_data},
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            count += 1
            
    print(f"📂 DB Sync: {count} posts updated/inserted for query: '{search_query}'")

n
if __name__ == "__main__":
    print("Testing database module...")