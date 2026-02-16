import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

# Configuración de rutas para Vercel
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Inicialización del cliente de IA
# Asegúrate de tener la variable GROQ_API_KEY en tu panel de Vercel
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # 1. Recepción y validación de datos del front-end
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        destino = data.get('destino', 'Paris')
        nacionalidad = data.get('nacionalidad', 'Argentino')
        estilo = data.get('estilo', 'standard')
        perfil = data.get('perfil', 'viajero')
        idioma = data.get('idioma', 'Español')
        moneda_usuario = data.get('moneda', 'USD')

        # 2. Construcción del Prompt con lógica de solvencia y segmentación
        prompt = f"""
        Actúa como un Concierge VIP Internacional de nivel Forbes Travel Guide. 
        Tu misión es diseñar una guía de viaje perfecta en idioma {idioma}.
        
        PERFIL DEL VIAJE:
        - Destino: {destino}
        - Viajero de: {nacionalidad}
        - Estilo de Vida: {estilo.upper()} (Si es PREMIUM, prioriza exclusividad y lujo. Si es ECONOMICO, prioriza valor inteligente).
        - Perfil: {perfil}

        REQUERIMIENTO DE MONEDA:
        En el campo 'p', debes expresar los costos estimados en este orden exacto:
        Moneda Local de {destino} / {moneda_usuario} / USD.

        RESPONDE EXCLUSIVAMENTE EN FORMATO JSON:
        {{
            "b": "Bienvenida sofisticada y breve que refleje solvencia.",
            "requisitos": "Lista detallada de trámites: Visa, pasaporte, vacunas o tasas necesarias para un {nacionalidad} en {destino}.",
            "servicios": {{
                "consulado": {{"n": "Representación de {nacionalidad} en {destino}", "m": "https://www.google.com/maps/search/consulate+{nacionalidad}+{destino}"}},
                "hospital": {{"n": "Hospital de Referencia {estilo}", "m": "https://www.google.com/maps/search/hospital+{destino}"}},
                "policia": {{"n": "Estación de Seguridad Central", "m": "https://www.google.com/maps/search/police+station+{destino}"}}
            }},
            "puntos": [
                {{
                    "n": "Nombre Real del Punto de Interés",
                    "h": "Horarios sugeridos",
                    "p": "Costo Local / {moneda_usuario} / USD",
                    "t": "Transporte recomendado (ej: transfer privado, metro, etc)",
                    "s": "Consejo de experto para {perfil} que no aparece en Google."
                }}
            ]
        }}
        Genera un total de 5 puntos de interés.
        """

        # 3. Llamada a la IA
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        # 4. Procesamiento de la respuesta
        respuesta_ia = json.loads(completion.choices[0].message.content)
        
        return jsonify(respuesta_ia)

    except Exception as e:
        # Registro del error en consola para debugging en Vercel
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({
            "error": "Error interno del Concierge",
            "details": str(e)
        }), 500

# Exportar para Vercel
app = app