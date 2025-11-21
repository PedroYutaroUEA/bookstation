from pydantic import BaseModel


class ItemRating(BaseModel):
    user_id: int
    item_id: int
    rating: int  # 1 ou 0
