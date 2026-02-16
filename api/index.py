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
        dest = data.get('destino').title() # Forzamos mayúscula inicial
        nac = data.get('nacionalidad').title()
        estilo = data.get('estilo')

        prompt = f"""
        Actúa como un Concierge VIP Internacional. Idioma: Español.
        Destino: {dest}. Viajero de: {nac}. Estilo: {estilo.upper()}.

        REQUISITOS DE FORMATO:
        - Ortografía perfecta. 
        - Todos los nombres de lugares (campo 'n') DEBEN empezar con Mayúscula.
        - Precios solo en USD y EUR (ej: '45 USD / 42 EUR').

        Responde en JSON:
        {{
            "b": "Bienvenida sofisticada con ortografía impecable.",
            "requisitos": "Requisitos legales detallados para entrar a {dest}.",
            "puntos": [
                {{
                    "n": "Nombre Del Lugar Con Mayúsculas",
                    "h": "Horarios detallados",
                    "p": "Precio USD / Precio EUR",
                    "t": "Transporte sugerido",
                    "s": "Tip de experto con excelente gramática.",
                    "img_search": "high quality photo of {dest} "
                }}
            ]
        }}
        Genera 5 puntos de interés reales.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500