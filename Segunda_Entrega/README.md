# Segunda Entrega
Na segunda etapa, o projeto foi expandido para incluir a implementação do protocolo RDT 3.0 (Reliable Data Transfer), que adiciona confiabilidade à transmissão de mensagens nesse chat de sala única. O RDT 3.0 é um protocolo de transferência de dados que garante a entrega correta e ordenada das mensagens, mesmo em ambientes onde há possibilidade de perda e corrupção de pacotes.

### Funcionalidades Implementadas
- Manutenção da troca de mensagens: Implementação de prints para a prevenção de possiveis erros e confirmações de ACKS e pacotes corrompidos

- Detecção de Erros: O RDT 3.0 utiliza **checksums** para detectar corrupção de dados durante a transmissão. Se um pacote é corrompido, ele será descartado e o remetente será notificado para reenviá-lo.

- Confirmação de Recebimento (ACK): O destinatário verifica a integridade do pacote recebido. Se o pacote estiver correto, um ACK (acknowledgment) é enviado de volta ao remetente para confirmar a recepção bem-sucedida.

- Reenvio de Pacotes: Se o remetente não receber um ACK dentro de um período de tempo determinado (timeout), ele reenviará o pacote. Isso garante que todos os pacotes sejam eventualmente entregues, mesmo em caso de perda temporária de conexão.

- Sequenciamento de Pacotes: Pacotes são numerados sequencialmente para evitar duplicações e garantir que as mensagens sejam recebidas na ordem correta. Se um pacote é perdido ou corrompido, ele pode ser retransmitido corretamente com base em seu número de sequência.

- Administração de Timeouts: Timeouts são utilizados para detectar perdas de pacotes. Se um ACK não é recebido dentro do tempo limite, o remetente presume que o pacote foi perdido e aciona a retransmissão.