# ProjetAgentIA - GestionDeCommande

Petit projet de portfolio construit autour d'un cas métier volontairement simple : permettre à un utilisateur de passer une commande en langage naturel, tout en conservant une logique métier fiable et déterministe.

Le projet met en évidence la séparation entre :

* l'interprétation du langage naturel par le LLM ;
* la décision conversationnelle de l'agent ;
* l'état métier de la commande ;
* l'exécution des actions par des outils Python ;
* la validation et les règles métier déterministes.


```text
                     ┌──────────────────────┐
                     │      Frontend        │
                     │  interface chat      │
                     └──────────┬───────────┘
                                │
                                │ POST /orders
                                ▼
                     ┌──────────────────────┐
                     │    OrderService      │
                     │   orchestration      │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │      OrderAgent      │
                     │                      │
                     │ LLM + interprétation │
                     │ + décision d'action  │
                     └──────────┬───────────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
                   ▼            ▼            ▼
             SET_CUSTOMER   SET_EMAIL   ADD_PRODUCT
                   │            │            │
                   └────────────┼────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │    OrderTools        │
                     │  outils de commande  │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │     OrderState       │
                     │   état courant       │
                     │   de la commande     │
                     └──────────┬───────────┘
                                │
                         commande complète ?
                           ┌────┴────┐
                          non       oui
                           │         │
                           ▼         ▼
                    question à     Pydantic
                    l'utilisateur   Order
                                     │
                                     ▼
                              Business Rules
                                     │
                  ┌──────────────────┼──────────────────┐
                  ▼                  ▼                  ▼
           REJECT_ORDER   SEND_CONFIRMATION_EMAIL   SEND_SUPPLIER_EMAIL     
```

### Principe architectural
L'utilisateur dialogue avec un agent IA en langage naturel.

Le LLM ne modifie pas directement la commande et n'exécute aucune action sensible. Il analyse le message de l'utilisateur et propose une action parmi une liste fermée.

L'application conserve un état de commande indépendant du LLM, puis exécute l'action proposée par l'agent uniquement via des outils Python autorisés.

```text
Utilisateur
     |
     | "Je veux 5 lampes à 3 €"
     v
OrderService
     |
     v
OrderAgent
     |
     | interprétation du message
     | décision d'action
     v
ADD_PRODUCT
     |
     v
OrderTools
     |
     v
OrderState
     |
     +--> customer manquant
     |
     v
Agent / Service
     |
     v
"Quel est votre nom ?"

Lorsque l'utilisateur répond :

Utilisateur
     |
     | "Claude"
     v
OrderAgent
     |
     v
SET_CUSTOMER
     |
     v
OrderTools
     |
     v
OrderState
```

L'état de la commande est ainsi construit progressivement jusqu'à ce que toutes les informations nécessaires soient disponibles.

## Rôle du LLM
Le LLM est utilisé pour comprendre le langage naturel et déterminer l'action appropriée.

Par exemple :

"Finalement, mettez-en 10 au lieu de 5"

peut être interprété comme une modification de la quantité du produit déjà présent dans la commande.

Le LLM ne décide cependant pas des règles métier finales.

## Rôle de Python

Python conserve l'état fiable de la commande et contrôle l'exécution des actions.

Il est responsable notamment de :
* vérifier les informations obligatoires ;
* valider les données avec Pydantic ;
* calculer le total ;
* appliquer les règles métier ;
* déterminer l'action métier finale ;
* empêcher une action invalide ou incohérente.

## Flux général

```text
Frontend
   |
   v
POST /orders
   |
   v
OrderService
   |
   v
OrderAgent
   |
   | décision
   v
OrderTools
   |
   v
OrderState
   |
   | commande complète
   v
Validation Pydantic 
Order
   |
   v
Business Rules
   |
   +--> REJECT_ORDER
   |
   +--> SEND_CONFIRMATION_EMAIL
   |
   +--> SEND_SUPPLIER_EMAIL
```

Cette architecture permet d'utiliser l'IA là où elle apporte une réelle valeur : compréhension du langage naturel, gestion du dialogue et interprétation des demandes.

La logique métier et les opérations sensibles restent sous le contrôle du code Python, ce qui rend le comportement prévisible, testable et sécurisé.

## Évolutions possibles

Plusieurs évolutions sont envisageables :

* ajouter des outils supplémentaires comme la modification ou la suppression d'un produit ;
* permettre à l'agent de gérer les corrections et changements de commande ;
* ajouter une étape explicite de confirmation avant l'envoi de la commande ;
* remplacer le stockage de l'état en mémoire par une base de données ;
* ajouter un mécanisme de reprise ou de `manual_review` en cas de décision ambiguë ;
* remplacer le modèle local par un modèle plus performant selon les besoins.


## Technologies

* Python
* FastAPI
* Pydantic
* HTTP API locale d'Ollama
* pytest

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

Le LLM ne reçoit pas le droit d'exécuter directement une action.

Il propose une action parmi une liste fermée, par exemple :

{
  "action": "SET_CUSTOMER",
  "customer": "Claude"
}

ou :

{
  "action": "ADD_PRODUCT",
  "name": "lampes",
  "unit_price": 3,
  "quantity": 5
}

Le code Python valide ensuite cette décision et exécute uniquement les outils autorisés.

L'état de la commande reste indépendant du LLM. Ainsi, même si le modèle produit une réponse incorrecte, l'application conserve le contrôle sur les données et les règles métier.

En cas de décision absente, invalide ou de problème avec le LLM, l'application peut basculer vers une voie sûre telle que `manual_review` (pas encore réellement implémenté ici).
