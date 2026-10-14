from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    price: Decimal
    timestamp: int