"""
@author:zhaoyuhang
@time:2024/11/14 16:00
@file:tools.py
"""
import os
from langchain_community.tools import TavilySearchResults
"""
1.写文件
2.读文件
3.追加
4.网络搜索

"""

def _get_workdir_root():
    workdir_root=os.environ.get('WORKDIR_ROOT','/data/llm_result')
    return workdir_root

workdir_root=get_workdir_root()
def read_file(filename):
    filename=os.path.join(_get_workdir_root(),filename)
    if not os.path.exists(filename):
        return f"{filename} not exists,please check file exist before read"
    with open(filename, "r", encoding="utf-8") as f:
        return  '\n'.join(f.readlines())

def append_to_file(filrnaem,content):
    filename=os.path.join(workdir_root,filename)
    if not os.path.exists(filename):
        return f"{filename} not exists,please check file exist before read"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(content)
    return f"append content to {filename} success"

def write_to_file(filename,content):
    filename=os.path.join(workdir_root,filename)
    if not os.path.exists(workdir_root):
        os.mkdir(workdir_root)
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"write content to {filename} success"





def search(query, api_key="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", max_results=5, include_answer=True, include_raw_content=True, include_images=True):
    # 设置环境变量
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
        return '\n'.join(content_list)
    except Exception as e:
        return f"search error: {e}"

tools_info=[
    {
        "name":"read_file",
        "description":"read file from agent generate,should write file before read",
        "args":[
            {
                "name":"filename",
                "type":"string",
                "decritpion":"read file name"
            }
        ]
    }
    ,
    {
        "name":"write_to_file",
        "description":"write content to file",
        "args":[
            {
                "name":"filename",
                "type":"string",
                "decritpion":"write file name"
            },
            {
                "name":"content",
                "type":"string",
                "decritpion":"write content"
            }
        ]
    },
    {
        "name":"append_to_file",
        "description":"append content to file",
        "args":[
            {
                "name":"filename",
                "type":"string",
                "decritpion":"append llm content to file,should write file before read"
            },
            {
                "name":"content",
                "type":"string",
                "decritpion":"append content"
            }
        ]
    },
    {
        "name":"search",
        "description":"this is a search engine,you can gain additional knowledge by searching when you are confused",
        "args":[
            {
                "name":"query",
                "type":"string",
                "decritpion":"search query to look up"
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
        args_desc=json.loads(json.dumps(args_desc),ensure_ascii=False)
        tool_desc=f"{idx+1}.{t['name']}:{t['description']},args:{args_desc}"
        tools_desc.append(tool_desc)  

    tools_prompt='\n'.join(tools_desc)  
    return tools_prompt
