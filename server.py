import socket
import threading
import os
import random
import string
import hashlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def calculate_checksum(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def random_lowercase_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(5))

def send_file(filename,name, client,addr):
    with open(filename, 'rb') as f:
        file_content = f.read()
    
    total_size = len(file_content)
    total_packets = (total_size // (BUFFER_SIZE - 50))
    total_packets = total_packets if total_packets > 0 else 1    
    randomId = random_lowercase_string()
        
    for i in range(total_packets):
        start = i * (BUFFER_SIZE -50)
        end = start + (BUFFER_SIZE - 50)
        packet = f"{randomId}|{total_packets}|{name}|{addr[0]}|{addr[1]}|{file_content[start:end].decode('utf-8')}".encode("utf-8")
        sock.sendto(packet, client)

def send_message(message, name, client, addr):
    filename = f'message-{name}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(message)
    send_file(filename, name, client, addr)
    os.remove(filename)

def handle_client(data, addr):
    try:
        if addr not in clients:
            clients.add(addr)

        try:
            message_type, *content = data.decode('utf-8').split('|')

        except UnicodeDecodeError as e:
            print(f"Erro de decodificação de dados: {e}")
            return
        
        if message_type == 'LOGIN':
            username = content[0]
            login_message = f"LOGIN|🔥 {username} entrou no chat."
            print(f'😮 Usuário {addr} com o username {username} entrou no chat.')
            for client in clients:
                if client != addr:
                    sock.sendto(login_message.encode('utf-8'), client)

        elif message_type in messages:
            total_packets, name, packetData, checksum = content
            packet = [message_type, total_packets, name, packetData]
            packet = '|'.join(packet)
            if checksum == calculate_checksum(packet):
                print(f"Checksum válido para o pacote {packetData}")
            messages[message_type] = { "name": name, "packets": [*messages[message_type]["packets"], packetData] }

            if (len(messages[message_type]["packets"]) == int(total_packets)):
                file_content = bytearray()
                for i in range(int(total_packets)):
                    file_content.extend(messages[message_type]["packets"][i].encode("utf-8"))
                message_text = file_content.decode('utf-8')
                for client in clients:
                    if client != addr:
                        send_message(message_text, name, client, addr)
        else: 
            total_packets, name, packetData, checksum = content
            packet = [message_type, total_packets, name, packetData]
            packet = '|'.join(packet)
            if checksum == calculate_checksum(packet):
                print(f"Checksum válido para o pacote {packetData}")
            messages[message_type] = {"name": name, "packets": [packetData] }

            if (total_packets == '1'):
                file_content = bytearray()
                for i in range(int(total_packets)):
                    file_content.extend(messages[message_type]['packets'][i].encode("utf-8"))
                message_text = file_content.decode('utf-8')

                for client in clients:
                    if client != addr:
                        send_message(message_text, name, client, addr)

    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}")

def server():
    print("Servidor iniciado! 📦")
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            threading.Thread(target=handle_client, args=(data, addr)).start()
        except Exception as e:
            print(f"Erro no servidor: {e}")

clients = set()
messages = {}

server_thread = threading.Thread(target=server)
server_thread.daemon = True  # Define a thread como daemon para encerrar junto com o programa principal
server_thread.start()

# Manter o servidor rodando
server_thread.join()