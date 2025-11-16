def shunting_yard(expresion):
    expresion = expresion.split()
    output = []
    operators = []
    precedence = {'*': 3, '/': 3, '%': 3, '+': 2, '-': 2}
    functions = {'max', 'min', 'abs'}
    for token in expresion:
        if token.startswith('v_'):
            output.append(token)
        elif token in functions:
            operators.append(token)
        elif token in precedence:
            while (operators and operators[-1] != '(' and (precedence[operators[-1]] >= precedence[token])):
                output.append(operators.pop())
            operators.append(token)
        elif token == ',':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()
            if operators and operators[-1] in functions:
                output.append(operators.pop())
    while operators:
        output.append(operators.pop())
    return output

def escritura(salida):
    archivo = open("salida.txt", "w")
    for linea in salida:
        archivo.write(linea + "\n")
    archivo.close()
    return

def traduccion(resultado):
    salida = []
    for i in range(len(resultado)):
        ecuacion = resultado[i].split()
        destino = ecuacion[ecuacion.index('=') - 1][1:]
        op1 = ecuacion[ecuacion.index('=') + 1]
        op2 = ecuacion[ecuacion.index('=') + 3][:-1]
        operador = ecuacion[ecuacion.index('=') + 2]

        salida.append(f"MOV A, ({op1})")
        salida.append(f"MOV B, ({op2})")

        if operador == '+':
            salida.append("ADD A, B")
        elif operador == '-':
            salida.append("SUB A, B")
        elif operador == '*':
            salida.append("MUL A, B")
        elif operador == '/':
            salida.append("DIV A, B")
        
        salida.append(f"MOV ({destino}), A")
        salida.append("")
    salida.append(f"MOV A, ({destino})")
    salida.append(f"MOV (result), A")
    return salida

# -----------------------
expresion = 'v_a + v_b * v_c / ( v_d - v_e )'
# expresion = 'v_a - (v_b + v_c - v_d)'
# escritura(traduccion(descomponer(expresion)))
print(shunting_yard(expresion))