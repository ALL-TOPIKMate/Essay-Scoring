from sklearn.feature_extraction.text import TfidfVectorizer
from PyKomoran import *
from flask import jsonify
import scipy as sp
komoran = Komoran('STABLE')
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