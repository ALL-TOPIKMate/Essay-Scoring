from PyKomoran import * #형태소 분석기 변경
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

#기능 파일 import
from check_function.gpt_response import gpt_response
from check_function.similarity_Check import similarity
from check_function.spell_Check import pusan_univ_spell
from check_function.count_Check import countCheck
from check_function.express_Check import Express, ExpressShort

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "https://port-0-docker-essay-score-jvvy2blm7ipnj3.sel5.cloudtype.app"}})
komoran = Komoran('STABLE')

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('./index.html')    
  
#점수 계산 함수
def calculate_score53(sim, sp, le, ex):
    #53번 기준 30점
    result = 25 - sim*5 + 5 - sp*0.5 + le + 3-(ex * 0.5)
    if result >=30:
      result = 30
    return result
def calculate_score(num, sim, sp, ex):
    #51번
    if num == 51:
      #print('51번 채점중')
      result = 3 - sim*5 + 1 - (0.4*sp) + ex * 2
    #52번
    elif num == 52:
       #print('52번 채점')
       result = 3 - sim*5 + 1.5 - (0.4*sp) + ex * 1.5
    else:
       pass
    if result <0:
      result = 0
    elif result > 5:
      result = 5
    else:
       pass
    return result
   
@app.route('/main' , methods=['POST'])
def get_score():
  data = request.json
  quest_num = data.get('number', )
  question = data.get('question', [])
  contents = data.get('contents', [])
  if quest_num <= 53:
    answer = data.get('answer', [])
    #사용자 답안과 , 실제 답안 content, answer
    similar = similarity(contents, answer)
    #사용자 답안 content
    spell = pusan_univ_spell(contents)

    if quest_num == 53:
      #문제와 사용자 답안 question
      length = countCheck(question, contents)
      #사용자 답안 content
      expressto = Express(contents)
      len_score = length['점수']#글자수
      len_message = length['글자 수 검사']
    elif quest_num <= 52:
      expressto = ExpressShort(quest_num, contents, answer)
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
