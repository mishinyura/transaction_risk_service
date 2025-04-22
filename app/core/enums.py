from enum import Enum


class TransactionType(str, Enum):
    TRANSFER = 'Transfer' #Перевод
    DEPOSIT = 'Deposit' #Поступление
    WITHDRAWAL = 'Withdrawal' #Снятие наличных


class TransactionStatus(str, Enum):
    FAILED = 'Failed' #Отклонено
    SUCCESS = 'Success' #Исполнено


class DeviceUser(str, Enum):
    DESKTOP = 'Desktop'
    MOBILE = 'Mobile'