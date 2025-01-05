"""
@author:zhaoyuhang
@time:2024/11/14 16:00
@file:tools.py
"""
import os
import json
from langchain_community.tools import TavilySearchResults
from qdrant_client import QdrantClient
from dotenv import load_dotenv
"""
1.写文件
2.读文件
3.追加
4.网络搜索

"""

search_api=os.getenv("SEARCH_API")

def _get_workdir_root():
    workdir_root=os.environ.get('WORKDIR_ROOT','/data/llm_result')
    workdir_root=os.getcwd()+workdir_root
    return workdir_root

workdir_root=_get_workdir_root()

def read_file(filename):
    print(f'正在读取文件{filename}')
    filename=os.path.join(_get_workdir_root(),filename)
    if not os.path.exists(filename):
        return f"{filename} not exists,please check file exist before read"
    with open(filename, "r", encoding="utf-8") as f:
        print(f'读取文件{filename}成功')
        return  f"{filename}内容："+'\n'.join(f.readlines())

def append_to_file(filrnaem,content):
    print(f'正在追加文件{filename}')
    filename=os.path.join(workdir_root,filename)
    if not os.path.exists(filename):
        return f"{filename} not exists,please check file exist before read"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(content)
        print(f'追加文件{filename}成功')
    return f"append content to {filename} success"

def write_to_file(filename,content):
    print(f'正在写文件{filename}')
    filename=os.path.join(workdir_root,filename)
    if not os.path.exists(workdir_root):
        os.makedirs(workdir_root)
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        print(f'写文件{filename}成功')
    return f"write content to {filename} success"



def get_collection():
    collection_map={"law":"法律","china_history":"中国历史"}
    qdrant_client = QdrantClient(host="localhost", port=6333)
    collections=[]
    print("正在获取collection")
    print(qdrant_client.get_collections())
    for collection in qdrant_client.get_collections().collections:
        print("collection:",collection)
        print(collection.name)
        collections.append(collection.name)
    print("获取collection成功")
    collection_content=str([{"数据库":collection,"描述":collection_map.get(collection)} for collection in collections])
    print("collection_content:",collection_content)
    return collection_content
    

def rag_query(text,collection_name,DENSE_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",SPARSE_MODEL = "prithivida/Splade_PP_en_v1"):
    qdrant_client = QdrantClient(host="localhost", port=6333)
    qdrant_client.set_model(DENSE_MODEL,cache_dir="./embedding_model")
            # comment this line to use dense vectors only
    qdrant_client.set_sparse_model(SPARSE_MODEL,cache_dir="./sparse_model")
    try:
        search_result = qdrant_client.query(
            collection_name=collection_name,
            query_text=text,
            query_filter=None,  # If you don't want any filters for now
            limit=4,  # 5 the closest results
        )
        print("search_result:",search_result)
        # 去重处理
        seen_ids = set()
        unique_results = []
        
        for hit in search_result:
            if hit.id not in seen_ids:
                seen_ids.add(hit.id)
                unique_results.append(hit)
        
        # 按相似度排序并限制数量
        unique_results.sort(key=lambda x: x.score, reverse=True)
        unique_results = unique_results[:4]
        
        # 返回metadata
        metadata = [str(i)+str(hit.metadata) for i,hit in enumerate(unique_results)]
        metadata='\n'.join(metadata)
        return "本地数据库搜索得到相关内容如下\n"+metadata
    except :
        return f"不存在数据集合{collection_name}，请先创建数据集合"
    

def search(query, api_key=search_api, max_results=5, include_answer=True, include_raw_content=True, include_images=True):
    # 设置环境变量
    print(f'正在搜索{query}')
    os.environ["TAVILY_API_KEY"] = api_key
    
    # 初始化 TavilySearchResults 实例
    tavily = TavilySearchResults(
        max_results=max_results,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        include_images=include_images,
    )
    try:
        # 执行搜索
        result = tavily.invoke(query)
        content_list=[obj['content'] for obj in result]
        print(f'搜索{query}成功')
        print(f"查询{query}得到如下信息："+'\n'.join(content_list))
        return f"查询{query}得到如下信息："+'\n'.join(content_list)
    except Exception as e:
        return f"search error: {e}"

tools_info=[
    {
        "name": "read_file",
        "description": "从代理生成的文件中读取内容，应先写入文件再读取",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "decritpion": "读取的文件名"
            }
        ]
    },
    {
        "name": "write_to_file",
        "description": "将内容写入文件",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "decritpion": "写入的文件名"
            },
            {
                "name": "content",
                "type": "string",
                "decritpion": "写入的内容"
            }
        ]
    },
    {
        "name": "append_to_file",
        "description": "向文件追加内容",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "decritpion": "追加内容的文件名，应先写入文件再追加"
            },
            {
                "name": "content",
                "type": "string",
                "decritpion": "追加的内容"
            }
        ]
    },
    {
        "name": "search",
        "description": "这是一个搜索引擎，当遇到疑惑时，可以通过搜索获取额外知识",
        "args": [
            {
                "name": "query",
                "type": "string",
                "decritpion": "搜索查询内容"
            }
        ]
    },
    {
        "name": "finish",
        "description": "完成操作",
        "args": [
            {
                "name": "answer",
                "type": "string",
                "decritpion": "当任务完成时，请返回最终答案"
            }
        ]
    },
    {
        "name": "get_collection",
        "description": "获取本地数据库中的数据集合列表，集合可以作为参数传入rag_query函数查找本地数据库中的数据",
        "args": []
    },
    {
        "name": "rag_query",
        "description": "给定需要查询的文本，查询本地数据集合中存储内容中最相关的内容，调用rag_query函数前需要先调用get_collection获取本地数据集合",
        "args": [
            {
                "name": "text",
                "type": "string",
                "decritpion": "查询的文本"
            },
            {
                "name": "collection_name",
                "type": "string",
                "decritpion": "查询的数据集合"
            }
        ]
    }

]

tools_map={
    "read_file":read_file,
    "write_to_file":write_to_file,
    "append_to_file":append_to_file,
    "search":search,
    "get_collection":get_collection,
    "rag_query":rag_query
}

def gen_tools_desc():
    tools_desc=[]
    for idx ,t in enumerate(tools_info):
        args_desc=[]
        for info in t['args']:
            args_desc.append({
                "name":info['name'],
                "type":info['type'],
                "description":info['decritpion']
            })
        args_desc=json.loads(json.dumps(args_desc,ensure_ascii=False))
        tool_desc=f"{idx+1}.{t['name']}:{t['description']},args:{args_desc}"
        tools_desc.append(tool_desc)  

    tools_prompt='\n'.join(tools_desc)  
    return tools_prompt
