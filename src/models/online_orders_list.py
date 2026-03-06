from pydantic import BaseModel, ConfigDict
from typing import List

class OrderItem(BaseModel):
    #Allow to ignore fields which aren't described
    model_config = ConfigDict(extra='ignore')
    # Describing fields of one order
    id: int
    name: str
    price: float
    totalBonus: float
    createdOn: str
    orderStatus: str
    status: str
    statusGroup: str
    seller: str
    quantity: int
    type: str
    deliveryId: int
    goods: List[str]

class OrdersResponse(BaseModel):
    items: List[OrderItem]
    pageIndex: int
    totalPages: int
    totalCount: int
    hasPreviousPage: bool
    hasNextPage: bool