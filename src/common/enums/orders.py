from enum import Enum

class OrderStatus(str, Enum):
    RECEIVED = "Received"
    CANCELED = "Canceled"
    ASSEMBLING = "Assembling"
    READY_FOR_PICKUP = "ReadyForPickup"

    @property
    def ukrainian(self):
        mapping = {
            OrderStatus.RECEIVED: StatusUA.RECEIVED,
            OrderStatus.CANCELED: StatusUA.CANCELED,
            OrderStatus.ASSEMBLING: StatusUA.IN_PROCESSING,
            OrderStatus.READY_FOR_PICKUP: StatusUA.READY_FOR_RECEIVE
        }
        return mapping.get(self)

    # Цей метод каже Python: "Коли мене хочуть надрукувати як текст — показуй тільки значення"
    def __str__(self):
        return str(self.value)

    # Цей метод каже: "Коли я знаходжусь всередині списку чи словника — теж показуй тільки значення"
    def __repr__(self):
        return str(self.value)


class Status(str, Enum):
    ALL = "All"
    DONE = "Done"
    CANCEL = "Cancel"
    ACTIVE = "Active"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class StatusUA(str, Enum):
    RECEIVED = "Отримано"
    CANCELED = "Скасовано"
    IN_PROCESSING = "В обробці"
    READY_FOR_RECEIVE = "Готово до видачі"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class StatusGroup(str, Enum):
    RECEIVED = "received"
    CANCELED = "canceled"
    IN_PROCESSING = "in_processing"
    READY_FOR_RECEIVE = "ready_for_receive"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class OrderType(str, Enum):
    ONLINE = "Online"
    MARKETPLACE = "Marketplace"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
