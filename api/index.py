import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='../templates')

# Variables de entorno (Configuradas en Vercel)
GROQ_KEY = os.environ.get("GROQ_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

client = Groq(api_key=GROQ_KEY)

def obtener_foto(lugar_busqueda):
    """Busca una imagen real en Unsplash."""
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": lugar_busqueda,
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
    # Imagen de respaldo global si falla la API
    return "https://images.unsplash.com/photo-1500835595367-9917d9c4aaad?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', '').title()
        nac = data.get('nacionalidad', '').title()

        prompt = f"""
        Actúa como un Concierge VIP de Global Home Assist.
        Crea una guía para {dest} para un viajero de {nac}.
        IMPORTANTE: Responde SOLO en formato JSON con esta estructura:
        {{
            "bienvenida": "Texto de bienvenida",
            "requisitos": "Info legal y salud",
            "puntos": [
                {{
                    "n": "Nombre del lugar",
                    "s": "Tip de experto",
                    "p": "Precio estimado"
                }}
            ]
        }}
        Genera exactamente 6 puntos de interés.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        respuesta = json.loads(completion.choices[0].message.content)

        # Buscamos las fotos para cada punto generado
        for punto in respuesta['puntos']:
            # Buscamos por "Lugar + Ciudad" para máxima precisión
            punto['imagen_url'] = obtener_foto(f"{punto['n']} {dest}")

        return jsonify(respuesta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500