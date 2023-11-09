from sklearn.feature_extraction.text import TfidfVectorizer
from PyKomoran import * #형태소 분석기 변경
import scipy as sp
from flask import Flask, request, jsonify, render_template
import requests
import json
import re
from gpt_response import gpt_response
from lsa_Similar import lsa_Similar
from flask_cors import CORS
app = Flask(__name__) #상태 알아보기2
cors = CORS(app, resources={r"*": {"origins": "https://port-0-docker-essay-score-jvvy2blm7ipnj3.sel5.cloudtype.app"}})
komoran = Komoran('STABLE')

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('./index.html')

#문장 유사도
vectorizer = TfidfVectorizer(min_df = 1, decode_error = 'ignore', analyzer='word', sublinear_tf=True)

def sentence_token(contents):
  contents_tokens = list()
  for i in range(len(contents)): 
    test = (komoran.get_plain_text(contents[i])).split(' ')
    for j in range(len(test)):
      temp = test[j].split('/')
      test[j] = temp[0]
    contents_tokens.append(test)


  contents_for_vectorize = []
  for content in contents_tokens:
    sentence = ''
    for word in content:
      sentence = sentence + ' ' + word
    contents_for_vectorize.append(sentence)
    
  #tf-idf 벡터화
  try:
    X = vectorizer.fit_transform(contents_for_vectorize)
    return X
  except ValueError as e:
    if str(e) == "empty vocabulary; perhaps the documents only contain stop words":
      print('빈 사전')
    return None

def new_token(new_post):
  new_post_vecs = []  # 결과 벡터를 저장할 리스트

  for post in new_post:
    # 문장을 토큰화하고 형태소만 추출
    tokens = (komoran.get_plain_text(post)).split(' ')
    new_post_tokens = [token.split('/')[0] for token in tokens]

    # 토큰들을 다시 문장으로 변환
    sentence = ' '.join(new_post_tokens)

    # 문장을 TF-IDF 벡터로 변환
    new_post_vec = vectorizer.transform([sentence])

    new_post_vecs.append(new_post_vec)

  return new_post_vecs


def dist_raw(v1,v2):
  delta = v1 - v2
  return sp.linalg.norm(delta.toarray())

def check_distance(X, new_post_vec, contents):
    best_dist = 65535
    best_i = None
    result = []
    for i, post_vec in enumerate(new_post_vec):
        d = dist_raw(X, post_vec)
        if d < best_dist:
            best_dist = d
            best_i = i
            result = [contents[0]] 
        elif d == best_dist:
            result.append(contents[0])

    return best_i, best_dist, result

def similarity(contents, new_post):
    
  if not contents or not new_post:
      return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
  #여기 불용어 들어올 때 에러
  if sentence_token(contents) is not None:
    X = sentence_token(contents)
    new_post_vec = new_token(new_post)
    best_i, best_dist, result = check_distance(X, new_post_vec, contents)

    response = {
        'best_i': best_i,
        'best_dist': best_dist,
        'result': result
    }
  else:
      response = {'에러': '답안에 불용어가 있습니다.'}
  
  
  return response

#맞춤법 검사
def pusan_univ_spell(text):
    
  if not text:
      return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
  text = text[0]
  text = text.replace('\n', '\r\n')
  # 2. 맞춤법 검사 요청 (requests)
  response = requests.post('http://164.125.7.61/speller/results', data={"text1": text})
  try:
      # 3. 응답에서 필요한 내용 추출 (html 파싱)
      data = response.text.split('data = [', 1)[-1].rsplit('];', 1)[0]

      # 4. 파이썬 딕셔너리 형식으로 변환
      data = json.loads(data)
      response = {}
      cnt = 1
      response_s = {}
      for err in data['errInfo']:
          #print(f"입력 내용 : {err['orgStr']}")
          #print(f"대치어 : {err['candWord']}")
          #print(f"도움말 : {err['help']}") #여기 apos; 나오고 <br/>이런거 나오는데 혹시 수정해야되면 메시지 작성 바람.
          #print("\n")
          response_add = {
              '입력 내용' : err['orgStr'],
              '대치어' : err['candWord'],
              '도움말' : err['help'],
          }
          response_s[cnt] = response_add
          cnt+=1
      response['에러 내용'] = response_s
      response['점수'] = cnt -1
      return response
  except json.JSONDecodeError:
    response = {'메시지': '에러가 발생하지 않았습니다. 문장이 완전합니다.'}
    return response
  except:
      response = {'메시지': '맞춤법 검사기 자체의 에러입니다.'}
      return response
    
    
