from dataclasses import dataclass
from typing import Dict, List, Set
from Lexer import Token

@dataclass
class Grammar:
    start_symbol: str
    productions: Dict[str, List[List[str]]]


def build_grammar() -> Grammar:
    prods: Dict[str, List[List[str]]] = {

        # ================================
        # PROGRAMA E ESTRUTURA GERAL
        # ================================

        # programa : MAIN LBRACE bloco RBRACE funcao* EOF
        # => Programa -> MAIN LBRACE Bloco RBRACE ListaFuncao EOF
        "Programa": [["MAIN", "LBRACE", "Bloco", "RBRACE", "ListaFuncao", "EOF"]],

        # ListaFuncao -> Funcao ListaFuncao | ε
        "ListaFuncao": [["Funcao", "ListaFuncao"], ["ε"]],

        # bloco : comandos
        "Bloco": [["Comandos"]],

        # comandos : comando*
        # => Comandos -> Comando Comandos | ε
        "Comandos": [["Comando", "Comandos"], ["ε"]],

        # comando
        #   : declaracao
        #   | comandoInicioID
        #   | comandoBuiltinChamada
        #   | condicional
        #   | laco
        #   | retorno
        "Comando": [
            ["Declaracao"],
            ["ComandoInicioID"],
            ["ComandoBuiltinChamada"],
            ["Condicional"],
            ["Laco"],
            ["Retorno"],
        ],

        # ================================
        # DECLARAÇÕES, ATRIBUIÇÕES E FUNÇÕES
        # ================================

        # declaracao : DTYPE ID (EQ expressao)? SEMI
        # => Declaracao -> DTYPE ID DeclInit SEMI
        #    DeclInit -> EQ Expressao | ε
        "Declaracao": [["DTYPE", "ID", "DeclInit", "SEMI"]],
        "DeclInit": [["EQ", "Expressao"], ["ε"]],

        # atribuicao : ID EQ expressao
        "Atribuicao": [["ID", "EQ", "Expressao"]],

        # comandoInicioID : ID comandoInicioIDSufixo
        "ComandoInicioID": [["ID", "ComandoInicioIDSufixo"]],

        # comandoInicioIDSufixo
        #   : EQ expressao SEMI
        #   | LPAREN argumentos? RPAREN SEMI
        # => usar ArgsOpt para argumentos?
        "ComandoInicioIDSufixo": [
            ["EQ", "Expressao", "SEMI"],
            ["LPAREN", "ArgsOpt", "RPAREN", "SEMI"],
        ],

        # Chamadas de funções pré-definidas como comandos (com ';')
        # comandoBuiltinChamada
        #   : WRITE LPAREN argumentos? RPAREN SEMI
        #   | INPUT LPAREN RPAREN SEMI
        #   | RANDOM LPAREN argumentos? RPAREN SEMI
        #   | RANGE LPAREN argumentos? RPAREN SEMI
        #   | ABS LPAREN argumentos RPAREN SEMI
        #   | SQRT LPAREN argumentos RPAREN SEMI
        "ComandoBuiltinChamada": [
            ["WRITE", "LPAREN", "ArgsOpt", "RPAREN", "SEMI"],
            ["INPUT", "LPAREN", "RPAREN", "SEMI"],
            ["RANDOM", "LPAREN", "ArgsOpt", "RPAREN", "SEMI"],
            ["RANGE", "LPAREN", "ArgsOpt", "RPAREN", "SEMI"],
            ["ABS", "LPAREN", "Argumentos", "RPAREN", "SEMI"],
            ["SQRT", "LPAREN", "Argumentos", "RPAREN", "SEMI"],
        ],

        # funcao
        #   : FUNCAO DTYPE ID LPAREN parametros? RPAREN LBRACE bloco RBRACE
        # => Funcao -> FUNCAO DTYPE ID LPAREN ParametrosOpt RPAREN LBRACE Bloco RBRACE
        "Funcao": [["FUNCAO", "DTYPE", "ID", "LPAREN", "ParametrosOpt",
                    "RPAREN", "LBRACE", "Bloco", "RBRACE"]],

        # ParametrosOpt -> Parametros | ε
        "ParametrosOpt": [["Parametros"], ["ε"]],

        # parametros : parametro (COMMA parametro)*
        # => Parametros -> Parametro ParametrosLinha
        "Parametros": [["Parametro", "ParametrosLinha"]],

        # ParametrosLinha -> COMMA Parametro ParametrosLinha | ε
        "ParametrosLinha": [["COMMA", "Parametro", "ParametrosLinha"], ["ε"]],

        # parametro : DTYPE ID
        "Parametro": [["DTYPE", "ID"]],

        # argumentos : expressao (COMMA expressao)*
        # => Argumentos -> Expressao ArgumentosLinha
        "Argumentos": [["Expressao", "ArgumentosLinha"]],

        # ArgumentosLinha -> COMMA Expressao ArgumentosLinha | ε
        "ArgumentosLinha": [["COMMA", "Expressao", "ArgumentosLinha"], ["ε"]],

        # ArgsOpt -> Argumentos | ε   (para "argumentos?")
        "ArgsOpt": [["Argumentos"], ["ε"]],

        # retorno : RETURN expressao SEMI
        "Retorno": [["RETURN", "Expressao", "SEMI"]],

        # ================================
        # CONDICIONAIS E LAÇOS
        # ================================

        # condicional
        #   : IF LPAREN expressao RPAREN LBRACE comandos RBRACE
        #     (ELSIF LPAREN expressao RPAREN LBRACE comandos RBRACE)*
        #     (ELSE LBRACE comandos RBRACE)?
        # => Condicional -> IF (...) ListaElsif OpcionalElse
        "Condicional": [
            ["IF", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos",
             "RBRACE", "ListaElsif", "OpcionalElse"]
        ],

        # ListaElsif -> ELSIF (...) {...} ListaElsif | ε
        "ListaElsif": [
            ["ELSIF", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos",
             "RBRACE", "ListaElsif"],
            ["ε"],
        ],

        # OpcionalElse -> ELSE LBRACE Comandos RBRACE | ε
        "OpcionalElse": [
            ["ELSE", "LBRACE", "Comandos", "RBRACE"],
            ["ε"],
        ],

        # laco
        #   : WHILE LPAREN expressao RPAREN LBRACE comandos RBRACE
        #   | FOR LPAREN atribuicao SEMI expressao SEMI atribuicao RPAREN
        #     LBRACE comandos RBRACE
        "Laco": [
            ["WHILE", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos", "RBRACE"],
            ["FOR", "LPAREN", "Atribuicao", "SEMI", "Expressao", "SEMI", "Atribuicao",
             "RPAREN", "LBRACE", "Comandos", "RBRACE"],
        ],

        # ================================
        # EXPRESSÕES (NÍVEIS DE PRECEDÊNCIA)
        # ================================

        # expressao : exprOr
        "Expressao": [["ExprOr"]],

        # exprOr : exprAnd (OR exprAnd)*
        # => ExprOr -> ExprAnd ExprOrLinha
        "ExprOr": [["ExprAnd", "ExprOrLinha"]],
        "ExprOrLinha": [["OR", "ExprAnd", "ExprOrLinha"], ["ε"]],

        # exprAnd : exprRel (AND exprRel)*
        # => ExprAnd -> ExprRel ExprAndLinha
        "ExprAnd": [["ExprRel", "ExprAndLinha"]],
        "ExprAndLinha": [["AND", "ExprRel", "ExprAndLinha"], ["ε"]],

        # exprRel
        #   : exprAdd
        #     ( (ISEQ | DIFF | GTHA | LTHA | GETHA | LETHA) exprAdd )*
        # => ExprRel -> ExprAdd ExprRelLinha
        "ExprRel": [["ExprAdd", "ExprRelLinha"]],
        "ExprRelLinha": [["OpRel", "ExprAdd", "ExprRelLinha"], ["ε"]],

        # OpRel -> ISEQ | DIFF | GTHA | LTHA | GETHA | LETHA
        "OpRel": [
            ["ISEQ"],
            ["DIFF"],
            ["GTHA"],
            ["LTHA"],
            ["GETHA"],
            ["LETHA"],
        ],

        # exprAdd : exprMul ( (SUM | SUB) exprMul )*
        # => ExprAdd -> ExprMul ExprAddLinha
        "ExprAdd": [["ExprMul", "ExprAddLinha"]],
        "ExprAddLinha": [["OpAdd", "ExprMul", "ExprAddLinha"], ["ε"]],

        # OpAdd -> SUM | SUB
        "OpAdd": [["SUM"], ["SUB"]],

        # exprMul : exprPow ( (MUL | DIV | MOD) exprPow )*
        # => ExprMul -> ExprPow ExprMulLinha
        "ExprMul": [["ExprPow", "ExprMulLinha"]],
        "ExprMulLinha": [["OpMul", "ExprPow", "ExprMulLinha"], ["ε"]],

        # OpMul -> MUL | DIV | MOD
        "OpMul": [["MUL"], ["DIV"], ["MOD"]],

        # exprPow : exprUnary (POW exprPow)?
        # => ExprPow -> ExprUnary ExprPowLinha
        "ExprPow": [["ExprUnary", "ExprPowLinha"]],
        "ExprPowLinha": [["POW", "ExprPow"], ["ε"]],

        # exprUnary
        #   : NOT exprUnary
        #   | SUB exprUnary
        #   | primario
        "ExprUnary": [
            ["NOT", "ExprUnary"],
            ["SUB", "ExprUnary"],
            ["Primario"],
        ],

        # primario
        #   : LPAREN expressao RPAREN
        #   | builtinCallExpr
        #   | ID primarioIdSufixo
        #   | literal
        "Primario": [
            ["LPAREN", "Expressao", "RPAREN"],
            ["BuiltinCallExpr"],
            ["ID", "PrimarioIdSufixo"],
            ["Literal"],
        ],

        # primarioIdSufixo
        #   : LPAREN argumentos? RPAREN
        #   | ε
        "PrimarioIdSufixo": [
            ["LPAREN", "ArgsOpt", "RPAREN"],
            ["ε"],
        ],

        # builtinCallExpr
        #   : WRITE LPAREN argumentos? RPAREN
        #   | INPUT LPAREN RPAREN
        #   | RANDOM LPAREN argumentos? RPAREN
        #   | RANGE LPAREN argumentos? RPAREN
        #   | ABS LPAREN argumentos RPAREN
        #   | SQRT LPAREN argumentos RPAREN
        "BuiltinCallExpr": [
            ["WRITE", "LPAREN", "ArgsOpt", "RPAREN"],
            ["INPUT", "LPAREN", "RPAREN"],
            ["RANDOM", "LPAREN", "ArgsOpt", "RPAREN"],
            ["RANGE", "LPAREN", "ArgsOpt", "RPAREN"],
            ["ABS", "LPAREN", "Argumentos", "RPAREN"],
            ["SQRT", "LPAREN", "Argumentos", "RPAREN"],
        ],

        # literal
        #   : INT
        #   | FLOAT
        #   | BOOL
        #   | STRING
        "Literal": [
            ["INT"],
            ["FLOAT"],
            ["BOOL"],
            ["STRING"],
        ],
    }

    return Grammar(start_symbol="Programa", productions=prods)


def first_of_sequence(seq: List[str],
                      first: Dict[str, Set[str]],
                      grammar: Grammar) -> Set[str]:
    result: Set[str] = set()
    for X in seq:
        if X == "ε":
            result.add("ε")
            break
        # terminal
        if X not in grammar.productions:
            result.add(X)
            break
        # não-terminal
        result.update(first[X] - {"ε"})
        if "ε" not in first[X]:
            break
    else:
        result.add("ε")
    return result


def compute_first(grammar: Grammar) -> Dict[str, Set[str]]:
    first: Dict[str, Set[str]] = {nt: set() for nt in grammar.productions}

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.productions.items():
            for prod in prods:
                i = 0
                while i < len(prod):
                    X = prod[i]
                    if X == "ε":
                        if "ε" not in first[A]:
                            first[A].add("ε")
                            changed = True
                        break
                    if X not in grammar.productions:  # terminal
                        if X not in first[A]:
                            first[A].add(X)
                            changed = True
                        break
                    before = len(first[A])
                    first[A].update(first[X] - {"ε"})
                    if "ε" not in first[X]:
                        break
                    if len(first[A]) != before:
                        changed = True
                    i += 1
                else:
                    if "ε" not in first[A]:
                        first[A].add("ε")
                        changed = True
    return first


def compute_follow(grammar: Grammar,
                   first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    follow: Dict[str, Set[str]] = {nt: set() for nt in grammar.productions}
    follow[grammar.start_symbol].add("EOF")

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.productions.items():
            for prod in prods:
                for i, B in enumerate(prod):
                    if B in grammar.productions:  # B é não-terminal
                        beta = prod[i + 1:]
                        if beta:
                            first_beta = first_of_sequence(beta, first, grammar)
                            before = len(follow[B])
                            follow[B].update(first_beta - {"ε"})
                            if len(follow[B]) != before:
                                changed = True
                            if "ε" in first_beta:
                                before = len(follow[B])
                                follow[B].update(follow[A])
                                if len(follow[B]) != before:
                                    changed = True
                        else:
                            before = len(follow[B])
                            follow[B].update(follow[A])
                            if len(follow[B]) != before:
                                changed = True
    return follow


def build_parsing_table(grammar: Grammar,
                        first: Dict[str, Set[str]],
                        follow: Dict[str, Set[str]]
                        ) -> Dict[str, Dict[str, List[str]]]:
    table: Dict[str, Dict[str, List[str]]] = {nt: {} for nt in grammar.productions}

    for A, prods in grammar.productions.items():
        for prod in prods:
            first_alpha = first_of_sequence(prod, first, grammar)
            for terminal in first_alpha - {"ε"}:
                if terminal in table[A]:
                    print(f"[AVISO] Conflito LL(1) em M[{A}, {terminal}]")
                table[A][terminal] = prod
            if "ε" in first_alpha:
                for terminal in follow[A]:
                    if terminal in table[A]:
                        print(f"[AVISO] Conflito LL(1) em M[{A}, {terminal}]")
                    table[A][terminal] = prod
    return table
