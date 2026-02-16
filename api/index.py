import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import create_client

# --- CONFIGURACIÓN DE LA APP ---
# Usamos os.path para que Vercel encuentre la carpeta 'templates' sin errores
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

# --- INICIALIZACIÓN DE CLIENTES ---
# Vercel leerá estas variables desde 'Environment Variables'
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""), 
        os.getenv("SUPABASE_KEY", "")
    )
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error cargando configuraciones: {e}")

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino', 'un destino desconocido')
        nacionalidad = data.get('nacionalidad', 'viajero')
        
        # El "System Prompt" define la personalidad de Global Home Assist
        system_prompt = f"""
        Eres el asistente de 'Global Home Assist'. Tu misión es que el usuario se sienta SEGURO y en CASA.
        El usuario es de {nacionalidad} y viaja a {destino}.
        Proporciona:
        1. Un mensaje cálido de bienvenida.
        2. Pasos exactos si pierde su pasaporte (Consulado de {nacionalidad} en {destino}).
        3. Números de emergencia locales.
        4. Un consejo para disfrutar el lugar sin miedos.
        Responde SIEMPRE en formato JSON con estas llaves exactas: 
        'bienvenida', 'pasos_pasaporte', 'emergencias', 'consejo_hogar'.
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        
        # Convertimos la respuesta de la IA a JSON para el frontend
        respuesta_ia = json.loads(completion.choices[0].message.content)
        return jsonify(respuesta_ia)

    except Exception as e:
        print(f"Error en la generación: {e}")
        return jsonify({"error": "No pudimos conectar con el asistente. Reintenta."}), 500

# Esto es vital para que Vercel reconozca la función
app = app