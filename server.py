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
            filename, filesize = content
            filesize = int(filesize)

            with open(f'received_{filename}', 'wb') as f:
                bytes_received = 0
                while bytes_received < filesize:
                    packet, _ = sock.recvfrom(BUFFER_SIZE)
                    f.write(packet)
                    bytes_received += len(packet)

            # Enviar arquivo recebido para outros clientes
            for client in clients:
                if client != addr:
                    with open(f'received_{filename}', 'rb') as f:
                        while (chunk := f.read(BUFFER_SIZE)):
                            sock.sendto(chunk, client)
        elif message_type == 'MESSAGE':
            message = content[0]
            print(f"Mensagem recebida de {addr}: {message}")
            for client in clients:
                if client != addr:
                    sock.sendto(data, client)
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
