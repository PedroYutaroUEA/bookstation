from pydantic import BaseModel


class SimulateRequest(BaseModel):
    categories: list
    price_min: float
    price_max: float
