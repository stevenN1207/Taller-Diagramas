from flask import Flask, render_template, request

app = Flask(__name__)

PALABRAS_CLAVE = {"if", "else", "while", "for", "return", "def", "class"}

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = ""
    entrada = ""
    tipo = "identificador"
    diagrama = ""

    if request.method == 'POST':
        entrada = request.form['entrada']
        tipo = request.form['tipo']

        if tipo == "identificador":
            diagrama, resultado = analizar_identificador(entrada)
        elif tipo == "numero":
            diagrama, resultado = analizar_numero(entrada)
        elif tipo == "delimitador":
            diagrama, resultado = analizar_delimitadores(entrada)
        elif tipo == "oprel":
            diagrama, resultado = analizar_oprel(entrada)



    return render_template('index.html', resultado=resultado, entrada=entrada, tipo=tipo, diagrama=diagrama)



def analizar_identificador(palabra):
    estados = ["stateDiagram-v2", "direction LR", "[*] --> 1"]
    if not palabra:
        return "\n".join(estados), " Entrada vacía"

    if not palabra[0].isalpha():
        estados.append("1 --> 3: " + palabra[0])
        estados.append("3 --> [*]")
        return "\n".join(estados), f" \"{palabra}\" no es válido: debe comenzar con una letra"

    estados.append(f"1 --> 2: {palabra[0]}")
    valido = True

    for c in palabra[1:]:
        if c.isalnum():
            estados.append(f"2 --> 2: {c}")
        else:
            estados.append(f"2 --> 3: {c}")
            estados.append("3 --> [*]")
            return "\n".join(estados), f" \"{palabra}\" no es válido: carácter inválido \"{c}\""

    estados.append("2 --> 3: (otro)")
    estados.append("3 --> [*]")

    return "\n".join(estados), f" \"{palabra}\" es un identificador válido"




def analizar_delimitadores(cadena):
    estados = ["stateDiagram-v2", "direction LR", "[*] --> 1"]
    estado = 1

    if not cadena:
        return "\n".join(estados), " Entrada vacía"

    for i, c in enumerate(cadena):
        if estado == 1 and c.isspace():
            estados.append(f"1 --> 2: {repr(c)}")
            estado = 2
        elif estado == 2 and c.isspace():
            estados.append(f"2 --> 2: {repr(c)}")
        elif estado == 2 and not c.isspace():
            estados.append(f"2 --> 3: {c}")
            estados.append("3 --> [*]")
            return "\n".join(estados), f" Secuencia válida. Termina al encontrar otro carácter: \"{c}\""
        else:
            estados.append(f"{estado} --> 3: {c}")
            estados.append("3 --> [*]")
            return "\n".join(estados), f" Secuencia inválida en: \"{c}\""

    estados.append("2 --> 3: (fin)")
    estados.append("3 --> [*]")
    return "\n".join(estados), " Solo espacios en blanco detectados correctamente"




def analizar_oprel(cadena):
    estados = ["stateDiagram-v2", "direction LR", "[*] --> 1"]

    if not cadena:
        return "", " Entrada vacía"

    c1 = cadena[0]

    if c1 == "<":
        estados.append("1 --> 2: <")
        if len(cadena) == 2:
            c2 = cadena[1]
            if c2 == "=":
                estados.append("2 --> 3: =")
                estados.append("3 --> [*]")
                return "\n".join(estados), " Operador relacional válido: <="
            elif c2 == ">":
                estados.append("2 --> 3: >")
                estados.append("3 --> [*]")
                return "\n".join(estados), " Operador relacional válido: <>"
            else:
                return "", f" Carácter no válido después de '<': {repr(c2)}"
        elif len(cadena) == 1:
            estados.append("2 --> 3: (otro)")
            estados.append("3 --> [*]")
            return "\n".join(estados), " Operador relacional válido: <"
        else:
            return "", f" Operador muy largo: {repr(cadena)}"

    elif c1 == "=":
        if len(cadena) == 1:
            estados.append("1 --> 2: =")
            estados.append("2 --> 3: (otro)")
            estados.append("3 --> [*]")
            return "\n".join(estados), " Operador relacional válido: ="
        else:
            return "", f" Carácter no válido después de '=': {repr(cadena[1])}"

    elif c1 == ">":
        estados.append("1 --> 2: >")
        if len(cadena) == 2:
            c2 = cadena[1]
            if c2 == "=":
                estados.append("2 --> 3: =")
                estados.append("3 --> [*]")
                return "\n".join(estados), " Operador relacional válido: >="
            else:
                return "", f" Carácter no válido después de '>': {repr(c2)}"
        elif len(cadena) == 1:
            estados.append("2 --> 3: (otro)")
            estados.append("3 --> [*]")
            return "\n".join(estados), " Operador relacional válido: >"
        else:
            return "", f" Operador muy largo: {repr(cadena)}"

    else:
        return "", f" \"{cadena}\" no es un operador relacional válido"









def analizar_numero(cadena):
    estados = ["stateDiagram-v2", "direction LR", "[*] --> 1"]
    estado = 1
    i = 0
    tiene_decimal = False
    tiene_exponente = False

    if not cadena:
        return "\n".join(estados), " Entrada vacía"

    while i < len(cadena):
        c = cadena[i]

        if estado == 1 and c.isdigit():
            estados.append(f"1 --> 2: {c}")
            estado = 2

        elif estado == 2 and c.isdigit():
            estados.append(f"2 --> 2: {c}")

        elif estado in [2] and c == '.' and not tiene_decimal:
            estados.append(f"2 --> 3: {c}")
            estado = 3
            tiene_decimal = True

        elif estado == 3 and c.isdigit():
            estados.append(f"3 --> 4: {c}")
            estado = 4

        elif estado == 4 and c.isdigit():
            estados.append(f"4 --> 4: {c}")

        elif estado in [2, 4] and c in 'Ee' and not tiene_exponente:
            estados.append(f"{estado} --> 5: {c}")
            estado = 5
            tiene_exponente = True

        elif estado == 5 and c in '+-':
            estados.append(f"5 --> 6: {c}")
            estado = 6

        elif estado in [5, 6] and c.isdigit():
            estados.append(f"{estado} --> 7: {c}")
            estado = 7

        elif estado == 7 and c.isdigit():
            estados.append(f"7 --> 7: {c}")

        else:
            estados.append(f"{estado} --> 9: {c}")
            estados.append("9 --> [*]")
            return "\n".join(estados), f" \"{cadena}\" no es un número válido. Error con: \"{c}\""

        i += 1

    estados.append(f"{estado} --> 8: (otro)")
    estados.append("8 --> [*]")
    return "\n".join(estados), f" \"{cadena}\" es un número válido"


if __name__ == '__main__':
    app.run(debug=True)
