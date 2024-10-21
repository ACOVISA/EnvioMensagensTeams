Automação de Extração de Leilões e Notificação via Azure Service Bus
Descrição
Este projeto automatiza a extração de informações de leilões do Diário da Justiça Eletrônico (DJE) e envia notificações com essas informações via Azure Service Bus para um endereço de e-mail especificado. A automação é realizada utilizando Selenium para a interação com a página web do DJE e o Azure Service Bus para o envio das notificações.

Funcionalidades
Acessa a página de consulta avançada do DJE e realiza buscas por leilões.
Extrai links e informações dos leilões encontrados.
Monta uma mensagem HTML com as informações extraídas.
Envia a mensagem para o Azure Service Bus para notificação.
Pré-requisitos
Dependências
Python 3.x
Pacotes Python:
azure-servicebus: Para interação com o Azure Service Bus.
selenium: Para automação de navegação web.
beautifulsoup4: Para manipulação de dados HTML.
webdriver-manager: Para gerenciar o WebDriver do Chrome.
Instalação dos pacotes
Execute o seguinte comando para instalar as dependências necessárias:

bash
Copiar código
pip install azure-servicebus selenium beautifulsoup4 webdriver-manager
Credenciais do Azure
Certifique-se de possuir as credenciais do Azure Service Bus, como CONNECTION_STR e QUEUE_NAME, para enviar as mensagens corretamente.

Como usar
Configuração da conexão com o Azure Service Bus:
Atualize a variável CONNECTION_STR com sua string de conexão do Azure Service Bus e QUEUE_NAME com o nome da fila que deseja utilizar.

Configuração dos destinatários:
Adicione o endereço de e-mail para onde deseja enviar a notificação, substituindo o valor da variável emails_destinatarios.

Execução do código: O código acessará o DJE, buscará por leilões e enviará os resultados via Service Bus. Basta executar o script em um ambiente Python com as dependências instaladas:

bash
Copiar código
python script.py
Fluxo do Script
Acessar o DJE: O Selenium é utilizado para acessar a página de consulta avançada e realizar uma busca por leilões.
Extração de dados: O BeautifulSoup, integrado ao Selenium, extrai as informações dos leilões listados na tabela de resultados.
Montagem da mensagem: Os dados extraídos são formatados em HTML.
Envio da mensagem: A mensagem HTML é enviada via Azure Service Bus para o e-mail especificado.
Notas
O script inclui funções de tratamento de erros para garantir que, caso ocorra algum erro durante a extração ou envio da mensagem, ele será exibido no console.
Caso queira ajustar o intervalo de tempo entre as etapas (carregamento da página, busca e extração), você pode modificar os valores dos comandos time.sleep() no código.
