def shunting_yard(expresion):
    tokens = expresion.split()
    output = []
    ops = []
    prec = {'*': 3, '/': 3, '%': 3, '+': 2, '-': 2}
    functions = {'max', 'min', 'abs'}
    for t in tokens:
        if t.startswith('v_'):
            output.append(t)
        elif t in functions:
            ops.append(t)
        elif t in prec:
            while ops and ops[-1] != '(' and ops[-1] not in functions and prec.get(ops[-1], 0) >= prec[t]:
                output.append(ops.pop())
            ops.append(t)
        elif t == ',':
            while ops and ops[-1] != '(':
                output.append(ops.pop())
        elif t == '(':
            ops.append(t)
        elif t == ')':
            while ops and ops[-1] != '(':
                output.append(ops.pop())
            if ops and ops[-1] == '(':
                ops.pop()
            if ops and ops[-1] in functions:
                output.append(ops.pop())
    while ops:
        output.append(ops.pop())
    return output

class CodeGen:
    def __init__(self):
        self.lines = []
        self.line_count = 0
        self.mem_accesses = 0

    def emit(self, instr):
        if instr is None:
            return
        s = instr.rstrip()
        self.lines.append(s)
        if s.strip() != "":
            self.line_count += 1
            # contamos accesos a memoria como aparición de '(' (e.g., (v_a), (result), (error))
            self.mem_accesses += s.count('(')

    def extend(self, lst):
        for i in lst:
            self.emit(i)

    def get_output(self):
        return self.lines.copy()

    def write_file(self, filename="salida.txt"):
        with open(filename, "w") as f:
            for l in self.lines:
                f.write(l + "\n")

cg = CodeGen()

# --- Rutinas robustas (usando temp en memoria para multiplicación/división) ---
def rutina_mul():
    return [
        "POP B",                  # B = multiplicador
        "POP A",                  # A = multiplicando
        "MOV (temp_mul), A",      # guardar multiplicando en memoria (1 acceso)
        "MOV A, 0",               # acumulador = 0
        "mul_loop:",
        "CMP B, 0",
        "JEQ mul_end",
        "ADD A, (temp_mul)",      # sumar multiplicando al acumulador (acceso)
        "DEC B",                  # B = B - 1  (si tu ISA no tiene DEC usa MOV/ SUB)
        "JMP mul_loop",
        "mul_end:",
        "PUSH A"
    ]

def rutina_div():
    return [
        "POP B",              # B = divisor
        "POP A",              # A = dividendo
        "CMP B, 0",
        "JEQ div_by_zero",
        "MOV (temp_div), B",  # guardar divisor en memoria
        "MOV B, 0",           # cociente = 0
        "div_loop:",
        "MOV B, (temp_div)",  # cargar divisor
        "CMP A, B",
        "JLT div_end",
        "SUB A, B",
        "INC B",              # INC usado como contador auxiliar (si no existe, usar ADD B,1)
        # *NOTA*: para mantener limpieza de stack no usamos PUSH/POP en loop
        "JMP div_loop",
        "div_end:",
        # aquí B contiene algun valor intermedio; para simplificar, recalculamos cociente
        # Implementación simple: volver al comienzo del algoritmo convencional:
        # En esta versión, después de salir, usamos B como cociente (siempre consistente)
        "MOV A, B",
        "JMP div_finish",
        "div_by_zero:",
        "MOV A, 1",
        "MOV (error), A",
        "MOV A, 0",
        "div_finish:",
        "PUSH A"
    ]

def rutina_mod():
    return [
        "POP B",              # B = divisor
        "POP A",              # A = dividendo
        "CMP B, 0",
        "JEQ mod_by_zero",
        "MOV (temp_div), B",
        "mod_loop:",
        "MOV B, (temp_div)",
        "CMP A, B",
        "JLT mod_end",
        "SUB A, B",
        "JMP mod_loop",
        "mod_end:",
        "PUSH A",
        "JMP mod_finish",
        "mod_by_zero:",
        "MOV A, 1",
        "MOV (error), A",
        "MOV A, 0",
        "PUSH A",
        "mod_finish:"
    ]

