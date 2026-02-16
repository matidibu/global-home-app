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
        
        prompt = f"""
        Actúa como guía de élite. Para un {nac} en {dest}, responde SOLO un JSON con:
        'b': Bienvenida corta,
        'clima': Descripción del clima,
        'h': Hospital recomendado,
        'c': Consulado de {nac} en {dest},
        'e': Protocolo seguridad,
        'puntos': Una lista de 5 objetos, cada uno con:
           'n': Nombre del lugar,
           'h': Horarios,
           'p': Precio,
           't': Transporte,
           's': Sugerencia experta,
           'link': Link de búsqueda en Civitatis para {dest},
           'maps': Link de Google Maps para el lugar en {dest}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = app