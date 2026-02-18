import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

# Configuración de rutas para Vercel
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
        dest = data.get('destino')
        nac = data.get('nacionalidad')
        estilo = data.get('estilo')
        perfil = data.get('perfil')
        idioma = data.get('idioma')
        moneda_nac = data.get('moneda')
        
        prompt = f"""
        Actúa como un Concierge VIP Internacional. Genera una guía en {idioma}.
        Perfil: {perfil} | Nivel: {estilo.upper()} | Viajero de: {nac}.
        
        INSTRUCCIÓN DE MONEDA:
        Para cada precio mencionado en 'puntos', indica el costo estimado en:
        1. Moneda local de {dest}.
        2. Moneda del viajero ({moneda_nac}).
        3. Dólares Estadounidenses (USD).

        Responde estrictamente en JSON con esta estructura:
        {{
            "b": "Bienvenida cálida y profesional",
            "requisitos": "Visa, pasaportes y tasas para {nac} entrando a {dest}",
            "servicios": {{
                "consulado": {{"n": "Representación de {nac}", "m": "http://googleusercontent.com/maps.google.com/search?q=consulate+{nac}+{dest}"}},
                "hospital": {{"n": "Hospital de Referencia {estilo}", "m": "http://googleusercontent.com/maps.google.com/search?q=hospital+{dest}"}},
                "policia": {{"n": "Seguridad Central", "m": "http://googleusercontent.com/maps.google.com/search?q=police+station+{dest}"}}
            }},
            "puntos": [
                {{
                    "n": "Nombre del lugar", 
                    "h": "Horarios sugeridos", 
                    "p": "Costo en moneda local / {moneda_nac} / USD", 
                    "t": "Transporte recomendado", 
                    "s": "Consejo de experto",
                    "key": "Lugar emblemático de {dest}"
                }}
            ]
        }}
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500