from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import List, Annotated
from datetime import datetime

class OrderItem(BaseModel):
    #Allow to ignore fields which aren't described
    model_config = ConfigDict(extra='ignore')
    # Describing fields of one order
    id: int
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    price: float
    totalBonus: float
    createdOn: datetime
    orderStatus: str = Field(min_length=1)
    status: str = Field(min_length=1)
    statusGroup: str = Field(min_length=1)
    seller: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    quantity: int
    type: str = Field(min_length=1)
    deliveryId: int
    goods: List[str]

class OrdersResponse(BaseModel):
    items: List[OrderItem]
    pageIndex: int
    totalPages: int
    totalCount: int
    hasPreviousPage: bool
    hasNextPage: bool