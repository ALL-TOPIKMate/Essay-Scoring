import os
import openai

def gpt_response(question, quest_content, user_answer):
    openai.api_key = os.environ.get('OPENAI_API_KEY') #호출할 때는 메모장에서 가져오기
    user_content = "질문: " + question +"\n" + '제시문: ' + quest_content + "\n\n" + '사용자 답: ' + user_answer
    message_info = [{
        "role": "system",
        "content": "질문과 제시문이 주어지면 사용자 답안이 이에 따라 주제, 문제점, 결론이 개요에 맞게 잘 구성되었는지 채점하여 잘한 점과 부족한 점에 대해 정리해주는 한국어 교사. 글자 수에 대한 지적은 하지 않는다. 점수는 50점 만점으로 진행한다."
        }]
    message_info.append({"role":"user","content":user_content})
    message_info.append({
        "role": "assistant",
        "content": "지시사항:\n점수: 00점\n잘한점:\n부족한점:"
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