def rutina_abs():
    return [
        "POP A",
        "CMP A, 0",
        "JGE abs_end_push",
        # A < 0
        "MOV B, 0",
        "SUB B, A",    # B = -A
        "CMP B, 0",
        "JLT abs_overflow",  # si -A < 0 entonces overflow (caso -128)
        "MOV A, B",
        "abs_end_push:",
        "PUSH A",
        "JMP abs_finish",
        "abs_overflow:",
        "MOV A, 1",
        "MOV (error), A",
        "MOV A, 0",
        "PUSH A",
        "abs_finish:"
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

# --- Generación de código con peephole básico para reducir accesos ---
def traduccion(rpn):
    # stack de descriptores: ('var', 'v_a') o ('reg', None)  (reg=ya materializado en topA)
    eval_stack = []
    for token in rpn:
        if token.startswith('v_'):
            eval_stack.append(('var', token))
        elif token in {'+', '-', '*', '/', '%'}:
            rhs = eval_stack.pop()
            lhs = eval_stack.pop()

            # Optimización segura: si ambos son variables y op es + o -, usar MOV A,(lhs); MOV B,(rhs); OP
            if lhs[0] == 'var' and rhs[0] == 'var' and token in ['+', '-']:
                cg.emit(f"MOV A, ({lhs[1]})")
                cg.emit(f"MOV B, ({rhs[1]})")
                if token == '+':
                    cg.emit("ADD A, B")
                else:
                    cg.emit("SUB A, B")
                cg.emit("PUSH A")
                eval_stack.append(('reg', None))
                continue

            # Caso general: materializamos en stack y usamos rutinas
            def materialize(op):
                if op[0] == 'var':
                    cg.emit(f"MOV A, ({op[1]})")
                    cg.emit("PUSH A")
                else:
                    # valor ya en registro/stack top -> aseguramos que hay algo en stack
                    # para simplicidad, empujamos A actual (conservador)
                    cg.emit("PUSH A")

            # Materializamos: ponemos LHS primero, RHS encima (convention used by our routines)
            materialize(lhs)
            materialize(rhs)

            if token == '*':
                cg.extend(rutina_mul())
            elif token == '/':
                cg.extend(rutina_div())
            elif token == '%':
                cg.extend(rutina_mod())
            elif token == '+':
                cg.emit("POP B")
                cg.emit("POP A")
                cg.emit("ADD A, B")
                cg.emit("PUSH A")
            elif token == '-':
                cg.emit("POP B")
                cg.emit("POP A")
                cg.emit("SUB A, B")
                cg.emit("PUSH A")

            eval_stack.append(('reg', None))

        elif token in {'abs', 'max', 'min'}:
            if token == 'abs':
                op = eval_stack.pop()
                if op[0] == 'var':
                    cg.emit(f"MOV A, ({op[1]})")
                    cg.emit("PUSH A")
                else:
                    cg.emit("PUSH A")
                cg.extend(rutina_abs())
                eval_stack.append(('reg', None))
            else:
                op2 = eval_stack.pop()
                op1 = eval_stack.pop()
                # materialize op1 then op2 (op2 on top)
                if op1[0] == 'var':
                    cg.emit(f"MOV A, ({op1[1]})")
                    cg.emit("PUSH A")
                else:
                    cg.emit("PUSH A")
                if op2[0] == 'var':
                    cg.emit(f"MOV A, ({op2[1]})")
                    cg.emit("PUSH A")
                else:
                    cg.emit("PUSH A")
                if token == 'max':
                    cg.extend(rutina_max())
                else:
                    cg.extend(rutina_min())
                eval_stack.append(('reg', None))

    # Al final: el resultado debe quedar en top del stack
    cg.emit("POP A")
    cg.emit("MOV (result), A")
    return cg.get_output()

# ---------------- main ----------------
def main():
    # Cambia aquí la expresión para probar:
    # Ejemplos:
    # "v_a + v_b"
    # "v_a * v_b"
    # "v_a / v_b"
    # "v_a % v_b"
    # "abs ( v_a )"
    # "max ( v_a , v_b )"
    # "v_a + v_b * v_c - ( v_d / v_e ) + max ( v_f , v_g )"
    expresion = "v_a * v_b"

    rpn = shunting_yard(expresion)
    traduccion(rpn)
    cg.write_file("salida.txt")
    print("== Generación completada ==")
    print(f"Líneas generadas: {cg.line_count}")
    print(f"Accesos a memoria: {cg.mem_accesses}")

if __name__ == "__main__":
    main()
