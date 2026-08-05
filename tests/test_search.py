from app.services.embeddings import create_embedding
from app.services.search import search_documents


question = "What skills are listed in the document?"


query_vector = create_embedding(question)


results = search_documents(query_vector)


for item in results:

    print("\n---")
    print("File:", item[0])
    print("Page:", item[1])
    print("Distance:", item[4])
    print(item[3][:300])