import os
from dashscope.api_entities.dashscope_response import Message
from prompt import user_prompt
import dashscope
import re
import json
from dotenv import load_dotenv
load_dotenv('.env')
# 输出所有环境变量
# print("Environment variables:", os.environ)
class ModelProvider:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.model_name=os.getenv('MODEL_NAME')
        print('model_name:',self.model_name)
        self._client=dashscope.Generation()
        self.max_retry_times=3
        
    def chat(self,prompt,chat_history):
        cur_retry_time=0
        while cur_retry_time<self.max_retry_times:
            cur_retry_time+=1
            try:
                messages=[Message(role='system',content=prompt)]
                for his in chat_history:
                    messages.append(Message(role='user',content=his[0]))
                    messages.append(Message(role='assistant',content=his[1]))
                messages.append(Message(role='user',content=user_prompt))   
                response = self._client.call(
                    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                    api_key=self.api_key,
                    model=self.model_name, # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                    messages=messages,
                    )
                
                response=re.search(r'(\{.*\})',response['output']['text'],re.DOTALL).group(0)
                
                content=json.loads(response)
                print('content:',content)
                return content
            except Exception as e:
                print(f'chat调用失败，{e}')
                return 
# mp=ModelProvider()
# mp.chat('你是一个大模型智能体，你的职责是为用户提出解决方案',[])