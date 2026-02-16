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
        Concierge Premium para {nac} en {dest}. Responde JSON:
        'b': Bienvenida inspiradora.
        'clima': Info clima actual.
        'servicios': {{
            'consulado': {{'n': 'Embajada/Consulado {nac}', 'm': 'https://www.google.com/maps/search/consulado+{nac}+{dest}'}},
            'hospital': {{'n': 'Hospital principal de {dest}', 'm': 'https://www.google.com/maps/search/hospital+{dest}'}},
            'policia': {{'n': 'Policía local de {dest}', 'm': 'https://www.google.com/maps/search/police+{dest}'}}
        }},
        'puntos': [{{
            'n': 'Lugar', 'h': 'Horario', 'p': 'Precio', 't': 'Bus/Metro', 's': 'Tip pro',
            'link': 'https://www.civitatis.com/es/{dest}/'
        }}] (Lista de 5 lugares importantes)
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