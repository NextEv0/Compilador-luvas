parser grammar ExprParser;

options {
  tokenVocab=ExprLexer;
}

// ================================
// PROGRAMA E ESTRUTURA GERAL
// ================================

// Ponto de entrada do programa
programa
  : MAIN LBRACE bloco RBRACE funcao* EOF
  ;

// Bloco principal
bloco
  : comandos
  ;

// Lista de comandos
comandos
  : comando*
  ;

// Comando genérico
comando
  : declaracao               // declaração de variáveis
  | comandoInicioID          // atribuição ou chamada de função de usuário
  | comandoBuiltinChamada    // chamadas WRITE/INPUT/etc como comando
  | condicional
  | laco
  | retorno
  ;

// ================================
// DECLARAÇÕES, ATRIBUIÇÕES E FUNÇÕES
// ================================

// Declaração de variável com tipo (ex: inteiro x = 5;)
declaracao
  : DTYPE ID (EQ expressao)? SEMI
  ;

// Usada em cabeçalho de FOR e internamente
atribuicao
  : ID EQ expressao
  ;

// Comandos que começam com ID: ou é atribuição, ou é chamada de função usuário
comandoInicioID
  : ID comandoInicioIDSufixo
  ;

comandoInicioIDSufixo
  : EQ expressao SEMI              // x = expr;
  | LPAREN argumentos? RPAREN SEMI // x(...);
  ;

// Chamadas de funções pré-definidas como comandos (com ';')
comandoBuiltinChamada
  : WRITE LPAREN argumentos? RPAREN SEMI
  | INPUT LPAREN RPAREN SEMI
  | RANDOM LPAREN argumentos? RPAREN SEMI
  | RANGE LPAREN argumentos? RPAREN SEMI
  | ABS LPAREN argumentos RPAREN SEMI
  | SQRT LPAREN argumentos RPAREN SEMI
  ;

// Definição de função personalizada
funcao
  : FUNCAO DTYPE ID LPAREN parametros? RPAREN LBRACE bloco RBRACE
  ;

parametros
  : parametro (COMMA parametro)*
  ;

parametro
  : DTYPE ID
  ;

argumentos
  : expressao (COMMA expressao)*
  ;

// Comando de retorno
retorno
  : RETURN expressao SEMI
  ;

// ================================
// CONDICIONAIS E LAÇOS
// ================================

condicional
  : IF LPAREN expressao RPAREN LBRACE comandos RBRACE
    (ELSIF LPAREN expressao RPAREN LBRACE comandos RBRACE)*
    (ELSE LBRACE comandos RBRACE)?
  ;

laco
  : WHILE LPAREN expressao RPAREN LBRACE comandos RBRACE
  | FOR LPAREN atribuicao SEMI expressao SEMI atribuicao RPAREN
    LBRACE comandos RBRACE
  ;

// ================================
// EXPRESSÕES (HIERARQUIA LL(1))
// ================================

// Expressão de mais alto nível
expressao
  : exprOr
  ;

// Nível 1: OR (menor precedência)
exprOr
  : exprAnd (OR exprAnd)*
  ;

// Nível 2: AND
exprAnd
  : exprRel (AND exprRel)*
  ;

// Nível 3: comparações == != > < >= <=
exprRel
  : exprAdd
    ( (ISEQ | DIFF | GTHA | LTHA | GETHA | LETHA) exprAdd )*
  ;

// Nível 4: soma/subtração + -
exprAdd
  : exprMul ( (SUM | SUB) exprMul )*
  ;

// Nível 5: multiplicação/divisão/módulo * / %
exprMul
  : exprPow ( (MUL | DIV | MOD) exprPow )*
  ;

// Nível 6: potência ^ (associatividade à direita)
exprPow
  : exprUnary (POW exprPow)?
  ;

// Nível 7: operadores unários NOT e -x
exprUnary
  : NOT exprUnary
  | SUB exprUnary
  | primario
  ;

// Primários: parênteses, chamadas, literais, identificadores
primario
  : LPAREN expressao RPAREN
  | builtinCallExpr
  | ID primarioIdSufixo
  | literal
  ;

// Sufixo depois de ID: ou chamada de função de usuário, ou variável simples
primarioIdSufixo
  : LPAREN argumentos? RPAREN      // chamada de função de usuário: ID(...)
  |                                // ε  (identificador simples)
  ;

// Chamadas de funções pré-definidas em expressão
builtinCallExpr
  : WRITE LPAREN argumentos? RPAREN
  | INPUT LPAREN RPAREN
  | RANDOM LPAREN argumentos? RPAREN
  | RANGE LPAREN argumentos? RPAREN
  | ABS LPAREN argumentos RPAREN
  | SQRT LPAREN argumentos RPAREN
  ;

// Literais (valores base)
literal
  : INTEGER
  | FLOAT
  | BOOL
  | STRING
  ;