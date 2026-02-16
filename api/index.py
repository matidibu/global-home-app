import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Cliente Groq ultra-rápido
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        # Prompt simplificado al máximo para evitar timeouts
        prompt = f"Concierge rápido. {nac} en {dest}. Retorna JSON: 'b' (saludo), 'p' (3 puntos interes), 'h' (link booking {dest}), 'a' (link rentalcars {dest}), 't' (link civitatis {dest}), 'e' (seguridad pasaporte {nac} en {dest})."

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2, # Menos creatividad = Más velocidad
            max_tokens=500
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": "Timeout"}), 500

app = app