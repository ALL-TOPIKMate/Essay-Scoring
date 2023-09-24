import os
import openai

def gpt_response2(user_answer):
    openai.api_key = os.getenv('OPENAI_API_KEY') #호출할 때는 메모장에서 가져오기
    user_content = "문장이 주어지면 잘못된 것이 있으면 교정해줘. 잘못된 것이 없으면 '정답'이라고 말해. " + user_answer
    message_info = [{
        "role": "system",
        "content": ""
        }]
    message_info.append({"role":"user","content":user_content})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = message_info,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response['choices'][0]['message']['content']
    return answer
