from enum import Enum


class Denomination(Enum):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50
    HUNDRED = 100 

class MachineState(Enum):
    IDLE = 'idle'
    COLLECTING_MONEY = 'collecting_money'
    DISPENSING = 'dispensing'
