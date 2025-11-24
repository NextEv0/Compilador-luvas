from dataclasses import dataclass
from typing import Dict, List


# Constante para representar o vazio (Epsilon).
EPSILON = "ε"

class Token:
    def __init__(self, type:str, value:str):
        self.type = type
        self.value = value

    def get_type(self)->str:
        return self.type

    def get_value(self)->str:
        return self.value
    

@dataclass
class Lexeme:
    keywords: Dict[str, str]
    operators: Dict[str, str]
    delimiters: Dict[str, str]


@dataclass
class Grammar:
    start_symbol: str
    productions: Dict[str, List[List[str]]]