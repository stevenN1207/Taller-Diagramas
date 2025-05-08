from flask import Flask, render_template, request
import re

app = Flask(__name__)

PALABRAS_CLAVE = {"if", "else", "while", "for", "return", "def", "class", "int", "float"}

# Función de tokenización e identificación
import re

PALABRAS_CLAVE = {"if", "else", "while", "for", "return", "def", "class", "int", "float"}

def interpretar_texto(texto):
    tokens = []
    espacio_total = 0

    operadores_relacionales = {"==", "!=", ">=", "<=", ">", "<"}
    caracteres_especiales = {"(", ")", "{", "}", "[", "]", ";", ":", ".", "+", "-", "*", "/", "%"}

    patron = re.compile(r'''
        ==|!=|>=|<=|>|<                           # operadores relacionales
        | \b(?:if|else|while|for|return|def|class|int|float)\b   # palabras clave
        | \d+\.\d+[eE][+-]?\d+                    # número científico
        | \d+\.\d+                                # número decimal
        | \d+                                     # número entero
        | [a-zA-Z_][a-zA-Z_0-9]*                  # identificadores
        | =                                       # igual (asignación)
        | [(){}\[\];:.\+\-\*/%]                   # caracteres especiales
        | \s+                                     # espacios
        | ,                                       # coma
        | .                                       # cualquier otro
    ''', re.VERBOSE)

    for match in patron.finditer(texto):
        lexema = match.group(0)

        if lexema.isspace():
            espacio_total += len(lexema)

        elif lexema in PALABRAS_CLAVE:
            tokens.append(('palabra_clave', lexema))

        elif lexema in operadores_relacionales:
            nombre_op = {
                '==': 'igual_igual',
                '!=': 'diferente',
                '>=': 'mayor_igual',
                '<=': 'menor_igual',
                '>': 'mayor_que',
                '<': 'menor_que'
            }[lexema]
            tokens.append(('operador_relacional', nombre_op))

        elif lexema == '=':
            tokens.append(('signo_igual', lexema))

        elif lexema in caracteres_especiales:
            tokens.append(('caracter_especial', lexema))

        elif re.fullmatch(r'\d+\.\d+[eE][+-]?\d+', lexema):
            tokens.append(('numero_cientifico', lexema))

        elif re.fullmatch(r'\d+\.\d+', lexema):
            tokens.append(('numero_decimal', lexema))

        elif re.fullmatch(r'\d+', lexema):
            tokens.append(('numero_entero', lexema))

        elif re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*', lexema):
            tokens.append(('identificador', lexema))

        elif lexema == ',':
            tokens.append(('coma', lexema))

        else:
            tokens.append(('desconocido', lexema))

    if espacio_total > 0:
        tokens.append(('espacio', espacio_total))

    return tokens




@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = []
    entrada = ""
    if request.method == 'POST':
        entrada = request.form['entrada'].strip()
        resultado = interpretar_texto(entrada)
    return render_template('index.html', tokens=resultado, entrada=entrada)

if __name__ == '__main__':
    app.run(debug=True)
