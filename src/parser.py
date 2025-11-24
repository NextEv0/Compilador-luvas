import pandas as pd
from typing import List, Dict, Set
from .models import Token, Grammar
from .models_utils import  compute_first, compute_follow, build_parsing_table, EPSILON


class Parser:
    def __init__(self, tokens: Token, grammar_set: Grammar):
        # 1. Tokens da análise léxica
        self.tokens = tokens
        
        # 2. Preparação da Gramática
        self.grammar = grammar_set
        self.start_symbol = grammar_set.start_symbol
        
        # 3. Construção das Tabelas
        self.first = compute_first(grammar_set)
        self.follow = compute_follow(grammar_set, self.first)
        self.parsing_table = build_parsing_table(grammar_set, self.first, self.follow)
        
        # 4. Dados para o Relatório Visual
        self.trace_data = [] 

    def parse(self):
        """
        Executa o algoritmo LL(1) com pilha e recuperação de erro (Modo Pânico).
        """
        # --- Inicialização ---
        # Pilha começa com [EOF, SimboloInicial]
        stack = ["EOF", self.start_symbol]
        
        # Cursor para ler os tokens
        cursor = 0
        
        # String para mostrar o que já foi "casado" (Matched)
        matched_str = ""
        
        # Variável para controle de loop infinito em erros
        max_steps = 10000 
        step = 0

        print(f" Starting analysis of {len(self.tokens)} tokens...")

        while len(stack) > 0:
            step += 1
            if step > max_steps:
                print(" [FATAL ERROR] Infinite loop detected in the parser.")
                break

            # Topo da pilha (X) e Token atual (a)
            top = stack[-1]
            
            if cursor < len(self.tokens):
                current_token = self.tokens[cursor]
                token_type = current_token.type
                token_val = str(current_token.value)
            else:
                # Caso passe do EOF (segurança)
                token_type = "EOF"
                token_val = "$"

            # Prepara a visualização da 'Entrada' restante
            input_view = " ".join([str(t.value) for t in self.tokens[cursor:]])

            # ====================================================
            # LÓGICA PRINCIPAL LL(1)
            # ====================================================

            # CASO 1: Topo é igual ao Token Atual (MATCH)
            if top == token_type:
                action = f"MATCH! ({token_val})"
                self._log_trace(matched_str, stack, input_view, action)
                
                if top == "EOF":
                    print(" Success! Analysis completed.")
                    break # Fim do parser
                
                # Consome pilha e avança entrada
                stack.pop()
                matched_str += token_val + " "
                cursor += 1

            # CASO 2: Topo é Terminal (mas diferente do token) -> ERRO
            elif top not in self.grammar.productions and top != "EOF":
                action = f"ERROR: Expected '{top}', but received '{token_val}'"
                self._log_trace(matched_str, stack, input_view, action)
                # Pânico simples: Desempilha o terminal esperado que falhou
                stack.pop() 

            # CASO 3: Topo é Não-Terminal
            else:
                # Busca na Tabela M[Top, Token]
                production = self.parsing_table.get(top, {}).get(token_type)

                if production is not None:
                    # Regra Encontrada!
                    stack.pop()
                    
                    # Converte produção para string (ex: "A -> B C")
                    prod_str = f"{top} -> {' '.join(production)}"
                    
                    # Empilha a produção INVERTIDA (exceto se for Epsilon)
                    if production != [EPSILON]:
                        for symbol in reversed(production):
                            stack.append(symbol)
                    else:
                        prod_str += " (void)"

                    self._log_trace(matched_str, stack, input_view, prod_str)

                else:
                    # ====================================================
                    # RECUPERAÇÃO DE ERRO (MODO PÂNICO)
                    # ====================================================
                    # Estratégia: 
                    # 1. Se o token atual está no FOLLOW(Top), assume que Top acabou (POP).
                    # 2. Caso contrário, o token atual é lixo. Pula ele (SCAN).
                    
                    follow_set = self.follow.get(top, set())
                    
                    if token_type in follow_set or "EOF" in follow_set:
                        # Sincronização: Desempilha (finge que completou o não-terminal)
                        action = f"ERROR (Panic): Pop {top} (Synchronize via Follow)"
                        self._log_trace(matched_str, stack, input_view, action)
                        stack.pop()
                    else:
                        # Sincronização: Descarta Token (Pula entrada)
                        action = f"ERROR (Panic): Discard '{token_val}'"
                        self._log_trace(matched_str, stack, input_view, action)
                        cursor += 1

    def _log_trace(self, matched, stack, inp, action):
        """Salva o estado atual para a tabela visual."""
        stack_str = " ".join(stack) 
        
        self.trace_data.append({
            "Casamento": matched,
            "Pilha LL(1)": stack_str,
            "Entrada": inp,
            "Ação": action
        })

    def build_execution_table(self):
        """Exibe a tabela final usando Pandas."""
        df = pd.DataFrame(self.trace_data)
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)
        pd.set_option('display.max_colwidth', None)
        
        return df