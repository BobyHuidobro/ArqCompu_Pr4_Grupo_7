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
        instrucciones.append(f"[{Tk} = {izq_temp} {op} {der_temp}]")
        contador += 1
        return Tk, contador

    instrucciones = []
    procesar(expresion, instrucciones, 1)
    return instrucciones




# -----------------------
expresion = 'a + b - (h * (c - d) + (e * (f / g)))'
resultado = descomponer(expresion)
for r in resultado:
    print(r)
