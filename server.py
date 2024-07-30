import os
import socket
import threading

from functions import *

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024
ACK_TIMEOUT = 0.1  # Tempo limite para receber um ACK

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
timers = {}
packets_dict = {}  # Dicionário para mapear seq_number aos pacotes


def start_timer(packet, addr, seq_num):
    global timers
    timer_key = (addr, seq_num)
    timer = threading.Timer(ACK_TIMEOUT, retransmit_packet, [packet, addr, seq_num])
    timer.start()
    timers[timer_key] = timer  # Armazena o timer no dicionário

def retransmit_packet(packet, addr, seq_num):
    global timers
    print(f"ACK não recebido para o pacote {seq_num}, retransmitindo pacote...")
    sock.sendto(packet, addr)
    start_timer(packet, addr, seq_num)  # Reinicia o timer

def send_file(filename, name, client, addr):
    with open(filename, 'rb') as f:
        file_content = f.read()

    total_size = len(file_content)
    total_packets = (total_size // (BUFFER_SIZE - 100)) + 1
    randomId = random_lowercase_string()
        
    for i in range(total_packets):
        start = i * (BUFFER_SIZE - 100)
        end = start + (BUFFER_SIZE - 100)
        content = file_content[start:end].decode('utf-8')
        checksum = calculate_checksum(content)
        seq_num = i + 1
        packet = f"{randomId}|{total_packets}|{name}|{addr[0]}|{addr[1]}|{content}|{checksum}|{seq_num}".encode('utf-8')
        packets_dict[seq_num] = packet
        sock.sendto(packet, client)
        start_timer(packet, client, seq_num)  # Inicia o timer para o pacote específico

def send_ack(seq_num, client):
    ack_message = f"ACK|{seq_num}".encode('utf-8')
    sock.sendto(ack_message, client)

def send_message(message, name, client, addr, isAck=False):
    filename = f'message-s-{name}.txt'
    if isAck:
        send_ack(message, client)
    else:
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

        elif message_type == "BYE":
            username = content[0]
            clients.discard(addr)
            message = (f'😪 Usuário {addr} com o username {username} saiu no chat.')
            print(message)
            for client in clients:
                if client != addr:
                    sock.sendto(f"BYE|{message}".encode('utf-8'), client)

        elif message_type == "ACK":
            seq_num = int(content[0])
            timer_key = (addr, seq_num)
            if timer_key in timers:
                timers[timer_key].cancel()  # Cancela o timer de retransmissão
                packets_dict.pop(seq_num)
                print(f"ACK recebido do cliente {addr} para o pacote {seq_num}")
                del timers[timer_key]  # Remove o timer do dicionário
        
        elif message_type == "CORRUPT":
                seq_num = int(content[0])
                if seq_num in packets_dict:
                    packet = packets_dict[seq_num]
                    print(f"Checksum inválido para o pacote {seq_num}, reenviando...")
                    retransmit_packet(packet, (UDP_IP, UDP_PORT), seq_num)

        elif message_type in messages:
            total_packets, name, packetData, checksum, seq_num = content
            if checksum == calculate_checksum(packetData):
                print(f"Checksum válido para o pacote {seq_num}")
                messages[message_type]["packets"][seq_num] = packetData
                
                send_message(seq_num, name, addr, addr, True)
                if len(messages[message_type]["packets"]) == int(total_packets):
                    print(messages[message_type]["packets"])
                    file_content = bytearray()
                    for i in range(1, int(total_packets) + 1):
                        file_content.extend(messages[message_type]["packets"][str(i)].encode("utf-8"))

                    message_text = file_content.decode('utf-8')

                    for client in clients:
                        if client != addr:
                            send_message(message_text, name, client, addr)
            else:
                print(f"Checksum inválido para o pacote {packetData}")
                sock.sendto(f"CORRUPT|{seq_num}".encode('utf-8'), addr)
        else: 
            total_packets, name, packetData, checksum, seq_num = content
            if checksum == calculate_checksum(packetData):
                print(f"Checksum válido para o pacote {seq_num}")
                messages[message_type] = {"name": name, "packets": {seq_num: packetData} }

                send_message(seq_num, name, addr, addr, True)

                if int(total_packets) == 1:
                    message_text = packetData

                    for client in clients:
                        if client != addr:
                            send_message(message_text, name, client, addr)
            else:
                print(f"Checksum inválido para o pacote {packetData}")
                sock.sendto(f"CORRUPT|{seq_num}".encode('utf-8'), addr)

    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}, {type(e).__name__}, {e.args}")

def server():
    print("Servidor iniciado! 📦")
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            threading.Thread(target=handle_client, args=(data, addr)).start()
        except Exception as e:
            print(f"Erro no servidor: {e}, {type(e).__name__}, {e.args}")

clients = set()
messages = {}

server_thread = threading.Thread(target=server)
server_thread.daemon = True  # Define a thread como daemon para encerrar junto com o programa principal
server_thread.start()

# Manter o servidor rodando
server_thread.join()
