from qdrant_client import QdrantClient
from typing import List
import numpy as np
from fastembed import TextEmbedding
#切分文档内容
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class rag_system():
    def __init__(self):
        client = QdrantClient(host="localhost", port=6333)
        embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",cache_dir="./embedding_model")

    def split_document(self,content:str,chunk_size:int,chunk_overlap:int)->List[str]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_text(content)   


    def add_document(self,input_data):
        import os
        """
        处理输入的数据，可以是字符串或文件路径。
        
        参数:
            input_data (str): 输入的字符串或文件路径。
            
        返回:
            str: 处理后的字符串内容。
        """
        content = ""
        
        # 判断输入是否为有效的文件路径
        if os.path.exists(input_data):
            # 获取文件扩展名
            _, ext = os.path.splitext(input_data)
            ext = ext.lower()
            
            if ext in ['.txt', '.md']:
                # 读取文本或Markdown文件
                with open(input_data, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
            elif ext == '.epub':
                # 读取EPUB文件
                try:
                    from ebooklib import epub
                    from bs4 import BeautifulSoup
                except ImportError:
                    raise ImportError("请先安装 ebooklib 和 beautifulsoup4 库：pip install ebooklib beautifulsoup4")
                
                book = epub.read_epub(input_data)
                texts = []
                for item in book.get_items():
                    if item.get_type() == epub.ITEM_DOCUMENT:
                        soup = BeautifulSoup(item.get_content(), 'html.parser')
                        texts.append(soup.get_text())
                content = '\n'.join(texts)
                
            else:
                raise ValueError(f"不支持的文件格式: {ext}")
                
        else:
            # 输入被视为字符串
            content = input_data
        
        # 分割为行，去除首尾空行和每行的首尾空格
        lines = content.splitlines()
        
        # 去除首位的空行
        while lines and lines[0].strip() == '':
            lines.pop(0)
        while lines and lines[-1].strip() == '':
            lines.pop()
            
        # 去除每行的首尾空格
        cleaned_lines = [line.strip() for line in lines]
        
        # 重新组合成字符串
        cleaned_content = '\n'.join(cleaned_lines)
        
        return cleaned_content
    
    if collection:

    def add_document(self,file_path:str,chunk_size:int,chunk_overlap:int):
        content=self.process_input(file_path)
        chunks = self.split_document(content, chunk_size, chunk_overlap)
        self.client.add(
            collection_name="test_collection",
            documents=docs,
            metadata=metadata,
            ids=ids
        )