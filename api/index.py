import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Cargamos las llaves desde las variables de entorno de Vercel
GROQ_KEY = os.environ.get("GROQ_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

client = Groq(api_key=GROQ_KEY)

def buscar_foto_unsplash(lugar):
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": lugar, 
            "per_page": 1, 
            "orientation": "landscape",
            "client_id": UNSPLASH_KEY
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Error Unsplash: {e}")
    # Imagen de respaldo si falla la búsqueda
    return "https://images.unsplash.com/photo-1500835595367-9917d9c4aaad?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Panamá').title()
        nac = data.get('nacionalidad', 'Argentino').title()
        
        prompt = f"""
        Eres un Concierge VIP de Global Home Assist.
        Genera una guía para {dest} dirigida a un viajero de nacionalidad {nac}.
        Responde estrictamente en formato JSON con esta estructura:
        {{
            "b": "Mensaje de bienvenida VIP",
            "requisitos": "Breve info sobre visados y salud",
            "puntos": [
                {{
                    "n": "Nombre del monumento o lugar",
                    "s": "Tip exclusivo del lugar",
                    "p": "Precio aprox en USD"
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
        
        guia = json.loads(completion.choices[0].message.content)

        # Inyectamos las URLs de las fotos reales antes de enviar al frontend
        for punto in guia['puntos']:
            punto['imagen_url'] = buscar_foto_unsplash(f"{punto['n']} {dest}")
            
        return jsonify(guia)
    except Exception as e:
        return jsonify({"error": str(e)}), 500