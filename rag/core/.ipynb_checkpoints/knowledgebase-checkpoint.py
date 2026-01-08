import chromadb

chroma_client = chromadb.Client()
collection_name = f"kb_{kb_id}"
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)
def store_chunks(collection, user_id, kb_id, doc_id, chunks, embeddings):
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        collection.add(
            ids=[f"{doc_id}_{idx}"],  # 各 chunk 唯一 ID
            embeddings=[emb],
            documents=[chunk],
            metadatas=[{
                "user_id": user_id,
                "kb_id": kb_id,
                "doc_id": doc_id,
                "chunk_index": idx,
            }]
        )
