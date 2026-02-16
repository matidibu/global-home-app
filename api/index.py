import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Cliente de IA - Configura GROQ_API_KEY en las variables de entorno de Vercel
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

        # Limpieza de entradas para asegurar mayúsculas
        destino = data.get('destino', '').strip().title()
        nacionalidad = data.get('nacionalidad', '').strip().title()
        estilo = data.get('estilo', 'standard')

        prompt = f"""
        Actúa como un Concierge VIP Internacional. 
        Destino: {destino}. Viajero: {nacionalidad}. Nivel: {estilo.upper()}.
        Idioma: Español.

        REGLAS DE ORO:
        1. ORTOGRAFÍA: Uso impecable de tildes y gramática.
        2. CAPITALIZACIÓN: Todos los nombres de lugares (campo 'n') DEBEN iniciar con Mayúscula.
        3. MONEDA: Mostrar costos únicamente en Dólares (USD) y Euros (EUR). Formato: 'XX USD / XX EUR'.
        4. CURADURÍA: Si el nivel es PREMIUM, priorizar exclusividad. Si es ECONOMICO, valor inteligente.

        Responde estrictamente en JSON:
        {{
            "b": "Bienvenida cálida y profesional.",
            "requisitos": "Documentación, visas y salud para un {nacionalidad} en {destino}.",
            "puntos": [
                {{
                    "n": "Nombre Del Lugar",
                    "h": "Horarios recomendados",
                    "p": "Costo en USD / Costo en EUR",
                    "t": "Transporte sugerido",
                    "s": "Consejo de experto con gramática perfecta."
                }}
            ]
        }}
        Genera exactamente 5 puntos de interés reales.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

app = app