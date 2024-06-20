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

def send_file(filename, name, addr):
    with open(filename, 'rb') as f:
        file_content = f.read()
    
    total_size = len(file_content)
    total_packets = (total_size // BUFFER_SIZE) + 1
    header = f"FILE|{filename}|{total_packets}|{name}".encode('utf-8')
    
    for client in clients:
        if client != addr:
            sock.sendto(header, client)
    
            for i in range(total_packets):
                start = i * BUFFER_SIZE
                end = start + BUFFER_SIZE
                packet = file_content[start:end]
                sock.sendto(packet, client)


def send_message(message, name, addr):
    filename = f'message-{name}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(message)
    send_file(filename, name, addr)
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
            login_message = f"MSG|🔥 {username} entrou no chat."
            print(f'usuário {addr} com o username {username} entrou no chat.')
            for client in clients:
                if client != addr:
                    sock.sendto(login_message.encode('utf-8'), client)

        elif message_type == 'FILE':
            filename, total_packets, username = content
            total_packets = int(total_packets)
            file_content = bytearray()

            for _ in range(total_packets):
                packet, _ = sock.recvfrom(BUFFER_SIZE)
                file_content.extend(packet)

            # Enviar arquivo recebido para outros clientes
            print(f"Mensagem recebida de {username}")

            try:
                message_text = file_content.decode('utf-8')

                send_message(message_text, username, addr)
                
            except UnicodeDecodeError as e:
                print(f"Erro de decodificação do conteúdo do arquivo: {e}")
                return
            
            # date_now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            # final_message = f"{addr[0]}:{addr[1]}/~{username}: {message_text} {date_now}"
                
            # for client in clients:
            #     if client != addr:
            #         sock.sendto(final_message.encode('utf-8'), client)

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
