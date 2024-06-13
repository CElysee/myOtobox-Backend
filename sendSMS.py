import requests
import os



def sendSMS(phone_number, message):
    url = 'https://api.mista.io/sms'

    payload = {'to': phone_number,
    'from': os.getenv("SENDER_ID"),
    'unicode': '0',
    'sms': message,
    'action': 'send-sms'}

    files = [

    ]

    headers = {
    'x-api-key': '386|hY4eAWqZdbXnMOccURnsvdkPF6myOZENEU7GPhOY '
    }

    response = requests.request('POST', url, headers=headers, data = payload, files = files)

    return response.text.encode('utf8')