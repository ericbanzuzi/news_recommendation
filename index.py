from elasticsearch import Elasticsearch
import os
import json

es = Elasticsearch(['http://localhost:9200/'])
folder_path = r'C:\Users\barta\OneDrive\Desktop\sep\news_recommendation\news_papers\FREEP'
for filename in os.listdir(folder_path):
    if filename.endswith(".json"): 
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                #print(data)
                response = es.index(index="your_index_name", document=data)
                print(f"Indexed {filename}: {response['_id']}")
            except json.JSONDecodeError:
                print(f"Failed to decode {filename}")
print("Indexing complete.")

