import requests
import pandas as pd
import time
import os
from datetime import datetime

# ================= CONFIG =================

GOOGLE_API_KEY = "AIzaSyDacHZaAwAJxRLlw433toGMptPL_Vo1ASs"

CIDADES = [
    "Votorantim, SP",
    "Sorocaba, SP",
]

TERMOS_BUSCA = [
    "clínica estética",
    "clínica de estética",
    "estética facial",
    "estética corporal",
]

ARQUIVO_SAIDA = f"leads_clinicas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

# ==========================================

def buscar_lugares(query):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    resultados = []
    next_page_token = None

    while True:
        params = {
            "query": query,
            "key": GOOGLE_API_KEY,
            "language": "pt-BR",
        }

        if next_page_token:
            params["pagetoken"] = next_page_token
            time.sleep(2)

        resp = requests.get(url, params=params).json()
        resultados.extend(resp.get("results", []))

        next_page_token = resp.get("next_page_token")
        if not next_page_token:
            break

    return resultados


def buscar_detalhes(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,international_phone_number,website,formatted_address",
        "key": GOOGLE_API_KEY,
    }

    resp = requests.get(url, params=params).json()

    return resp.get("result", {})


def formatar_whatsapp(telefone):
    if not telefone:
        return ""

    digitos = "".join(filter(str.isdigit, telefone))

    if digitos.startswith("55"):
        return digitos
    elif len(digitos) >= 10:
        return "55" + digitos

    return digitos


def main():
    leads = {}

    for cidade in CIDADES:
        for termo in TERMOS_BUSCA:
            query = f"{termo} em {cidade}"
            print(f"\n🔍 Buscando: {query}")

            lugares = buscar_lugares(query)

            for lugar in lugares:
                place_id = lugar.get("place_id")

                if not place_id or place_id in leads:
                    continue

                detalhes = buscar_detalhes(place_id)
                time.sleep(0.1)

                if detalhes.get("website"):
                    continue

                telefone = detalhes.get("international_phone_number") or detalhes.get("formatted_phone_number")

                whatsapp = formatar_whatsapp(telefone)

                leads[place_id] = {
                    "Nome": detalhes.get("name"),
                    "Telefone": telefone,
                    "WhatsApp": whatsapp,
                    "Cidade": cidade,
                    "Endereço": detalhes.get("formatted_address"),
                }

                print(f"✅ {detalhes.get('name')}")

    df = pd.DataFrame(list(leads.values()))
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")

    print(f"\n📁 Salvo: {ARQUIVO_SAIDA}")
    print(f"📊 Total: {len(df)} leads")


if __name__ == "__main__":
    main()