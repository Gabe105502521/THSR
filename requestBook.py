# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 10:28:07 2020

@author: Jing
"""
import requests
from bs4 import BeautifulSoup as bs
import re
from PIL import Image
import numpy as np
import tensorflow as tf

#URL = 'https://irs.thsrc.com.tw/IMINT'
#from keras.models import load_model

#model = load_model('./model/cnn_model.hdf5')

dic19 = {'2':0, '3':1, '4':2, '5':3, '7':4, '9':5, 'A':6, 'C':7, 'F':8, 'H':9, 'K':10, 'M':11, 'N':12, 'P':13, 'Q':14, 'R':15, 'T':16, 'Y':17, 'Z':18}

#to avoid "Tensor is not an element of this graph; deploying Keras model" this error
#beacuse the tensorflow model is not loaded and used in the same thread. One workaround is to force tensorflow to use the gloabl default graph 
global graph
graph = tf.get_default_graph() 

def to_text2(int):
    text = []
    text.append(list(dic19.keys())[list(dic19.values()).index(int)])
    return "".join(text)


def book(model, selectStartStation=4, selectStartStation_2=11, day='2020/08/27', time='500A', fall='1F', student='0P', ID='S124852299', cellphone='0966099087', num=0):    
    URL = 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1:BookingS1Form::IFormSubmitListener'
    
    #網站依照header看是不是爬蟲，需要偽裝成瀏覽器
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    
    #website use it to recognize user(cookie)
    session_requests = requests.session()
    response = session_requests.get('https://irs.thsrc.com.tw/IMINT/', headers = headers)
    soup = bs(response.text, "html.parser")

    #download image and predict
    for img in soup.select('img'):
            match = re.search(r'.*src="/IMINT/(.*?)"',str(img))
            if match:
                imgUrl = 'https://irs.thsrc.com.tw/IMINT/' + match.group(1)
                html = requests.get(imgUrl, headers=headers)
                with open(str(num) + '.jpg','wb') as f:
                    f.write(html.content)
    image = Image.open(str(num) + '.jpg')
    image = image.resize((140, 48),Image.ANTIALIAS)
    image.save(str(num) + '.jpg')
    x_train = np.stack([np.array(Image.open(str(num) + '.jpg'))/255.0])
    
    Captcha = ''
    with graph.as_default():
       prediction = model.predict(x_train)       
       for predict in prediction:
           Captcha += to_text2(np.argmax(predict))

    data = {'BookingS1Form:hf:0:': '', 
            'selectStartStation': selectStartStation, 
            'selectDestinationStation': selectStartStation_2, 
            'trainCon:trainRadioGroup': 0, 
            'seatCon:seatRadioGroup': 'radio17', 
            'bookingMethod': 0, 
            'toTimeInputField': day, 
            'toTimeTable': time, 
            'toTrainIDInputField': '',
            'backTimeInputField': day,
            'backTimeTable': '',
            'backTrainIDInputField': '', 
            'ticketPanel:rows:0:ticketAmount': fall,
            'ticketPanel:rows:1:ticketAmount': '0H',
            'ticketPanel:rows:2:ticketAmount': '0W',
            'ticketPanel:rows:3:ticketAmount': '0E',
            'ticketPanel:rows:4:ticketAmount': student,
            'homeCaptcha:securityCode': Captcha,
            'portalTag': 'false',
            'SubmitButton': '開始查詢'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'referer': 'https://irs.thsrc.com.tw/IMINT/?locale=tw'}
    #header需要特別加refer(表從哪裡連)?
    #print(dict(response.cookies)['JSESSIONID'])
    #第一個post
    #URL = 'https://irs.thsrc.com.tw/IMINT/;jsessionid=' + dict(response.cookies)['JSESSIONID'] + '?wicket:interface=:0:BookingS1Form::IFormSubmitListener'
    URL = 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:0:BookingS1Form::IFormSubmitListener'
    response  = session_requests.post(URL, data = data, headers=headers)
    if(response.text.find('檢測碼輸入錯誤') != -1):
        print('oops') #預測錯誤
        return
    data = {'BookingS2Form:hf:0:': '',
            'TrainQueryDataViewPanel:TrainGroup': 'radio18',
            'SubmitButton': '確認車次'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'referer': 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1::'}
    ##第二個post
    URL = 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1:BookingS2Form::IFormSubmitListener'
    response  = session_requests.post(URL, data = data, headers=headers)
    ##last post    
    URL = 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:2:BookingS3Form::IFormSubmitListener'
    data = {
        'BookingS3FormSP:hf:0': '', 
        'diffOver': 1,
        'idInputRadio': 'radio36',
        'idInputRadio:idNumber': ID,
        'eaiPhoneCon:phoneInputRadio': 'radio43',
        'eaiPhoneCon:phoneInputRadio:mobilePhone': cellphone,
        'email': '',
        'agree': 'on',
        'isGoBackM': '',
        'backHome': '',
        'TgoError': 1}
    
    response  = session_requests.post(URL, data = data, headers=headers)
'''
if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    book(model)
 '''