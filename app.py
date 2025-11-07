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
def simple_servidor():

    var_a = request.args.get('a')
    var_b = request.args.get('b')
    
    if not var_a or not var_b:
        return "Servidor funcionando. Por favor, provee 'a' y 'b' en la URL. Ejemplo: /?a=valor1&b=valor2"


    return f"Servidor funcionando. Variable 'a' es: {var_a}, Variable 'b' es: {var_b}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # 'host="0.0.0.0"' es VITAL para Docker y Render
    app.run(host='0.0.0.0', port=port)