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
        Actúa como un Concierge de Lujo. Destino: {dest}, Viajero: {nac}.
        Responde en JSON con estos campos:
        'b': Bienvenida sofisticada.
        'clima': Breve estado del tiempo.
        'servicios': {{
            'consulado': {{'n': 'Embajada {nac}', 'm': 'https://www.google.com/maps/search/{nac}+embassy+{dest}'}},
            'hospital': {{'n': 'Hospital Privado {dest}', 'm': 'https://www.google.com/maps/search/private+hospital+{dest}'}},
            'policia': {{'n': 'Police Department', 'm': 'https://www.google.com/maps/search/police+station+{dest}'}}
        }},
        'puntos': [{{
            'n': 'Nombre en español', 
            'key': 'Nombre en inglés para buscador de fotos',
            'h': 'Horario', 'p': 'Precio', 't': 'Transporte', 's': 'Tip de lujo',
            'link': 'https://www.civitatis.com/es/{dest}/'
        }}] (Lista de 5)
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app