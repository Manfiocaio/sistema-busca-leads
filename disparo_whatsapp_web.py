import pandas as pd
import webbrowser
import time
import glob
import os

# ================= CONFIG =================

MENSAGEM_TEMPLATE = """Olá, tudo bem? 😊

Vi que a *{nome}* ainda não possui um site.

Hoje, muitos clientes pesquisam no Google antes de escolher uma clínica, e um site profissional pode aumentar bastante seus agendamentos.

Posso te mostrar um exemplo rápido sem compromisso?"""

INTERVALO = 20

# ==========================================

def carregar_csv():
    arquivos = glob.glob("leads_clinicas_*.csv")

    if not arquivos:
        raise FileNotFoundError("Nenhum CSV encontrado.")

    mais_recente = max(arquivos, key=os.path.getmtime)
    print(f"📂 Usando: {mais_recente}")

    return pd.read_csv(mais_recente)


def main():
    df = carregar_csv()

    df = df[df["WhatsApp"].notna() & (df["WhatsApp"] != "")]

    print(f"\n📊 Leads com WhatsApp: {len(df)}\n")

    for _, row in df.iterrows():
        nome = row["Nome"]
        numero = str(row["WhatsApp"])

        mensagem = MENSAGEM_TEMPLATE.format(nome=nome)

        mensagem_url = mensagem.replace("\n", "%0A").replace(" ", "%20")

        link = f"https://wa.me/{numero}?text={mensagem_url}"

        print(f"📤 Abrindo: {nome}")

        webbrowser.open(link)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()