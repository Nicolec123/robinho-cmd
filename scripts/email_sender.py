import os
import base64
import requests
 
def obter_novo_token():
    """
    Obtém um novo token de autenticação com credenciais fixas.
    """
    url_auth = "https://notifications-api.mobileng.com.br/auth"  
    payload = {
        "username": "contato_sender",  
        "password": "Cont@to#Sender2025"  
    }
   
    try:
        response = requests.post(url_auth, json=payload)
        if response.ok:
            return response.json().get("token")  
        else:
            print("Erro ao obter novo token:", response.status_code, response.text)
            return None
    except Exception as e:
        print(f"Erro durante a obtenção do token: {e}")
        return None
 
 
def enviar_email_api(destinatario, assunto, mensagem, caminho_arquivo_pdf):
    """
    Envia um e-mail com o PDF em anexo utilizando a API da Mobileng.
    Obtém um novo token de autenticação antes de cada envio.
    """
    token = obter_novo_token()  # Gera um novo token para cada envio
 
    if not token:
        print("Erro: Não foi possível obter um token de autenticação.")
        return
 
    url = "https://notifications-api.mobileng.com.br/mail/send_email"
 
    # Lê o arquivo PDF e o codifica em base64 para envio
    try:
        with open(caminho_arquivo_pdf, "rb") as f:
            pdf_data = f.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo PDF: {e}")
        return
 
    pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
 
    # Monta o payload do e-mail
    data = {
        "from": {
            "email": "noreply@beneficiocerto.com.br",
            "name": "Alerta de Domínios!"
        },
        "subject": assunto,
        "body": {
            "content": mensagem,
            "is_html": False
        },
        "recipients": [
            {
                "email": destinatario,
                "name": destinatario  
            }
        ],
        "attachments": [
            {
                "filename": os.path.basename(caminho_arquivo_pdf),
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
 
 
# Enviar Email
if __name__ == "__main__":
    destinatario = "danielefloripa42@gmail.com"
    assunto = "Relatório de Domínios"
    mensagem = "Olá,\n\nSegue em anexo o relatório de domínios.\n\nAtenciosamente."
    caminho_arquivo_pdf = "relatorio_dominios.pdf"
 
    enviar_email_api(destinatario, assunto, mensagem, caminho_arquivo_pdf)
