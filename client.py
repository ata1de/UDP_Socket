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
    with open(filename, 'rb') as f:
        file_content = f.read()
    
    total_size = len(file_content)
    total_packets = (total_size // BUFFER_SIZE) + 1
    header = f"FILE|{filename}|{total_packets}|{name}".encode('utf-8')
    
    client_socket.sendto(header, (UDP_IP, UDP_PORT))
    
    for i in range(total_packets):
        start = i * BUFFER_SIZE
        end = start + BUFFER_SIZE
        packet = file_content[start:end]
        client_socket.sendto(packet, (UDP_IP, UDP_PORT))

def send_message(message):
    filename = f'message-{name}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(message)
    send_file(filename)
    os.remove(filename)

def send_login_message():
    login_message = f"LOGIN|{name}".encode('utf-8')
    client_socket.sendto(login_message, (UDP_IP, UDP_PORT))

def receive_messages():
    while True:
        try:
            data, client_addr = client_socket.recvfrom(BUFFER_SIZE)
            try:
                message_type, *content = data.decode('utf-8').split('|')
            except UnicodeDecodeError as e:
                print(f"Erro ao receber o message type {e}")
                continue
            if message_type == 'FILE':
                filename, total_packets, username = content
                total_packets = int(total_packets)
                file_content = bytearray()

                for _ in range(total_packets):
                    packet, _ = client_socket.recvfrom(BUFFER_SIZE)
                    file_content.extend(packet) 

                try:
                    message_text = file_content.decode('utf-8')
                    date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                    final_message = f"{client_addr[0]}:{client_addr[1]}/~{username}: {message_text} {date_now}"
                    print(final_message)

                except UnicodeDecodeError as e:
                    print(f"Erro ao receber a mensagem: {e}")
                return
            
            elif message_type == 'MSG':
                print(content[0])

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Faz com que a thread encerre junto com o programa principal
receive_thread.start()

print("Cliente iniciado. Primeiramente, qual o seu nome?")
name = input()
send_login_message()
print(f"Olá, {name}! Vamos começar o chat! Digite sua mensagem abaixo:")

while True:
    message = input()
    send_message(message)
