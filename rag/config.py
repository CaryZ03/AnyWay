import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()


class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir / "rag.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = basedir / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}
    
    # RAG配置
    VECTOR_STORE_PATH = basedir / 'vector_store'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200










