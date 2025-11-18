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
            while (operators 
                    and operators[-1] != '(' 
                    and operators[-1] not in functions 
                    and precedence[operators[-1]] >= precedence[token]):
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
    operadores = {'+', '-', '*', '/', '%'}
    for token in resultado:
        if token.startswith('v_'):
            salida.append(f"MOV A, ({token})")
            salida.append("PUSH A")

        elif token in operadores:
            if token == '+':
                salida.append("POP B")
                salida.append("POP A")
                salida.append("ADD A, B")
            elif token == '-':
                salida.append("POP B")
                salida.append("POP A")
                salida.append("SUB A, B")
            elif token == '*':
                salida.extend(rutina_mul())
            elif token == '/':
                salida.extend(rutina_div())
            elif token == '%':
                salida.extend(rutina_mod())
            salida.append("PUSH A")

        elif token == 'abs':
            salida.extend(rutina_abs())

        elif token in {'max', 'min'}:
            #salida.append("POP B")
            #salida.append("POP A")
            #salida.append("CMP A, B")
            if token == 'max':
                salida.extend(rutina_max())
            if token == 'min':
                salida.extend(rutina_min())
    salida.append("POP A")
    salida.append(f"MOV (result), A")
    return salida

def rutina_mul():
    return [
        "POP B",
        "POP A",
        "PUSH 0",            # acumulador

        "mul_loop:",
        "CMP B, 0",
        "JEQ mul_end",

        "POP C",
        "ADD C, A",
        "PUSH C",

        "MOV C, 1",
        "SUB B, C",
        "JMP mul_loop",

        "mul_end:",
        "POP A",
        "PUSH A"
    ]


def rutina_div():
    return [
        "POP B",     # divisor
        "POP A",     # dividendo
        "PUSH 0",    # cociente

        "div_loop:",
        "CMP A, B",
        "JLT div_end",

        "SUB A, B",

        "POP C",
        "INC C",
        "PUSH C",

        "JMP div_loop",

        "div_end:",
        "POP A",
        "PUSH A"
    ]


def rutina_mod():
    return [
        "POP B",
        "POP A",

        "mod_loop:",
        "CMP A, B",
        "JLT mod_end",

        "SUB A, B",
        "JMP mod_loop",

        "mod_end:",
        "PUSH A"
    ]


def rutina_abs():
    return [
       "POP A",
        "CMP A, 0",
        "JGE abs_end",
        "MOV B, 0",
        "SUB B, A",
        "MOV A, B",
        "abs_end:",
        "PUSH A"
    ]


def rutina_min():
    return [
        "POP B",
        "POP A",
        "CMP A, B",
        "JLE min_is_a",
        "PUSH B",
        "JMP min_end",
        "min_is_a:",
        "PUSH A",
        "min_end:"
    ]


def rutina_max():
    return [
        "POP B",
        "POP A",
        "CMP A, B",
        "JGE max_is_a",
        "PUSH B",
        "JMP max_end",
        "max_is_a:",
        "PUSH A",
        "max_end:"
    ]


# -----------------------
expresion = "abs ( v_c )"
rpn = shunting_yard(expresion)
codigo = traduccion(rpn)
escritura(codigo)
