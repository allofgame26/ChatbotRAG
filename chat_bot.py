import mysql.connector
import json
import ollama

from sentence_transformers import SentenceTransformer

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:8b"

llm_agent = ollama.Client(host=OLLAMA_HOST)

embedder = SentenceTransformer('BAAI/bge-m3')

db = mysql.connector.connect(
    host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port = 4000,
    user = "4YvLUbDeDAvchK1.root",
    password = "W2aTVSgdXCXkno0D",
    database = "RAG",
    ssl_ca = "isrgrootx1.pem",
    ssl_verify_cert = True,
    ssl_verify_identity = True
) # menyambungkan ke database TiDB Cloud

# melakukan query untuk mengambil data dari tabel knowledge_base

def search_document(database,query , top_k=5):
    results = []
    
    query_embedding_list = embedder.encode(query).tolist()
    query_embedding_str = json.dumps(query_embedding_list)

    cursor = database.cursor()
    
    sql_query = """ SELECT text, vec_cosine_distance(embedding, %s ) AS distance FROM documents order BY distance ASC limit %s; """
    cursor.execute(sql_query, (query_embedding_str,top_k))
    search_results = cursor.fetchall()
    database.commit()
    cursor.close()

    for result in search_results:
        text, distance = result
        results.append({
            'text': text,
            'distance': distance
        })
    return results

def respone_query(database,query):
    retrieve_doc = search_document(database, query)

    context = "\n".join([doc['text'] for doc in retrieve_doc])
    prompt = f"You are a helpful assistant. Use the following context to answer the question. answer following question based on the provided context {context} \n\n question:{query}"
    response = llm_agent.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])

    return response['message']['content']

if __name__ == "__main__":
    print("Chat Bot is running...")
    while True:
        query_text = input("Prompt: ")

        if query_text.lower() in ['exit', 'quit', 'q']:
            print("Exiting Chat Bot.")
            break
    
        response = respone_query(db,query_text)
        print("Chatbot:", response)

print("Chat Bot has stopped.")