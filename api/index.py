import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

# Configuración de carpetas para que Flask no se pierda
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Cargamos la API KEY
api_key = os.getenv("GROQ_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # Si no hay API KEY, avisamos de inmediato
        if not api_key:
            return jsonify({"error": "Falta la GROQ_API_KEY en Vercel"}), 500

        client = Groq(api_key=api_key)
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        prompt = f"JSON con: 'b' (bienvenida a {dest}), 'p' (3 puntos interes), 'e' (seguridad para {nac} en {dest})."

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esta línea es para que Vercel reconozca la app
app = app