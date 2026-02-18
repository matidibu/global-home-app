import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Configuración de Claves
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def buscar_foto_profesional(lugar, ciudad):
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": f"{lugar} {ciudad}", "per_page": 1, "client_id": UNSPLASH_KEY}
        r = requests.get(url, timeout=5)
        data = r.json()
        return data["results"][0]["urls"]["regular"] if data.get("results") else "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
    except:
        return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'San Juan').title()
        nac = data.get('nacionalidad', 'Viajero').title()
        
        prompt = f"""
        Eres un Concierge VIP de 'Global Home Assist'. Crea un itinerario de lujo para un {nac} en {dest}.
        Responde SOLO JSON con esta estructura exacta:
        {{
            "bienvenida": "Texto VIP de bienvenida",
            "puntos": [
                {{"n": "Nombre del lugar", "s": "Resumen elegante", "p": "Precio estimado USD"}}
            ]
        }}
        Genera 6 puntos turísticos reales.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        res_ia = json.loads(completion.choices[0].message.content)

        # Enriquecer con fotos
        for punto in res_ia['puntos']:
            punto['img'] = buscar_foto_profesional(punto['n'], dest)
            
        return jsonify(res_ia)
    except Exception as e:
        return jsonify({"error": str(e)}), 500