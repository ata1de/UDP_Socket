import re
import random
import string
import hashlib

def getUserName(intro):
    # Função para extrair o nome do usuário a partir de uma string de introdução
    padrao = r"hi, meu nome eh (.+)"  # Define o padrão regex para capturar o nome
    correspondencia = re.match(padrao, intro)  # Tenta fazer a correspondência da string com o padrão
    
    if correspondencia:
        return correspondencia.group(1)  # Retorna o nome do usuário se encontrado
    else:
        return None  # Retorna None se o padrão não corresponder
    

def calculate_checksum(data):
    # Função para calcular o checksum (hash) MD5 de uma string
    return hashlib.md5(data.encode('utf-8')).hexdigest()  # Retorna o hash MD5 da string codificada em UTF-8

def random_lowercase_string():
    # Função para gerar uma string aleatória de 5 letras minúsculas
    letters = string.ascii_lowercase  # Define o conjunto de letras minúsculas
    return ''.join(random.choice(letters) for _ in range(5))  # Gera e retorna a string aleatória
