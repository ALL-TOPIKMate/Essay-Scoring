import os
import openai

def gpt_response2(user_answer):
    openai.api_key = os.getenv('OPENAI_API_KEY') #호출할 때는 메모장에서 가져오기
    user_content = user_answer
    message_info = [{
        "role": "system",
        "content": "문법적으로 구조가 맞지 않는 문장이 주어지는 경우에만 교정한다. 한글의 문장 구조는 주어-목적어-서술어 순이다. 수정이 필요하면 수정된 문장을 답으로 준다."
        }]
    message_info.append({"role":"user","content":user_content})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = message_info,
        temperature=1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response['choices'][0]['message']['content']
    return answer
