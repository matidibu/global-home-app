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
        dest = data.get('destino')
        nac = data.get('nacionalidad')
        estilo = data.get('estilo') # economico, standard, premium
        perfil = data.get('perfil')
        idioma = data.get('idioma', 'Español')
        
        # Lógica de refinamiento de búsqueda para la IA
        contexto_clase = {
            "economico": "enfócate en hostels, comida callejera de alta calidad, museos gratuitos y transporte público eficiente.",
            "standard": "enfócate en hoteles 3-4 estrellas, restaurantes recomendados por locales, tours grupales y comodidad equilibrada.",
            "premium": "enfócate en hoteles de lujo 5 estrellas, experiencias exclusivas, gastronomía de autor, transporte privado y lugares con acceso VIP. Incluye también los hitos históricos pero desde una perspectiva de exclusividad."
        }

        prompt = f"""
        Actúa como un Concierge de Élite. Genera una guía en {idioma} para un {nac} en {dest}.
        Nivel de servicio solicitado: {estilo.upper()}.
        Perfil del viajero: {perfil}.
        
        Criterios de selección para {estilo}: {contexto_clase.get(estilo)}

        Responde en JSON:
        {{
            "b": "Bienvenida acorde al estatus {estilo}",
            "requisitos": "Requisitos legales específicos para {nac}",
            "servicios": {{
                "consulado": {{"n": "Consulado {nac}", "m": "https://www.google.com/maps/search/consulado+{nac}+{dest}"}},
                "hospital": {{"n": "Centro médico de alta complejidad", "m": "https://www.google.com/maps/search/best+hospital+{dest}"}},
                "policia": {{"n": "Estación de policía central", "m": "https://www.google.com/maps/search/police+station+{dest}"}}
            }},
            "puntos": [
                {{
                    "n": "Nombre del lugar", 
                    "h": "Horarios VIP", 
                    "p": "Precio acorde a {estilo}", 
                    "t": "Transporte sugerido", 
                    "s": "Tip de experto",
                    "img_search": "high quality photo of {dest} landmark"
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