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
        
        # Prompt optimizado para asegurar datos
        prompt = f"""
        Como Asesor Senior, genera una guía en {idioma} para un {nac} viajando a {dest}.
        Estilo: {estilo}, Perfil: {perfil}.
        Responde exclusivamente en JSON con esta estructura:
        {{
            "b": "Bienvenida vital",
            "requisitos": "Lista de 3 a 5 requisitos migratorios (Visa, Pasaporte, etc)",
            "servicios": {{
                "consulado": {{"n": "Embajada de {nac}", "m": "https://www.google.com/maps/search/embassy+{nac}+{dest}"}},
                "hospital": {{"n": "Hospital de Referencia", "m": "https://www.google.com/maps/search/hospital+{dest}"}},
                "policia": {{"n": "Seguridad Local", "m": "https://www.google.com/maps/search/police+{dest}"}}
            }},
            "puntos": [
                {{"n": "Nombre", "h": "Horarios", "p": "Precio", "t": "Transporte", "s": "Tip experto", "key": "Nombre en inglés para fotos"}}
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

app = app