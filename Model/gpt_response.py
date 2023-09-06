import os
import openai

def respond_result(question, quest_content, user_answer):
    #openai.api_key = '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' #openAI KEY
    user_content = "질문: " + question +"\n" + '제시문: ' + quest_content + "\n\n" + '사용자 답: ' + user_answer
    message_info = [{
        "role": "system",
        "content": "질문과 제시문이 주어지면 사용자 답안이 이에 따라 주제, 문제점, 결론이 개요에 맞게 잘 구성되었는지 채점하여 잘한 점과 부족한 점에 대해 정리해주는 한국어 교사. 점수는 50점 만점으로 진행한다."
        }]
    message_info.append({"role":"user","content":user_content})
    message_info.append({
        "role": "assistant",
        "content": "지시사항:\n점수: 00점\n잘한점:\n부족한점:"
        })
    return message_info
    '''
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    
    messages=message_info[
        
        {
        "role": "system",
        "content": "질문과 제시문이 주어지면 사용자 답안이 이에 따라 주제, 문제점, 결론이 개요에 맞게 잘 구성되었는지 채점하여 잘한 점과 부족한 점에 대해 정리해주는 한국어 교사. 점수는 50점 만점으로 진행한다."
        },
        {
        "role": "user",
        "content": "질문: 다음을 주제로 하여 자신의 생각을 600~700자로 글을 쓰시오. 단 문제를 그대로 옮겨 쓰지 마시오.\n제시문: 세계 어느 나라에서나 역사를 가르칩니다. 이는 지나간 일을 기록한 역사가 오늘날의 우리에게 주는 가치가 분명히 있기 때문일 것입니다. 여러분은 우리가 왜 역사를 알아야 하고, 그 역사를 통해서 무엇을 배울 수 있다고 생각하십니까? 이에 대해 쓰십시오.\n\n사용자 답:  독일 사람들에게서 역사를 대하는 방법을 배운다. 제2차 세계대전에서 독일 나치는 굉장히 많은 유대인들을 유대인이라는 이유 하나만으로 잔인하게 학살했다. 이 역사적 사건에 대해서 독일 사람들은 현재에도 피해자들에게 사과하고 그에 대한 책임을 지려는 자세를 취하고 있다. 이런 독일인의 모습을 보고 지나간 역사를 어떻게 바라봐야 하는지를 생각할 수 있다.\n   우리는 역사를 통해서 우리 선조들이 지나온 길을 볼 수 있다. 그 길이 부끄러운 길일 수도 있고 자랑스러운 길일 수도 있다. 하지만 그 모습 자체를 희화화하거나 왜곡해서는 안 된다고 생각한다. 역사에 대해서 객관적인 자세를 취하려는 태도는 굉장히 중요하다고 본다. 부끄러운 역사를 통해서는 다시는 그런 전철을 밟지 않도록 조치해야 하고, 자랑스러운 역사를 통해서는 길이길이 보전해서 현재에도 그런 모습을 가질 수 있도록 후손들이 노력해야 할 것이다.\n 몇 년 전에 한국에서는 국사 ‘국정교과서’에 대한 논의가 있었던 적이 있었다. 이 부분은 절대 있어서는 안 된다고 본다. 역사에 대한 다양한 시각이 반드시 필요한데, 하나의 교과서로 만들어진다는 것에 염려를 표한다. 역사에 대해서 다양한 시선으로 보는 과점이 현대를 살아가는 우리에게 굉장히 필요한 부분이라고 생각한다."
        },
        {
        "role": "assistant",
        "content": "지시사항:\n점수: 00점\n잘한점:\n부족한점:"
        }
        
        
    ],
    temperature=0.7,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    answer = response['choices'][0]['message']['content']
    return answer
'''