#글자수 검사
def countCheck(quest_num, answer):
    if not quest_num or not answer:
        return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
    if quest_num == 53:
       max_length = 300
       min_length = 200
    else:
       max_length = 700
       min_length = 600
    answer = answer[0]
    
    if len(answer) > int(max_length):
        #print('글자 수가 초과되었습니다.')
        result = str(len(answer))+ '자. 글자 수가 초과되었습니다.'
        if quest_num == 53:
            score = 1
        else:
           score = 2.5
    elif len(answer) < int(min_length):
        #print('글자 수가 부족합니다.')
        result =  str(len(answer))+ '자. 글자 수가 부족합니다.'
        score = 0
    else:
        #print('글자 수가 적당합니다')
        result = str(len(answer))+ '자. 글자 수가 적당합니다'
        if quest_num == 53:
            score = 2
        else:
           score = 5
    response = {'글자 수 검사' : result, '점수' : score}
    print('확인', score)
    return response

#53번 표현 가점, 감점
def Express(sentence):
  #문장 끝 표현 체크, 감점
  check = (komoran.get_plain_text(sentence[0][:]).split(' '))
  for i in range(len(check)):
     temp = check[i].split('/')
     check[i] = temp
  cnt = 0
  for i in range(len(check)): #-ㅂ/ 습니다, -아/-어요 
    if check[i][0].endswith('습니다') or check[i][0].endswith('ㅂ니다') or check[i][0].endswith('요') or check[i][0].endswith('아요') or check[i][0].endswith('어요') :
      cnt+=1

  #대조 표현 사용, 가점
  pattern = re.compile(r'지만|는데 반해|와 달리|과 달리')
  matches = re.findall(pattern, sentence[0])
  result = '문장 끝 표현 ' + str(cnt) + '회, 대조표현 사용 ' + str(len(matches)) + '회 사용함.'
  result_cnt = -1 * cnt + len(matches)
  if result_cnt < 0:
     result_cnt = 0
  response = {"표현 검사" : result , "점수" : result_cnt}
  return response

#51번, 52번 
def ExpressShort(sentence, answer):
  cnt_Result = []
  #print(sentence[:], answer[:])
  for i in range(len(answer)):
    cnt = 0
    sen = (komoran.get_plain_text(sentence[0]).split(' '))
    sen2 = (komoran.get_plain_text(answer[0]).split(' '))

    for i in range(len(sen)):
      temp = sen[i].split('/')
      sen[i] = temp
    for i in range(len(sen2)):
      temp = sen2[i].split('/')
      sen2[i] = temp
    if sen[-1][1] == sen2[-1][1] and sen[-1][0] == sen2[-1][0]: #모든 값이 같은 경우
      #print('동일', sen[-1][1], sen2[-1][1])
      cnt=1
    elif sen[-1][1] == sen2[-1][1]: #문법 종류는 맞으나 완전히 답안이 같지 않은 경우
        cnt = 0.5
    else:
      #print('비동일', sen[-1][1], sen2[-1][1])
      cnt = 0
    cnt_Result.append(cnt)

  
  result = '문장 끝 표현 ' + str(max(cnt_Result)) + '회 사용'
  
  response = {"표현 검사" : result , "점수" : cnt}
  return response
  
#점수 계산 함수
def calculate_score53(sim, sp, le, ex):
    #53번 기준 30점
    #유사도 22점, 맞춤법 5점, 글자 수 2점, 표현 점수 1점
    if sim > 1:
       sim = 1
    sp_score = 5 - (0.2 * sp)
    if sp_score < 0:
       sp_score = 0
    if ex >= 3:
       ex_score = 1
    elif ex> 0:
       ex_score = 0.5
    else:
       ex_score = 0
    result = round(22*(1-sim),2) + sp_score + le + ex_score
    return result
