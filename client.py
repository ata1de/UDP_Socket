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
    client_socket.sendto(f'FILE|{filename}|{filesize}|{UDP_IP}|{UDP_PORT}|{name}'.encode('utf-8'), (UDP_IP, UDP_PORT))
    

def send_message(message):
    filename = f'message-{name}.txt'
    with open(filename, 'w') as f:
        f.write(message)
    send_file(filename)

def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message_type, receive_file, UDP_IP_RCV, UDP_PORT_RCV, username, filesize = data.decode('utf-8').split('|')
            filesize = int(filesize)
            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            
            if message_type == 'FILE':
                content = b''  # Armazena conteúdo como bytes
                
                # Salvando a mensagem em um arquivo de texto
                with open(receive_file, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        packet, _ = client_socket.recvfrom(BUFFER_SIZE)
                        f.write(packet)
                        bytes_received += len(packet)
                        content += packet  # Adiciona o pacote ao conteúdo

                content_str = content.decode('utf-8')
                print(f"{UDP_IP_RCV}:{UDP_PORT_RCV}/~{username}: {content_str} {date_now}")
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
    send_message(message)
