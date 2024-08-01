import datetime
import os
import socket
import threading
from math import ceil

from functions import *


# Classe para gerenciar pacotes e suas retransmissões
class PacketHandler:
    ACK_TIMEOUT = 0.1  # Tempo limite para receber um ACK

    def __init__(self, client_socket):
        self.client_socket = client_socket
        # Dicionário para armazenar informações dos pacotes
        # {seq_num: { "packet": pacote, "ack_count": contagem_de_acks, "timer": temporizador } }
        self.packets_dict = {}

    # Inicia o temporizador para retransmissão do pacote
    def start_timer(self, packet, addr, expected_seq_num):
        # Cria um temporizador que chama retransmit_packet se o ACK não for recebido a tempo
        timer = threading.Timer(self.ACK_TIMEOUT, self.retransmit_packet, [packet, addr, expected_seq_num])
        timer.start()
        # Armazena o temporizador no dicionário de pacotes
        self.packets_dict[expected_seq_num]["timer"] = timer

    # Retransmite o pacote caso o ACK não seja recebido
    def retransmit_packet(self, packet, addr, expected_seq_num):
        # Verifica se o ACK foi recebido
        if self.packets_dict[expected_seq_num]["ack_count"] == 0:
            print("ACK não recebido, retransmitindo pacote...")
            self.client_socket.sendto(packet, addr)
            # Reinicia o temporizador
            self.start_timer(packet, addr, expected_seq_num)

    # Envia um ACK para o cliente
    def send_ack(self, seq_num, client):
        checksum = calculate_checksum(str(seq_num))  # Calcula o checksum do seq_num
        # Cria o conteúdo do ACK com o seq_num e checksum
        contentWHeader = f"ACK|{seq_num}|{checksum}".encode('utf-8')
        self.client_socket.sendto(contentWHeader, client)  # Envia o ACK para o cliente


