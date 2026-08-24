# ProjetAgentIA-GestionDeCommande

Petit projet de portfolio construit autour d'un cas métier volontairement simple : analyser une commande et choisir une action.

```text
HTTP /orders
    |
    v
  Order (validation Pydantic)
    |
    v
 OrderService
    |
    +--> LLM local (Ollama)
    |
    v
 décision contrôlée
    |
    +--> REJECT
    +--> SEND_EMAIL
    +--> SEND_TO_SUPPLIER
    +--> manual_review si problème
```

## Technologies

- Python
- FastAPI
- Pydantic
- HTTP API locale d'Ollama
- pytest

## LLM choisi

La configuration utilise `qwen2.5:3b-instruct`, un petit modèle disponible via Ollama. 
Il est adapté au français et à la génération JSON structurée. 
Le modèle est exécuté localement : aucune clé API OpenAI n'est nécessaire.

## Installation Windows

Installer Ollama puis :

```powershell
ollama pull qwen2.5:3b-instruct
```

Créer l'environnement Python :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Tester :

```powershell
python -m pytest
uvicorn app.main:app --reload
```

Documentation API : `http://127.0.0.1:8000/docs`

## Point important sur l'IA

Le LLM ne reçoit pas le droit d'exécuter directement une action. Il propose une décision parmi une liste fermée, puis le service métier vérifie la décision et applique une voie sûre (`manual_review`) si la réponse est absente, invalide ou si le LLM est indisponible.
