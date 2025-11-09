#!/usr/bin/env python3
import requests

# =============================================================================
# CONFIGURACIÓ DEL CHATBOT
# =============================================================================

API_KEY = "REDACTED_HISTORICAL_PUBLICAI_CREDENTIAL"  # La teva clau
API_URL = "https://api.publicai.co/v1/chat/completions"

# Tria el model que vols utilitzar
# MODEL = "BSC-LT/ALIA-40b-instruct_Q8_0"
MODEL = "BSC-LT/salamandra-7b-instruct-tools-16k" # (Opció més ràpida)

# Personalitza el comportament del chatbot
SYSTEM_PROMPT = "Ets un analista expert en estratègia financera i expansió de mercat, especialitzat en el territori català. " \
"Actues com a consultor principal per a Caixa Enginyers. La teva missió és analitzar dades demogràfiques, econòmiques i de competència bancària per identificar oportunitats de creixement. " \
"Proporciona respostes precises, basades en dades i orientades a la presa de decisions estratègiques, com l'obertura de noves oficines o l'adaptació de serveis a mercats locals. " \
"El teu to ha de ser professional i analític."


# =============================================================================
# FUNCIÓ PRINCIPAL
# =============================================================================

def preguntar_chatbot(historial_missatges, temperatura=0.7, max_tokens=1000):
    """
    Envia l'historial complet de missatges a l'API.
    L'historial JA ha d'incloure el system prompt i el nou missatge de l'usuari.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "UAB-THE-HACK/1.0"
    }

    payload = {
        "model": MODEL,
        "messages": historial_missatges,
        "max_tokens": max_tokens,
        "temperature": temperatura
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "❌ Error: API key invàlida. Verifica la teva configuració."
        elif response.status_code == 429:
            return "⚠️ Massa peticions. Espera uns segons i torna a intentar-ho."
        else:
            return f"❌ Error {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return "⏱️ Timeout: El model està trigant massa. Torna a intentar-ho."
    except Exception as e:
        return f"❌ Error: {str(e)}"