# Classe principal do cliente UDP
class Client:
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    BUFFER_SIZE = 1024

    def __init__(self):
        # Cria um socket UDP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(10)  # Define o tempo limite para receber dados
        self.packet_handler = PacketHandler(self.client_socket)  # Cria um manipulador de pacotes
        self.messages = {}  # Dicionário para armazenar mensagens recebidas
        self.leaved = False  # Flag para indicar se o cliente saiu
        self.start_receive_thread()  # Inicia a thread para receber mensagens

    # Inicia uma thread para receber mensagens do servidor
    def start_receive_thread(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    # Envia um arquivo fragmentado em pacotes via UDP
    def send_file(self, filename, name):
        with open(filename, 'rb') as f:
            file_content = f.read()

        total_size = len(file_content)
        # Calcula o número total de pacotes necessários removendo os bits do cabeçalho
        total_packets = ceil(total_size / (self.BUFFER_SIZE - 100))
        total_packets = total_packets if total_packets > 0 else 1

        randomId = random_lowercase_string()  # Gera um ID aleatório para o arquivo
        expected_seq_num = 0  # Número de sequência esperado do próximo pacote
        for i in range(total_packets):
            start = i * (self.BUFFER_SIZE - 100)
            end = start + (self.BUFFER_SIZE - 100)
            content = file_content[start:end].decode('utf-8')
            checksum = calculate_checksum(content)  # Calcula o checksum do conteúdo do pacote
            expected_seq_num = i + 1
            # Cria o pacote com os dados necessários
            packet = f"{randomId}|{total_packets}|{name}|{content}|{checksum}|{expected_seq_num}".encode('utf-8')
            # Armazena informações do pacote no dicionário
            self.packet_handler.packets_dict[expected_seq_num] = {"packet": packet, "ack_count": 0, "timer": None}
            self.client_socket.sendto(packet, (self.UDP_IP, self.UDP_PORT))  # Envia o pacote
            self.packet_handler.start_timer(packet, (self.UDP_IP, self.UDP_PORT), expected_seq_num)  # Inicia o temporizador

    # Envia uma mensagem para o servidor
    def send_message(self, message, name, isAck=False):
        if isAck:
            self.packet_handler.send_ack(message, (self.UDP_IP, self.UDP_PORT))  # Envia um ACK
        else:
            filename = f'message-c-{name}.txt'  # Nome do arquivo temporário
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(message)
            self.send_file(filename, name)  # Envia o arquivo contendo a mensagem
            os.remove(filename)  # Remove o arquivo temporário

# ----------------------------------------------------------------------------------------------------------------------
    # Envia uma mensagem de login para o servidor
    def send_login_message(self, name):
        login_message = f"LOGIN|{name}".encode('utf-8')
        self.client_socket.sendto(login_message, (self.UDP_IP, self.UDP_PORT))

    # Envia uma mensagem de despedida para o servidor
    def send_bye_message(self, name):
        bye_message = f"BYE|{name}".encode('utf-8')
        self.client_socket.sendto(bye_message, (self.UDP_IP, self.UDP_PORT))

    # Recebe mensagens do servidor
    def receive_messages(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(self.BUFFER_SIZE)  # Recebe dados do servidor
                message_type, *content = data.decode('utf-8').split('|')  # Decodifica e separa o tipo de mensagem e conteúdo

                if message_type == "LOGIN":
                    print(*content)  # Exibe a mensagem de login

                elif message_type == "BYE":
                    print(*content)  # Exibe a mensagem de despedida

                elif message_type == "ACK":
                    seq_num = int(content[0])
                    checksum = content[1]

                    # Verifica se o checksum é válido
                    if checksum == calculate_checksum(str(seq_num)):
                        # Verifica se o ACK é duplicado
                        if self.packet_handler.packets_dict[seq_num]["ack_count"] >= 1:
                            # Retransmite o próximo pacote
                            self.packet_handler.retransmit_packet(self.packet_handler.packets_dict[seq_num + 1]["packet"],
                                                                  (self.UDP_IP, self.UDP_PORT), seq_num + 1)
                            print("ACK duplicado recebido, retransmitindo pacote...")
                            self.packet_handler.packets_dict[seq_num]["ack_count"] += 1
                        else:
                            self.packet_handler.packets_dict[seq_num]["ack_count"] = 1
                            print("ACK recebido para o pacote", seq_num)
                        self.packet_handler.packets_dict[seq_num]["timer"].cancel()  # Cancela o temporizador
                    else:
                        print(f"ACK {seq_num} chegou corrompido.")  # Checksum inválido para o ACK

                # Verifica se a mensagem já está no dicionário
                elif message_type in self.messages:
                    total_packets, name, addrIp, addrPort, packet, checksum, seq_num = content

                    # Verifica se o pacote já foi recebido
                    if seq_num in self.messages[message_type]["packets"]:
                        print(f"Pacote já foi recebido pra esse seq num {seq_num}, reenviando o ACK...")
                        self.send_message(seq_num, name, True)  # Reenvia o ACK
                    else:
                        # Verifica se o checksum do pacote é válido
                        if checksum == calculate_checksum(packet):
                            print(f"Checksum válido para o pacote {seq_num}")
                            self.send_message(seq_num, name, True)  # Envia o ACK
                            self.messages[message_type]["packets"][seq_num] = packet  # Armazena o pacote

                            # Verifica se todos os pacotes foram recebidos
                            if int(total_packets) == len(self.messages[message_type]["packets"]):
                                date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                                gatheredPackets = ""
                                for i in range(1, int(total_packets) + 1):
                                    gatheredPackets += self.messages[message_type]["packets"][str(i)]
                                final_message = f"{addrIp}:{addrPort}/~{name}: {gatheredPackets} {date_now}"
                                print(final_message)
                                print()
                        else:
                            print(f"Checksum inválido para o pacote {packet}")
                            if int(seq_num) > 1:
                                self.send_message(int(seq_num) - 1, name, True)  # Reenvia o ACK do pacote anterior

                # Se a mensagem não estiver no dicionário
                else:
                    total_packets, name, addrIp, addrPort, packet, checksum, seq_num = content
                    if checksum == calculate_checksum(packet):  # Verifica se o checksum é válido
                        print(f"Checksum válido para o pacote {seq_num}")
                        self.send_message(seq_num, name, True)  # Envia o ACK
                        self.messages[message_type] = {"name": name, "packets": {seq_num: packet}}
                        if total_packets == '1':
                            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                            final_message = f"{addrIp}:{addrPort}/~{name}: {packet} {date_now}"
                            print(final_message)
                            print()
                    else:
                        print(f"Checksum inválido para o pacote {packet}")
                        if int(seq_num) > 1:
                            self.send_message(int(seq_num) - 1, name, True)  # Reenvia o ACK do pacote anterior

            except socket.timeout:
                continue  # Continua no loop se houver um timeout
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")  # Exibe erros durante o recebimento de mensagens

client = Client()
print("🤠 Pra se conectar a sala digite 'hi, meu nome eh <nome_do_usuario>':")

while not client.leaved:
    intro = input()

    if intro.startswith("hi, meu nome eh "):
        name = getUserName(intro)
        client.send_login_message(name)
        print(f"Olá, {name} 😃! Vamos começar o chat! Digite sua mensagem abaixo ⬇")
        while True:
            message = input()
            if message.lower() == "bye":
                client.send_bye_message(name)
                client.leaved = True
                break
            client.send_message(message, name)
    else:
        print("😭 Deu errado! Pra se conectar a sala digite 'hi, meu nome eh <nome_do_usuario>':")
