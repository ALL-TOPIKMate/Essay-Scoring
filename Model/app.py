from sklearn.feature_extraction.text import TfidfVectorizer
import konlpy
from konlpy.tag import Okt
import scipy as sp
from flask import Flask, request, jsonify
import requests
import json
app = Flask(__name__)
t = Okt()

vectorizer = TfidfVectorizer(min_df = 1, decode_error = 'ignore')

def sentence_token(contents):
  contents_tokens = [t.morphs(row) for row in contents]

  contents_for_vectorize = []
  for content in contents_tokens:
    sentence = ''
    for word in content:
      sentence = sentence + ' ' + word
    contents_for_vectorize.append(sentence)

  #tf-idf 벡터화
  X = vectorizer.fit_transform(contents_for_vectorize)
  num_samples, num_features = X.shape
  print(num_samples, num_features)
  return X
def new_token(new_post):
  new_post_tokens = [t.morphs(row) for row in new_post]
  new_post_for_vectorize = []
  for content in new_post_tokens:
    sentence = ''
    for word in content:
      sentence = sentence + ' ' + word
    new_post_for_vectorize.append(sentence)
  new_post_vec = vectorizer.transform(new_post_for_vectorize)
  print(new_post_for_vectorize)
  return new_post_vec

def dist_raw(v1,v2):
  delta = v1 - v2
  return sp.linalg.norm(delta.toarray())

def check_distance(X, new_post_vec, contents):
  best_doc = None
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

@app.route('/api/similarity', methods=['POST'])
def similarity():
    data = request.json
    contents = data.get('contents', [])
    new_post = data.get('new_post', [])
    
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
    
    return jsonify(response)
@app.route('/api/spelling', methods=['POST'])
def pusan_univ_spell():
    data = request.json
    text = data.get('sen', [])
    
    if not text:
        return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
    text = text[0]
    text = text.replace('\n', '\r\n')
    # 2. 맞춤법 검사 요청 (requests)
    response = requests.post('http://164.125.7.61/speller/results', data={'text1': text})
    try:
        # 3. 응답에서 필요한 내용 추출 (html 파싱)
        data = response.text.split('data = [', 1)[-1].rsplit('];', 1)[0]

        # 4. 파이썬 딕셔너리 형식으로 변환
        data = json.loads(data)
        response = {}
        cnt = 1
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
            response[cnt] = response_add
            cnt+=1
        return jsonify(response)
    except:
        #print('오류가 발생하지 않았습니다. 문장이 완전합니다.')
        response = {'결과 ': '오류가 발생하지 않았습니다. 문장이 완전합니다.'}
        return jsonify(response)
@app.route('/api/countCheck', methods=['POST'])   
def countCheck():
    data = request.json
    question = data.get('question', [])
    answer = data.get('answer' , [])
    print(question, answer)
    if not question or not answer:
        return jsonify({'error': 'Invalid input. Missing "contents" or "new_post" parameter.'}), 400
    question = question[0]
    answer = answer[0]
    for i in range(len(question)):
        if question[i] == '자':
            max_length = question[i-3:i]
            min_length = question[i-7:i-4]
    #print(len(answer))
    if len(answer) > int(max_length):
        #print('글자 수가 초과되었습니다.')
        result = str(len(answer))+ '자. 글자 수가 초과되었습니다.'
    elif len(answer) < int(min_length):
        #print('글자 수가 부족합니다.')
        result =  str(len(answer))+ '자. 글자 수가 부족합니다.'
    else:
        #print('글자 수가 적당합니다')
        result = str(len(answer))+ '자. 글자 수가 적당합니다'
    response = {'글자 수 검사: ' : result}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
