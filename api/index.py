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
        # Aseguramos que el destino y nacionalidad tengan mayúsculas
        dest = data.get('destino', '').strip().title()
        nac = data.get('nacionalidad', '').strip().title()
        idioma = data.get('idioma', 'Español')
        estilo = data.get('estilo', 'standard')

        prompt = f"""
        Eres un Concierge VIP experto. Genera una guía turística en {idioma}.
        Destino: {dest}. Viajero de: {nac}. Estilo: {estilo.upper()}.
        
        REGLAS CRÍTICAS:
        1. Ortografía perfecta. Nombres de lugares SIEMPRE con Mayúscula.
        2. Precios obligatorios en USD y EUR (ej: 50 USD / 46 EUR).
        3. El campo 'n' debe ser el nombre del lugar.
        
        Responde exclusivamente en este formato JSON:
        {{
            "b": "Bienvenida elegante al viajero",
            "requisitos": "Normativa de visas, salud y aduana para ciudadanos de {nac} que visitan {dest}",
            "puntos": [
                {{
                    "n": "Nombre Del Monumento O Lugar",
                    "p": "Precio USD / EUR",
                    "s": "Tip de experto breve"
                }}
            ]
        }}
        Genera 5 puntos de interés.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500