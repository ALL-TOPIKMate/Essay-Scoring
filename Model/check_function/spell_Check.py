from flask import jsonify
import requests
import json
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