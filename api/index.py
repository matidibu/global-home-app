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
        # Extraemos variables para personalización extrema
        dest, nac, estilo = data.get('destino'), data.get('nacionalidad'), data.get('estilo')
        perfil, idioma, moneda = data.get('perfil'), data.get('idioma'), data.get('moneda')
        
        prompt = f"""
        Actúa como un Concierge VIP con estándares de GetYourGuide y Forbes Travel Guide.
        Ciudad: {dest}. Viajero: {nac}. Nivel: {estilo}. Idioma: {idioma}.
        
        INSTRUCCIONES DE CURADURÍA:
        - Si es PREMIUM: Solo opciones de exclusividad mundial (Michelin, VIP access, Luxury Cars).
        - Si es ECONOMICO: Opciones inteligentes de alto valor pero bajo costo.
        - MONEDA: Precios en local de {dest}, en {moneda} y en USD.
        
        Responde en JSON:
        {{
            "b": "Bienvenida sofisticada",
            "requisitos": "Visa, salud y aduana detallados",
            "puntos": [
                {{
                    "n": "Nombre Real",
                    "h": "Horarios",
                    "p": "Precios (Local / {moneda} / USD)",
                    "t": "Transporte Elite",
                    "s": "Tip de Insider para {perfil}",
                    "query": "Termino exacto de búsqueda para imagen de alta calidad de {dest}"
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