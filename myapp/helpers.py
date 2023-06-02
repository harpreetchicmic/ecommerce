import requests
import random
from django.conf import settings


def send_otp_to_phone(phone_number,otp):
    try:
        
        url=f'https://2factor.in/API/V1/{settings.API_KEY}/SMS/{phone_number}/{otp}'
        reponse=requests.get(url)
        return otp
    except Exception as e:
        return None
