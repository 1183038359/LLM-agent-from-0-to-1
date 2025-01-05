from flask import Flask, render_template, request, jsonify
from cli_main import mp, parse_thought
import os
from prompt import gen_prompt,user_prompt
from tools import tools_map

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static'))

@app.route('/')
def index():
    print(f"Looking for template in: {app.template_folder}")  # 调试信息
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        # 调用agent_exec处理用户输入
        response = agent_exec(user_message)
        
        # 确保返回有意义的响应
        if response and isinstance(response, dict):
            thought = parse_thought(response)
            return jsonify({'response': thought})
        elif response:
            return jsonify({'response': response})
        else:
            return jsonify({'response': "处理失败，请重试"})
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': f"处理出错: {str(e)}"}), 500

def agent_exec(query, max_call_times=10):
    cur_request_time = 0
    chat_history = []
    agent_scracth = ""
    
    while cur_request_time < max_call_times:
        cur_request_time += 1
        print("当前第{}次请求".format(cur_request_time))
        prompt = gen_prompt(query, agent_scracth)
        response = mp.chat(prompt, chat_history)
        
        if not response or not isinstance(response, dict):
            continue
            
        action_info = response.get('action')
        if not action_info:
            continue
            
        action_name = action_info.get('name')
        action_args = action_info.get('args')
        
        if action_name == 'finish':
            # return response  # 返回完整响应供parse_thought处理
            return action_args.get('answer')
            
        try:
            func = tools_map.get(action_name)
            if func:
                # print("执行动作：", func)
                observation = func(**action_args)
                # print("动作结果：", observation)
                agent_scracth = agent_scracth + '\n' + f"执行动作{func}完成，动作结果为：\n" + observation
                
        except Exception as e:
            print(f'工具调用失败: {e}')
            continue
            
        user_msg = user_prompt
        assistant_message = parse_thought(response)
        chat_history.append([user_msg, assistant_message])
        
    return response  # 确保返回最后一次响应

if __name__ == '__main__':
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")    # 进入项目目录
    
    app.run(debug=True, port=5000)