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
        dest = data.get('destino', 'San Juan')
        nac = data.get('nacionalidad', 'Argentino')
        moneda_nac = data.get('moneda', 'USD')
        
        prompt = f"""
        Actúa como Concierge VIP de Global Home Assist. Guía para {nac} en {dest}.
        Responde exclusivamente en JSON:
        {{
            "bienvenida": "Texto elegante de bienvenida",
            "requisitos": "Breve estatus legal y visas",
            "puntos": [
                {{
                    "n": "Nombre del Lugar",
                    "h": "Horario VIP",
                    "p": "Precio en Local / {moneda_nac} / USD",
                    "s": "Reseña corta y sofisticada",
                    "img_keyword": "sigla del lugar para buscador de fotos"
                }}
            ]
        }}
        Genera 6 puntos turísticos de alta calidad.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500