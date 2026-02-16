import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# La API KEY debe estar en Vercel como Environment Variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Prompt optimizado para monetización y triple moneda
        prompt = f"""
        Actúa como un Concierge VIP. Genera una guía en {data.get('idioma')}.
        Destino: {data.get('destino')}. Viajero: {data.get('nacionalidad')}. Nivel: {data.get('estilo')}.
        
        Responde estrictamente en JSON:
        {{
            "b": "Bienvenida sofisticada",
            "requisitos": "Requisitos legales detallados",
            "puntos": [
                {{
                    "n": "Nombre Real",
                    "h": "Horarios",
                    "p": "Costo Local / {data.get('moneda')} / USD",
                    "t": "Transporte sugerido",
                    "s": "Tip de experto",
                    "gyg_query": "Nombre exacto en inglés para tickets"
                }}
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