import random
import string
from datetime import datetime, timedelta

def random_string(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def random_date():
    days_ago = random.randint(1, 30)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    
    date = datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)
    return date.strftime("%Y-%m-%dT%H:%M:%S.000000Z")

# Test
print("String 1:", random_string())
print("String 2:", random_string())
print("String 3:", random_string(16))
print("Date 1:", random_date())
print("Date 2:", random_date())