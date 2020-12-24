import json
import os
import requests
import time

OCR_KEY = '2d2e22ea11664d498e934e19cd90a64b'
ANALYZE_URL = 'https://stickers-recognition.cognitiveservices.azure.com/vision/v3.0/read/analyze'

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def validate_default(text):
    return has_numbers(text)

def validate_football_2020(text):
    return text.isnumeric() \
           and int(text) < 650

def validate_365_2021(text):
    return has_numbers(text) \
           and (text[-1].isdigit() or text[-1] == 'b') \
           and text != '365'

def load_from_json(json_data, collection_numbers):
    numbers = []
    texts = []
    lines = json_data['analyzeResult']['readResults'][0]['lines']
    for line in lines:
        texts.append(line['text'])
        for word in line['words']:
            text = word['text'].replace(' ', '').replace(',', '').rstrip('b')
            if (text in collection_numbers):
                numbers.append(text)

    #try a different strategy for stickers with multiple words on the same line
    if(len(numbers) == 0):
        for line in lines:
            text = line['text'].replace(' ', '')
            if (text in collection_numbers):
                numbers.append(text)

    #try a different strategy for collections split in multiple lines
    if(len(numbers) == 0): 
        for i in range(len(lines) - 1):
            text = lines[i]['text'] + lines[i+1]['text']
            if (text in collection_numbers):
                numbers.append(text)
                
    return numbers


def post_media(image_bytes):
    headers = {
        'Ocp-Apim-Subscription-Key': OCR_KEY
    }

    resp = requests.post(ANALYZE_URL, headers=headers,
                        files={'file': ("image.jpeg", image_bytes, 'image/jpeg')})
 

    resp.raise_for_status()
    return resp.headers['Operation-Location']


def read_result(location):
    headers = {
        'Ocp-Apim-Subscription-Key': OCR_KEY
    }

    resp = requests.get(location, headers=headers)
    resp.raise_for_status()
    return resp.json()

def process_image(image_bytes, collection_numbers,  expected_count=60):
    result_url = post_media(image_bytes)
    time.sleep(1)
    result_json = read_result(result_url)
    while result_json['status'] == 'running':
        time.sleep(1)
        result_json = read_result(result_url)
    
    numbers = load_from_json(result_json, collection_numbers)
    print("expected count " + str(expected_count) + ", actual count " + str(len(numbers)))
    print(numbers)
    return numbers


