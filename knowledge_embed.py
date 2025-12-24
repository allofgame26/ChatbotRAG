#install pip Ollama
#pip sentence-transformers untuk mengubah data menjadi vektor
#install mysql-connector-python untuk koneksi database mysql TiDB
#intall pandas untuk mengolah data
import json
import pandas as pd
import mysql.connector

from sentence_transformers import SentenceTransformer

#membuat instance untuk embedding model

embedder = SentenceTransformer('BAAI/bge-m3') #running pertama kali untuk menginstal model

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
cursor = db.cursor()

# membaca data knowledge base dari file csv

df = pd.read_csv('data_knowledge.csv', sep=';') # jika menggunakan delimiter ;, jangan lupa memberikan sep=';'
# print(df)

for index, row in df.iterrows():
    text = str(row['question']) + " " + str(row['answer'])
    # print(text)

    try:
        # melakukan encoding teks menjadi vektor
        embeding_list = embedder.encode(text).tolist()
        # merubah vektor menjadi string json
        embedding_str = json.dumps(embeding_list)

        sql_query = """ INSERT INTO documents (text,embedding) values (%s,%s)"""

        #mengirim data ke database
        cursor.execute(sql_query, (text, embedding_str))
        print(f"Inserted embedding for index {index}")

        # print(embeding_list) # menampilkan hasil embedding
    except Exception as e:
        # pass
        print(f"Error encoding text at index {index}: {e}")

db.commit()
cursor.close()
print("Data berhasil di tambahkan ke database.")