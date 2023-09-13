from sklearn.feature_extraction.text import TfidfVectorizer
from PyKomoran import * #형태소 분석기 변경
import scipy as sp
from flask import Flask, request, jsonify, render_template
import requests
import json
import re
from gpt_response import gpt_response
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "https://port-0-docker-essay-score-jvvy2blm7ipnj3.sel5.cloudtype.app"}})
komoran = Komoran('STABLE')

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('./index.html')

#문장 유사도
vectorizer = TfidfVectorizer(min_df = 1, decode_error = 'ignore')

def sentence_token(contents):
  contents_tokens = list()
  for i in range(len(contents)): 
    result = []
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
  X = vectorizer.fit_transform(contents_for_vectorize)
  return X

def new_token(new_post):
  test = (komoran.get_plain_text(new_post[0])).split(' ')
  new_post_tokens = []
  for j in range(len(test)):
      temp = test[j].split('/')
      new_post_tokens.append(temp[0])

  new_post_for_vectorize = []
  sentence = ' '.join(new_post_tokens)
  new_post_for_vectorize.append(sentence)

  new_post_vec = vectorizer.transform(new_post_for_vectorize)
  return new_post_vec

def dist_raw(v1,v2):
  delta = v1 - v2
  return sp.linalg.norm(delta.toarray())

def check_distance(X, new_post_vec, contents):
  best_dist = 65535
  best_i = None
  result = []
  for i in range(len(contents)):
    post_vec = X.getrow(i)
    d = dist_raw(post_vec, new_post_vec)
    #print(d)
    #print('== Post %i with dist = %.2f : %s' %(i,d, contents[i]))
    if d < best_dist:
      best_dist = d
      best_i = i
      result = []
    if d == best_dist:
      result.append(contents[i])
  return best_i, best_dist, result

def similarity(contents, new_post):
    
  if not contents or not new_post:
      return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400

  X = sentence_token(contents)
  new_post_vec = new_token(new_post)
  best_i, best_dist, result = check_distance(X, new_post_vec, contents)

  response = {
      'best_i': best_i,
      'best_dist': best_dist,
      'result': result
  }
  
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
              '입력 내용:' : err['orgStr'],
              '대치어:' : err['candWord'],
              '도움말: ' : err['help'],
          }
          response_s[cnt] = response_add
          cnt+=1
      response['에러 내용'] = response_s
      response['점수'] = cnt
      return response
  except json.JSONDecodeError:
    response = {'메시지': '에러가 발생하지 않았습니다. 문장이 완전합니다.'}
    return response
  except:
      response = {'메시지': '맞춤법 검사기 자체의 에러입니다.'}
      return response
    
    
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
        score = 0
    elif len(answer) < int(min_length):
        #print('글자 수가 부족합니다.')
        result =  str(len(answer))+ '자. 글자 수가 부족합니다.'
        score -=1
    else:
        #print('글자 수가 적당합니다')
        result = str(len(answer))+ '자. 글자 수가 적당합니다'
        score += 1
    response = {'글자 수 검사' : result, '점수' : score}
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
  result_cnt = cnt*0.5 + len(matches)
  response = {"표현 검사" : result , "점수" : result_cnt}
  return response

#51번, 52번 
def ExpressShort(q_num, sentence, answer):
  cnt = 0
  #print(sentence[:], answer[:])
  if q_num == 51:
    sen = (komoran.get_plain_text(sentence[0]).split(' '))
    sen2 = (komoran.get_plain_text(answer[0]).split(' '))
    for i in range(len(sen)):
     temp = sen[i].split('/')
     sen[i] = temp
    for i in range(len(sen2)):
     temp = sen2[i].split('/')
     sen2[i] = temp
    if sen[-1][1] == sen2[-1][1]:
      #print('동일', sen[-1][1], sen2[-1][1])
      cnt+=1
    else:
      #print('비동일', sen[-1][1], sen2[-1][1])
      pass

  elif q_num == 52:
     check = (komoran.get_plain_text(sentence[0][:]).split(' '))
     for i in range(len(check)):
        temp = check[i].split('/')
        check[i] = temp
     for i in range(len(check)): #-ㅂ/ 습니다, -아/-어요 
      if check[i][0].endswith('ㄴ다') or check[i][0].endswith('다') or check[i][0].endswith('는다') :
        cnt+=1
  result = '문장 끝 표현 ' + str(cnt) + '회 사용'
  result_cnt = cnt*0.5 
  response = {"표현 검사" : result , "점수" : result_cnt}
  return response
  
#점수 계산 함수
def calculate_score53(sim, sp, le, ex):
    #53번 기준 30점
    result = 25 - sim*5 + 3 - sp*0.5 + 2 * le + ex * 0.5
    if result >=30:
      result = 30
    return result
def calculate_score(num, sim, sp, ex):
    #51번
    if num == 51:
      #print('51번 채점중')
      result = 7 - sim*5 + sp + ex * 2
    #52번
    elif num == 52:
       #print('52번 채점')
       result = 7 - sim*5 + sp*1.5 + ex * 1.5
    return result
   
   
   

@app.route('/main' , methods=['GET', 'POST'])
def get_score():
  data = request.json
  quest_num = data.get('number', )
  question = data.get('question', [])
  contents = data.get('contents', [])
  if quest_num <= 53:
    new_post = data.get('new_post', [])
    #사용자 답안과 , 실제 답안 content, new_post
    similar = similarity(contents, new_post)
    #사용자 답안 content
    spell = pusan_univ_spell(contents)

    if quest_num == 53:
      #문제와 사용자 답안 question
      length = countCheck(question, contents)
      #사용자 답안 content
      expressto = Express(contents)
      length_data = length.json()
      len_score = length_data.get('점수', []) #글자수
      len_message = length_data.get('글자 수 검사', [])
    elif quest_num <= 52:
      expressto = ExpressShort(quest_num, contents, new_post)
    #similar_data = similar.json()
    s_score = similar['best_dist'] #유사성
    if s_score > 1:
      s_message = '유사성이 매우 낮습니다.'
    else:
      s_message = '유사성은 높습니다. 나머지 메시지 확인하세요.'
    #spell_data = spell.json()
    if spell['메시지']:
      sp_score = 0
      sp_message = spell['메시지']
    else:
      sp_score = spell['점수'] #스펠링
      sp_message = spell['에러 내용']
    if quest_num <= 53:
      #ex_data = expressto.json()
      print(expressto)
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
      #print(question, quest_con, contents)
      gpt_result = gpt_response(question[0], quest_con[0], contents[0])
      response = {'채점결과': gpt_result}
      return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
