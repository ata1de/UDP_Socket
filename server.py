import socket
import threading
import os

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
            filename, filesize, udp_ip_client, udp_port_client, name_client = content
            filesize = int(filesize)

            
            # Enviar arquivo recebido para outros clientes
            print(f"Mensagem recebida de {addr}")
            for client in clients:
                if client != addr:
                    sock.sendto(f'FILE|{filename}|{udp_ip_client}|{udp_port_client}|{name_client}|{filesize}', client)

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
