from pymongo import MongoClient
# Establish a connection to MongoDB
client = MongoClient('mongodb://172.16.232.251:27017/')

# Create a new database
db = client['health_articles']
# Create a new collection (table)
collection = db['articles']
# Close the connection
client.close()