from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import List, Annotated
from datetime import datetime

from src.common.enums.orders import OrderStatus, StatusGroup, Type, StatusUA


class OrderItem(BaseModel):
    #Allow to ignore fields which aren't described
    model_config = ConfigDict(extra='ignore')
    # Describing fields of one order
    id: int = Field(gt=0)
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    price: float = Field(ge=0)
    totalBonus: float = Field(ge=0)
    createdOn: datetime
    orderStatus: OrderStatus
    status: StatusUA
    statusGroup: StatusGroup
    seller: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    quantity: int = Field(gt=0)
    type: Type
    deliveryId: int = Field(gt=0)
    goods: List[str]

class OrdersResponse(BaseModel):
    items: List[OrderItem]
    pageIndex: int = Field(ge=0)
    totalPages: int = Field(ge=0)
    totalCount: int = Field(ge=0)
    hasPreviousPage: bool
    hasNextPage: bool