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

def load_from_json(json_data, validator=validate_default):
    numbers = []
    texts = []
    lines = json_data['analyzeResult']['readResults'][0]['lines']
    for line in lines:
        texts.append(line['text'])
        text = line['text'].replace(' ', '')
        if validator(text) and line['words'][0]['confidence'] > 0.9:
            numbers.append(text.rstrip('b'))

    numbers.sort()
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

def process_image(image_bytes, expected_count=60, collection_id=None):
    result_url = post_media(image_bytes)
    time.sleep(1)
    result_json = read_result(result_url)
    while result_json['status'] == 'running':
        time.sleep(1)
        result_json = read_result(result_url)
    
    validator = validate_default
    if (collection_id == "Panini - Football 2020"):
        validator = validate_football_2020 
    numbers = load_from_json(result_json, validator)
    print("expected count " + str(expected_count) + ", actual count " + str(len(numbers)))
    print(numbers)
    return numbers


