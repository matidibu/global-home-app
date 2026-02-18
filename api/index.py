import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def obtener_foto_real(lugar, destino):
    try:
        # Forzamos la búsqueda combinada para que Unsplash no se pierda
        busqueda = f"{lugar} {destino} tourism"
        url = f"https://api.unsplash.com/search/photos?query={busqueda}&per_page=1&client_id={UNSPLASH_KEY}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get('results'):
            return data['results'][0]['urls']['regular']
    except:
        pass
    return "https://images.unsplash.com/photo-1500835595367-9917d9c4aaad?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino', 'Puerto Rico')
        nacionalidad = data.get('nacionalidad', 'viajero')

        prompt = f"""
        Eres el Concierge VIP de Global Home Assist. 
        Crea una guía de lujo para un {nacionalidad} visitando {destino}.
        Responde exclusivamente en JSON:
        {{
            "bienvenida": "Texto corto y elegante de bienvenida",
            "puntos": [
                {{"nombre": "Lugar icónico", "tip": "Consejo VIP", "precio": "Costo aprox"}}
            ]
        }}
        Genera 6 puntos.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        guia = json.loads(completion.choices[0].message.content)

        # Inyectamos fotos reales
        for p in guia['puntos']:
            p['imagen'] = obtener_foto_real(p['nombre'], destino)
            
        return jsonify(guia)
    except Exception as e:
        return jsonify({"error": str(e)}), 500