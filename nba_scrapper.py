import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Get the current date
current_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

url = 'https://br.betano.com/sport/basquete/eua/nba/441g/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Obtenha o conteúdo HTML da página
response = requests.get(url, headers=headers)
html_content = response.content

# Crie um objeto BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Encontre o script que contém os dados JSON
script_tag = soup.find('script', {'type': 'application/ld+json'})
tag = soup.find('div', {'class': 'selections__selection__odd'})
#print(soup )
#Obtenha o conteúdo do script como uma string
script_content = script_tag.string

# Carregue os dados JSON
json_data = json.loads(script_content)

# Configurar o deslocamento de UTC-3
utc_offset = timedelta(hours=-5)

with open('/home/thor/nba/nbaprediction.json') as arquivo:
    dados_prediction = json.load(arquivo)

for event in json_data:
    name_event = event.get('name', {})
    get_date = event.get('startDate', {})
    get_url = event.get('url', {})
    event_date_utc = datetime.fromisoformat(get_date[:-1])

    for jogo in dados_prediction:
        nome_do_jogo = jogo["game"]["name"]
        game_id = jogo["game"]["game_id"]
        predicao_ambos = jogo['both_team_avarages']
        predicao_casa = jogo['home_team_avarages']
        predicao_fora = jogo['away_team_avarages']

        if nome_do_jogo == name_event:
            # Aplicar o deslocamento de UTC-3 manualmente
            event_date_etzone = event_date_utc + utc_offset
            print(f'{name_event} - {game_id}\n{event_date_etzone.strftime("%Y-%m-%dT%H:%M:%SET")},\t{get_url}')

            # Fazer uma solicitação para a URL e obter o conteúdo HTML
            get_url_equipes = get_url + "?bt=6"
            print(get_url_equipes)
            response_url = requests.get(get_url_equipes, headers=headers)
            html_content_url = response_url.content
            # Criar um objeto BeautifulSoup para a URL
            soup_url = BeautifulSoup(html_content_url, 'html.parser')
            script_tag = soup_url.find('script', string=lambda text: text and 'window["initial_state"]=' in text)

            # Verifica se a tag foi encontrada
            if script_tag:
                # Extrai o JSON da string do script
                script_text = script_tag.string
                json_start = script_text.find('{"data":')
                json_end = script_text.rfind('}') + 1
                json_data = script_text[json_start:json_end]
                # Carrega o JSON
                json_object = json.loads(json_data)
                fmarket = json_object['data']['event']['markets']
                for market in fmarket:
                    # Acesse a chave 'uniqueId' dentro de cada mercado
                    get_id_market = market.get('uniqueId')
                    get_name_market = market.get('name')
                    get_handcap = market.get('handicap')
                    if get_name_market in predicao_ambos:
                        # Obtém o valor correspondente ao nome do mercado no JSON
                        value = predicao_ambos[get_name_market]
                        if value > get_handcap + 1:  # Verifica se a previsão é 1 ou mais que o handicap
                            print(f'{get_name_market} | Handcap: {get_handcap} | Prediction: {value}')
                    if get_name_market in predicao_casa:
                        # Obtém o valor correspondente ao nome do mercado no JSON
                        value_casa = predicao_casa[get_name_market]
                        if value_casa > get_handcap + 1:  # Verifica se a previsão é 1 ou mais que o handicap
                            print(f'{get_name_market} | Handcap: {get_handcap} | Prediction: {value_casa}')

                    if get_name_market in predicao_fora:
                        # Obtém o valor correspondente ao nome do mercado no JSON
                        value_fora = predicao_fora[get_name_market]
                        if value_fora > get_handcap + 1:  # Verifica se a previsão é 1 ou mais que o handicap
                            print(f'{get_name_market} | Handcap: {get_handcap} | Prediction: {value_fora}')
            
            else:
                print("Tag não encontrada.")
            print('*' * 100)
            print("\n")
            break
