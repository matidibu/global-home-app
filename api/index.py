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
        Actúa como un Consultor de Viajes Senior. Genera una guía en {idioma} para un {nac} en {dest}.
        Estilo: {estilo}, Perfil: {perfil}.
        Responde estrictamente en JSON:
        {{
            "b": "Bienvenida profesional",
            "requisitos": "Lista de requisitos de entrada (Visas, seguros, pasaporte)",
            "servicios": {{
                "consulado": {{"n": "Consulado de {nac}", "m": "https://www.google.com/maps/search/consulado+{nac}+{dest}"}},
                "hospital": {{"n": "Hospital de Referencia", "m": "https://www.google.com/maps/search/hospital+{dest}"}},
                "policia": {{"n": "Policía Local", "m": "https://www.google.com/maps/search/police+station+{dest}"}}
            }},
            "puntos": [
                {{"n": "Lugar", "h": "Horario", "p": "Precio", "t": "Transporte", "s": "Tip experto", "img_keywords": "famous landmark {dest}"}}
            ]
        }}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500