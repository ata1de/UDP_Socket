import datetime
import os
import socket
import threading
from math import ceil

from functions import *

# Definição das constantes do servidor e buffer
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024
ACK_TIMEOUT = 0.1  # Tempo limite para receber um ACK

# Criação do socket do cliente para comunicação UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(10)  # Define um timeout para evitar bloqueios no recvfrom

packets_dict = {} 
# Dicionário para armazenar informações sobre os pacotes enviados
# Estrutura: { numero_sequencia: { "packet": pacote, "ack_count": contagem_de_acks, "timer": temporizador } }

def start_timer(packet, addr, expected_seq_num):
    # Função para iniciar o temporizador para retransmissão de pacotes
    timer = threading.Timer(ACK_TIMEOUT, retransmit_packet, [packet, addr, expected_seq_num])
    timer.start()
    packets_dict[expected_seq_num]["timer"] = timer  # Armazena o timer no dicionário de pacotes

def retransmit_packet(packet, addr, expected_seq_num):
    # Função que retransmite o pacote caso o ACK não seja recebido dentro do tempo limite
    if packets_dict[expected_seq_num]["ack_count"] == 0:
        print("ACK não recebido, retransmitindo pacote...")
        client_socket.sendto(packet, addr)  # Reenvia o pacote para o servidor
        start_timer(packet, addr, expected_seq_num)  # Reinicia o temporizador para nova tentativa

def send_ack(seq_num, client):
    # Função para enviar um ACK para o cliente
    checksum = calculate_checksum(str(seq_num))
    contentWHeader = f"ACK|{seq_num}|{checksum}".encode('utf-8')
    client_socket.sendto(contentWHeader, client)  # Envia o ACK para o cliente

def send_file(filename, name):
    # Função para enviar um arquivo .txt fragmentado em pacotes via UDP
    with open(filename, 'rb') as f:
        file_content = f.read()

    total_size = len(file_content)
    total_packets = ceil(total_size / (BUFFER_SIZE - 100))  # Calcula o número total de pacotes necessários
    total_packets = total_packets if total_packets > 0 else 1

    randomId = random_lowercase_string()  # Gera um ID aleatório para o arquivo
    expected_seq_num = 0 
    for i in range(total_packets):
        # Fragmenta e envia os pacotes
        start = i * (BUFFER_SIZE - 100)
        end = start + (BUFFER_SIZE - 100)
        content = file_content[start:end].decode('utf-8')
        checksum = calculate_checksum(content)
        expected_seq_num = i + 1 
        packet = f"{randomId}|{total_packets}|{name}|{content}|{checksum}|{expected_seq_num}".encode('utf-8')
        packets_dict[expected_seq_num] = { "packet": packet,"ack_count": 0, "timer": None } 
        client_socket.sendto(packet, (UDP_IP, UDP_PORT))  # Envia o pacote
        start_timer(packet, (UDP_IP, UDP_PORT), expected_seq_num)  # Inicia o temporizador para retransmissão

def send_message(message, name, isAck=False):
    # Função para enviar uma mensagem do cliente
    if isAck:
        send_ack(message, (UDP_IP, UDP_PORT))  # Envia um ACK caso seja uma mensagem de confirmação
    else:
        filename = f'message-c-{name}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(message)  # Escreve a mensagem em um arquivo .txt temporário
        send_file(filename, name)  # Envia o arquivo
        os.remove(filename)  # Remove o arquivo após o envio

def send_login_message(name):
    # Função para enviar uma mensagem de login ao servidor
    login_message = f"LOGIN|{name}".encode('utf-8')
    client_socket.sendto(login_message, (UDP_IP, UDP_PORT))

def send_bye_message(name):
    # Função para enviar uma mensagem de saída ao servidor
    bye_message = f"BYE|{name}".encode('utf-8')
    client_socket.sendto(bye_message, (UDP_IP, UDP_PORT))

