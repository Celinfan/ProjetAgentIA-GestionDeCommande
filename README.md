# ProjetAgentIA - GestionDeCommande

Petit projet de portfolio construit autour d'un cas métier volontairement simple : analyser une demande de commande et déterminer l'action à effectuer.

Le projet met volontairement en évidence la séparation entre interprétation par le LLM et logique métier déterministe.



```text
   HTTP POST /orders
       |
       | { "text": "Je veux 3 lampes à 10€ pièce" } 
       v  
+----------------------+ 
| OrderRequest         | 
| Pydantic             | 
|                      | 
| Validation de        | 
| la requête HTTP      |  
+----------------------+ 
       | 
       v  
+----------------------+ 
| OrderService         | 
|                      | 
| process_text()       | 
+----------------------+ 
        | 
        v 
+----------------------+ 
| LLM local            | 
| Ollama               | 
|                      |  
| Interprétation de la | 
| demande utilisateur  | 
+----------------------+ 
        | 
        | données structurées 
        v 
+----------------------+ 
| Order                | 
| Pydantic             | 
|                      | 
| Validation des       | 
| données extraites    | 
+----------------------+ 
        | 
        v 
+----------------------+ 
| Règles métier        | 
|                      | 
| total < 20 €         | 
| -> REJECT            | 
|                      | 
| 20 € <= total        | 
| <= 500 €             | 
| -> CONFIRM           | 
|                      | 
| total > 500 €        | 
| -> SUPPLIER          | 
+----------------------+ 
        | 
        v 
   Résultat    
```

### Principe architectural
Le LLM n'est pas responsable de la décision métier.

Son rôle est d'interpréter une demande en langage naturel et d'en extraire les informations nécessaires :

```text
"Je veux 3 lampes à 10€ pièce"
              |
              v
             LLM
              |
              v
{
  "products": [
    {
      "name": "lampe",
      "unit_price": 10,
      "quantity": 3
    }
  ]
}
```

Une fois les données extraites et validées, ce sont les règles Python qui déterminent l'action.

```text
LLM
 |
 | interprète
 v
Order
 |
 | décision déterministe
 v
Business Rules
 |
 +--> REJECT_ORDER
 |
 +--> SEND_CONFIRMATION_EMAIL
 |
 +--> SEND_SUPPLIER_EMAIL
```

Cette séparation permet de conserver une logique métier prévisible, testable et déterministe, tout en utilisant le LLM pour traiter le langage naturel.

## Technologies

- Python
- FastAPI
- Pydantic
- HTTP API locale d'Ollama
- pytest

## LLM choisi

La configuration utilise `qwen2.5:3b-instruct`, un petit modèle disponible via Ollama. Il est adapté au français et à la génération JSON structurée. Le modèle est exécuté localement : aucune clé API OpenAI n'est nécessaire.

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
