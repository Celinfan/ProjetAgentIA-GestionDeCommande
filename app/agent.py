# Raisonnement / décision de l'agent

import logging


logger = logging.getLogger("Agent")


class OrderAgent:

    def __init__(
        self,
        llm,
        tools,
    ):
        self.llm = llm
        self.tools = tools

    def run(
        self,
        conversation_id: str,
        messages: list[dict[str, str]],
        expected_field: str | None = None,
    ) -> dict:

        state = self.tools.get_order_state(
            conversation_id
        )

        logger.debug(
            "État actuel de la commande : %s",
            state,
        )

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

        logger.debug(
            "Décision brute de l'agent : %s",
            decision,
        )

        # ---------------------------------------------------------
        # Normalisation
        # ---------------------------------------------------------

        actions = self.normalize_actions(
            decision
        )

        # ---------------------------------------------------------
        # Validation des actions
        # ---------------------------------------------------------

        actions = self.validate_actions(
            actions
        )

        # ---------------------------------------------------------
        # Suppression des doublons
        # ---------------------------------------------------------

        actions = self.deduplicate_actions(
            actions
        )

        logger.debug(
            "Actions finales de l'agent : %s",
            actions,
        )

        # ---------------------------------------------------------
        # Garde-fou pour les réponses aux questions
        # ---------------------------------------------------------

        if expected_field == "email":

            has_email = any(
                action.get("action") == "SET_EMAIL"
                for action in actions
            )

            if not has_email:

                raise ValueError(
                    "Le LLM n'a pas correctement interprété "
                    "la réponse attendue comme email."
                )

        elif expected_field == "customer":

            has_customer = any(
                action.get("action") == "SET_CUSTOMER"
                for action in actions
            )

            if not has_customer:

                raise ValueError(
                    "Le LLM n'a pas correctement interprété "
                    "la réponse attendue comme nom."
                )

        # ---------------------------------------------------------
        # Exécution des outils
        # ---------------------------------------------------------

        return self.execute_decisions(
            conversation_id,
            actions,
        )

    # =============================================================
    # Normalisation
    # =============================================================

    @staticmethod
    def normalize_actions(
        decision: dict,
    ) -> list[dict]:

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
            "La décision du LLM ne contient ni "
            "'actions' ni 'action'."
        )

    # =============================================================
    # Validation
    # =============================================================

    @staticmethod
    def validate_actions(
        actions: list[dict],
    ) -> list[dict]:

        allowed_actions = {
            "SET_CUSTOMER",
            "SET_EMAIL",
            "ADD_PRODUCT",
        }

        validated = []

        for action in actions:

            if not isinstance(action, dict):

                raise ValueError(
                    "Une action de l'agent n'est pas un objet JSON."
                )

            action_type = action.get("action")

            if action_type not in allowed_actions:

                raise ValueError(
                    f"Action de l'agent invalide : {action_type}"
                )

            if action_type == "SET_CUSTOMER":

                customer = action.get("customer")

                if not customer:

                    raise ValueError(
                        "SET_CUSTOMER sans nom fourni."
                    )

            elif action_type == "SET_EMAIL":

                email = action.get("email")

                if not email:

                    raise ValueError(
                        "SET_EMAIL sans email fourni."
                    )

            elif action_type == "ADD_PRODUCT":

                name = action.get("name")
                unit_price = action.get("unit_price")
                quantity = action.get("quantity")

                if not name:

                    raise ValueError(
                        "ADD_PRODUCT sans nom de produit."
                    )

                if unit_price is None:

                    raise ValueError(
                        "ADD_PRODUCT sans prix unitaire."
                    )

                if quantity is None:

                    raise ValueError(
                        "ADD_PRODUCT sans quantité."
                    )

            validated.append(action)

        return validated

    # =============================================================
    # Déduplication
    # =============================================================

    @staticmethod
    def deduplicate_actions(
        actions: list[dict],
    ) -> list[dict]:

        unique_actions = []
        seen = set()

        for action in actions:

            action_type = action.get("action")

            if action_type == "SET_CUSTOMER":

                key = (
                    "SET_CUSTOMER",
                    action.get("customer"),
                )

            elif action_type == "SET_EMAIL":

                key = (
                    "SET_EMAIL",
                    action.get("email"),
                )

            elif action_type == "ADD_PRODUCT":

                key = (
                    "ADD_PRODUCT",
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

    # =============================================================
    # Exécution
    # =============================================================

    def execute_decisions(
        self,
        conversation_id: str,
        actions: list[dict],
    ) -> dict:

        results = []

        for action in actions:

            result = self.execute_decision(
                conversation_id,
                action,
            )

            results.append(result)

        return {
            "success": True,
            "actions": results,
        }

    # =============================================================
    # Une action
    # =============================================================

    def execute_decision(
        self,
        conversation_id: str,
        decision: dict,
    ) -> dict:

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