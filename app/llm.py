# Communication avec Ollama

from abc import ABC, abstractmethod
import json
import urllib.request
import logging


logger = logging.getLogger("LLM")


class LLM(ABC):

    @abstractmethod
    def decide(
        self,
        messages: list[dict[str, str]],
        order_state: dict,
        expected_field: str | None = None,
    ) -> dict:
        raise NotImplementedError


class OllamaLLM(LLM):

    def __init__(
        self,
        model="qwen2.5:3b-instruct",
        base_url="http://localhost:11434",
    ):
        self.model = model
        self.url = f"{base_url.rstrip('/')}/api/chat"

    # =========================================================
    # Appel générique Ollama
    # =========================================================

    def _call_ollama(self, prompt: str) -> dict:

        logger.debug(
            "Prompt spécialisé envoyé à Ollama :\n%s",
            prompt,
        )

        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt,
                    }
                ],
                "format": "json",
                "stream": False,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            self.url,
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:

            raw_response = response.read().decode("utf-8")

        logger.debug(
            "Réponse brute Ollama : %s",
            raw_response,
        )

        result = json.loads(raw_response)

        content = result["message"]["content"]

        logger.debug(
            "Contenu retourné par Ollama : %s",
            content,
        )

        data = json.loads(content)

        logger.debug(
            "JSON spécialisé extrait : %s",
            data,
        )

        return data

    # =========================================================
    # Décision principale
    # =========================================================

    def decide(
        self,
        messages: list[dict[str, str]],
        order_state: dict,
        expected_field: str | None = None,
    ) -> dict:

        logger.debug(
            "État transmis au LLM : %s",
            order_state,
        )

        logger.debug(
            "Champ attendu : %s",
            expected_field,
        )

        # -----------------------------------------------------
        # Première passe : informations client
        # -----------------------------------------------------

        client_result = self._extract_customer_information(
            messages=messages,
            order_state=order_state,
            expected_field=expected_field,
        )

        # -----------------------------------------------------
        # Deuxième passe : produit
        # -----------------------------------------------------

        product_result = self._extract_product_information(
            messages=messages,
            order_state=order_state,
            expected_field=expected_field,
        )

        logger.debug(
            "Résultat extraction CLIENT : %s",
            client_result,
        )

        logger.debug(
            "Résultat extraction PRODUIT : %s",
            product_result,
        )

        # -----------------------------------------------------
        # Conversion en actions
        # -----------------------------------------------------

        actions = []

        if client_result.get("customer") is not None:

            actions.append(
                {
                    "action": "SET_CUSTOMER",
                    "customer": client_result["customer"],
                }
            )

        if client_result.get("email") is not None:

            actions.append(
                {
                    "action": "SET_EMAIL",
                    "email": client_result["email"],
                }
            )

        if product_result.get("product") is not None:

            product = product_result["product"]

            name = product.get("name")
            unit_price = product.get("unit_price")
            quantity = product.get("quantity")

            # On ne crée l'action que si le produit est complet.
            if (
                name is not None
                and unit_price is not None
                and quantity is not None
            ):

                actions.append(
                    {
                        "action": "ADD_PRODUCT",
                        "name": name,
                        "unit_price": unit_price,
                        "quantity": quantity,
                    }
                )

        logger.debug(
            "Actions construites après fusion : %s",
            actions,
        )

        result = {
            "actions": actions,
        }

        logger.debug(
            "Décision fusionnée : %s",
            result,
        )

        return result

    # =========================================================
    # Extraction client
    # =========================================================

    def _extract_customer_information(
        self,
        messages: list[dict[str, str]],
        order_state: dict,
        expected_field: str | None = None,
    ) -> dict:

        messages_json = json.dumps(
            messages,
            ensure_ascii=False,
            indent=2,
        )

        state_json = json.dumps(
            order_state,
            ensure_ascii=False,
            indent=2,
        )

        pending_context = ""

        if expected_field in {
            "customer",
            "email",
        }:

            pending_context = f"""

IMPORTANT :

L'assistant vient juste de demander une information correspondant
au champ "{expected_field}".

Le dernier message utilisateur est probablement une réponse
à cette question.

Analyse le dernier message utilisateur en priorité pour ce champ.

Si le dernier message répond à cette question, extrais uniquement
la valeur réellement fournie par l'utilisateur.
"""

        prompt = """
Tu es un extracteur d'informations CLIENT.

Tu dois analyser le DERNIER message de l'utilisateur.

ÉTAT ACTUEL :

""" + state_json + """

HISTORIQUE :

""" + messages_json + pending_context + """

Ta mission consiste UNIQUEMENT à extraire :

- customer : nom réellement fourni par l'utilisateur
- email : adresse email réellement fournie par l'utilisateur

RÈGLES ABSOLUES :

1. Analyse uniquement ce que l'utilisateur fournit réellement.
2. N'invente jamais un nom.
3. N'invente jamais une adresse email.
4. Ne copie jamais une valeur provenant d'un exemple.
5. Ne transforme pas "je", "moi", "bonjour", etc. en nom.
6. Une information absente doit être null.
7. Ne retourne jamais une valeur fictive comme :
   "Claude", "Lilian", "nom", "email@example.com",
   "unknown", "not_provided", etc.
8. Une information déjà connue dans l'état ne doit pas être
   recréée sauf si l'utilisateur la fournit explicitement
   dans son dernier message.
9. Si le dernier message ne contient aucune information client,
   retourne null pour customer et email.
10. Si le dernier message contient un nom et un email,
    retourne les deux.
11. Si le dernier message répond à la question précédente
    concernant le nom, utilise cette réponse comme customer.
12. Si le dernier message répond à la question précédente
    concernant l'email, utilise cette réponse comme email.
13. Ne t'occupe PAS des produits.
14. Ne crée aucune action.
15. Retourne uniquement du JSON valide.

FORMAT OBLIGATOIRE :

{
    "customer": null,
    "email": null
}
""".strip()

        return self._call_ollama(prompt)

    # =========================================================
    # Extraction produit
    # =========================================================

    def _extract_product_information(
        self,
        messages: list[dict[str, str]],
        order_state: dict,
        expected_field: str | None = None,
    ) -> dict:

        # ---------------------------------------------------------
        # On ne travaille que sur le dernier message utilisateur.
        # ---------------------------------------------------------

        last_user_message = None

        for message in reversed(messages):
            if message["role"] == "user":
                last_user_message = message["content"]
                break

        if not last_user_message:
            return {"product": None}

        logger.debug(
            "Dernier message utilisateur pour extraction produit : %r",
            last_user_message,
        )

        # ---------------------------------------------------------
        # Si on est en train de demander le nom ou l'email,
        # une réponse courte ne doit pas être transformée en produit.
        # ---------------------------------------------------------

        if expected_field in {"customer", "email"}:
            return {"product": None}

        # ---------------------------------------------------------
        # Prompt volontairement minimal.
        # ---------------------------------------------------------

        prompt = """
    Tu dois extraire un produit à partir d'une phrase utilisateur.

    DERNIER MESSAGE UTILISATEUR :
    """ + last_user_message + """

    Cherche ces 3 informations :

    - nom du produit
    - quantité
    - prix unitaire

    Exemples :

    "5 lampes à 10€ pièce"
    => produit = lampes
    => quantité = 5
    => prix = 10

    "je veux 3 ordinateurs à 800 euros"
    => produit = ordinateurs
    => quantité = 3
    => prix = 800

    "2 bureaux à 150 €"
    => produit = bureaux
    => quantité = 2
    => prix = 150

    Si les 3 informations sont présentes, retourne exactement :

    {
        "product": {
            "name": "lampes",
            "unit_price": 10,
            "quantity": 5
        }
    }

    Sinon retourne exactement :

    {
        "product": null
    }

    RÈGLES :

    - Lis uniquement le message utilisateur.
    - N'invente rien.
    - N'utilise aucune information absente du message.
    - Le prix est le prix unitaire.
    - La quantité est le nombre d'articles.
    - Retourne uniquement du JSON valide.
    """.strip()

        result = self._call_ollama(prompt)

        logger.debug(
            "Résultat extraction produit : %s",
            result,
        )

        return result