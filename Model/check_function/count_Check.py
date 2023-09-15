from flask import jsonify
#글자수 검사
def countCheck(question, answer):
    if not question or not answer:
        return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
    question = question[0]
    answer = answer[0]
    for i in range(len(question)):
        if question[i] == '자':
            max_length = question[i-3:i]
            min_length = question[i-7:i-4]
    score = 0
    if len(answer) > int(max_length):
        #print('글자 수가 초과되었습니다.')
        result = str(len(answer))+ '자. 글자 수가 초과되었습니다.'
        score = 1
    elif len(answer) < int(min_length):
        #print('글자 수가 부족합니다.')
        result =  str(len(answer))+ '자. 글자 수가 부족합니다.'
        score = 0
    else:
        #print('글자 수가 적당합니다')
        result = str(len(answer))+ '자. 글자 수가 적당합니다'
        score = 2
    response = {'글자 수 검사' : result, '점수' : score}
    return response