# état courant de la commande
from app.models import OrderState, OrderProduct


class OrderStateManager:

    def __init__(self):
        """ 
        Ici le dictionnaire est en mémoire, c'est volontaire pour ce projet.
        Plus une véritable application il faudra remplacer par un stockage persistant ou partagé
        par exemple : SQLite, PostgreSQL, Redis
        
        Le principe fondammental du gestionnaire d'état, mais l'implémentation du stockage changera.
        """
        self.states: dict[str, OrderState] = {} 

    def create(self, conversation_id: str) -> OrderState:
        state = OrderState()
        self.states[conversation_id] = state
        return state

    def get(self, conversation_id: str) -> OrderState:

        if conversation_id not in self.states:
            return self.create(conversation_id)

        return self.states[conversation_id]

    def set_customer(
        self,
        conversation_id: str,
        customer: str,
    ):
        state = self.get(conversation_id)
        state.customer = customer

    def set_email(
        self,
        conversation_id: str,
        email: str,
    ):
        state = self.get(conversation_id)
        state.email = email

    def add_product(
        self,
        conversation_id: str,
        name: str,
        unit_price: float,
        quantity: int,
    ):
        state = self.get(conversation_id)

        product = OrderProduct(
            name=name,
            unit_price=unit_price,
            quantity=quantity,
        )

        state.products.append(product)

    def is_complete(
        self,
        conversation_id: str,
    ) -> bool:

        state = self.get(conversation_id)

        if state.customer is None:
            return False

        if state.email is None:
            return False

        if not state.products:
            return False

        for product in state.products:
            if product.name is None:
                return False
            if product.unit_price is None:
                return False
            if product.quantity is None:
                return False

        return True

    def get_state(
        self,
        conversation_id: str,
    ) -> OrderState:

        return self.get(conversation_id)