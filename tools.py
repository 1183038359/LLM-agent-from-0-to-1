"""
@author:zhaoyuhang
@time:2024/11/14 16:00
@file:tools.py
"""
import os
import json
from langchain_community.tools import TavilySearchResults
"""
1.写文件
2.读文件
3.追加
4.网络搜索

"""

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





def search(query, api_key="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", max_results=5, include_answer=True, include_raw_content=True, include_images=True):
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
    }

]

tools_map={
    "read_file":read_file,
    "write_to_file":write_to_file,
    "append_to_file":append_to_file,
    "search":search
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
