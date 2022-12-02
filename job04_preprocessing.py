import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from konlpy.tag import Okt
from keras_preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import pickle

pd.set_option('display.unicode.east_asian_width', True)
df = pd.read_csv('./crawling_data_3/laftel_crawling_data_1_20221201.csv')
print(df.head(10))
print(df.category.value_counts())
df.info()

X = df['summary']
for i in range(len(X)):
    if len(X[i].split()) > 100:
        temp = X[i].split()[:100]
        X[i] = ' '.join(temp)


Y = df['category']

encoder = LabelEncoder()
labeled_Y = encoder.fit_transform(Y)
print(labeled_Y[:10])
print(encoder.classes_)
with open('./models/label_encoder.pickle', 'wb') as f:
    pickle.dump(encoder, f)
onehot_Y = to_categorical(labeled_Y)
print(onehot_Y[:10])

okt = Okt()

for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)
    if i % 1000 == 0:
        print('.', end='')
    if i % 10000 == 0:
        print()

stopwords = pd.read_csv('./stopwords.csv', index_col=0)
for j in range(len(X)): # 2글자 이상만 출력
    words = []
    for i in range(len(X[j])):
        if len(X[j][i]) > 1:
            if X[j][i] not in stopwords['stopword']: #불용어에 없으면 words에 추가
                words.append(X[j][i])
    X[j] = ' '.join(words) #불용어 사전에 없는 단어만 출력

token = Tokenizer()
token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X) # 순서대로 할때는 시퀀스를 사용한다
wordsize = len(token.word_index) + 1

with open('./models/laftel_token.pickle', 'wb') as f:
    pickle.dump(token, f)

# 제일 긴 문장의 길이에 맞춘다 -> 짧은문장 앞쪽 빈자리에 0을 붙여준다
max_len = 0
for i in range(len(tokened_X)):
    if max_len < len(tokened_X[i]):
        max_len = len(tokened_X[i])
print(max_len)

X_pad = pad_sequences(tokened_X, max_len) #패딩을 줘서 제일 긴문장의 길이로 맞춰준다

X_train, X_test, Y_train, Y_test = train_test_split(
    X_pad, onehot_Y, test_size=0.1)
print(X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)

xy = X_train, X_test, Y_train, Y_test
np.save('./models/laftel_titles_data_max_{}_wordsize_{}.npy'.format(max_len, wordsize), xy)
