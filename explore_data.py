#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

# Connect to MongoDB
mongo_url = "mongodb+srv://Tracity:Iate3ChocoL%40teC%40kes%21@cluster0.jhrt8ne.mongodb.net/"
client = AsyncIOMotorClient(mongo_url)
db = client["world_data"]

async def explore_database():
    print("🔍 Exploring MongoDB Database Structure...")
    print("=" * 60)
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"📁 Found {len(collections)} collections:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i}. {collection}")
    
    print("\n" + "=" * 60)
    
    # Explore each collection
    for collection_name in collections:
        if collection_name.startswith('system.'):
            continue
            
        print(f"\n📊 Collection: {collection_name}")
        print("-" * 40)
        
        # Get count
        count = await db[collection_name].count_documents({})
        print(f"Total documents: {count}")
        
        # Get sample documents
        sample_docs = await db[collection_name].find().limit(3).to_list(3)
        
        if sample_docs:
            print(f"\nSample document structure:")
            first_doc = sample_docs[0]
            # Remove _id for cleaner display
            clean_doc = {k: v for k, v in first_doc.items() if k != '_id'}
            print(json.dumps(clean_doc, indent=2, default=str))
            
            # Check for state-related fields
            state_fields = []
            for key in first_doc.keys():
                if any(term in key.lower() for term in ['state', 'region', 'province', 'area']):
                    state_fields.append(key)
            
            if state_fields:
                print(f"\n🌍 Potential state fields: {state_fields}")
                
                # Get unique values for state fields
                for field in state_fields[:2]:  # Limit to first 2 state fields
                    unique_values = await db[collection_name].distinct(field)
                    print(f"  {field} values ({len(unique_values)}): {unique_values[:10]}...")
            
            # Check for year-related fields
            year_fields = []
            for key in first_doc.keys():
                if any(term in key.lower() for term in ['year', 'date', 'time']):
                    year_fields.append(key)
            
            if year_fields:
                print(f"\n📅 Potential year fields: {year_fields}")
        
        print("\n" + "-" * 40)

if __name__ == "__main__":
    asyncio.run(explore_database())