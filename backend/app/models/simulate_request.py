from pydantic import BaseModel


class SimulateRequest(BaseModel):
    genres: list
    price_min: float
    price_max: float
