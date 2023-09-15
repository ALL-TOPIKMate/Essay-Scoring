from PyKomoran import *
import re

komoran = Komoran('STABLE')
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