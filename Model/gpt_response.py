import os
import openai
import json

def gpt_response(question, quest_content, user_answer, answer, length):
    updated_question = question.split('600~700자로 글을')[0].strip() + ' 글로 ' + question.split('600~700자로 글을')[1].strip()
    openai.api_key = os.getenv('OPENAI_API_KEY') #호출할 때는 메모장에서 가져오기
    user_content = "문제: " + updated_question +"\n" + '제시문: ' + quest_content + "\n\n" + '사용자 답안: ' + user_answer +"\n"+ '예시 답안' + answer
    message_info = [{
        "role": "system",
        "content": "사용자 답안이 제시문을 바탕으로 충족해 작성했는지 예시 답안과 비교해 채점해주는 한국어 교사. 잘한 점(Good Points), 부족한 점(Weak Points)을 피드백해준다. 45점이 최고점으로 사용자 답안이 제시문 조건에 맞추어 설명이 90%이상 작성되었으면 40~45점, 60%이상~90%미만은 30점~40점, 40%이상~60%미만은 20~30점, 20%이상~40%미만은 10~20점, 10%미만은 10점 아래로 부여한다. 글자 수 지적은 하지 않는다. 답변 형식은 JSON 형식으로 제공한다.  Score, Good Points, Weak Points로 구성된다."
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
    answer = json.loads(answer)
    answer['Length_Check'] = length
    return answer
