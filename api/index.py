import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Solo necesitamos Groq para esta función rápida
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error de API: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino', 'Madrid')
        nacionalidad = data.get('nacionalidad', 'Argentino')
        
        # Prompt ultra-directo para velocidad máxima
        system_prompt = f"""
        Eres un Concierge de viajes. Usuario: {nacionalidad} a {destino}.
        Responde SOLO un JSON con:
        'bienvenida': saludo corto.
        'puntos_interes': lista de 3 lugares.
        'hospedaje_url': 'https://www.booking.com/search.html?ss={destino}'
        'autos_url': 'https://www.rentalcars.com/search-results?locationName={destino}'
        'tickets_url': 'https://www.civitatis.com/es/busqueda/?q={destino}'
        'emergencia': consejo breve sobre pasaporte {nacionalidad} en {destino}.
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"},
            timeout=20.0 # Esperamos hasta 20 segundos
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "La IA está ocupada. Intenta de nuevo."}), 500

app = app