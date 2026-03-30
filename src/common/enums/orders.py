from enum import Enum

class OrderStatus(str, Enum):
    RECEIVED = "Received"
    CANCELED = "Canceled"
    ASSEMBLING = "Assembling"
    READY_FOR_PICKUP = "ReadyForPickup"

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

class Type(str, Enum):
    ONLINE = "Online"
    MARKETPLACE = "Marketplace"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
