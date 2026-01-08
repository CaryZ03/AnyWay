import os
import hashlib
import threading

from flask import Blueprint, request, jsonify, current_app
from app import db
from .models import KnowledgeBase, Document

from core.knowledge import (
    load_text_file,
    split_text,
    store_document,
    query_kb,
    chroma_client,
)
from chromadb.errors import NotFoundError as ChromaNotFoundError

bp = Blueprint("kb", __name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===============================================================
# 异步向量化任务
# ===============================================================
def _process_document_vector(app, doc_id: int, user_id: int):
    """后台线程：向量化文档"""
    with app.app_context():
        doc = Document.query.get(doc_id)
        if not doc:
            print(f"[向量化失败] 文档 {doc_id} 不存在")
            return

        doc.status = "processing"
        db.session.commit()

        try:
            text = load_text_file(doc.file_path)

            chunks = split_text(text)
            doc.chunk_count = len(chunks)
            db.session.commit()

            store_document(
                user_id=user_id,
                kb_id=doc.knowledge_base_id,
                doc_id=doc.id,
                text=text,
            )

            doc.status = "completed"

        except Exception as e:
            print("[向量化失败]:", e)
            doc.status = "failed"

        db.session.commit()


# ===============================================================
# 1. 创建知识库（参数在 body）
# ===============================================================
@bp.route("/kb/create", methods=["POST"])
def create_knowledge_base():
    data = request.json or {}
    user_id = data.get("user_id")
    name = data.get("name")
    description = data.get("description", "")

    if not user_id or not name:
        return jsonify({"code": 1, "msg": "user_id 和 name 必填"}), 400

    kb = KnowledgeBase(user_id=int(user_id), name=name, description=description)
    db.session.add(kb)
    db.session.commit()

    return jsonify({"code": 0, "data": kb.to_dict()})


# ===============================================================
# 2. 查询用户所有知识库
# ===============================================================
@bp.route("/kb/list", methods=["GET"])
def list_kb():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"code": 1, "msg": "user_id 必填"}), 400

    kbs = KnowledgeBase.query.filter_by(user_id=int(user_id)).all()
    return jsonify({"code": 0, "data": [kb.to_dict() for kb in kbs]})


# ===============================================================
# 3. 查询某知识库下文档（kb_id 改为参数）
# ===============================================================
@bp.route("/kb/documents", methods=["GET"])
def list_documents():
    user_id = request.args.get("user_id")
    kb_id = request.args.get("knowledge_base_id")

    if not user_id or not kb_id:
        return jsonify({"code": 1, "msg": "user_id 和 knowledge_base_id 必填"}), 400

    kb = KnowledgeBase.query.get(int(kb_id))
    if not kb:
        return jsonify({"code": 1, "msg": "知识库不存在"}), 404

    if kb.user_id != int(user_id):
        return jsonify({"code": 1, "msg": "无权访问该知识库"}), 403

    docs = Document.query.filter_by(knowledge_base_id=int(kb_id)).all()
    return jsonify({"code": 0, "data": [d.to_dict() for d in docs]})


# ===============================================================
# 4. 上传文档（kb_id 改为参数）
# ===============================================================
@bp.route("/kb/upload", methods=["POST"])
def upload_document():
    user_id = request.form.get("user_id")
    kb_id = request.form.get("knowledge_base_id")

    if not user_id or not kb_id:
        return jsonify({"code": 1, "msg": "user_id 和 knowledge_base_id 必填"}), 400

    kb = KnowledgeBase.query.get(int(kb_id))
    if not kb:
        return jsonify({"code": 1, "msg": "知识库不存在"}), 404
    if kb.user_id != int(user_id):
        return jsonify({"code": 1, "msg": "无权访问该知识库"}), 403

    file = request.files.get("file")
    if not file:
        return jsonify({"code": 1, "msg": "必须上传文件"}), 400

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["txt", "md"]:
        return jsonify({"code": 1, "msg": "只支持 txt / md 文件"}), 400

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(save_path)

    sha256 = hashlib.sha256(open(save_path, "rb").read()).hexdigest()

    doc = Document(
        knowledge_base_id=int(kb_id),
        filename=file.filename,
        file_path=save_path,
        file_size=os.path.getsize(save_path),
        file_type=ext,
        sha256=sha256,
        status="pending",
    )

    db.session.add(doc)
    db.session.commit()

    app_obj = current_app._get_current_object()

    threading.Thread(
        target=_process_document_vector,
        args=(app_obj, doc.id, int(user_id))
    ).start()

    return jsonify({"code": 0, "msg": "上传成功，后台处理中", "document": doc.to_dict()})


# ===============================================================
# 5. 删除单个文档（doc_id 仍在 URL，因为这是资源主体）
# ===============================================================
@bp.route("/kb/document/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id: int):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"code": 1, "msg": "user_id 必填"}), 400

    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({"code": 1, "msg": "文档不存在"}), 404

    kb = KnowledgeBase.query.get(doc.knowledge_base_id)
    if kb.user_id != int(user_id):
        return jsonify({"code": 1, "msg": "无权删除此文档"}), 403

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    try:
        col = chroma_client.get_collection(f"kb_{doc.knowledge_base_id}")
        col.delete(where={"doc_id": doc.id})
    except ChromaNotFoundError:
        pass

    db.session.delete(doc)
    db.session.commit()

    return jsonify({"code": 0, "msg": "文档已删除"})


# ===============================================================
# 6. 删除知识库（kb_id 改为参数）
# ===============================================================
@bp.route("/kb/delete", methods=["DELETE"])
def delete_kb():
    user_id = request.args.get("user_id")
    kb_id = request.args.get("knowledge_base_id")

    if not user_id or not kb_id:
        return jsonify({"code": 1, "msg": "user_id 和 knowledge_base_id 必填"}), 400

    kb = KnowledgeBase.query.get(int(kb_id))
    if not kb:
        return jsonify({"code": 1, "msg": "知识库不存在"}), 404
    if kb.user_id != int(user_id):
        return jsonify({"code": 1, "msg": "无权删除此知识库"}), 403

    # 删除文档文件
    for doc in kb.documents:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

    # 删除向量库
    try:
        chroma_client.delete_collection(name=f"kb_{kb_id}")
    except ChromaNotFoundError:
        pass

    db.session.delete(kb)
    db.session.commit()

    return jsonify({"code": 0, "msg": "知识库已删除"})


# ===============================================================
# 7. 查询向量库（无 Query 模型）
# ===============================================================
@bp.route("/kb/query", methods=["POST"])
def query_knowledge_base():
    data = request.json or {}
    user_id = data.get("user_id")
    kb_id = data.get("knowledge_base_id")
    query_text = data.get("query")
    top_k = data.get("top_k", 3)

    if not all([user_id, kb_id, query_text]):
        return jsonify({"code": 1, "msg": "user_id, knowledge_base_id, query 必填"}), 400

    kb = KnowledgeBase.query.get(int(kb_id))
    if not kb:
        return jsonify({"code": 1, "msg": "知识库不存在"}), 404
    if kb.user_id != int(user_id):
        return jsonify({"code": 1, "msg": "无权访问此知识库"}), 403

    try:
        docs, metas, scores = query_kb(
            user_id=int(user_id),
            kb_id=int(kb_id),
            query=query_text,
            top_k=int(top_k)
        )
    except ChromaNotFoundError:
        return jsonify({"code": 1, "msg": "知识库暂无向量数据"}), 400

    return jsonify({
        "code": 0,
        "data": {
            "documents": docs,
            "metadatas": metas,
            "scores": scores,
        }
    })
