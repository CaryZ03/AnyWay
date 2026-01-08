from datetime import datetime
from app import db


class KnowledgeBase(db.Model):
    """知识库模型"""
    __tablename__ = 'knowledge_bases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 用户 ID
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ★ 文档带有级联删除 orphan delete
    documents = db.relationship(
        'Document',
        backref='knowledge_base',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'document_count': len(self.documents)
        }


class Document(db.Model):
    """文档模型"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_bases.id'), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))

    sha256 = db.Column(db.String(64))
    chunk_count = db.Column(db.Integer, default=0)

    status = db.Column(db.String(50), default='pending')  # pending / processing / completed / failed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'knowledge_base_id': self.knowledge_base_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'sha256': self.sha256,
            'chunk_count': self.chunk_count,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
