def descomponer(expresion):
    expresion = expresion.replace(' ', '')

    def encontrar_operador(expr):
        profundidad = 0
        candidatos = []
        for i, c in enumerate(expr):
            if c == '(':
                profundidad += 1
            elif c == ')':
                profundidad -= 1
            elif profundidad == 0 and c in '+-*/':
                candidatos.append((i, c))

        for i, c in reversed(candidatos):
            if c in '+-':
                return i, c

        for i, c in reversed(candidatos):
            if c in '*/':
                return i, c
        return None, None

    def limpiar_parentesis(expr):
        while expr.startswith('(') and expr.endswith(')'):

            prof = 0
            balanceado = True
            for i, c in enumerate(expr):
                if c == '(':
                    prof += 1
                elif c == ')':
                    prof -= 1
                    if prof == 0 and i != len(expr) - 1:
                        balanceado = False
                        break
            if not balanceado:
                break
            expr = expr[1:-1]
        return expr

    def procesar(expr, instrucciones, contador):
        expr = limpiar_parentesis(expr)
        i, op = encontrar_operador(expr)
        if op is None:
            return expr, contador

        izquierda = expr[:i]
        derecha = expr[i + 1:]

        izq_temp, contador = procesar(izquierda, instrucciones, contador)
        der_temp, contador = procesar(derecha, instrucciones, contador)

        Tk = f"T{contador}"
        instrucciones.append(f"[{izq_temp} = {izq_temp} {op} {der_temp}]")
        contador += 1
        return izq_temp, contador

    instrucciones = []
    procesar(expresion, instrucciones, 1)
    return instrucciones


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
        salida.append(f"MOV A, {ecuacion[ecuacion.index('=') + 1]}")
        salida.append(f"MOV B, {ecuacion[ecuacion.index('=') + 3][:-1]}")

        operador = ecuacion[ecuacion.index('=') + 2]
        if operador == '+':
            salida.append("ADD A, B")
        elif operador == '-':
            salida.append("SUB A, B")
        elif operador == '*':
            salida.append("MUL A, B")
        elif operador == '/':
            salida.append("DIV A, B")
        
        salida.append(f"MOV {ecuacion[ecuacion.index('=') + 1]}, A")
        salida.append("")
    salida.append(f"MOV result, {ecuacion[ecuacion.index('=') + 1]}")
    return salida

# -----------------------
expresion = 'v_a + v_b - (v_h * (v_c - v_d) + (v_e * (v_f / v_g)))'
escritura(traduccion(descomponer(expresion)))