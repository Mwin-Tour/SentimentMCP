# tools/sentiment_tools.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:31b-cloud"  # Assurez-vous que ce modèle est disponible dans Ollama

def analyze_sentiment(text, prompt):
    """Analyse le sentiment avec Ollama"""
    try:
        payload = {
            "model": MODEL,
            "prompt": f"{prompt}\n\nTexte à analyser : {text}",
            "stream": False,  # IMPORTANT : stream=False
        }
        
        # AUGMENTEZ LE TIMEOUT à 120 secondes
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        else:
            return f"Erreur HTTP {response.status_code}: {response.text}"
        
    except requests.exceptions.Timeout:
        return " Timeout : Ollama ne répond pas. Vérifiez qu'il est démarré."
    except requests.exceptions.ConnectionError:
        return " Connexion impossible à Ollama. Lancez 'ollama serve' d'abord."
    except Exception as e:
        return f"Erreur : {str(e)}"