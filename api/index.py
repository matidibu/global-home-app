import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import create_client

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

try:
    supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino', 'Madrid')
        nacionalidad = data.get('nacionalidad', 'Argentino')
        
        system_prompt = f"""
        Eres el Concierge Pro de 'Global Home Assist'. El usuario ({nacionalidad}) viaja a {destino}.
        Tu respuesta debe ser un JSON estricto con:
        1. 'bienvenida': Saludo cálido.
        2. 'puntos_interes': Lista de 3 lugares imperdibles.
        3. 'links': Un objeto con URLs de búsqueda REALES para:
           - 'hospedaje': (Booking.com o Airbnb con el destino)
           - 'autos': (Rentalcars o similar)
           - 'entradas': (Civitatis o GetYourGuide con el destino)
        4. 'emergencia': Pasos para el pasaporte.
        
        IMPORTANTE: Devuelve solo el JSON con estas llaves: 'bienvenida', 'puntos_interes', 'links', 'emergencia'.
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app