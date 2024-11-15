import time
from tools import tools_map
from prompt import gen_prompt
def parse_thought(response):
    """
    response:
    {
        "action"{
            "name":"action_name",
            "args":{
                "args_name":"args_value"
            }
        },
        "thoughts":
        {
            "text":"thought",
            "plan":"plan",
            "criticism":"criticism",
            "speak":"当前步骤返回给用户的总结",
            "reasoning":"reasoning"
        }
    }
    """
    try:
        thoughts=response.get('thoughts')
        observation=thoughts.get('speak')
        plan=thoughts.get('plan')
        reasoning=thoughts.get('reasoning')
        criticism=thoughts.get('criticism')
        prompt=f"plan:{plan}\nreasoning:{reasoning}\ncriticism:{criticism}\nobervation:{observation}"
        return prompt
    except Exception as e:
        print('解析thoughts失败',e)
        return e



def agent_exec(query,max_call_times=10):
    cur_request_time=0
    chat_history=[]
    agent_scracth=""
    while cur_request_time<max_call_times:
        cur_request_time+=1
        """
        如果返回结果达到预期则直接返回
        """
        """
        pormpt包含以下功能：
            1.任务被描述
            2.工具描述
            3.用户输入的user_msg
            4.assistant_msg
            5.限制
            6.给出更好实践的描述
        """
        
        prompt=gen_prompt(query,agent_scracth)
        start_time=time.time()
        print(f'........{start_time}。开始调用大模型')
        #call_llm
        """
        syss_prompt:
        user_msg,assistant_msg,history
        """
        response=call_llm(prompt)
        end_time=time.time()
        print(f'........{end_time}.调用大模型结束。耗时{end_time-start_time}')
        
        if not response or not isinstance(response,dict):
            print('调用大模型失败,即将重试。。。',reponse)
            continue
        

        action_info=response.get('action')
        action_name=action_info.get('name')
        action_args=action_info.get('args')
        print('当前action name:',action_name,'当前action args:',action_args)
        if action_name=='finish':
            final_answer=action_args.get('answer')
            print('最终回答：',final_answer)
            break
        
        obersevation=response.get('thoughts').get('speak')
        try:
            """"action_name到函数的映射：map->{action_name:func}"""
            
            func=tools_map.get(action_name)
            observation=func(**action_args)
        except Exception as e:
            print('调用工具函数失败',e)
        
        agent_scracth=agent_scracth+'\n'+observation
        user_msg="决定使用哪个工具"
        assistant_message=parse_thought(reponse)
        chat_history.append(user_msg,assistant_message)
def main():
    max_call_times=10
    while True:
        query=input("请输入prompt：")
        if query=="exit":
            break
        answer=agent_exec(query,max_call_times)
        