# server.py - Version corrigée
import sys
import json
import os
from mcp.server.fastmcp import FastMCP

# === Chemins absolus ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMENTS_FILE = os.path.join(BASE_DIR, "ressources", "commentaires_plat.json")
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "sentiment.txt")

mcp = FastMCP("Sentiment Server")

# 1. Resource - commentaires
@mcp.resource("comments://all")
def get_comments():
    try:
        if not os.path.exists(COMMENTS_FILE):
            return json.dumps({"error": f"Fichier non trouvé: {COMMENTS_FILE}"})
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            return json.dumps(json.load(f), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

# 2. Prompt - règles
@mcp.prompt("sentiment_rules")
def get_rules():
    try:
        if not os.path.exists(PROMPT_FILE):
            return "Règles par défaut: Analyse le sentiment (positif/négatif/neutre)."
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erreur: {str(e)}"

# 3. Tool - analyse d'un commentaire
@mcp.tool()
def analyze_sentiment_tool(comment: str):
    """Analyse le sentiment d'un commentaire en utilisant les règles du fichier sentiment.txt"""
    try:
        if not os.path.exists(PROMPT_FILE):
            return "Fichier sentiment.txt non trouvé"
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_rules = f.read()
        try:
            # Import correct : BASE_DIR est déjà dans le path
            sys.path.insert(0, BASE_DIR)
            from tools.sentiment_tools import analyze_sentiment
            result = analyze_sentiment(comment, prompt_rules)
            return f"Analyse avec nos règles :\n\n{result}"
        except ImportError as ie:
            return f"Module sentiment_tools non disponible : {str(ie)}"
    except Exception as e:
        return f"Erreur : {str(e)}"

# 4. Tool de test
@mcp.tool()
def tester_serveur():
    """Teste si le serveur fonctionne"""
    return "Serveur Sentiment opérationnel"

# 5. Tool - Analyse globale
@mcp.tool()
def analyze_all_comments():
    """Analyse le sentiment de tous les commentaires"""
    try:
        if not os.path.exists(COMMENTS_FILE):
            return "Aucun fichier de commentaires trouvé."
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            comments_data = json.load(f)
        results = []
        for comment in comments_data:
            text = comment.get("Commentaires", "")
            comment_id = comment.get("commentaire_id", "?")
            auteur = comment.get("Auteur", "Inconnu")
            if text:
                # CORRECTION: analyze_sentiment_tool ne prend qu'un seul argument
                analysis = analyze_sentiment_tool(text)
                results.append(f"[{comment_id}] {auteur}: {analysis[:120]}")
        return f"Analyse de {len(results)} commentaires :\n" + "\n".join(results)
    except Exception as e:
        return f"Erreur : {str(e)}"

def main():
    print("Démarrage du serveur Sentiment MCP...", file=sys.stderr)
    print(f"Répertoire: {BASE_DIR}", file=sys.stderr)
    print(f"Fichier commentaires: {COMMENTS_FILE}", file=sys.stderr)
    print(f"Fichier prompt: {PROMPT_FILE}", file=sys.stderr)
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Arrêt du serveur", file=sys.stderr)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()