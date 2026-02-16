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
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        prompt = f"""
        Eres un Concierge de Lujo para 'Global Home Assist'.
        Destino: {dest}, Pasajero: {nac}.
        Responde estrictamente en JSON con:
        'b': Bienvenida elegante y tranquilizadora.
        'clima': Info del clima.
        'servicios': {{
            'consulado': {{'info': 'Nombre y dirección', 'maps': 'Link Google Maps'}},
            'hospital': {{'info': 'Nombre y dirección', 'maps': 'Link Google Maps'}},
            'policia': {{'info': 'Estación central/emergencia', 'maps': 'Link Google Maps'}}
        }},
        'puntos': [5 lugares con: 'n' (nombre), 'h' (horario), 'p' (precio), 't' (transporte), 's' (tip), 'img' (URL imagen Unsplash sobre {dest} y el lugar), 'link' (Civitatis), 'maps' (Google Maps)]
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app