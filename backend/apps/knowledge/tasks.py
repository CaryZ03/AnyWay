"""
知识库异步任务
"""
from celery import shared_task
from django.core.files.storage import default_storage
from datetime import datetime
import logging

from .models import Document, DocumentChunk

logger = logging.getLogger(__name__)


@shared_task
def process_document(document_id):
    """
    处理文档：分块和向量化
    
    Args:
        document_id: 文档ID
    """
    try:
        document = Document.objects.get(id=document_id)
        logger.info(f'开始处理文档: {document.filename}')
        
        # 更新状态
        document.status = 'processing'
        document.save()
        
        # 读取文件内容
        with default_storage.open(document.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        document.content = content
        
        # 分块
        chunks = split_text(content)
        
        # 保存分块
        for i, chunk_text in enumerate(chunks):
            # TODO: 生成向量嵌入
            # embedding = generate_embedding(chunk_text)
            
            DocumentChunk.objects.create(
                document=document,
                content=chunk_text,
                chunk_index=i,
                # embedding=embedding,
                metadata={'length': len(chunk_text)}
            )
        
        # 更新文档状态
        document.status = 'completed'
        document.chunk_count = len(chunks)
        document.processed_at = datetime.now()
        document.save()
        
        logger.info(f'文档处理完成: {document.filename}, 分块数: {len(chunks)}')
        
    except Exception as e:
        logger.error(f'文档处理失败: {document_id}, 错误: {str(e)}')
        document.status = 'failed'
        document.error_message = str(e)
        document.save()


def split_text(text, chunk_size=500, overlap=50):
    """
    分割文本为块
    
    Args:
        text: 文本内容
        chunk_size: 块大小（字符数）
        overlap: 重叠大小
    
    Returns:
        文本块列表
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks
