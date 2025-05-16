import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Reference to 'users' collection
users_ref = db.collection("users")

# Insert sample documents (like rows)
sample_users = [
    {"id": "u001", "name": "Alice", "email": "alice@example.com", "role": "Admin", "location": "Mumbai"},
    {"id": "u002", "name": "Bob", "email": "bob@example.com", "role": "User", "location": "Delhi"},
    {"id": "u003", "name": "Charlie", "email": "charlie@example.com", "role": "Guest", "location": "Chennai"},
]

for user in sample_users:
    users_ref.document(user["id"]).set(user)

print("✅ Data inserted into Firestore.")

# Read back data
docs = users_ref.stream()
data = [doc.to_dict() for doc in docs]

# Convert to DataFrame
df = pd.DataFrame(data)
print("\n📄 Firestore Data as DataFrame:")
print(df)
