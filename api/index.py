import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # Recuperamos la clave
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return jsonify({"error": "Falta configurar la GROQ_API_KEY en Vercel"}), 500

        # Iniciamos el cliente de IA
        client = Groq(api_key=api_key)
        
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        # Le pedimos a la IA una respuesta ultra-corta para que no tarde
        prompt = f"Responde solo un JSON con estas llaves: 'b' (bienvenida corta a {dest}), 'p' (lista de 3 puntos interes), 'e' (consejo seguridad para {nac} en {dest})."

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))

    except Exception as e:
        # Si la API de Groq da error (por ejemplo, clave inválida o cupo lleno), 
        # lo capturamos y lo enviamos al front-end para saber qué pasó.
        return jsonify({"error": str(e)}), 500

app = app