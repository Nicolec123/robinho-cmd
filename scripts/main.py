import pandas as pd
from datetime import datetime
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Adiciona o diretório 'scripts' ao sys.path (se necessário)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from whois_checker import check_whois
from email_sender import enviar_email_api  # Importa a função de envio de e-mail

def gerar_relatorio_pdf(dominios_info):
    """
    Gera um relatório em PDF com as informações dos domínios.
    
    Args:
        dominios_info (list): Lista de dicionários contendo informações dos domínios.
    """
    nome_arquivo = "relatorio_dominios.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    largura, altura = letter

    # Título do relatório
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, altura - 50, "Relatório de Domínios")

    # Data e hora da geração
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.setFont("Helvetica", 10)
    c.drawString(100, altura - 70, f"Gerado em: {data_geracao}")

    # Posicionamento inicial dos dados
    y = altura - 100
    espacamento = 20  # Espaço entre as linhas
    margem_inferior = 50  # Margem para evitar corte

    for dominio_info in dominios_info:
        # Se a posição Y está próxima da margem, cria uma nova página
        if y < margem_inferior:
            c.showPage()  # Cria nova página
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, altura - 50, "Relatório de Domínios (continuação)")
            y = altura - 100  # Reseta a posição Y

        c.setFont("Helvetica", 12)
        c.drawString(100, y, f"Domínio: {dominio_info['dominio']}")
        y -= espacamento
        c.drawString(100, y, f"Expiração: {dominio_info['data_expiracao']}")
        y -= espacamento
        c.drawString(100, y, f"Status: {dominio_info['status']}")
        y -= espacamento
        c.drawString(100, y, f"Dias restantes: {dominio_info['dias_restantes']}")
        y -= espacamento * 2  # Espaço extra entre blocos de domínios

    c.save()
    print(f"\nRelatório gerado: {nome_arquivo}")
    return nome_arquivo  # Retorna o nome do arquivo para ser usado no envio do e-mail

def main():
    try:
        print("Iniciando o script...")

        # Carregar lista de domínios
        print("Carregando lista de domínios do arquivo 'data/dominios.csv'...")
        dominios_df = pd.read_csv(
            '../data/dominios.csv', header=None, names=["dominio", "data_expiracao"], dtype=str
        )

        if "dominio" not in dominios_df.columns or "data_expiracao" not in dominios_df.columns:
            raise ValueError("O arquivo 'dominios.csv' não contém as colunas esperadas.")

        print(f"Total de domínios carregados: {len(dominios_df)}")

        dominios_info = []

        for _, row in dominios_df.iterrows():
            dominio = row['dominio']
            data_expiracao_csv = row['data_expiracao']

            print(f"\nProcessando domínio: {dominio}")
            print(f"Data de expiração registrada (CSV): {data_expiracao_csv}")

            # Recebe status, dias restantes e a data de expiração obtida via API
            status_api, dias_restantes, expiration_date_api = check_whois(dominio, data_expiracao_csv)

            # Se a data da API estiver disponível, usamos; caso contrário, mantemos a do CSV
            data_expiracao = expiration_date_api if expiration_date_api else data_expiracao_csv

            # Definindo o valor numérico para ordenação
            if dias_restantes is None:
                dias_numericos = float('inf')
            else:
                dias_numericos = dias_restantes

            # Verifica se o domínio está "congelado" (dias restantes negativo)
            if dias_restantes is not None and dias_restantes < 0:
                status_text = "Congelado"
                dias_text = f"Expirado há {abs(dias_restantes)} dias"
            else:
                status_text = "Próximo de expirar" if status_api else "OK"
                dias_text = f"{dias_restantes} dias" if dias_restantes is not None else "Desconhecido"

            dominios_info.append({
                "dominio": dominio,
                "data_expiracao": data_expiracao,
                "status": status_text,
                "dias_restantes": dias_text,
                "dias_numericos": dias_numericos
            })

        # Ordena a lista de domínios com base na quantidade de dias (do menor para o maior)
        dominios_info.sort(key=lambda d: d["dias_numericos"])

        # Gera o PDF com a lista completa de domínios
        arquivo_pdf = gerar_relatorio_pdf(dominios_info)

        # Configura os parâmetros do e-mail
        destinatario = "tecnologia@beneficiocerto.com.br"  # E-mail de destino
        assunto = "Relatório de Domínios"
        mensagem = "Olá,\n\nSegue em anexo o relatório de domínios.\n\nAtenciosamente."

        # Validação: somente envia se houver algum domínio com dias_numericos < 30 e status "Próximo de expirar" sem isso ele envia semanalmente um email.
        notificacao = any(d["dias_numericos"] < 30 and d["status"] == "Próximo de expirar" for d in dominios_info)
        
        if notificacao:
            enviar_email_api(destinatario, assunto, mensagem, arquivo_pdf)
        else:
            print("Nenhum domínio com menos de 30 dias para expirar e com status 'Próximo de expirar'. E-mail não será enviado.")

    except FileNotFoundError:
        print("Erro: O arquivo 'data/dominios.csv' não foi encontrado.")
    except ValueError as e:
        print(f"Erro no formato do arquivo CSV: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
