# Projeto de Redes - Transmissão de Arquivos com UDP

### Descrição do Projeto
Este projeto foi desenvolvido para a disciplina de Redes e implementa a comunicação de arquivos utilizando o protocolo UDP com a biblioteca Socket em Python. A aplicação simula um chat de sala única, onde os usuários podem enviar e receber arquivos de texto (.txt) que são exibidos no terminal de cada cliente conectado. Além disso, foi implementado o protocolo RDT 3.0 (Reliable Data Transfer), que adiciona confiabilidade à transmissão de mensagens, garantindo a entrega correta e ordenada mesmo em ambientes sujeitos a perdas e corrupção de pacotes.





# Objetivos
O objetivo deste trabalho é desenvolver um sistema de comunicação via UDP, com a implementação de um chat de sala única que permita a troca de mensagens entre múltiplos clientes de forma simultânea. Além disso, busca-se criar um ambiente de chat onde os usuários possam enviar e receber mensagens com formato específico, incluindo IP, porta, nome do usuário, mensagem e timestamp, bem como notificar os participantes sobre novas conexões à sala.

Outro objetivo fundamental do trabalho é adicionar confiabilidade à comunicação através da implementação do protocolo RDT 3.0, garantindo a transferência confiável das mensagens, mesmo em ambientes sujeitos a perda e corrupção de pacotes. Isso envolve a detecção e correção de erros de transmissão utilizando checksums, números de sequência e retransmissão de pacotes em caso de problemas.


# Primeira Entrega
Este projeto foi desenvolvido como parte da disciplina de Redes e consiste na implementação de um sistema de comunicação via UDP utilizando a biblioteca Socket em Python. A aplicação simula um chat de sala única, onde os usuários podem enviar e receber arquivos de texto (.txt), que são exibidos diretamente no terminal de cada cliente conectado.
### Funcionalidades Implementadas
Conexão de Múltiplos Clientes:
A aplicação suporta múltiplos clientes conectados ao mesmo tempo, sem interrupção do funcionamento do chat. Cada cliente pode enviar e receber mensagens de todos os outros participantes na sala.

Troca de Arquivos de Texto (.txt):
Os usuários podem enviar mensagens que são convertidas em arquivos .txt e enviadas ao servidor. O servidor, por sua vez, repassa o arquivo de texto para todos os outros clientes conectados.

Fragmentação e Reconstrução de Pacotes:
Mensagens que ultrapassam o limite de 1024 bytes são fragmentadas em pacotes menores e, ao serem recebidas, são reconstruídas para exibição no terminal do cliente.

Notificações de Conexão e Desconexão:

Quando um novo usuário se conecta à sala, todos os usuários já conectados recebem uma mensagem notificando a nova presença. Da mesma forma, quando um usuário sai da sala, os outros usuários são notificados.
Comandos de Controle:

Os usuários podem se conectar à sala utilizando o comando:






# Bibliotecas
A biblioteca socket foi amplamente empregada ao longo de todo o projeto, desempenhando um papel fundamental na criação e na manutenção das conexões entre o cliente e o servidor.






# Integrantes
Antônio Robério (arbof@cin.ufpe.br)

Daniel Dias (dmdf@cin.ufpe.br)

Eric Bezerra (eblb@cin.ufpe.br)

Mateus Ataide (mhal@cin.ufpe.br)
