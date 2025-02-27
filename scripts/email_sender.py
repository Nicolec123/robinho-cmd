import os
import base64
import requests
from dotenv import load_dotenv
load_dotenv()  # Isso carrega as variáveis do arquivo .env para o ambiente


def enviar_email_api(destinatario, assunto, mensagem, caminho_arquivo_pdf):
    """
    Envia um e-mail com o PDF em anexo utilizando a API da Mobileng.
    O token de autenticação é obtido a partir da variável de ambiente MOBILENG_TOKEN.
    
    Args:
        destinatario (str): E-mail do destinatário.
        assunto (str): Assunto do e-mail.
        mensagem (str): Corpo do e-mail.
        caminho_arquivo_pdf (str): Caminho para o arquivo PDF a ser anexado.
    """
    token = os.environ.get("MOBILENG_TOKEN")
    if not token:
        print("Erro: A variável de ambiente MOBILENG_TOKEN não está definida.")
        return

    url = "https://notifications-api.mobileng.com.br/mail/send_email" # API QUE MANDA O EMAIL

    # Lê o arquivo PDF e o codifica em base64 para envio
    try:
        with open(caminho_arquivo_pdf, "rb") as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo PDF: {e}")
        return

    pdf_b64 = base64.b64encode(pdf_data).decode('utf-8') # TIPO QUE A API DO EMIAL ACEITA

    # Monta o payload do e-mail, incluindo o anexo
    data = {
        "from": {
            "email": "noreply@beneficiocerto.com.br",
            "name": "Alerta de Dominios!"
        },
        "subject": assunto,
        "body": {
            "content": mensagem,
            "is_html": False
        },
        "recipients": [
            {
                "email": destinatario,# TÁ TUDO MAIS ABAIXO REFERENTE AS CONFIGURAÇÕES
                "name": destinatario  
            }
        ],
        "attachments": [
            {
             "filename": os.path.basename(caminho_arquivo_pdf), # essa parte é do pdf que é enviado por email, cuidado!
             "base64": pdf_b64  
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.ok:
            print("E-mail enviado com sucesso!")
        else:
            print("Erro ao enviar e-mail:", response.status_code, response.text)
    except Exception as e:
        print(f"Erro durante o envio do e-mail: {e}")

# Enviar Email(CONFIGURAÇÕES):
if __name__ == "__main__":
    destinatario = "tecnologia@beneficiocerto.com.br"  # E-mail de destino
    assunto = "Relatório de Domínios"
    mensagem = "Olá,\n\nSegue em anexo o relatório de domínios.\n\nAtenciosamente."
    caminho_arquivo_pdf = "relatorio_dominios.pdf"  # Caminho para o arquivo PDF gerado

    enviar_email_api(destinatario, assunto, mensagem, caminho_arquivo_pdf)
