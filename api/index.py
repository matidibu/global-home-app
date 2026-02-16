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
        dest = data.get('destino').title()
        nac = data.get('nacionalidad').title()
        idioma = data.get('idioma', 'Español')
        estilo = data.get('estilo', 'standard')

        prompt = f"""
        Concierge VIP. Idioma: {idioma}. Destino: {dest}. Viajero: {nac}. Estilo: {estilo.upper()}.
        REQUISITOS: Ortografía perfecta. Nombres propios con Mayúscula. 
        Costos en USD y EUR obligatoriamente.
        
        Responde en JSON:
        {{
            "b": "Bienvenida elegante",
            "requisitos": "Visas y salud para {nac} en {dest}",
            "puntos": [
                {{
                    "n": "Nombre Del Lugar",
                    "h": "Horarios",
                    "p": "XX USD / XX EUR",
                    "t": "Transporte VIP",
                    "s": "Tip experto",
                    "img_query": "{dest} {estilo} landmark"
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