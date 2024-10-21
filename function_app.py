import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

app = func.FunctionApp()

@app.schedule(schedule="0 0 6 * * 1-5", arg_name="myTimer", run_on_startup=True,
              use_monitor=False)
def timer_trigger(myTimer: func.TimerRequest) -> None:



    # Define os destinatários e a mensagem padrão
    emails_destinatarios = ['francieli.lima@acovisa.com.br', 'kaline.ferreira@acovisa.com.br']

    # Configuração inicial do Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Abrir a página da consulta avançada do DJE
    url = "https://dje.tjsp.jus.br/cdje/consultaAvancada.do"
    driver.get(url)

    # Esperar a página carregar
    time.sleep(5)

    # Rolar até a seção com a âncora #buscaavancada
    driver.execute_script("window.location.href='#buscaavancada';")

    # Esperar um pouco para garantir que a rolagem foi concluída
    time.sleep(2)

    # Selecionar o "Caderno 5 - Editais e Leilões" na seção de Consulta Avançada
    caderno_avancado_select = Select(driver.find_element(By.XPATH, "//select[@name='dadosConsulta.cdCaderno']"))
    caderno_avancado_select.select_by_visible_text("caderno 5 - Editais e Leilões")

    # Inserir a palavra-chave "leiloeiro" no campo de palavras-chave da consulta avançada
    campo_palavra_chave = driver.find_element(By.XPATH, "//input[@name='dadosConsulta.pesquisaLivre']")
    campo_palavra_chave.clear()
    campo_palavra_chave.send_keys("leiloeiro")

    # Clicar no botão "Pesquisar" na consulta avançada
    botao_pesquisar = driver.find_element(By.XPATH, "//input[@value='Pesquisar' and @type='submit']")
    botao_pesquisar.click()

    # Esperar os resultados carregarem
    time.sleep(5)

    # Extrair os links e informações dos resultados
    resultados = driver.find_elements(By.XPATH, "//table[@class='']/tbody/tr")

    # Criar uma lista para armazenar as informações extraídas
    informacoes_extracao = []

    # URL base do site
    url_base = "https://dje.tjsp.jus.br"

    # Iterar sobre os resultados encontrados
    for resultado in resultados:
        try:
            # Extrair o link do leilão
            link_elemento = resultado.find_element(By.XPATH, ".//a[contains(@title, 'Visualizar')]")
            link_onclick = link_elemento.get_attribute("onclick")

            # Extrair a URL real da função popup
            link_extrato = link_onclick.split("'")[1]  # Extrair o link da string do 'onclick'
            link_completo = url_base + link_extrato  # Formar a URL completa

            # Extrair o título (data, caderno, página)
            titulo = link_elemento.text.strip()

            # Guardar as informações extraídas
            informacoes_extracao.append({
                "link": link_completo,
                "titulo": titulo
            })
        except Exception as e:
            print(f"Erro ao extrair resultado: {e}")

    # Fechar o navegador
    driver.quit()



    # Exemplo de uso
    mensagem_leiloeiros_html = create_html_leiloes_simples(informacoes_extracao)

    # Preparar a mensagem em formato JSON para o Service Bus
    mensagem_json = {
        "email": emails_destinatarios[0],
        "message": mensagem_leiloeiros_html
    }

    # Converter para string JSON
    mensagem_string = json.dumps(mensagem_json, ensure_ascii=False).encode('utf-8')

    # Verificar o conteúdo da mensagem JSON antes de enviar
    print("Mensagem JSON sendo enviada para o Service Bus:", mensagem_string)



    # Chama a função para enviar a mensagem
    enviar_para_service_bus(mensagem_string)

    # Enviar a mensagem para o Service Bus
def enviar_para_service_bus(mensagem_string):
    CONNECTION_STR = os.getenv("CONNECTION_STR")
    QUEUE_NAME = os.getenv("QUEUE_NAME") if os.getenv("QUEUE_NAME") else "teams-tadeu"
    try:
        # Cria o client para se conectar ao Azure Service Bus
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
        with servicebus_client:
            # Enviar a mensagem para a queue do Service Bus
            sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
            with sender:
                # Criar a mensagem e enviá-la
                message = ServiceBusMessage(mensagem_string)

                # Adicionar impressão para verificar a mensagem que está sendo enviada
                print("Enviando a seguinte mensagem para o Service Bus:", mensagem_string)

                sender.send_messages(message)
                print("Mensagem enviada ao Service Bus com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Service Bus: {e}")

# Função para criar a mensagem em formato HTML para o Microsoft Teams
def create_html_leiloes_simples(informacoes_extracao):
    # Cabeçalho
    html = "<strong>🔔 Informações de Leilões do Dia 🔔</strong><br><br>"

    # Adicionar uma linha para cada leilão, com o título e o link na mesma linha
    for info in informacoes_extracao:
        titulo = info['titulo'].replace("\n", " ").strip()  # Remover quebras de linha e espaços extras
        link = info['link'].strip()  # Garantir que o link não tenha espaços em branco
        # Adicionar título e link com uma separação clara
        html += f"<strong>{titulo}</strong><br><a href='{link}'>Acessar Leilão</a><br><br>"

    return html.strip()