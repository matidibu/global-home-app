import os
from flask import Flask, render_template, request, jsonify

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    # ESTO ES UNA PRUEBA SIN IA PARA VER SI EL PUENTE FUNCIONA
    return jsonify({
        "b": "¡Prueba exitosa! El servidor funciona.",
        "p": ["Lugar de prueba 1", "Lugar de prueba 2", "Lugar de prueba 3"],
        "e": "Si ves esto, el problema NO es el código, es la conexión con la API de Groq."
    })

app = app