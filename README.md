# 🚀 Ejemplo de CI/CD con GitHub Actions, Docker y Render

Este repositorio demuestra un flujo de trabajo de CI/CD moderno para una aplicación en **Python (Flask)**. A diferencia de un buildpack nativo de Render, este enfoque utiliza **GitHub Actions** para la Integración Continua (CI) y la creación de un **paquete Docker**. Render se encarga del Despliegue Continuo (CD) consumiendo ese paquete.

[Imagen de un pipeline CI/CD con GitHub Actions, Docker y Render]

## 1. Conceptos Clave en este Flujo

* **CI (Continuous Integration):** Ocurre enteramente en **GitHub Actions**. Cada vez que se sube código a la rama `Cristian`, GitHub Actions ejecuta automáticamente las pruebas (`pytest`) para validar la integridad del código.
* **"Package" (El Paquete):** En este flujo, el "paquete" no es código fuente. Es una **imagen de Docker** completa, autocontenida e inmutable. Esta imagen contiene la aplicación, las dependencias de Python y todo lo necesario para ejecutarse.
* **Registro (Container Registry):** Una vez construido, el "paquete" (la imagen Docker) se almacena en un registro. En nuestro caso, es **GitHub Container Registry (GHCR)**.
* **CD (Continuous Deployment):** Ocurre en **Render**. Render está configurado para "observar" nuestro registro de contenedores (GHCR). Cuando detecta una nueva versión de la imagen, la descarga automáticamente, inicia un nuevo contenedor con ella y pone en marcha la aplicación.

## 2. Nuestro Flujo de Trabajo (El Ciclo)

Este es el ciclo detallado, explicando cómo interactúan todos nuestros archivos.

### Paso 1: Desarrollo Local

```
El ciclo comienza con la creación de varios archivos de configuración.
proyecto-flask-docker/
│
├── .github/
│   └── workflows/
│       └── ci.yml          // Define el pipeline de GitHub Actions (CI y Package) 
│
├── app.py                  // La aplicación principal de Flask
├── Dockerfile              // La "configuración" para construir la imagen Docker (Package)
├── README.md               // La documentación del proyecto
├── requirements.txt        // Las dependencias de Python (flask, pytest)
└── test_app.py             // Las pruebas unitarias para la CI
```

1.  El desarrollador crea y modifica la lógica de la aplicación en `app.py`.

    ```python
    # Archivo: app.py
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
    ```

2.  Luego, escribe pruebas unitarias en `test_app.py` para validar esos cambios.

    ```python
    # Archivo: test_app.py
    from app import sumar, restar, multiplicar, dividir

    def test_sumar_enteros_positivos():
        assert sumar(2, 3) == 5

    def test_sumar_negativos():
        assert sumar(-1, -1) == -2

    def test_sumar_con_cero():
        assert sumar(10, 0) == 10

    def test_restar():
        assert restar(10, 5) == 5

    def test_multiplicar():
        assert multiplicar(3, 4) == 12

    def test_dividir_normal():
        assert dividir(10, 2) == 5

    def test_dividir_con_resultado_flotante():
        assert dividir(5, 2) == 2.5

    def test_dividir_por_cero():
        assert dividir(10, 0) == "Error: División por cero"
    ```

3.  Se asegura de que las dependencias estén listadas en `requirements.txt`.

    ```
    # Archivo: requirements.txt
    flask
    pytest
    ```

4.  Ejecuta las pruebas localmente (`pip install -r requirements.txt` y `pytest`) y, si todo pasa, sube los cambios: `git push origin Cristian`.

### Paso 2: Disparador (Trigger) en GitHub Actions

El `git push` a la rama `Cristian` es detectado por GitHub. Esto activa el flujo de trabajo completo definido en `.github/workflows/ci.yml`. Este archivo es el cerebro de todo el proceso de CI/CD.

```yaml
# Archivo: .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches:
      - Cristian

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: 🧾 Checkout repository
      uses: actions/checkout@v3

    - name: 🐍 Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: 📦 Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install flake8

    - name: 🧪 Run tests
      run: pytest

    - name: 🔐 Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: 🏗️ Build and push Docker image
      uses: docker/build-push-action@v6
      with:
        push: true
        tags: ghcr.io/altamiranoyavirac/ejemplo-render:1.0.1
```

### Paso 3: Fase de "Package" (Construcción del Docker Image)

Si las pruebas (CI) son exitosas, el "job" continúa con los pasos de Docker definidos en `ci.yml`:

1. `Login to GitHub Container Registry`: Se autentica en el registro.

2. `Build and push Docker image`: Este paso crucial busca el `Dockerfile` en el repositorio para construir la imagen (el "Package").

Este es el `Dockerfile` que utiliza:

```
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Paso 4: Fase de CI (Pruebas en GitHub Actions)

Como se ve en el archivo `ci.yml` de arriba, un "runner" de GitHub se activa y ejecuta los primeros pasos del `job`:

1. `Checkout repository`: Descarga el código.

2. `Set up Python`: Prepara el entorno de Python 3.10.

3. `Install dependencies`: Instala `flask` y `pytest` desde nuestro `requirements.txt`.

4. `Run tests`: Ejecuta el comando `pytest`.

> **Punto Clave:** Si el paso `pytest` falla (porque una prueba en `test_app.py` falló), el "job" se detiene aquí. El "Package" (imagen Docker) **nunca se construye**.

GitHub Actions usa este archivo para construir la imagen, la etiqueta (`ghcr.io/altamiranoyavirac/ejemplo-render:1.0.1`) y la sube al GitHub Container Registry (GHCR).

### Paso 5: Despliegue (Render)

Finalmente, Render entra en acción:

1. **Configuración:** El servicio en Render está configurado como **"Docker"**.

2. **Conexión:** Apunta a la URL de la imagen en GHCR: `ghcr.io/altamiranoyavirac/ejemplo-render`.

3. **Detección:** Render detecta que una nueva imagen ha sido subida.

4. **Ejecución:** Render descarga la nueva imagen e inicia un contenedor ejecutando el comando `CMD` del `Dockerfile` (es decir, `python app.py`). El nuevo código ya está en producción.


## Nota:

Los archivos y su contendio el cual es explicado en este documento, es encuentra en la Rama `Cristian` de este repositorio.

## Pertenencia

Cristian Alexander Altamirano Venegas

5to "A" Matutina

DEVOPS

