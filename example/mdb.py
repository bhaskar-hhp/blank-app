#import streamlit as st
from pymongo import MongoClient

client = MongoClient("mongodb+srv://bhaskar:bhaskar@cluster0.tvgh7sc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["my_database"]

print("✅ Connected!")

# List collections in the DB
print("Collections:", db.list_collection_names())

collection = db["Dist"]

print("📋 Serached Distributor Names")

results = collection.find_one({"id": "RTL1000","pwd":1234}, {"_id":0,"name":1,"id":1,"pwd":1})  # The second argument is the projection (empty = return all fields)
#print(results)

if results:
    #for doc in results:
    print(results)    
else:
    print("No record Found")
