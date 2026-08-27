from abc import ABC, abstractmethod
import json
import urllib.request
import logging

logger = logging.getLogger("LLM")

class LLM(ABC):
    @abstractmethod
    def extract_order(self, text: str) -> dict:
        raise NotImplementedError

class OllamaLLM(LLM):
    """Petit adaptateur synchrone vers Ollama (en local)."""

    
    def __init__(self, model="qwen2.5:3b-instruct", base_url="http://localhost:11434"):
        self.model = model
        self.url = f"{base_url.rstrip('/')}/api/chat"

    def extract_order(self, text: str) -> dict:
            logger.debug("Texte envoyé au LLM : %r", text)
                    
            prompt = f'''Tu extrais les informations d'une commande.
    
    Retourne UNIQUEMENT un objet JSON valide 
    
    Ne mets aucun texte avant ou après le JSON.
    
    Si une information n'est pas présente dans la demande, utilise la valeur "INCONNU" pour ne nom et "INCONNU@gmail.fr" pour l'email.
    
    Ne jamais inventer une information.

Format attendu ::
    {{
      "id": 1,
      "customer": "nom",
      "email": "email@example.com",
      "products": [
        {{
          "id": 1,
          "name": "produit",
          "unit_price": 1.0,
          "quantity": 1
        }}
      ]
    }}  

    Demande client :
    {text}'''.strip()
            
            logger.debug("Prompt envoyé à Ollama :\n%s", prompt)

            payload = json.dumps({
                "model": self.model,
                # prompt": prompt,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt,
                    }
                ],
                "format": "json",
                "stream": False,
            }).encode("utf-8")

            logger.debug("Appel Ollama avec le modèle %s", self.model)
            logger.debug("Texte utilisateur : %r", text)
    
            request = urllib.request.Request(
                self.url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=60) as response:
                # appel Ollama...
                raw_response = response.read().decode("utf-8")

            logger.debug("Réponse brute Ollama : %s", raw_response)
            result = json.loads(raw_response)
            logger.debug("Réponse JSON Ollama : %s", result)
            # /api/chat renvoie le texte dans message.content.
            content = result["message"]["content"]
            logger.debug("Contenu retourné par le LLM : %s", content)
            data = json.loads(content)
            logger.debug("JSON final extrait : %s", data)
            return data

            # avant mise en place des logs debug : version condensée
            with urllib.request.urlopen(request, timeout=60) as response:
                 result = json.loads(response.read().decode("utf-8"))
            # /api/chat renvoie le texte dans message.content.
            content = result["message"]["content"]
            return json.loads(content)
    
            # initialement
            # return json.loads(result["response"])
