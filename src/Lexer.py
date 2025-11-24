import json


class Token:

    def __init__(self, type:str, value:str):
        self.type = type
        self.value = value

    def get_type(self)->str:
        return self.type

    def get_value(self)->str:
        return self.value


class LukeraTokenizer:
    # Dicionários que armazenam os lexemas da linguagem.
    KEYWORDS = {
        # Palavras-chave para a estrutura da linguagem
        'principal': 'MAIN', 'retorna': 'RETURN', 'funcao': 'FUNCAO', 
        
        # Tipos de dados
        'inteiro': 'DTYPE', 'real': 'DTYPE', 'logico': 'DTYPE', 'texto': 'DTYPE',
        
        # Operadores lógicos
        'e': 'AND', 'ou': 'OR', 'nao': 'NOT',
        
        # Loops
        'enquanto': 'WHILE', 'para': 'FOR', 
        
        # Funções embutidas
        'entrada': 'INPUT', 'escreve': 'WRITE', 'aleatorio': 'RANDOM', 'faixa': 'RANGE',
        'absoluto': 'ABS', 'raiz': 'SQRT',
        
        # Valores booleanos
        'verdadeiro': 'BOOL',
        'falso'     : 'BOOL',
        
        # Estruturas condicionais
        'se'      : 'IF',
        'senaose' : 'ELSIF',
        'senao'   : 'ELSE'
    }
    
    # Operadores
    OPERATORS = {
        '+': 'SUM', '-': 'SUB', '*': 'MUL', '/': 'DIV', '^': 'POW', '%': 'MOD', '=': 'EQ', 
        '==': 'ISEQ', '!=': 'DIFF', '>': 'GTHA', '<': 'LTHA', '>=': 'GETHA', '<=': 'LETHA'
    }
    
    # Delimitadores
    DELIMITERS = {
        ':': 'DELIM', ',': 'COMMA', ';': 'SEMI', '(': 'LPAREN', ')': 'RPAREN',
        '[': 'LBRACK', ']': 'RBRACK', '{': 'LBRACE', '}': 'RBRACE'
    }

    # Métodos da classe tokenizer
    def __init__(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text = file.read()
        except FileNotFoundError:
            print(f"Error: File not found at '{file_path}'")
            self.text = ""
        
        self.tokens = []
        self.position = 0
        self.current_char = self.text[self.position] if self.position < len(self.text) else None

    def advance(self):
        """Avança o ponteiro em um caracter no texto"""
        self.position += 1
        self.current_char = self.text[self.position] if self.position < len(self.text) else None

    def peek(self):
        """Olha para o próximo caracter sem avançar o ponteiro."""
        next_pos = self.position + 1
        return self.text[next_pos] if next_pos < len(self.text) else None

    def skip_whitespace(self):
        """Pula todos os caracteres de espaço em branco"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_line_comment(self):
        """Pula toda as linhas de comentário (//...)."""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    def skip_block_comment(self):
        """Pula um bloco de comentário (/* ... */)."""
        self.advance() # Pula o '*'
        
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance() # Pula o '*'
                self.advance() # Pula o '/'
                return # Fim do comentário
            
            # Manipula erros de comentários não fechados
            if self.current_char is None:
                raise Exception("Lexical Error: Unterminated block comment.")
                
            self.advance()

    def read_number(self) -> Token:
        """
        Lê um inteiro ou número flutuante (incluindo anotações científicas)
        INT:   [0-9]+
        FLOAT: [0-9]+ '.' [0-9]+ ( [eE] [+\-]? [0-9]+ )?
        """
        num_str = ""
        
        # Lê a parte inteira
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()

        # Checa pelo número flutuante
        if self.current_char == '.':
            # Checa se o próximo caractere é também um dígito (para 1. vs 1.2)
            if self.peek() and self.peek().isdigit():
                num_str += '.'
                self.advance() # Consume o '.'
                
                # Lê a parte fracionária
                while self.current_char is not None and self.current_char.isdigit():
                    num_str += self.current_char
                    self.advance()
                
                # Checa pela notação científica (e/E)
                if self.current_char in ('e', 'E'):
                    num_str += self.current_char
                    self.advance()
                    
                    # Checa pelo sinal opcional (+/-)
                    if self.current_char in ('+', '-'):
                        num_str += self.current_char
                        self.advance()
                        
                    # Lê os dígitos do expoente
                    while self.current_char is not None and self.current_char.isdigit():
                        num_str += self.current_char
                        self.advance()
                
                return Token(type='FLOAT', value=float(num_str))
            else:
                return Token(type='INTEGER', value=int(num_str))
        
        # Se nenhum '.' foi encontrado, é apenas um inteiro
        return Token(type='INTEGER', value=int(num_str))

    def read_string(self) -> Token:
        """
        Lê uma string literal, manipulando caracteres de escape
        STRING: '"' ( '\\' [btnr"\\] | ~["\\\r\n] )* '"'
        """
        self.advance()
        string_val = ""
        
        while self.current_char is not None and self.current_char != '"':
            
            # Checa pelo caracter de escape
            if self.current_char == '\\':
                self.advance() # Consome o '\'
                
                if self.current_char == 'n':
                    string_val += '\n'
                elif self.current_char == 't':
                    string_val += '\t'
                elif self.current_char == 'b':
                    string_val += '\b'
                elif self.current_char == 'r':
                    string_val += '\r'
                elif self.current_char == '"':
                    string_val += '"'
                elif self.current_char == '\\':
                    string_val += '\\'
                else:
                    # Sequência de escape desconhecida, apenas adiciona o caractere
                    string_val += self.current_char 
            else:
                string_val += self.current_char
                
            self.advance()
            
        if self.current_char != '"':
            raise Exception("Lexical Error: Unterminated string.")
            
        self.advance() # Pula o fechamento "
        return Token(type='STRING', value=string_val)

    def read_word(self) -> Token:
        """
        Lê a uma palavra-chave ou um identificador.
        ID: [a-zA-Z_][a-zA-Z_0-9]*
        """
        word = ""
        # O primeiro caractere já foi checado (isalpha() ou '_') pelo get_next_token
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            word += self.current_char
            self.advance()

        # Checa se é uma palavra-chave (incluindo os booleanos e ifs)    
        token_type = self.KEYWORDS.get(word, 'ID') # Padrão para 'ID'
        
        # Manipula 'verdadeiro'/'falso' que são BOOLs, não DTYPEs ou IDs
        if token_type == 'BOOL':
            return Token(type='BOOL', value=('verdadeiro' if word == 'verdadeiro' else 'falso'))
        
        return Token(type=token_type, value=word)

    def get_next_token(self) -> Token:
        """
        Retorna o próximo token para a stream
        """
        while self.current_char is not None:
            
            # 1. Pula o espaço em branco
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # 2. Pula comentários (// and /*)
            if self.current_char == '/':
                if self.peek() == '/':
                    self.advance() # Consome primeiro /
                    self.advance() # Consome segundo /
                    self.skip_line_comment()
                    continue
                elif self.peek() == '*':
                    self.advance() # Consome /
                    self.advance() # Consome *
                    self.skip_block_comment()
                    continue

            # 3. Números (Inteiros ou Flutuantes)
            if self.current_char.isdigit():
                return self.read_number()

            # 4. Palavras (Palavras-chave, IDs, booleanos)
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_word()
                
            # 5. Strings
            if self.current_char == '"':
                return self.read_string()

            # 6. Operadores (Multi caracter primeiro)
            double_char = self.current_char + (self.peek() or '')
            if double_char in self.OPERATORS:
                op_type = self.OPERATORS[double_char]
                self.advance()
                self.advance()
                return Token(type=op_type, value=double_char)

            # 7. Operadores e delimitadores (únicos caracteres)
            if self.current_char in self.OPERATORS:
                op = self.current_char
                op_type = self.OPERATORS[op]
                self.advance()
                return Token(type=op_type, value=op)
                
            if self.current_char in self.DELIMITERS:
                delim = self.current_char
                delim_type = self.DELIMITERS[delim]
                self.advance()
                return Token(type=delim_type, value=delim)

            # 8. Error
            # Não avança, não avisa. Apenas lança um erro e para.
            invalid_char = self.current_char
            raise Exception(f"Erro Léxico: Caractere inválido '{invalid_char}' na posição {self.position}")
            # --------------------------

        # Fim do arquivo
        return Token(type='EOF', value=None)

    def tokenize(self) -> list[Token]:
        """Método para retornar a lista de todos os tokens"""
        try:
            token = self.get_next_token()
            while token.type != 'EOF':
                self.tokens.append(token)
                token = self.get_next_token()
            self.tokens.append(token) # Adiciona o token EOF
            
        except Exception as e:
            print(e)
            return self.tokens 
            
        return self.tokens
    
    def save_as_json(self, output_file) -> None:
        """Método para salvar a lista de tokens em um arquivo JSON"""
        tokens_collection = [[token.get_type(), token.get_value()] for token in self.tokens]
        
        data = {
            "tokens": tokens_collection
        }

        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)