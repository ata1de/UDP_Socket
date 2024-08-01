# Primeira Entrega
A aplicação simula um chat de sala única, onde os usuários podem enviar e receber arquivos de texto (.txt), que são exibidos diretamente no terminal de cada cliente conectado.


### Funcionalidades Implementadas
- Conexão de Múltiplos Clientes:
A aplicação suporta múltiplos clientes conectados ao mesmo tempo, sem interrupção do funcionamento do chat. Cada cliente pode enviar e receber mensagens de todos os outros participantes na sala.

- Troca de Arquivos de Texto (.txt):
Os usuários podem enviar mensagens que são convertidas em arquivos .txt e enviadas ao servidor. O servidor, por sua vez, repassa o arquivo de texto para todos os outros clientes conectados.

- Fragmentação e Reconstrução de Pacotes:
Mensagens que ultrapassam o limite de 1024 bytes são fragmentadas em pacotes menores e, ao serem recebidas, são reconstruídas para exibição no terminal do cliente.

- Notificações de Conexão e Desconexão:
Quando um novo usuário se conecta à sala, todos os usuários já conectados recebem uma mensagem notificando a nova presença. Da mesma forma, quando um usuário sai da sala, os outros usuários são notificados.
Comandos de Controle:

- Os usuários para se conectarem e se desligarem à sala utilizam o comando:
Para se conectar: "hi meu nome eh". Para se desligar "bye".
