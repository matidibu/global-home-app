import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')
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
        idioma = data.get('idioma')
        estilo = data.get('estilo')

        prompt = f"""
        Actúa como un Concierge VIP de nivel internacional. Idioma: {idioma}.
        Destino: {dest}. Viajero de: {nac}. Estilo: {estilo.upper()}.

        REGLAS DE MONEDA:
        - Solo debes mostrar precios en Dólares Estadounidenses (USD) y Euros (EUR).
        - Formato en el campo 'p': "100 USD / 92 EUR".

        Responde estrictamente en JSON:
        {{
            "b": "Bienvenida sofisticada",
            "requisitos": "Visas y salud para {nac} en {dest}",
            "puntos": [
                {{
                    "n": "Nombre del lugar",
                    "h": "Horarios",
                    "p": "Costo en USD / Costo en EUR",
                    "t": "Transporte VIP",
                    "s": "Tip de experto",
                    "gyg_query": "Nombre en inglés para tickets"
                }}
            ]
        }}
        Genera 5 puntos.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500