def calculate_score(num, sim, sp, ex):
    if sim > 1:
       sim = 1
    #51번
    if num == 51:
      #print('51번 채점중')
      if sp!= 0:
        result = round(3 - sim*3,2) + round(1/sp,2) + ex * 1
      else:
         result = round(3 - sim*3,2) + 1.00 + ex * 1
      
    #52번
    elif num == 52:
       #print('52번 채점')
      if sp!= 0:
         result = round(3 - sim*3,2) + round(1.5/sp,2)+ 0.5 * ex
      else:
         result = round(3 - sim*3,2) + 1.5+ 0.5 * ex
      

    return result
   
@app.route('/main' , methods=['POST'])
def get_score():
  data = request.json
  quest_num = data.get('number', )
  question = data.get('question', [])
  contents = data.get('contents', [])
  if quest_num <= 53:
    answer = data.get('answer', [])
    if contents[0]  == ''  and quest_num < 53:
       response = {'result_score': 0, 's_message': '빈 문자열이라 유사도 검사가 되지 않았습니다.', 'sp_message': '빈 문자열이라 맞춤법 검사가 되지 않았습니다.', 'ex_message': '빈 문자열이라 표현 검사가 되지 않았습니다.'}
       return jsonify(response)
    elif contents[0] == '' and quest_num == 53: #만약 값이 비어있으면
       response = {'result_score': 0, 's_message': '빈 문자열이라 유사도 검사가 되지 않았습니다.', 'sp_message': '빈 문자열이라 맞춤법 검사가 되지 않았습니다.', 'len_message': '빈 문자열이라 글자 수 검사가 되지 않았습니다.', 'ex_message': '빈 문자열이라 표현 검사가 되지 않았습니다.'}
       return jsonify(response)
    else:
      #사용자 답안 content
      spell = pusan_univ_spell(contents)

      if quest_num == 53:
        #문제와 사용자 답안 question
        similar = lsa_Similar(contents, answer)
        length = countCheck(quest_num, contents)
        #사용자 답안 content
        expressto = Express(contents)
        len_score = length['점수']#글자수
        len_message = length['글자 수 검사']
      elif quest_num <= 52:
        similar = similarity(contents, answer)
        expressto = ExpressShort(contents, answer)
      #similar_data = similar.json()
      if '에러' in similar:
         s_score = 1
         s_message = '불용어로 인해 유사도 채점이 되지 않습니다.'
      else:
        s_score = similar['best_dist'] #유사성
        if s_score > 0.5:
          s_message = '유사성이 매우 낮습니다.'
        else:
          s_message = '유사성은 높습니다. 나머지 메시지 확인하세요.'
      #spell_data = spell.json()
      if '메시지' in spell:
        sp_score = 0
        sp_message = spell['메시지']
      else:
        sp_score = spell['점수'] #스펠링
        sp_message = spell['에러 내용']
      if quest_num <= 53:
        #ex_data = expressto.json()
        ex_score = expressto['점수'] #표현점수
        ex_message = expressto['표현 검사']
      #print(s_score, sp_score, ex_score)
      if quest_num == 53:
        result_score = calculate_score53(s_score, sp_score, len_score, ex_score)  
        response = {'result_score': round(result_score,1), 's_message': s_message, 'sp_message': sp_message, 'len_message': len_message, 'ex_message': ex_message}
        return jsonify(response)
      elif quest_num <= 52: #51번과 52번 일 때의 계산
        response={'result': '51번과 52번'}
        result_score = calculate_score(quest_num, s_score, sp_score, ex_score)  
        response = {'result_score': round(result_score,1), 's_message': s_message, 'sp_message': sp_message,'ex_message': ex_message}
        return jsonify(response)
        #result_score(calculate_score(quest_num))
      else:
        response = {'result': 'error'}
        return jsonify(response)
  else:
      response={'result': '54번은 chatgpt'}
      quest_con = data.get('quest_con', [])
      answer = data.get('answer', [])
      if len(contents[0]) == 0:
         response = {'score': 0, 'Length':  '빈 문자열이라 글자 수 검사가 되지 않았습니다.'}
      else:
        #print(question, quest_con, contents)
        length = countCheck(quest_num, contents)
        gpt_result = gpt_response(question[0], quest_con[0], contents[0], answer[0], length['글자 수 검사'])
        gpt_result['score'] += length['점수']
        response = gpt_result
  return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
