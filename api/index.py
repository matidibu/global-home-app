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
        # Recuperamos la clave de las variables de entorno de Vercel
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            return jsonify({"error": "No se encontró la GROQ_API_KEY en Vercel"}), 500

        client = Groq(api_key=key)
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        # Prompt super simplificado para evitar errores de la IA
        system_prompt = f"Eres un concierge. Responde solo en JSON con llaves 'b' (bienvenida), 'p' (lista de 3 imperdibles), 'e' (consejo seguridad para {nac} en {dest})."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": system_prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        # Esto nos va a decir el error real en la alerta de la página
        return jsonify({"error": str(e)}), 500

app = app