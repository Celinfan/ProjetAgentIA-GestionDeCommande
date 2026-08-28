import pytest
from app.models import Order, Product
from app.service import OrderService, Action

class FakeLLM:
    def __init__(self, data): 
        self.data = data
    def extract_order(self, text): 
        return self.data
    
class BrokenLLM:
    def extract_order(self, text):
        raise RuntimeError("LLM offline")

def make_order(total: float) -> dict:
    return {
        "id": 1,
        "customer": "Alice",
        "email": "alice@example.com",
        "products": [{
            "id": 1,
            "name": "Produit test",
            "unit_price": total,
            "quantity": 1,
        }],
    }

def order(total):
    return Order(
        id=1,
        customer="Alice",
        email="alice@example.com",
        products=[Product(id=1,name="Lamp",unit_price=total,quantity=1)]
    )

# ---------------------------------------------------------
# 1. Les règles métier sont déterministes
# ---------------------------------------------------------

@pytest.mark.parametrize(
    ("total", "expected"),
    [
        (10, Action.REJECT_ORDER),
        (20, Action.SEND_CONFIRMATION_EMAIL),
        (100, Action.SEND_CONFIRMATION_EMAIL),
        (500, Action.SEND_CONFIRMATION_EMAIL),
        (501, Action.SEND_SUPPLIER_EMAIL),
        (3000, Action.SEND_SUPPLIER_EMAIL),
    ],
)
def test_business_rules_are_deterministic(total, expected):
    service = OrderService(FakeLLM(make_order(total)))

    result = service.process_text("n'importe quelle demande")

    assert result["action"] == expected.value
    assert result["total"] == total


# ---------------------------------------------------------
# 2. Une commande invalide est rejetée par Pydantic
# ---------------------------------------------------------

def test_invalid_order_is_rejected_by_validation():
    bad_order = make_order(30)
    bad_order["email"] = "pas-un-email"

    service = OrderService(FakeLLM(bad_order))

    with pytest.raises(Exception):
        service.process_text("commande invalide")


# ---------------------------------------------------------
# 3. Le LLM extrait les données,
#    mais ne décide pas de l'action métier
# ---------------------------------------------------------

def test_llm_only_extracts_data():
    service = OrderService(FakeLLM(make_order(3000)))

    result = service.process_text("commande quelconque")

    assert result["total"] == 3000
    assert result["action"] == Action.SEND_SUPPLIER_EMAIL.value


# ---------------------------------------------------------
# 4. Une commande classique est acceptée
# ---------------------------------------------------------

def test_standard_order_is_accepted():
    service = OrderService(FakeLLM(make_order(100)))

    result = service.process_text("commande quelconque")

    assert result["status"] == "accepted"
    assert result["action"] == Action.SEND_CONFIRMATION_EMAIL.value


# ---------------------------------------------------------
# 5. Une commande trop faible est rejetée
# ---------------------------------------------------------

def test_small_order_is_rejected():
    service = OrderService(FakeLLM(make_order(10)))

    result = service.process_text("commande quelconque")

    assert result["status"] == "rejected"
    assert result["action"] == Action.REJECT_ORDER.value


# ---------------------------------------------------------
# 6. Le LLM peut être remplacé par un Fake
# ---------------------------------------------------------

def test_fake_llm_is_used_to_extract_order():
    fake = FakeLLM(make_order(3000))
    service = OrderService(fake)

    result = service.process_text("texte sans importance")

    assert result["customer"] == "Alice"
    assert result["total"] == 3000