from pydantic import BaseModel


class ItemRating(BaseModel):
    usuario_id: int
    item_id: int
    rating: int  # 1 ou 0
