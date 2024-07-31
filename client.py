import datetime
import os
import socket
import threading
from math import ceil

from functions import *

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024
ACK_TIMEOUT = 0.1  # Tempo limite para receber um ACK

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(10)  # Define um timeout para evitar bloqueios

packets_dict = {} 
# seq_number { packet, ack_count, timer }

#  PS: ao terminar de enviar uma mensagem faz sentido esse packets_dict ser zerado 0> nõa ta feito ainda

def start_timer(packet, addr, expected_seq_num):
    timer = threading.Timer(ACK_TIMEOUT, retransmit_packet, [packet, addr, expected_seq_num])
    timer.start()
    packets_dict[expected_seq_num]["timer"] = timer

def retransmit_packet(packet, addr, expected_seq_num):
    if packets_dict[expected_seq_num]["ack_count"] == 0:
        print("ACK não recebido, retransmitindo pacote...")
        client_socket.sendto(packet, addr)
        start_timer(packet, addr, expected_seq_num)

def send_ack(seq_num, client):
    checksum = calculate_checksum(str(seq_num))
    contentWHeader = f"ACK|{seq_num}|{checksum}".encode('utf-8')
    client_socket.sendto(contentWHeader, client)

def send_file(filename, name):
    with open(filename, 'rb') as f:
        file_content = f.read()

    total_size = len(file_content)

    total_packets = ceil(total_size / (BUFFER_SIZE - 100))
    total_packets = total_packets if total_packets > 0 else 1

    randomId = random_lowercase_string()
    expected_seq_num = 0 
    for i in range(total_packets):
        start = i * (BUFFER_SIZE - 100)
        end = start + (BUFFER_SIZE - 100)
        content = file_content[start:end].decode('utf-8')
        checksum = calculate_checksum(content)
        expected_seq_num = i + 1 
        packet = f"{randomId}|{total_packets}|{name}|{content}|{checksum}|{expected_seq_num}".encode('utf-8')
        packets_dict[expected_seq_num] = { "packet": packet,"ack_count": 0, "timer": None } # esse timer vai ser mudado dentro do start do timer
        client_socket.sendto(packet, (UDP_IP, UDP_PORT))
        start_timer(packet, (UDP_IP, UDP_PORT), expected_seq_num) 


def send_message(message, name, isAck=False):
    if isAck:
        send_ack(message, (UDP_IP, UDP_PORT))
    else:
        filename = f'message-c-{name}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(message)
        send_file(filename, name)
        os.remove(filename)

def send_login_message(name):
    login_message = f"LOGIN|{name}".encode('utf-8')
    client_socket.sendto(login_message, (UDP_IP, UDP_PORT))

def send_bye_message(name):
    bye_message = f"BYE|{name}".encode('utf-8')
    client_socket.sendto(bye_message, (UDP_IP, UDP_PORT))

def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message_type, *content = data.decode('utf-8').split('|')

            if message_type == "LOGIN":
                print(*content)

            elif message_type == "BYE":
                print(*content)

            elif message_type == "ACK":
                seq_num = int(content[0])
                checksum = content[1]

                if(checksum == calculate_checksum(str(seq_num))):
                    if (packets_dict[seq_num]["ack_count"] >= 1): 
                        retransmit_packet(packets_dict[seq_num + 1]["packet"], (UDP_IP, UDP_PORT), seq_num + 1)       
                        print("ACK duplicado recebido, retransmitindo pacote...")   
                        packets_dict[seq_num]["ack_count"] += 1
                    else: 
                        packets_dict[seq_num]["ack_count"] = 1
                        print("ACK recebido para o pacote", seq_num)
                
                    packets_dict[seq_num]["timer"].cancel()
                else: 
                    print(f"ACK {seq_num} chegou corrompido.")

       
            elif message_type in messages:
                total_packets, name, addrIp, addrPort, packet, checksum, seq_num = content

                if seq_num in messages[message_type]["packets"]: 
                    print(f"Pacote já foi recebido pra esse seq num {seq_num}, reenviando o ACK...")
                    send_message(seq_num, name, True)
                else:
                    if checksum == calculate_checksum(packet):
                        print(f"Checksum válido para o pacote {seq_num}")
                        send_message(seq_num, name, True)
                        # messages[message_type] = { "name": name, "packets": [*messages[message_type]["packets"], packet] }
                        messages[message_type]["packets"][seq_num] = packet

                        if (int(total_packets) == len(messages[message_type]["packets"])):
                            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                            gatheredPackets = ""
                            for i in range(1, int(total_packets) + 1):
                                gatheredPackets +=  messages[message_type]["packets"][str(i)]
                            final_message = f"{addrIp}:{addrPort}/~{name}: {gatheredPackets} {date_now}"
                            print(final_message)   
                            print() 
                    else:
                        print(f"Checksum inválido para o pacote {packet}")
                        if (int(seq_num) > 1):
                            send_message(int(seq_num)-1, name, True)                      
            else: 
                total_packets, name, addrIp, addrPort, packet, checksum, seq_num =  content
                if checksum == calculate_checksum(packet):
                    print(f"Checksum válido para o pacote {seq_num}")
                    send_message(seq_num, name, True)
                    messages[message_type] = {"name": name, "packets": {seq_num: packet} }
                    if (total_packets == '1'):
                        date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                        final_message = f"{addrIp}:{addrPort}/~{name}: {packet} {date_now}"
                        print(final_message)
                        print()
                else:
                    print(f"Checksum inválido para o pacote {packet}")
                    if (int(seq_num) > 1):
                        send_message(int(seq_num)-1, name, True)

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")



messages = {}
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Faz com que a thread encerre junto com o programa principal
receive_thread.start()

leaved =  False
print("🤠 Pra se conectar a sala digite 'hi, meu nome eh <nome_do_usuario>':")

while not leaved: 
    intro = input()

    if (intro.startswith("hi, meu nome eh ")):
        name = getUserName(intro)
        send_login_message(name)
        print(f"Olá, {name} 😃! Vamos começar o chat! Digite sua mensagem abaixo ⬇️:")

        while True:
            message = input()
            if (message.lower() == "bye"):
                send_bye_message(name)
                leaved = True
                break
            send_message(message, name)
    else:
        print("😭 Deu errado! Pra se conectar a sala digite 'hi, meu nome eh <nome_do_usuario>':")
