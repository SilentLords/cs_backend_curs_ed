from enum import Enum

class WITHDRAW_REQUEST_STATUS_CHOICES_ENUM(Enum):
    IN_PROGRESS = 'В процессе'
    DONE = 'Выполнен'
    FAILED = 'Неуспешно'

class TRANSACTION_TYPE_CHOICES_ENUM(Enum):
    EMPTY = ''
    FROZEN = 'Заморожено'
    UNFROZEN = 'Разморожено'
    WITHDRAW = 'Вывод средств'


TRANSACTION_TYPE_CHOICES = (
    (TRANSACTION_TYPE_CHOICES_ENUM.WITHDRAW, 'Вывод средств'),
)

WITHDRAW_REQUEST_STATUS_CHOICES =(
    (TRANSACTION_TYPE_CHOICES_ENUM.IN_PROGRESS, 'В процессе'),
    (TRANSACTION_TYPE_CHOICES_ENUM.DONE, 'Выполнен'),
    (TRANSACTION_TYPE_CHOICES_ENUM.FAILED, 'Неуспешно'),

)