import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Inicializamos el cliente. Vercel leerá la KEY de las variables de entorno.
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        dest = data.get('destino')
        nac = data.get('nacionalidad')
        estilo = data.get('estilo')
        idioma = data.get('idioma')
        moneda = data.get('moneda')
        perfil = data.get('perfil')

        prompt = f"""
        Actúa como un Concierge VIP de élite. Genera una guía de viaje profesional en {idioma}.
        Destino: {dest}. Viajero de: {nac}. Nivel de servicio: {estilo.upper()}.
        
        INSTRUCCIONES CRÍTICAS:
        1. REQUISITOS: Indica detalladamente visas, pasaporte y salud para un {nac} entrando a {dest}.
        2. MONEDA: En el campo 'p', muestra el precio estimado en: Local de {dest} / {moneda} / USD.
        3. CURADURÍA: Si es PREMIUM, incluye hitos pero con enfoque en exclusividad y servicios VIP.
        
        Responde estrictamente en JSON:
        {{
            "b": "Bienvenida sofisticada y breve",
            "requisitos": "Texto detallado de requisitos legales",
            "puntos": [
                {{
                    "n": "Nombre del lugar",
                    "h": "Horarios",
                    "p": "Costo Local / {moneda} / USD",
                    "t": "Transporte recomendado",
                    "s": "Tip de experto para {perfil}",
                    "gyg_query": "Nombre exacto en inglés para búsqueda de tickets"
                }}
            ]
        }}
        Genera exactamente 5 puntos de interés.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Cargamos el contenido de la IA
        resultado = json.loads(completion.choices[0].message.content)
        return jsonify(resultado)

    except Exception as e:
        # AQUÍ ESTÁ EL CIERRE QUE FALTABA
        print(f"Error detectado: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Esta línea es vital para que Vercel encuentre la app
app = app