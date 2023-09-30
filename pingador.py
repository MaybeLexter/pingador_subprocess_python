import subprocess
import time
import PySimpleGUI as sg
import requests
from datetime import datetime
from pytz import timezone
import threading
import re
from unidecode import unidecode
import unicodedata

def data_horario_atual_log():
        data_e_hora_atuais = datetime.now()
        fuso_horario = timezone("America/Manaus")
        data_e_hora_mt = data_e_hora_atuais.astimezone(fuso_horario)
        data_e_hora_mt_em_texto = data_e_hora_mt.strftime("%d/%m/%Y %H:%M")
        return(data_e_hora_mt_em_texto)

def token_api(token):
        try:
            url = "https://api.telegram.org/bot{}/getUpdates".format(token)
            response = requests.get(url)
            if response.status_code == 200:
                json_msg = response.json()
                for json_result in reversed(json_msg['result']):
                    message_keys = json_result['message'].keys()
                    if ('new_chat_member' in message_keys) or ('group_chat_created' in message_keys):
                        return json_result['message']['chat']['id']
                print('Nenhum grupo encontrado')
            else:
                print('A resposta falhou, código de status: {}'.format(response.status_code))
        except Exception as e:
            print("Erro no getUpdates:", e)

def enviar_mensagem(mensagem_enviada,conteudo_mensagem):
        chat_id = '-4036229008'
        token = '6636139178:AAHzbYli07ln7BAgW4WA_85O4Z8-90zwHVU'
        if mensagem_enviada == True:
            msg = f'{conteudo_mensagem} \n log:{str(data_horario_atual_log())}'
            try:
                data = {"chat_id": chat_id, "text": msg}
                url = "https://api.telegram.org/bot{}/sendMessage".format(token)
                requests.post(url, data)
            except Exception as e:
                print("Erro no sendMessage:", e)
def substituir_palavras(string):
    substituicoes = {
    ""
    "n£mero": "número",
    "M ximo": "Máximo",
    "M‚dia": "Média",
    "M¡nimo": "Mínimo",
    "Estat¡sticas" : "Estatísticas"
    }
    for palavra, substituicao in substituicoes.items():
        string = string.replace(palavra, substituicao)
    return string

def ping_e_atualizar_janela(ip, numero_maximo_pings, window):
    global cancelar_ping  
    cancelar_ping = False
    window['Pingar'].update(disabled=True)
    linhas_acumuladas = []

    try:
            if numero_maximo_pings != '0':
                comando_ping = f"ping {ip} -n {numero_maximo_pings}"
                processo = subprocess.Popen(comando_ping, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
            elif numero_maximo_pings == '0':
                comando_ping = f"ping {ip} -t"
                processo = subprocess.Popen(comando_ping, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
    except subprocess.CalledProcessError as Erro:
            enviar_mensagem(token, chat_id, msg)

    while True:
        if cancelar_ping:
            processo.terminate()
            break
        linha = processo.stdout.readline()
        if not linha:
            break
        
        linhas_acumuladas.append(linha.strip())
        sem_acento = [substituir_palavras(string) for string in linhas_acumuladas]
        window['-output-'].update('\n'.join(sem_acento))
    achar_palavra(sem_acento,False)
    processo.wait()
    window['Pingar'].update(disabled=False)   
def achar_palavra(sem_acento,cancelou):
    sem_acento = sem_acento
    mensagem_teste = '\n'.join(sem_acento)
    padrao = r'Estatísticas do Ping para [\d.]+:\n(.+)$'
    match = re.search(padrao, mensagem_teste, re.DOTALL)

    if match and cancelou == False:
        parte_desejada = match.group(0).strip()
        enviar_mensagem(True, parte_desejada)   

    




layout = [
        [sg.Text("Bem-vindo! Qual seria o IP que você deseja pingar?",background_color='Black')],
        [sg.Input(key='-ip-', default_text='8.8.8.8', enable_events=True,size=60)],
        [sg.Text("E o intervalo?",background_color='Black')],
        [sg.Input(key='-intervalo-', default_text='2',size=60)],
        [sg.Text("Quantas vezes? OBS: Se for continuamente é só colocar 0",background_color='Black')],
        [sg.Input(key='-numerodepings-', default_text='5',size=60)],
        [sg.Button('Pingar'), sg.Button('Cancelar'),sg.Button('Sair')],
        [sg.Output(key='-output-', size=(60, 10))],
    ]
sg.theme('Black')

window = sg.Window('Pingador Por Telegram', layout)

while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Sair':
            break
        if event == 'Cancelar':
            cancelar_ping = True
            
        if event == 'Pingar':
            cancelar_ping = False  
            ip_alvo = values['-ip-']
            intervalo_entre_pings = values['-intervalo-']
            numero_de_pings = values['-numerodepings-']        
           
            threading.Thread(target=ping_e_atualizar_janela, args=(ip_alvo, numero_de_pings, window)).start()
            

window.close()