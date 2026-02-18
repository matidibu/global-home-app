import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

def buscar_foto(q):
    try:
        r = requests.get(f"https://api.unsplash.com/search/photos?query={q}&per_page=1&client_id={UNSPLASH_KEY}", timeout=5)
        return r.json()['results'][0]['urls']['regular']
    except:
        return "https://images.unsplash.com/photo-1500835595367-9917d9c4aaad?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Puerto Rico')
        prompt = f"Concierge VIP. Destino: {dest}. Retorna SOLO JSON: {{'b': 'bienvenida', 'puntos': [{{'n': 'nombre', 's': 'tip', 'p': 'precio'}}]}}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        for p in res['puntos']:
            p['img'] = buscar_foto(f"{p['n']} {dest}")
            
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500