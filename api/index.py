import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import create_client

# Configuración de rutas para Vercel
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Inicialización de clientes
try:
    supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error de config: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino', 'Madrid')
        nacionalidad = data.get('nacionalidad', 'Argentino')
        
        # Prompt optimizado para evitar errores de formato
        system_prompt = f"""
        Eres el Concierge experto de 'Global Home Assist'.
        Usuario: {nacionalidad} viajando a {destino}.
        Responde estrictamente en JSON con estas llaves:
        'bienvenida': un saludo corto.
        'puntos_interes': lista de 3 lugares.
        'hospedaje_url': link de búsqueda en Booking para {destino}.
        'autos_url': link de búsqueda en Rentalcars para {destino}.
        'tickets_url': link de búsqueda en Civitatis para {destino}.
        'emergencia': qué hacer si pierde el pasaporte siendo {nacionalidad} en {destino}.
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        print(f"Error detectado: {e}")
        return jsonify({"error": str(e)}), 500

app = app