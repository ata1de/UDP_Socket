import os
import socket
import threading
from math import ceil

from functions import *


class Server:
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    BUFFER_SIZE = 1024
    ACK_TIMEOUT = 0.1  # Tempo limite para receber um ACK

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.packets_dict = {}
        self.clients = set()
        self.messages = {}

    # Função para iniciar o temporizador para retransmissão de pacotes
    def start_timer(self, packet, addr, seq_num):
        timer = threading.Timer(self.ACK_TIMEOUT, self.retransmit_packet, [packet, addr, seq_num])
        timer.start()
        self.packets_dict[(addr, seq_num)]["timer"] = timer

    # Função que retransmite o pacote caso o ACK não seja recebido dentro do tempo limite
    def retransmit_packet(self, packet, addr, seq_num):
        print(f"ACK não recebido para o pacote {seq_num}, retransmitindo pacote do cliente {addr}...")
        self.sock.sendto(packet, addr)
        self.start_timer(packet, addr, seq_num)  # Reinicia o timer

    # Função para enviar um arquivo .txt fragmentado em pacotes via UDP
    def send_file(self, filename, name, client, addr):
        with open(filename, 'rb') as f:
            file_content = f.read()

        total_size = len(file_content)
        # Calcula o número total de pacotes necessários removendo os bits do cabeçalho
        total_packets = ceil(total_size / (self.BUFFER_SIZE - 100))
        randomId = random_lowercase_string()

        # Envia os pacotes para o cliente
        for i in range(total_packets):
            start = i * (self.BUFFER_SIZE - 100)
            end = start + (self.BUFFER_SIZE - 100)
            content = file_content[start:end].decode('utf-8')
            checksum = calculate_checksum(content)
            seq_num = i + 1
            packet = f"{randomId}|{total_packets}|{name}|{addr[0]}|{addr[1]}|{content}|{checksum}|{seq_num}".encode('utf-8')
            self.packets_dict[(client, seq_num)] = {"packet": packet, "ack_count": 0, "timer": None}
            self.sock.sendto(packet, client)
            self.start_timer(packet, client, seq_num)  # Inicia o timer para o pacote específico

    # Função para enviar um ACK para o cliente
    def send_ack(self, seq_num, client):
        checksum = calculate_checksum(str(seq_num))
        ack_message = f"ACK|{seq_num}|{checksum}".encode('utf-8')
        self.sock.sendto(ack_message, client)

    # Função para enviar uma mensagem para o cliente
    def send_message(self, message, name, client, addr, isAck=False):
        filename = f'message-s-{name}.txt'
        if isAck:
            self.send_ack(message, client)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(message)
            self.send_file(filename, name, client, addr)
            os.remove(filename)

    def handle_client(self, data, addr):
        try:
            # Adiciona o endereço do cliente à lista de clientes
            if addr not in self.clients:
                self.clients.add(addr)

            try:
                message_type, *content = data.decode('utf-8').split('|')
            except UnicodeDecodeError as e:
                print(f"Erro de decodificação de dados: {e}")
                return

            # tratamento para mensagem do tipo login
            if message_type == 'LOGIN':
                username = content[0]
                login_message = f"LOGIN|🔥 {username} entrou no chat."
                print(f'😮 Usuário {addr} com o username {username} entrou no chat.')
                for client in self.clients:
                    if client != addr:
                        self.sock.sendto(login_message.encode('utf-8'), client)

            # tratamento para mensagem de saída
            elif message_type == "BYE":
                username = content[0]
                self.clients.discard(addr)
                message = (f'😪 Usuário {addr} com o username {username} saiu no chat.')
                print(message)
                for client in self.clients:
                    if client != addr:
                        self.sock.sendto(f"BYE|{message}".encode('utf-8'), client)

            # -----------------------------------------------------------------------------------------------

            # tratamento para mensagem do tipo ACK
            elif message_type == "ACK":
                seq_num = int(content[0])
                checksum = content[1]
                # verifica se o checksum do pacote é válido
                if (checksum == calculate_checksum(str(seq_num))):
                    # verifica se o pacote foi retransmitido
                    if (self.packets_dict[(addr, seq_num)]["ack_count"] >= 1):
                        self.retransmit_packet(self.packets_dict[(addr, seq_num + 1) + 1]["packet"], addr, seq_num + 1)
                        print(f"ACK duplicado recebido, retransmitindo pacote {seq_num} do cliente {addr}...")
                        self.packets_dict[(addr, seq_num)]["ack_count"] += 1
                    else:
                        # Confirma o recebimento do ACK
                        self.packets_dict[(addr, seq_num)]["ack_count"] = 1
                        print(f"ACK recebido para o pacote {seq_num} do cliente {addr}")

                    # cancela o timer
                    self.packets_dict[(addr, seq_num)]["timer"].cancel()
                else:
                    print(f"ACK {seq_num} do cliente {addr} chegou corrompido.")

            # verificação se a mensagem já está no dicionário
            elif message_type in self.messages:
                total_packets, name, packetData, checksum, seq_num = content

                # verifica se o pacote já foi recebido
                if seq_num in self.messages[message_type]["packets"]:
                    print(f"Pacote já foi recebido pra esse seq_num {seq_num} para o cliente {addr}, reenviando o ACK...")
                    self.send_message(seq_num, name, addr, addr, True)
                else:
                    # verifica se o checksum do pacote é válido
                    if checksum == calculate_checksum(packetData):
                        print(f"Checksum válido para o pacote {seq_num} do cliente {addr}")
                        # adiciona pacote ao dicionário
                        self.messages[message_type]["packets"][seq_num] = packetData

                        self.send_message(seq_num, name, addr, addr, True)

                        if len(self.messages[message_type]["packets"]) == int(total_packets):
                            file_content = bytearray()
                            for i in range(1, int(total_packets) + 1):
                                file_content.extend(self.messages[message_type]["packets"][str(i)].encode("utf-8"))

                            message_text = file_content.decode('utf-8')

                            print(f'Clientes: {self.clients}')
                            for client in self.clients:
                                if client != addr:
                                    self.send_message(message_text, name, client, addr)
                    else:
                        # checksum inválido para o pacote, então é enviado o ack do pacote anterior
                        print(f"Checksum inválido para o pacote {packetData} do cliente {addr}")
                        if (int(seq_num) > 1):  # no caso de se o primeiro seq_num -> vai acontecer estouro do timeout
                            self.send_ack(int(seq_num) - 1, addr)
            else:
                # se a mensagem não for de nenhum tipo do header
                total_packets, name, packetData, checksum, seq_num = content
                # verifica o checksum do pacote
                if checksum == calculate_checksum(packetData):
                    print(f"Checksum válido para o pacote {seq_num} do cliente {addr}")
                    self.messages[message_type] = {"name": name, "packets": {seq_num: packetData}}

                    self.send_message(seq_num, name, addr, addr, True)

                    if int(total_packets) == 1:
                        message_text = packetData

                        for client in self.clients:
                            if client != addr:
                                self.send_message(message_text, name, client, addr)
                else:
                    # verificação do checksum do pacote
                    print(f"Checksum inválido para o pacote {packetData} do cliente {addr}")
                    if (int(seq_num) > 1):  # no caso de se o primeiro seq_num
                        self.send_ack(int(seq_num) - 1, addr)

        except Exception as e:
            print(f"Erro ao lidar com o cliente {addr}: {e}, {type(e).__name__}, {e.args}")

    def start_server(self):
        print("Servidor iniciado! 📦")
        # Loop para receber mensagens dos clientes
        while True:
            try:
                data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
                threading.Thread(target=self.handle_client, args=(data, addr)).start()
            except Exception as e:
                print(f"Erro no servidor: {e}, {type(e).__name__}, {e.args}")


server = Server()
server.start_server()
