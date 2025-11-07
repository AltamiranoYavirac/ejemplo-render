import os
from flask import Flask, request



def sumar(a, b):

    return a + b

def restar(a, b):

    return a - b

def multiplicar(a, b):

    return a * b

def dividir(a, b):

    if b == 0:
        return "Error: División por cero"
    return a / b


app = Flask(__name__)


@app.route('/')
def calcular():

    op = request.args.get('op')
    val_a = request.args.get('a')
    val_b = request.args.get('b')

    if not op or not val_a or not val_b:
        return "Servidor funcionando. Por favor, provee 'op', 'a' y 'b'. Ejemplo: /?op=sumar&a=10&b=5"
    
    try:
        a = float(val_a)
        b = float(val_b)
    except ValueError:
        return f"Error: 'a' ('{val_a}') y 'b' ('{val_b}') deben ser números."
    
    resultado = None
    
    if op == 'sumar':
        resultado = sumar(a, b)
    elif op == 'restar':
        resultado = restar(a, b)
    elif op == 'multiplicar':
        resultado = multiplicar(a, b)
    elif op == 'dividir':
        resultado = dividir(a, b) 
    else:
        return f"Error: Operación '{op}' no reconocida. Usa 'sumar', 'restar', 'multiplicar' o 'dividir'."

    return f"La operación fue: {op}<br>a = {a}<br>b = {b}<br><b>Resultado = {resultado}</b>"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)