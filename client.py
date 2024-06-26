import datetime
import socket
import threading
import os
import random
import string

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(10)  # Define um timeout para evitar bloqueios

def random_lowercase_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(5))

def send_file(filename):
    with open(filename, 'rb') as f:
        file_content = f.read()

    total_size = len(file_content)

    total_packets = (total_size // (BUFFER_SIZE - 50))
    total_packets = total_packets if total_packets > 0 else 1

    # print("total de pacotes " + str(total_packets))
    randomId = random_lowercase_string()
    for i in range(total_packets):
        start = i * (BUFFER_SIZE - 50)
        end = start + (BUFFER_SIZE - 50)
        packet = f"{randomId}|{total_packets}|{name}|{file_content[start:end].decode('utf-8')}".encode("utf-8")

        # print()
        # print("pacote " + str(i))
        # print(packet.decode('utf-8'))
        # print(file_content[start:end])
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
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message_type, *content = data.decode('utf-8').split('|')

            if (message_type == "LOGIN"):
                print(*content)

            elif (message_type in messages):
                total_packets, name, addrIp, addrPort, packet = content
                messages[message_type] = { "name": name, "packets": [*messages[message_type]["packets"], packet] }
                if (int(total_packets) == len(messages[message_type]["packets"])):
                    date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                    gatheredPackets = ""
                    for i in range(int(total_packets)):
                        gatheredPackets +=  messages[message_type]["packets"][i]
                    final_message = f"{addrIp}:{addrPort}/~{name}: {gatheredPackets} {date_now}"
                    print(final_message)   
                    print()                 
            else: 
                total_packets, name, addrIp, addrPort, packet =  content
                messages[message_type] = {"name": name, "packets": [packet] }
                if (total_packets == '1'):
                    date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                    final_message = f"{addrIp}:{addrPort}/~{name}: {packet} {date_now}"
                    print(final_message)
                    print()

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

messages = {}

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Faz com que a thread encerre junto com o programa principal
receive_thread.start()

print("🤠 Cliente iniciado. Primeiramente, qual o seu nome?")
name = input()
send_login_message()
print(f"Olá, {name} 😃! Vamos começar o chat! Digite sua mensagem abaixo ⬇️:")

while True:
    message = input()
    send_message(message)
