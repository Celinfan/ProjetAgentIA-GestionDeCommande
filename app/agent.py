import logging

logger = logging.getLogger(__name__)

class OrderAgent:
    """Agent chargé de transformer une décision LLM en actions métier."""

    ALLOWED_ACTIONS = {
        "SET_CUSTOMER",
        "SET_EMAIL",
        "ADD_PRODUCT",
    }

    def __init__(self, llm, tools) -> None:
        self.llm = llm
        self.tools = tools

    def run(
        self,
        conversation_id: str,
        messages: list[dict[str, str]],
        expected_field: str | None = None,
    ) -> dict:
        """Analyse une conversation et exécute les actions résultantes."""
        state = self.tools.get_order_state(conversation_id)

        logger.debug("État actuel de la commande : %s", state)
        logger.debug(
            "Champ attendu suite à la question précédente : %s",
            expected_field,
        )

        # ---------------------------------------------------------
        # Le LLM analyse le message.
        # Il peut produire une ou plusieurs actions.
        # ---------------------------------------------------------
        decision = self.llm.decide(
            messages=messages,
            order_state=state,
            expected_field=expected_field,
        )

        logger.debug("Décision brute de l'agent : %s", decision)

        # Normalisation
        actions = self.normalize_actions(decision)
        # Validation des actions
        actions = self.validate_actions(actions)
        # Suppression des doublons
        actions = self.deduplicate_actions(actions)

        logger.debug("Actions finales de l'agent : %s", actions)

        # Garde-fou pour les réponses aux questions
        self._validate_expected_field(expected_field, actions)
        # Exécution des outils
        return self.execute_decisions(conversation_id, actions)


    @staticmethod
    def normalize_actions(decision: dict) -> list[dict]:
        """Normalise les anciens et nouveaux formats d'actions."""

        if not isinstance(decision, dict):
            raise ValueError(
                "La décision de l'agent n'est pas un objet JSON."
            )

        # Nouveau format
        if "actions" in decision:
            actions = decision["actions"]

            if not isinstance(actions, list):

                raise ValueError(
                    "Le champ 'actions' doit être une liste."
                )

            return actions

        # Compatibilité ancien format
        if "action" in decision:
            return [decision]

        raise ValueError(
            "La décision du LLM ne contient ni 'actions' ni 'action'."
        )


    @classmethod
    def validate_actions(cls, actions: list[dict]) -> list[dict]:
        """Valide les actions produites par le LLM."""

        validated = []

        for action in actions:
            if not isinstance(action, dict):
                raise ValueError(
                    "Une action de l'agent n'est pas un objet JSON."
                )

            action_type = action.get("action")

            if action_type not in cls.ALLOWED_ACTIONS:

                raise ValueError(
                    f"Action de l'agent invalide : {action_type}"
                )
            cls._validate_action(action)

            validated.append(action)

        return validated

    @staticmethod
    def _validate_action(action : dict) -> None:
        """Valide les données associées à une action."""
        action_type = action["action"]
    
        if action_type == "SET_CUSTOMER":
            if not action.get("customer"):
                raise ValueError(
                    "SET_CUSTOMER sans nom fourni."
                )
            return
    
        elif action_type == "SET_EMAIL":
            if not action.get("email"):
                raise ValueError(
                    "SET_EMAIL sans email fourni."
                )
    
        elif action_type == "ADD_PRODUCT":  
            if not action.get("name"):
                raise ValueError(
                    "ADD_PRODUCT sans nom de produit."
                )
    
            if action.get("unit_price") is None:
                raise ValueError(
                    "ADD_PRODUCT sans prix unitaire."
               )
    
            if action.get("quantity") is None:
                raise ValueError(
                    "ADD_PRODUCT sans quantité."
                )
            
    @staticmethod
    def _validate_expected_field(
        expected_field: str | None,
        actions: list[dict],
    ) -> None:
        """Vérifie la réponse à une question précédente."""        
        expected_actions = {
            "email": "SET_EMAIL",
            "customer": "SET_CUSTOMER",
        }

        expected_action = expected_actions.get(expected_field)

        if expected_action is None:
            return

        if not any(
            action.get("action") == expected_action
            for action in actions
        ):
            raise ValueError(
                f"Le LLM n'a pas correctement interprété "
                f"la réponse attendue comme {expected_field}."
            )


    @staticmethod
    def deduplicate_actions(actions: list[dict]) -> list[dict]:
        """Supprime les actions strictement identiques."""

        unique_actions = []
        seen = set()

        for action in actions:
            action_type = action.get("action")

            if action_type == "SET_CUSTOMER":
                key = (
                    action_type,
                    action.get("customer"),
                )
            elif action_type == "SET_EMAIL":
                key = (
                    action_type,
                    action.get("email"),
                )
            elif action_type == "ADD_PRODUCT":
                key = (
                    action_type,
                    action.get("name"),
                    action.get("unit_price"),
                    action.get("quantity"),
                )
            else:
                key = (
                    action_type,
                    str(action),
                )

            if key in seen:
                continue

            seen.add(key)
            unique_actions.append(action)

        return unique_actions

    def execute_decisions(
        self,
        conversation_id: str,
        actions: list[dict],
    ) -> dict:
        """Exécute toutes les actions validées."""

        results = [
            self.execute_decision(conversation_id,action)
            for action in actions

        ]

        return {
            "success": True,
            "actions": results,
        }


    def execute_decision(
        self,
        conversation_id: str,
        decision: dict,
    ) -> dict:
        """Exécute une action métier."""

        action = decision.get("action")

        if action == "SET_CUSTOMER":
            return self.tools.set_customer(
                conversation_id,
                decision["customer"],
            )

        if action == "SET_EMAIL":
            return self.tools.set_email(
                conversation_id,
                decision["email"],
            )

        if action == "ADD_PRODUCT":
            return self.tools.add_product(
                conversation_id,
                decision["name"],
                decision["unit_price"],
                decision["quantity"],
            )

        raise ValueError(
            f"Action de l'agent inconnue : {action}"
        )