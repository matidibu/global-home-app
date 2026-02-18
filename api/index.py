import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino')
        nac = data.get('nacionalidad')
        
        prompt = f"""
        Actúa como Concierge VIP de Global Home Assist. Destino: {dest}, Origen: {nac}.
        Responde exclusivamente en este formato JSON:
        {{
            "b": "Bienvenida corta y elegante",
            "req": "Estatus legal/visas para {nac}",
            "puntos": [
                {{
                    "n": "Nombre del lugar",
                    "h": "Breve descripción tipo tip de experto",
                    "p": "Precio aproximado con símbolo",
                    "lat": "Coordenadas o dirección para Maps"
                }}
            ]
        }}
        Genera 6 puntos turísticos.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500