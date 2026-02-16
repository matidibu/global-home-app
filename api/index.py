import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest = data.get('destino', 'Madrid')
        nac = data.get('nacionalidad', 'Argentino')
        
        # Le pedimos a la IA toda la data que tenía el Streamlit
        prompt = f"""
        Actúa como guía experto. Para un {nac} en {dest}, responde SOLO un JSON con:
        'b': saludo,
        'clima': breve descripción del clima actual/típico,
        'consulado': dirección o contacto del consulado de {nac} en {dest},
        'hospital': nombre del hospital principal recomendado,
        'p': lista de 3 imperdibles,
        'e': protocolo de emergencia.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app