import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Set

# Constante para representar o vazio (Epsilon).
EPSILON = "ε"

@dataclass
class Grammar:
    start_symbol: str
    productions: Dict[str, List[List[str]]]

def build_lukera_grammar() -> Grammar:
    """
    Constrói a gramática LL(1) da linguagem Lukera.
    Retorna um objeto Grammar contendo o símbolo inicial e as produções.
    """

    prods: Dict[str, List[List[str]]] = {

        # ================================
        # 1. ESTRUTURA GERAL DO PROGRAMA
        # ================================

        # Programa -> MAIN LBRACE Bloco RBRACE ListaFuncao EOF
        "Programa": [
            ["MAIN", "LBRACE", "Bloco", "RBRACE", "ListaFuncao", "EOF"]
        ],

        # ListaFuncao -> Funcao ListaFuncao | ε
        # ListaFuncao implementa (funcao)*
        "ListaFuncao": [
            ["Funcao", "ListaFuncao"], 
            [EPSILON]
        ],

        # Bloco -> Comandos
        "Bloco": [["Comandos"]],

        # Comandos -> Comando Comandos | ε
        # Comandos implementar (comando)*
        "Comandos": [
            ["Comando", "Comandos"], 
            [EPSILON]
        ],

        # Comando -> (Lista de todos os tipos de comandos possíveis)
        "Comando": [
            ["Declaracao"],
            ["ComandoInicioID"],       # Cobre atribuições e chamadas de func usuário
            ["ComandoBuiltinChamada"], # Cobre escreve(), leia(), etc usadas como comando
            ["Condicional"],
            ["Laco"],
            ["Retorno"],
        ],

        # ================================
        # 2. DECLARAÇÕES E ATRIBUIÇÕES
        # ================================

        # Declaracao -> DTYPE ID DeclInit SEMI
        "Declaracao": [["DTYPE", "ID", "DeclInit", "SEMI"]],

        # DeclInit -> EQ Expressao | ε
        # DeclInit implmenta (expressao)? em Declaracao
        "DeclInit": [
            ["EQ", "Expressao"], 
            [EPSILON]
        ],

        # Atribuicao -> ID EQ Expressao (Usada dentro do FOR)
        "Atribuicao": [["ID", "EQ", "Expressao"]],

        # ComandoInicioID -> ID ComandoInicioIDSufixo
        "ComandoInicioID": [["ID", "ComandoInicioIDSufixo"]],

        # ComandoInicioIDSufixo -> EQ Expressao SEMI | LPAREN ArgsOpt RPAREN SEMI
        "ComandoInicioIDSufixo": [
            ["EQ", "Expressao", "SEMI"],             # x = 10;
            ["LPAREN", "ArgsOpt", "RPAREN", "SEMI"], # minhaFuncao();
        ],

        # OTIMIZAÇÃO: Reutiliza a regra de expressão para comandos built-in
        # ComandoBuiltinChamada -> BuiltinCallExpr SEMI
        "ComandoBuiltinChamada": [
            ["BuiltinCallExpr", "SEMI"]
        ],

        # ================================
        # 3. FUNÇÕES E PARÂMETROS
        # ================================

        # Funcao -> FUNCAO DTYPE ID LPAREN ParametrosOpt RPAREN LBRACE Bloco RBRACE
        "Funcao": [
            ["FUNCAO", "DTYPE", "ID", "LPAREN", "ParametrosOpt", "RPAREN", "LBRACE", "Bloco", "RBRACE"]
        ],

        # ParametrosOpt -> Parametros | ε
        "ParametrosOpt": [
            ["Parametros"], 
            [EPSILON]
        ],

        # Parametros -> Parametro ParametrosLinha
        "Parametros": [["Parametro", "ParametrosLinha"]],

        # ParametrosLinha -> COMMA Parametro ParametrosLinha | ε
        # ParametrosLinha implementa (COMMA parametro)*
        "ParametrosLinha": [
            ["COMMA", "Parametro", "ParametrosLinha"], 
            [EPSILON]
        ],

        # Parametro -> DTYPE ID
        "Parametro": [["DTYPE", "ID"]],

        # Retorno -> RETURN Expressao SEMI
        "Retorno": [["RETURN", "Expressao", "SEMI"]],

        # ================================
        # 4. ARGUMENTOS (Chamadas)
        # ================================

        # ArgsOpt -> Argumentos | ε
        "ArgsOpt": [
            ["Argumentos"], 
            [EPSILON]
        ],

        # Argumentos -> Expressao ArgumentosLinha
        "Argumentos": [["Expressao", "ArgumentosLinha"]],

        # ArgumentosLinha -> COMMA Expressao ArgumentosLinha | ε
        # ArgumentosLinha implementa (COMMA expressao)*
        "ArgumentosLinha": [
            ["COMMA", "Expressao", "ArgumentosLinha"], 
            [EPSILON]
        ],

        # ================================
        # 5. ESTRUTURAS DE CONTROLE
        # ================================

        # Condicional -> IF ( Expr ) { Comandos } ListaElsif OpcionalElse
        "Condicional": [
            ["IF", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos", "RBRACE", "ListaElsif", "OpcionalElse"]
        ],

        # ListaElsif -> ELSIF ( Expr ) { Comandos } ListaElsif | ε
        "ListaElsif": [
            ["ELSIF", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos", "RBRACE", "ListaElsif"],
            [EPSILON],
        ],

        # OpcionalElse -> ELSE { Comandos } | ε
        "OpcionalElse": [
            ["ELSE", "LBRACE", "Comandos", "RBRACE"],
            [EPSILON],
        ],

        # Laco -> WHILE ... | FOR ...
        "Laco": [
            ["WHILE", "LPAREN", "Expressao", "RPAREN", "LBRACE", "Comandos", "RBRACE"],
            ["FOR", "LPAREN", "Atribuicao", "SEMI", "Expressao", "SEMI", "Atribuicao", "RPAREN", "LBRACE", "Comandos", "RBRACE"],
        ],

        # ================================
        # 6. EXPRESSÕES (Hierarquia LL(1))
        # ================================

        # Expressao -> ExprOr
        "Expressao": [["ExprOr"]],

        # Nível 1: OR
        "ExprOr": [["ExprAnd", "ExprOrLinha"]],
        "ExprOrLinha": [
            ["OR", "ExprAnd", "ExprOrLinha"], 
            [EPSILON]
        ],

        # Nível 2: AND
        "ExprAnd": [["ExprRel", "ExprAndLinha"]],
        "ExprAndLinha": [
            ["AND", "ExprRel", "ExprAndLinha"], 
            [EPSILON]
        ],

        # Nível 3: Relacional e Igualdade
        "ExprRel": [["ExprAdd", "ExprRelLinha"]],
        "ExprRelLinha": [
            ["OpRel", "ExprAdd", "ExprRelLinha"], 
            [EPSILON]
        ],

        "OpRel": [
            ["ISEQ"], ["DIFF"], ["GTHA"], ["LTHA"], ["GETHA"], ["LETHA"]
        ],

        # Nível 4: Adição e Subtração
        "ExprAdd": [["ExprMul", "ExprAddLinha"]],
        "ExprAddLinha": [
            ["OpAdd", "ExprMul", "ExprAddLinha"], 
            [EPSILON]
        ],

        "OpAdd": [["SUM"], ["SUB"]],

        # Nível 5: Multiplicação, Divisão, Módulo
        "ExprMul": [["ExprPow", "ExprMulLinha"]],
        "ExprMulLinha": [
            ["OpMul", "ExprPow", "ExprMulLinha"], 
            [EPSILON]
        ],

        "OpMul": [["MUL"], ["DIV"], ["MOD"]],

        # Nível 6: Potência
        "ExprPow": [["ExprUnary", "ExprPowLinha"]],
        "ExprPowLinha": [
            ["POW", "ExprPow"], # Recursão à direita aqui simula associatividade à direita
            [EPSILON]
        ],

        # Nível 7: Unários
        "ExprUnary": [
            ["NOT", "ExprUnary"],
            ["SUB", "ExprUnary"],
            ["Primario"],
        ],

        # Nível 8: Primários (Átomos)
        "Primario": [
            ["LPAREN", "Expressao", "RPAREN"],
            ["BuiltinCallExpr"],
            ["ID", "PrimarioIdSufixo"],
            ["Literal"],
        ],

        # Resolve ambiguidade ID vs Chamada de Função em expressões
        "PrimarioIdSufixo": [
            ["LPAREN", "ArgsOpt", "RPAREN"],
            [EPSILON], # É apenas uma variável
        ],

        # Funções Nativas (Built-ins)
        "BuiltinCallExpr": [
            ["WRITE", "LPAREN", "ArgsOpt", "RPAREN"],
            ["INPUT", "LPAREN", "RPAREN"],
            ["RANDOM", "LPAREN", "ArgsOpt", "RPAREN"],
            ["RANGE", "LPAREN", "ArgsOpt", "RPAREN"],
            ["ABS", "LPAREN", "Argumentos", "RPAREN"],
            ["SQRT", "LPAREN", "Argumentos", "RPAREN"],
        ],

        # Literais
        "Literal": [
            ["INTEGER"],
            ["FLOAT"],
            ["BOOL"],
            ["STRING"],
        ],
    }

    return Grammar(start_symbol="Programa", productions=prods)


def first_of_sequence(seq: List[str],
                      first: Dict[str, Set[str]],
                      grammar: Grammar) -> Set[str]:
    """
    Calcula o FIRST de uma sequência de símbolos (ex: o lado direito de uma produção).
    """
    result: Set[str] = set()
    
    # Se a sequência for vazia, o FIRST é epsilon (ex: A -> ε)
    if not seq:
        result.add(EPSILON)
        return result

    for X in seq:
        if X == EPSILON:
            result.add(EPSILON)
            break
        
        # Se X é terminal (não está nas chaves do dicionário de produções)
        if X not in grammar.productions:
            result.add(X)
            break
        
        # Se X é não-terminal, adiciona FIRST(X) - {ε}
        result.update(first[X] - {EPSILON})
        
        # Se ε não está no FIRST(X), paramos (não propagamos mais)
        if EPSILON not in first[X]:
            break
    else:
        # Se o loop terminou sem break, significa que todos eram anuláveis
        result.add(EPSILON)
        
    return result


def compute_first(grammar: Grammar) -> Dict[str, Set[str]]:
    """
    Calcula o conjunto FIRST para todos os não-terminais da gramática.
    """
    # Inicializa conjuntos vazios
    first: Dict[str, Set[str]] = {nt: set() for nt in grammar.productions}

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.productions.items():
            for prod in prods:
                # OTIMIZAÇÃO: Reutiliza first_of_sequence em vez de reescrever a lógica
                rhs_first = first_of_sequence(prod, first, grammar)
                
                # Se encontrarmos novos símbolos, atualizamos e marcamos mudança
                if not rhs_first.issubset(first[A]):
                    first[A].update(rhs_first)
                    changed = True
    return first


def compute_follow(grammar: Grammar,
                   first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Calcula o conjunto FOLLOW para todos os não-terminais.
    """
    follow: Dict[str, Set[str]] = {nt: set() for nt in grammar.productions}
    
    # Regra 1: O símbolo inicial contém EOF
    follow[grammar.start_symbol].add("EOF")

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.productions.items():
            for prod in prods:
                # Percorre a produção buscando Não-Terminais (B)
                for i, B in enumerate(prod):
                    if B in grammar.productions:  # B é não-terminal
                        beta = prod[i + 1:] # O que vem depois de B
                        
                        if beta:
                            # Regra 2: FOLLOW(B) recebe FIRST(beta) - {ε}
                            first_beta = first_of_sequence(beta, first, grammar)
                            before_len = len(follow[B])
                            
                            follow[B].update(first_beta - {EPSILON})
                            
                            if len(follow[B]) != before_len:
                                changed = True
                                
                            # Regra 3: Se beta é anulável, FOLLOW(B) recebe FOLLOW(A)
                            if EPSILON in first_beta:
                                before_len = len(follow[B])
                                follow[B].update(follow[A])
                                if len(follow[B]) != before_len:
                                    changed = True
                        else:
                            # Regra 3 (Caso final): A -> alpha B (beta é vazio)
                            # FOLLOW(B) recebe FOLLOW(A)
                            before_len = len(follow[B])
                            follow[B].update(follow[A])
                            if len(follow[B]) != before_len:
                                changed = True
    return follow


def build_parsing_table(grammar: Grammar,
                        first: Dict[str, Set[str]],
                        follow: Dict[str, Set[str]]
                        ) -> Dict[str, Dict[str, List[str]]]:
    """
    Constrói a Tabela de Parsing M[Não-Terminal, Terminal] = Produção.
    """
    table: Dict[str, Dict[str, List[str]]] = {nt: {} for nt in grammar.productions}
    
    # Itera sobre todas as produções A -> alpha
    for A, prods in grammar.productions.items():
        for prod in prods:
            # Calcula FIRST(alpha)
            first_alpha = first_of_sequence(prod, first, grammar)
            
            # 1. Para cada terminal 'a' em FIRST(alpha), M[A, a] = alpha
            for terminal in first_alpha - {EPSILON}:
                if terminal in table[A]:
                    print(f"[CRÍTICO] Conflito LL(1) em M[{A}, {terminal}]. Regras colidindo!")
                    # Você pode optar por levantar erro aqui:
                    # raise Exception(f"Gramática não é LL(1): Conflito em {A} com token {terminal}")
                table[A][terminal] = prod
            
            # 2. Se epsilon está em FIRST(alpha), para cada 'b' em FOLLOW(A), M[A, b] = alpha
            if EPSILON in first_alpha:
                for terminal in follow[A]:
                    if terminal in table[A]:
                        print(f"[CRÍTICO] Conflito LL(1) (via Follow) em M[{A}, {terminal}]")
                    table[A][terminal] = prod
                    
    return table


def parsing_table_pandas(grammar:Grammar, first:dict, follow: dict, jupyter=True) -> pd.DataFrame:
    """
    Executa os algoritmos LL(1) e exibe a tabela resultante usando Pandas.
    """
    # 1. Executar a lógica do parser
    parsing_table = build_parsing_table(grammar, first, follow)

    # 2. Preparar dados para o Pandas
    # Linhas: Todos os Não-Terminais
    rows = list(grammar.productions.keys())
    
    # Colunas: Todos os terminais encontrados na tabela
    cols = set()
    for row_dict in parsing_table.values():
        cols.update(row_dict.keys())
    sorted_cols = sorted(list(cols))
    
    # Ajuste visual: EOF no final
    if "EOF" in sorted_cols:
        sorted_cols.remove("EOF")
        sorted_cols.append("EOF")

    # 3. Construir a Matriz de Strings
    data = []
    for nt in rows:
        row_data = []
        for term in sorted_cols:
            if term in parsing_table[nt]:
                # Transforma a lista ['IF', 'LPAREN'...] em string "IF LPAREN..."
                prod_list = parsing_table[nt][term]
                prod_str = " ".join(prod_list)
                cell_value = f"{nt} -> {prod_str}"
            else:
                cell_value = "" # Célula vazia
            row_data.append(cell_value)
        data.append(row_data)

    # 4. Criar e Exibir DataFrame
    df = pd.DataFrame(data, index=rows, columns=sorted_cols)
    
    # Configurações para exibir a tabela inteira no terminal sem cortes
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.max_colwidth', None)
    
    return df