# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 10:28:34 2020

@author: gabe
"""
from keras.models import load_model
import numpy as np
import requests
from bs4 import BeautifulSoup as bs
import re
from PIL import Image
import time
import matplotlib.pyplot as plt
import cv2
from skimage import transform,data
import csv

dic19 = {'2':0, '3':1, '4':2, '5':3, '7':4, '9':5, 'A':6, 'C':7, 'F':8, 'H':9, 'K':10, 'M':11, 'N':12, 'P':13, 'Q':14, 'R':15, 'T':16, 'Y':17, 'Z':18}

def to_onelist(text):
    label_list = []
    for c in text:
        onehot = [0 for _ in range(19)]
        onehot[ dic19[c] ] = 1
        label_list.append(onehot)
    return label_list

def to_text(l_list):
    text=[]
    pos = []
    for i in range(4):
        for j in range(19):
            if(l_list[i][j]):
                pos.append(j)

    for i in range(4):
        char_idx = pos[i]
        text.append(list(dic19.keys())[list(dic19.values()).index(char_idx)])
        return "".join(text)

def to_text2(int):
    text = []
    text.append(list(dic19.keys())[list(dic19.values()).index(int)])
    return "".join(text)


def test_accu(correct_cnt, total_cnt, CaptchaList):
    
    #URL = 'https://irs.thsrc.com.tw/IMINT'

    for i in range(0, 1000):
        URL = 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1:BookingS1Form::IFormSubmitListener'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
        
        session_requests = requests.session()
        response = session_requests.get('https://irs.thsrc.com.tw/IMINT/', headers = headers)
        soup = bs(response.text, "html.parser")
        for img in soup.select('img'):
                match = re.search(r'.*src="/IMINT/(.*?)"',str(img))
                if match:
                    imgUrl = 'https://irs.thsrc.com.tw/IMINT/' + match.group(1)
                    html = requests.get(imgUrl, headers=headers)
                    with open('0.jpg','wb') as f:
                        f.write(html.content)
        try:
            image = Image.open('0.jpg')
        except:
            continue
        image = image.resize((140, 48),Image.ANTIALIAS)
        image.save('0.jpg')
        x_train = np.stack([np.array(Image.open('0.jpg'))/255.0])
        prediction = model.predict(x_train)
        Captcha = ''
        for predict in prediction:
            Captcha += to_text2(np.argmax(predict))

        payload = {'BookingS1Form:hf:0:': '', 
                'selectStartStation': 11, 
                'selectDestinationStation': 4, 
                'trainCon:trainRadioGroup': 0, 
                'seatCon:seatRadioGroup': 'radio17', 
                'bookingMethod': 0, 
                'toTimeInputField': '2020/08/26', 
                'toTimeTable': '230P', 
                'toTrainIDInputField': '',
                'backTimeInputField': '2020/08/26',
                'backTimeTable': '',
                'backTrainIDInputField': '', 
                'ticketPanel:rows:0:ticketAmount':' 1F',
                'ticketPanel:rows:1:ticketAmount': '0H',
                'ticketPanel:rows:2:ticketAmount': '0W',
                'ticketPanel:rows:3:ticketAmount': '0E',
                'ticketPanel:rows:4:ticketAmount': '0P',
                'homeCaptcha:securityCode': Captcha,
                'portalTag': 'false',
                'SubmitButton': '開始查詢'}
        headers = {
            'Referer': 'https://irs.thsrc.com.tw/IMINT/?locale=tw',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
        URL = 'https://irs.thsrc.com.tw/IMINT/;jsessionid=' + dict(response.cookies)['JSESSIONID'] + '?wicket:interface=:0:BookingS1Form::IFormSubmitListener'
        response  = session_requests.post(URL, data = payload, headers=headers)
        if(response.text.find('檢測碼輸入錯誤') == -1):
            #image.save('./img_download/' + str(correct_cnt) + '.jpg')
            #CaptchaList.append([Captcha])
            correct_cnt += 1
        total_cnt += 1

        time.sleep(0.1)
    print(total_cnt, correct_cnt)

print('model loading...')
model = load_model('./model/cnn_model.hdf5')
print('loading end')

correct_cnt = 0
CaptchaList = []
test_accu(correct_cnt, 0, CaptchaList)

'''
try:
    test_accu(correct_cnt, 0, CaptchaList)
finally:
    with open('download_label.csv','w',newline='') as f:
        writeCsv = csv.writer(f)
        writeCsv.writerows(CaptchaList)
'''