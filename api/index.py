import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Configuración de Claves desde Vercel
GROQ_KEY = os.environ.get("GROQ_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

client = Groq(api_key=GROQ_KEY)

def buscar_foto(lugar):
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": lugar, "per_page": 1, "client_id": UNSPLASH_KEY}
        r = requests.get(url, params=params)
        data = r.json()
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
    except:
        pass
    return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Paris').title()
        
        # PROMPT AJUSTADO PARA EVITAR EL "UNDEFINED"
        prompt = f"Genera 5 puntos turísticos para {dest}. Responde SOLO con un JSON con esta estructura: {{'b': 'Bienvenida', 'requisitos': 'Visas', 'puntos': [{{'n': 'Nombre', 's': 'Tip corto', 'p': 'Precio USD'}}]}}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        # Buscamos la foto real para cada punto
        for p in res['puntos']:
            p['imagen_url'] = buscar_foto(f"{p['n']} {dest}")
            
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500