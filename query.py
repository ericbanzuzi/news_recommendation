from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200/'])

# Define the query to search for a specific title
query = {
    "query": {
        "match": {
            "title": "You'll never guess where Detroit Tigers went, but it shows why they can be good this year"
        }
    }
}

# Perform the search on the specified index
resp = es.search(index="your_index_name", body=query)
print("Search results:")
for hit in resp['hits']['hits']:
    # Print only the title from the source of each hit
    print(hit['_source']['url'])
