import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from groq import Groq

# Configuración inicial
app = Flask(__name__, template_folder='../templates')

# Cargamos las llaves desde las Variables de Entorno de Vercel
# Asegúrate de haberlas configurado en el panel de Vercel como:
# GROQ_API_KEY y UNSPLASH_ACCESS_KEY
GROQ_KEY = os.environ.get("GROQ_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

client = Groq(api_key=GROQ_KEY)

def buscar_foto_unsplash(lugar, ciudad):
    """
    Función que conecta con Unsplash para traer la imagen profesional.
    """
    if not UNSPLASH_KEY:
        return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"

    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"{lugar} {ciudad} architecture",
            "per_page": 1,
            "orientation": "landscape",
            "client_id": UNSPLASH_KEY
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Error en Unsplash: {e}")
    
    # Imagen de respaldo si falla la búsqueda
    return "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # 1. Recibir datos del frontend
        data = request.json
        destino = data.get('destino', '').strip().title()
        nacionalidad = data.get('nacionalidad', '').strip().title()

        if not destino or not nacionalidad:
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        # 2. Consultar a la IA (Groq) para generar el contenido
        prompt = f"""
        Actúa como un Concierge VIP de Global Home Assist. 
        Genera una guía de viaje para un ciudadano de {nacionalidad} que visita {destino}.
        
        Responde estrictamente en formato JSON con esta estructura:
        {{
            "bienvenida": "Un saludo elegante y breve",
            "requisitos": "Breve resumen de visas o salud para {nacionalidad} en {destino}",
            "puntos": [
                {{
                    "nombre": "Nombre del monumento o lugar (con mayúsculas)",
                    "precio": "Precio estimado en USD y EUR",
                    "tip": "Consejo experto exclusivo",
                    "busqueda": "Nombre del lugar en inglés para buscador de fotos"
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

        res_ia = json.loads(completion.choices[0].message.content)

        # 3. Integrar las fotos de Unsplash a los resultados de la IA
        for punto in res_ia['puntos']:
            # Usamos el término de búsqueda generado por la IA + la ciudad
            punto['imagen_url'] = buscar_foto_unsplash(punto['busqueda'], destino)

        return jsonify(res_ia)

    except Exception as e:
        print(f"Error General: {e}")
        return jsonify({"error": str(e)}), 500

# Necesario para ejecución local si fuera el caso
if __name__ == "__main__":
    app.run(debug=True)