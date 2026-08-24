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
        return sum(p.unit_price * p.quantity for p in self.products)
