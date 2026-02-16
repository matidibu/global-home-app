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
        estilo = data.get('estilo')
        perfil = data.get('perfil')
        idioma = data.get('idioma', 'Español')
        
        prompt = f"""
        Actúa como un Asesor de Viajes Senior. Cliente: {nac}, Destino: {dest}, Estilo: {estilo}, Perfil: {perfil}.
        Idioma: {idioma}.
        Responde en JSON con:
        'b': Bienvenida vital y profesional.
        'requisitos': 'Lista detallada de requisitos de entrada para un {nac} a {dest} (Visa, pasaporte, seguros, etc.)',
        'clima': 'Información climática útil',
        'servicios': {{
            'consulado': {{'n': 'Embajada/Consulado de {nac}', 'm': 'https://www.google.com/maps/search/{nac}+embassy+{dest}'}},
            'hospital': {{'n': 'Hospital de Alta Complejidad', 'm': 'https://www.google.com/maps/search/hospital+{dest}'}},
            'policia': {{'n': 'Centro de Seguridad Local', 'm': 'https://www.google.com/maps/search/police+station+{dest}'}}
        }},
        'puntos': [{{
            'n': 'Lugar', 'h': 'Horarios', 'p': 'Precios aproximados', 't': 'Cómo llegar', 's': 'Consejo de experto para {perfil}',
            'key': 'English location name for photo search',
            'link': 'https://www.civitatis.com/es/{dest}/'
        }}] (5 puntos)
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