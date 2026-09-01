from app.models import OrderState, OrderProduct


class OrderStateManager:
    """Gère l'état courant des commandes en mémoire."""

    def __init__(self):
        """ 
        Initialise le stockage des états.

        Le stockage est volontairement en mémoire pour ce projet.
        En production, il pourra être remplacé par une base de données
        ou un stockage partagé comme PostgreSQL ou Redis
        
        Le principe fondammental du gestionnaire d'état retera,
        mais l'implémentation du stockage changera.
        """
        self.states: dict[str, OrderState] = {} 

    def create(self, conversation_id: str) -> OrderState:
        """Crée un état de commande."""
        state = OrderState()
        self.states[conversation_id] = state

        return state

    def get(self, conversation_id: str) -> OrderState:
        """Retourne l'état d'une commande."""
        if conversation_id not in self.states:
            return self.create(conversation_id)

        return self.states[conversation_id]

    def set_customer(
        self,
        conversation_id: str,
        customer: str,
    ) -> None:
        """Définit le nom du client."""
        state = self.get(conversation_id)
        state.customer = customer

    def set_email(
        self,
        conversation_id: str,
        email: str,
    ) -> None:
        """Définit l'adresse email du client."""
        state = self.get(conversation_id)
        state.email = email

    def add_product(
        self,
        conversation_id: str,
        name: str,
        unit_price: float,
        quantity: int,
    ) -> None:
        """Ajoute un produit à la commande."""
        state = self.get(conversation_id)

        product = OrderProduct(
            name=name,
            unit_price=unit_price,
            quantity=quantity,
        )

        state.products.append(product)

    def is_complete(self, conversation_id: str) -> bool:
        """Indique si la commande contient toutes les informations."""
        state = self.get(conversation_id)

        if state.customer is None:
            return False

        if state.email is None:
            return False

        if not state.products:
            return False

        return all(
            product.name is not None
            and product.unit_price is not None
            and product.quantity is not None
            for product in state.products
        )

    def get_state(self, conversation_id: str) -> OrderState:
        """Retourne l'état courant d'une commande."""
        return self.get(conversation_id)