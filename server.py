import socket
import threading
import os
import datetime

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

clients = set()

def handle_client(data, addr):
    try:
        if addr not in clients:
            clients.add(addr)

        message_type, *content = data.decode('utf-8').split('|')
        
        if message_type == 'FILE':
            filename, total_packets, username = content
            total_packets = int(total_packets)
            file_content = bytearray()

            for _ in range(total_packets):
                packet, _ = sock.recvfrom(BUFFER_SIZE)
                file_content.extend(packet)

            # Enviar arquivo recebido para outros clientes
            print(f"Mensagem recebida de {username}")

            message_text = file_content.decode('utf-8')
            date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            final_message = f"{addr[0]}:{addr[1]}/~{username}: {message_text} {date_now}"
                
            for client in clients:
                if client != addr:
                    sock.sendto(final_message.encode('utf-8'), client)

        else:
            print("Tipo de mensagem desconhecido:", message_type)

    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}")

def server():
    print("Servidor iniciado...")
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            threading.Thread(target=handle_client, args=(data, addr)).start()
        except Exception as e:
            print(f"Erro no servidor: {e}")

server_thread = threading.Thread(target=server)
server_thread.daemon = True  # Define a thread como daemon para encerrar junto com o programa principal
server_thread.start()

# Manter o servidor rodando
server_thread.join()
