from pydantic import BaseModel


class SimulateRequest(BaseModel):
    categories: list
