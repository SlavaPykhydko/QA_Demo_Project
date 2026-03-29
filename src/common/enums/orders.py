from enum import Enum

class OrderStatus(str, Enum):
    RECEIVED = "Received"
    CANCELED = "Canceled"
    ASSEMBLING = "Assembling"
    READY_FOR_PICKUP = "ReadyForPickup"


class Status(str, Enum):
    ALL = "All"
    DONE = "Done"
    CANCEL = "Cancel"
    ACTIVE = "Active"

class StatusUA(str, Enum):
    RECEIVED = "Отримано"
    CANCELED = "Скасовано"
    IN_PROCESSING = "В обробці"
    READY_FOR_RECEIVE = "Готово до видачі"

class StatusGroup(str, Enum):
    RECEIVED = "received"
    CANCELED = "canceled"
    IN_PROCESSING = "in_processing"
    READY_FOR_RECEIVE = "ready_for_receive"

class Type(str, Enum):
    ONLINE = "Online"
    MARKETPLACE = "Marketplace"
