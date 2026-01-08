# pip install chromadb sentence_transformers

import os
import chromadb
from sentence_transformers import SentenceTransformer


# # ==============================================
# # 1. 初始化：向量数据库 + Embedding 模型
# # ==============================================
# chroma_client = chromadb.Client()
#
# # 🔥 推荐你未来换成：BAAI/bge-m3 或 bge-small-zh-v1.5
# # EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# MODEL_NAME = "BAAI/bge-small-zh-v1.5"
# CACHE_DIR = "./model_cache"
#
# embedder = SentenceTransformer(
#     MODEL_NAME,
#     cache_folder=CACHE_DIR
# )

# 本地下载
# ==============================================
# 1. 初始化：向量数据库 + Embedding 模型
# ==============================================
chroma_client = chromadb.Client()

# 改为本地模型目录
MODEL_NAME = "./model_cache/models--BAAI--bge-small-zh-v1.5/snapshots/7999e1d3359715c523056ef9478215996d62a620"
CACHE_DIR = "./model_cache"

embedder = SentenceTransformer(
    MODEL_NAME,
    # cache_folder=CACHE_DIR,
    local_files_only=True  # 禁止联网，只从本地加载
)


# ==============================================
# 2. 文本加载（支持 txt / md）
# ==============================================
def load_text_file(path: str) -> str:
    """读取用户上传的 txt/md 文件"""
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext not in [".txt", ".md"]:
        raise ValueError(f"不支持的文件格式: {ext}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ==============================================
# 3. 文本分片（Chunking）
# ==============================================
def split_text(text: str, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


# ==============================================
# 4. Embedding（向量化）
# ==============================================
def embed_text_list(text_list):
    return embedder.encode(text_list).tolist()


# ==============================================
# 5. 写入向量库
# ==============================================
def store_document(user_id: int, kb_id: int, doc_id: int, text: str):
    print("\n===== [1] 文本分片 =====")
    chunks = split_text(text)
    print(f"共生成 {len(chunks)} 个 chunk")

    print("\n===== [2] 向量化 =====")
    embeddings = embed_text_list(chunks)
    print(f"已生成 {len(embeddings)} 个向量")

    collection_name = f"kb_{kb_id}"
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    print("\n===== [3] 写入向量数据库 =====")
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        id_val = f"{doc_id}_{idx}"
        collection.add(
            ids=[id_val],
            embeddings=[emb],
            documents=[chunk],
            metadatas=[{
                "user_id": user_id,
                "kb_id": kb_id,
                "doc_id": doc_id,
                "chunk_idx": idx
            }],
        )
        print(f"写入 chunk {idx}")

    print("\n✔ 文档已成功写入知识库\n")


# ==============================================
# 6. 查询知识库 Top-K
# ==============================================
def query_kb(user_id: int, kb_id: int, query: str, top_k=3):
    print("\n===== 开始查询知识库 =====")

    query_embedding = embedder.encode([query]).tolist()[0]

    collection_name = f"kb_{kb_id}"
    collection = chroma_client.get_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"user_id": user_id},  # 用户隔离
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    ids = results["ids"][0]
    distances = results["distances"][0]

    print(f"\n查询：{query}")
    print("Top K 结果：")
    for i in range(len(documents)):
        print(f"\n[{i}] doc_id={metadatas[i]['doc_id']}  chunk={metadatas[i]['chunk_idx']}  score={distances[i]:.4f}")
        print(documents[i][:200], "...")

    return documents, metadatas, distances


# ==============================================
# 7. 测试入口
# ==============================================
def test():
    user_id = 1
    kb_id = 101
    doc_id = 1

    # 测试文件（你可以换成自己路径）
    file_path = "test_info.txt"

    print("\n===== 加载文件 =====")
    text = load_text_file(file_path)

    print("\n===== 写入文档 =====")
    store_document(user_id, kb_id, doc_id, text)

    print("\n===== 测试查询 =====")
    query_kb(user_id, kb_id, "我要睡觉", top_k=3)


# ==============================================
# 程序入口
# ==============================================
if __name__ == "__main__":
    test()
