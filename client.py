import datetime
import socket
import threading
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(10)  # Define um timeout para evitar bloqueios

def send_file(filename):
    filesize = os.path.getsize(filename)
    client_socket.sendto(f'FILE|{filename}|{filesize}'.encode('utf-8'), (UDP_IP, UDP_PORT))
    
    with open(filename, 'rb') as f:
        while (chunk := f.read(BUFFER_SIZE)):
            client_socket.sendto(chunk, (UDP_IP, UDP_PORT))

def send_message(message):
    client_socket.sendto(f'MESSAGE|{message}|{UDP_IP}|{UDP_PORT}|{name}'.encode('utf-8'), (UDP_IP, UDP_PORT))

def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message_type, content, UDP_IP_RCV, UDP_PORT_RCV, username = data.decode('utf-8').split('|')
            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if message_type == 'MESSAGE':
                print(f"{UDP_IP_RCV}:{UDP_PORT_RCV}/~{username}: {content} {date_now}")
                # Salvando a mensagem em um arquivo de texto
                with open('received_message.txt', 'a') as f:
                    f.write(content + '\n')
            else:
                # Lida com outros tipos de mensagens, se necessário
                pass
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Faz com que a thread encerre junto com o programa principal
receive_thread.start()

print("Cliente iniciado. Primeiramente, qual o seu nome?")
name = input()
print(f"Olá, {name}! Vamos começar o chat! Envie sua mensagem.")

while True:
    message = input()
    if os.path.isfile(message):
        send_file(message)
    else:
        send_message(message)
        # Salvando a mensagem em um arquivo de texto
        with open('mensagem.txt', 'w') as f:
            f.write(message)