def receive_messages():
    # Função para receber e processar mensagens do servidor
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message_type, *content = data.decode('utf-8').split('|')

            if message_type == "LOGIN":
                # Mensagem de login recebida
                print(*content)

            elif message_type == "BYE":
                # Mensagem de saída recebida
                print(*content)

            elif message_type == "ACK":
                # Processamento de um ACK recebido
                seq_num = int(content[0])
                checksum = content[1]

                if checksum == calculate_checksum(str(seq_num)):
                    # Verifica a integridade do ACK recebido
                    if packets_dict[seq_num]["ack_count"] >= 1: 
                        # Retransmite o próximo pacote se o ACK for duplicado
                        retransmit_packet(packets_dict[seq_num + 1]["packet"], (UDP_IP, UDP_PORT), seq_num + 1)       
                        print("ACK duplicado recebido, retransmitindo pacote...")   
                        packets_dict[seq_num]["ack_count"] += 1
                    else: 
                        # Confirma o recebimento do ACK
                        packets_dict[seq_num]["ack_count"] = 1
                        print("ACK recebido para o pacote", seq_num)
                    packets_dict[seq_num]["timer"].cancel()  # Cancela o temporizador associado ao pacote
                else: 
                    print(f"ACK {seq_num} chegou corrompido.")

            elif message_type in messages:
                # Processamento de pacotes de mensagem recebidos
                total_packets, name, addrIp, addrPort, packet, checksum, seq_num = content

                if seq_num in messages[message_type]["packets"]: 
                    # Verifica se o pacote já foi recebido
                    print(f"Pacote já foi recebido pra esse seq num {seq_num}, reenviando o ACK...")
                    send_message(seq_num, name, True)
                else:
                    if checksum == calculate_checksum(packet):
                        # Verifica a integridade do pacote e envia um ACK
                        print(f"Checksum válido para o pacote {seq_num}")
                        send_message(seq_num, name, True)
                        messages[message_type]["packets"][seq_num] = packet

                        if int(total_packets) == len(messages[message_type]["packets"]):
                            # Se todos os pacotes foram recebidos, monta e exibe a mensagem completa
                            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                            gatheredPackets = ""
                            for i in range(1, int(total_packets) + 1):
                                gatheredPackets +=  messages[message_type]["packets"][str(i)]
                            final_message = f"{addrIp}:{addrPort}/~{name}: {gatheredPackets} {date_now}"
                            print(final_message)   
                            print() 
                    else:
                        # Se o checksum falhar, trata o pacote corrompido
                        print(f"Checksum inválido para o pacote {packet}")
                        if int(seq_num) > 1:
                            send_message(int(seq_num)-1, name, True)                      
            else: 
                # Tratamento para mensagens de tipos desconhecidos
                total_packets, name, addrIp, addrPort, packet, checksum, seq_num = content
                if checksum == calculate_checksum(packet):
                    print(f"Checksum válido para o pacote {seq_num}")
                    send_message(seq_num, name, True)
                    messages[message_type] = {"name": name, "packets": {seq_num: packet} }
                    if total_packets == '1':
                        date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                        final_message = f"{addrIp}:{addrPort}/~{name}: {packet} {date_now}"
                        print(final_message)
                        print()
                else:
                    print(f"Checksum inválido para o pacote {packet}")
                    if int(seq_num) > 1:
                        send_message(int(seq_num)-1, name, True)

        except socket.timeout:
            # Ignora o timeout e continua recebendo mensagens
            continue
        except Exception as e:
            # Tratamento de exceções
            print(f"Erro ao receber mensagem: {e}")

messages = {}
# Inicia a thread para receber mensagens
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Faz com que a thread encerre junto com o programa principal
receive_thread.start()

leaved =  False
print("🤠 Pra se conectar a sala digite 'hi, meu nome eh <nome_do_usuario>':")

# Loop principal para interação com o usuário
while not leaved: 
    intro = input()

    if intro.startswith("hi, meu nome eh "):
        # Processa o comando de login do usuário
        name = getUserName(intro)
        send_login_message(name)
        print(f"Olá, {name} 😃! Vamos começar o chat! Digite sua mensagem abaixo

