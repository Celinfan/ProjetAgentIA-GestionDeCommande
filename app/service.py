# Orchestration HTTP / conversation

import logging

from app.conversation import ConversationMemory
from app.order_state import OrderStateManager
from app.order_tools import OrderTools
from app.agent import OrderAgent
from app.models import Order


logger = logging.getLogger("Service")


class OrderService:

    MINIMUM_AMOUNT = 20.0
    SUPPLIER_THRESHOLD = 500.0

    def __init__(
        self,
        llm,
        memory: ConversationMemory,
    ):

        self.memory = memory

        self.state_manager = OrderStateManager()

        self.tools = OrderTools(
            self.state_manager
        )

        self.agent = OrderAgent(
            llm,
            self.tools
        )

    def process_message(
        self,
        text: str,
        conversation_id: str | None = None,
    ) -> dict:

        # ---------------------------------------------------------
        # 1. Créer une conversation si nécessaire
        # ---------------------------------------------------------

        if conversation_id is None:

            conversation_id = self.memory.create()

            self.state_manager.create(
                conversation_id
            )

        # ---------------------------------------------------------
        # 2. Ajouter le message utilisateur
        # ---------------------------------------------------------

        self.memory.add_message(
            conversation_id,
            "user",
            text,
        )

        # ---------------------------------------------------------
        # 3. Récupérer l'historique
        # ---------------------------------------------------------

        messages = self.memory.get(
            conversation_id
        )

        logger.debug(
            "Historique conversation : %s",
            messages,
        )

        # ---------------------------------------------------------
        # 4. Déterminer si l'assistant vient de poser une question
        # ---------------------------------------------------------

        pending_field = self.get_pending_field(
            conversation_id
        )

        logger.debug(
            "Champ demandé par le dernier message assistant : %s",
            pending_field,
        )

        # ---------------------------------------------------------
        # 5. Agent
        # ---------------------------------------------------------

        agent_result = self.agent.run(
            conversation_id,
            messages,
            pending_field,
        )

        logger.debug(
            "Résultat agent : %s",
            agent_result,
        )

        # ---------------------------------------------------------
        # 6. Récupérer l'état après exécution des outils
        # ---------------------------------------------------------

        state = self.state_manager.get_state(
            conversation_id
        )

        logger.debug(
            "Nouvel état : %s",
            state,
        )

        # ---------------------------------------------------------
        # 7. Commande incomplète
        # ---------------------------------------------------------

        if not self.state_manager.is_complete(
            conversation_id
        ):

            return self.ask_next_information(
                conversation_id
            )

        # ---------------------------------------------------------
        # 8. Commande complète
        # ---------------------------------------------------------

        order_data = {
            # TODO : remplacer par l'ID généré par la persistance
            "id": 1,

            "customer": state.customer,

            "email": state.email,

            "products": [
                {
                    "id": index,
                    **product.model_dump(),
                }
                for index, product in enumerate(
                    state.products,
                    start=1,
                )
            ],
        }

        logger.debug(
            "Commande avant validation : %s",
            order_data,
        )

        # ---------------------------------------------------------
        # 9. Validation Pydantic
        # ---------------------------------------------------------

        order = Order.model_validate(
            order_data
        )

        logger.debug(
            "Commande validée : %s",
            order,
        )

        # ---------------------------------------------------------
        # 10. Règles métier
        # ---------------------------------------------------------

        processed_order = self.process_order(
            order
        )

        logger.debug(
            "processed_order : %s",
            processed_order,
        )

        # ---------------------------------------------------------
        # 11. Résultat final
        # ---------------------------------------------------------

        final_result = {
            "conversation_id": conversation_id,
            "message": "Commande traitée.",
            **processed_order,
        }

        logger.debug(
            "Résultat final : %s",
            final_result,
        )

        return final_result

    def ask_next_information(
        self,
        conversation_id: str,
    ) -> dict:

        state = self.state_manager.get_state(
            conversation_id
        )

        if state.customer is None:

            message = "Quel est votre nom ?"
            field = "customer"

        elif state.email is None:

            message = "Quelle est votre adresse email ?"
            field = "email"

        elif not state.products:

            message = "Quel produit souhaitez-vous commander ?"
            field = "products"

        else:

            # Cette situation ne devrait normalement pas arriver.
            message = "Quelle information souhaitez-vous ajouter ?"
            field = None

        self.memory.add_message(
            conversation_id,
            "assistant",
            message,
        )

        logger.debug(
            "Question envoyée à l'utilisateur : %s",
            message,
        )

        return {
            "conversation_id": conversation_id,
            "status": "NEED_INFORMATION",
            "message": message,
            "missing": [field] if field else [],
            "order": state.model_dump(),
        }

    def get_pending_field(
        self,
        conversation_id: str,
    ) -> str | None:

        messages = self.memory.get(
            conversation_id
        )

        if not messages:
            return None

        # On cherche le dernier message de l'assistant.
        # S'il s'agit de la question qui vient d'être posée,
        # elle détermine le contexte du dernier message utilisateur.
        for message in reversed(messages):

            if message["role"] != "assistant":
                continue

            content = (
                message["content"]
                .strip()
                .lower()
            )

            if "quel est votre nom" in content:
                return "customer"

            if "quelle est votre adresse email" in content:
                return "email"

            if "quel produit souhaitez-vous commander" in content:
                return "products"

            if "quel est le nom du produit" in content:
                return "products.name"

            if "quel est le prix unitaire du produit" in content:
                return "products.unit_price"

            if "quelle quantité souhaitez-vous commander" in content:
                return "products.quantity"

            # Si le dernier message assistant n'est pas une question
            # connue, on ne cherche pas une question plus ancienne.
            return None

        return None

    def process_order(
        self,
        order: Order,
    ) -> dict:

        total = order.total

        if total < self.MINIMUM_AMOUNT:

            return {
                "status": "rejected",
                "action": "REJECT_ORDER",
                "order_id": order.id,
                "customer": order.customer,
                "email": str(order.email),
                "total": round(total, 2),
                "reason": (
                    "Montant inférieur au minimum autorisé."
                ),
            }

        if total > self.SUPPLIER_THRESHOLD:

            return {
                "status": "accepted",
                "action": "SEND_SUPPLIER_EMAIL",
                "order_id": order.id,
                "customer": order.customer,
                "email": str(order.email),
                "total": round(total, 2),
                "reason": (
                    "Commande importante nécessitant "
                    "un traitement fournisseur."
                ),
            }

        return {
            "status": "accepted",
            "action": "SEND_CONFIRMATION_EMAIL",
            "order_id": order.id,
            "customer": order.customer,
            "email": str(order.email),
            "total": round(total, 2),
            "reason": "Commande standard.",
        }