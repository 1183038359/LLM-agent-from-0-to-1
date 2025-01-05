from qdrant_client import QdrantClient

from typing import List
import numpy as np
from fastembed import TextEmbedding
#切分文档内容
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter



class HybridSearcher:
    def __init__(self, collection_name,DENSE_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",SPARSE_MODEL = "prithivida/Splade_PP_en_v1"):
        self.collection_name = collection_name
        # initialize Qdrant client
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.qdrant_client.set_model(DENSE_MODEL,cache_dir="./embedding_model")
        # comment this line to use dense vectors only
        self.qdrant_client.set_sparse_model(SPARSE_MODEL,cache_dir="./sparse_model")
        if not self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=self.qdrant_client.get_fastembed_vector_params(),
                # comment this line to use dense vectors only
                sparse_vectors_config=self.qdrant_client.get_fastembed_sparse_vector_params(),  
            )
    
    def delete_collection(self, collection_name):
        if  self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.delete_collection(collection_name=collection_name)
            print(f"已删除数据集合: {collection_name}")
        else:
            print(f"集合不存在: {collection_name}")

    #函数定义
    def split_document(self,content: str, chunk_size: int = 400, chunk_overlap: int = 50):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_text(content)


    def search(self, text: str,collection="",limit=4):
        if collection:
                collection_choice=collection,
        else:
            collection_choice=self.collection_name
        search_result = self.qdrant_client.query(
            collection_name=collection_choice,
            query_text=text,
            query_filter=None,  # If you don't want any filters for now
            limit=limit*2,  # 5 the closest results
        )

        # 去重处理
        seen_ids = set()
        unique_results = []
        
        for hit in search_result:
            if hit.id not in seen_ids:
                seen_ids.add(hit.id)
                unique_results.append(hit)
        
        # 按相似度排序并限制数量
        unique_results.sort(key=lambda x: x.score, reverse=True)
        unique_results = unique_results[:limit]
        
        # 返回metadata
        metadata = [hit.metadata for hit in unique_results]
        return metadata
    
    def store_data(self, input_data: str,collection="",batch_size=500):
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
            print(f"读取文件: {input_data}")
            # 获取文件扩展名
            _, ext = os.path.splitext(input_data)
            ext = ext.lower()
            
            if ext in ['.txt', '.md']:
                # 读取文本或Markdown文件
                with open(input_data, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
            elif ext == '.epub':
                try:
                    from ebooklib import epub
                    from bs4 import BeautifulSoup
                except ImportError:
                    raise ImportError("请先安装 ebooklib 和 beautifulsoup4 库：pip install ebooklib beautifulsoup4")
                
                book = epub.read_epub(input_data)
                content_pieces = []
                for item in book.get_items():
                    if item.get_type() == 9:
                        soup = BeautifulSoup(item.get_body_content(), "html.parser")
                        text = soup.get_text(strip=True)
                        if text:
                            content_pieces.append(text)
                content= "\n".join(content_pieces)
                
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

        # 分批处理文档
        print("开始处理文档...")
        chunks = self.split_document(cleaned_content)
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            if collection:
                collection_name = collection
            else:
                collection_name = self.collection_name
            
            self.qdrant_client.add(
                collection_name=collection_name,
                documents=batch,
                parallel=0
            )
        