# historique conversation
import uuid

class ConversationMemory:
    """Stocke temporairement les messages des conversations en mémoire."""

    def __init__(self):
        self._conversations: dict[str, list[dict[str, str]]] = {}

    def create(self) -> str:
        """Crée une nouvelle conversation et retourne son identifiant."""
        conversation_id = str(uuid.uuid4())
        self._conversations[conversation_id] = []
        return conversation_id

    def get(self, conversation_id: str) -> list[dict[str, str]]:
        """Retourne l'historique d'une conversation."""
        return self._conversations.get(conversation_id, [])

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        """Ajoute un message à une conversation."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append(
            {
                "role": role,
                "content": content,
            }
        )