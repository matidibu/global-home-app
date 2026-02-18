import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Configuración de clientes
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def buscar_foto_segura(query):
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": query, "per_page": 1, "client_id": UNSPLASH_KEY}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except:
        pass
    # Foto de respaldo profesional si la API falla o no hay resultados
    return "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Puerto Rico')
        
        # Prompt simplificado para que la IA no invente nombres de campos
        prompt = f"Eres un Concierge VIP. Destino: {dest}. Retorna SOLO un objeto JSON: {{'b': 'bienvenida', 'p': [{{'n': 'nombre', 's': 'descripcion', 'v': 'precio'}}]}}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        res_ia = json.loads(completion.choices[0].message.content)

        # Buscamos las fotos para cada punto
        for punto in res_ia.get('p', []):
            punto['img'] = buscar_foto_segura(f"{punto['n']} {dest}")
            
        return jsonify(res_ia)
    except Exception as e:
        return jsonify({"error": str(e)}), 500