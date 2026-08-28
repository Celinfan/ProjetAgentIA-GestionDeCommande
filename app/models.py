# validation Pydantic
from pydantic import BaseModel, EmailStr, Field

class Product(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=1)
    unit_price: float = Field(gt=0)
    quantity: int = Field(gt=0)


class Order(BaseModel):
    id: int = Field(ge=1)
    customer: str = Field(min_length=1)
    email: EmailStr
    products: list[Product] = Field(min_length=1)

    @property
    def total(self) -> float:
        return sum(
            product.unit_price * product.quantity
            for product in self.products
        )
    
class OrderProduct(BaseModel):
    """
    État courant du produit.
    Contrairement à Product, cet objet peut être incomplet.
    """
    name: str | None = None
    unit_price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, gt=0)


class OrderState(BaseModel):
    """
    État courant de la commande.
    Contrairement à Order, cet objet peut être incomplet.
    """
    customer: str | None = None
    email: EmailStr | None = None
    products: list[OrderProduct] = Field(default_factory=list)