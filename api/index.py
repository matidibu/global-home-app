import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# TU CLAVE DE ACCESO ACTIVADA
UNSPLASH_ACCESS_KEY = "TiIhQkMxP3EEe_RcSsaADorW4HvGDtT1LU3AREOsfus"

def buscar_foto_real(lugar, ciudad):
    try:
        url = "https://api.unsplash.com/search/photos"
        # Buscamos por el nombre del lugar y la ciudad para mayor precisión
        params = {
            "query": f"{lugar} {ciudad} architecture",
            "per_page": 1,
            "orientation": "landscape",
            "client_id": UNSPLASH_ACCESS_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
    except:
        pass
    # Imagen de respaldo si la API falla o no encuentra nada
    return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', '').strip().title()
        nac = data.get('nacionalidad', '').strip().title()
        
        # Prompt optimizado para obtener términos de búsqueda precisos
        prompt = f"""
        Actúa como Concierge VIP. Genera una guía para {dest} (viajero de {nac}).
        Responde estrictamente en JSON con esta estructura:
        {{
            "b": "Bienvenida personalizada",
            "r": "Requisitos de visa/salud",
            "puntos": [
                {{
                    "n": "Nombre del lugar (en mayúsculas)",
                    "p": "Precio en USD/EUR",
                    "s": "Tip experto breve",
                    "q": "Nombre del monumento en INGLÉS para el buscador de fotos"
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
        
        resultado = json.loads(completion.choices[0].message.content)
        
        # INTEGRAMOS LAS FOTOS DE UNSPLASH ANTES DE ENVIAR AL FRONTEND
        for punto in resultado['puntos']:
            punto['imagen_url'] = buscar_foto_real(punto['q'], dest)
            
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500