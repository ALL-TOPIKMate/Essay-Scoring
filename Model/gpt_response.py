import os
import openai

def gpt_response(question, quest_content, user_answer, answer):
    updated_question = question.split('600~700자로 글을')[0].strip() + ' 글로 ' + question.split('600~700자로 글을')[1].strip()
    openai.api_key = os.getenv('OPENAI_API_KEY') #호출할 때는 메모장에서 가져오기
    user_content = "문제: " + updated_question +"\n" + '제시문: ' + quest_content + "\n\n" + '사용자 답안: ' + user_answer + '예시 답안' + answer
    message_info = [{
        "role": "system",
        "content": "문제와 제시문이 주어지면 사용자 답안을 예시 답안과 비교하여 잘한 점과 부족한 점에 대해 채점해주는 한국어 교사."
        }]
    message_info.append({"role":"user","content":user_content})
    message_info.append({
        "role": "assistant",
        "content": "잘한점:\n부족한점:"
        })
    
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
