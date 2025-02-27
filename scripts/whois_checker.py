from datetime import datetime
import requests

def check_whois(dominio, data_expiracao):
    try:
        print(f"Consultando informações WHOIS para o domínio: {dominio}")

        url = f"https://rdap.registro.br/domain/{dominio}"
        response = requests.get(url)

        if response.status_code == 200:
            print("Requisição bem-sucedida. Processando dados...")
            data = response.json()

            expiration_event = next(
                (event for event in data.get("events", []) if event.get("eventAction", "").upper() == "EXPIRATION"),
                None
            )

            if not expiration_event:
                print(f"Erro: Não foi possível encontrar a data de expiração para {dominio}.")
                return False, None, None

            expiration_date_str = expiration_event.get("eventDate")
            if not expiration_date_str:
                print(f"Erro: A data de expiração está ausente para {dominio}.")
                return False, None, None

            # Converte a string ISO para um objeto datetime
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%dT%H:%M:%SZ")
            dias_restantes = (expiration_date - datetime.now()).days
            print(f"Dias restantes para expiração: {dias_restantes}")

            # Converte para o formato brasileiro (dd/mm/aaaa HH:MM:SS)
            expiration_date_br = expiration_date.strftime("%d/%m/%Y %H:%M:%S")

            return dias_restantes <= 30, dias_restantes, expiration_date_br
        else:
            print(f"Erro ao consultar domínio {dominio}: Código HTTP {response.status_code}")
            return False, None, None

    except Exception as e:
        print(f"Erro ao verificar domínio {dominio}: {e}")
        return False, None, None
