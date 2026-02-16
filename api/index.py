import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Inicialización rápida
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error API: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        # Prompt conciso para máxima velocidad
        prompt = f"""
        Como Concierge de 'Global Home Assist', ayuda a un {nac} en {dest}.
        Retorna JSON con:
        'bienvenida': saludo corto.
        'puntos': lista de 3 lugares.
        'hospedaje': URL búsqueda Booking para {dest}.
        'autos': URL búsqueda Rentalcars para {dest}.
        'tickets': URL búsqueda Civitatis para {dest}.
        'emergencia': pasos pérdida pasaporte {nac} en {dest}.
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": "Reintenta en un momento"}), 500

app = app