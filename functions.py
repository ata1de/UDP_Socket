import re
import random
import string
import hashlib

def getUserName(intro):
    padrao = r"hi, meu nome eh (.+)"
    correspondencia = re.match(padrao, intro)
    
    if correspondencia:
        return correspondencia.group(1)
    else:
        return None
    

def calculate_checksum(data):
  return hashlib.md5(data.encode('utf-8')).hexdigest()

def random_lowercase_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(5))