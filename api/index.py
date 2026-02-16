import os
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import create_client

# Configuración de rutas para Vercel
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

def get_ai_response(nacionalidad, destino):
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        
        if not api_key:
            return {"error": "Falta la llave GROQ_API_KEY en Vercel"}

        client = Groq(api_key=api_key)
        
        # ACTUALIZACIÓN: Usamos el modelo llama-3.3-70b-versatile (actualizado a 2026)
        system_prompt = f"""
        Eres 'Global Home Assist'. El usuario es de {nacionalidad} y viaja a {destino}.
        Responde en JSON con estas llaves exactas: 'bienvenida', 'pasos_pasaporte', 'emergencias', 'consejo_hogar'.
        Tono: Contenedor y profesional.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        nacionalidad = data.get('nacionalidad', 'Viajero')
        destino = data.get('destino', 'el mundo')
        
        resultado = get_ai_response(nacionalidad, destino)
        
        if "error" in resultado:
            print(f"Error detectado: {resultado['error']}")
            return jsonify(resultado), 500
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Exportar para Vercel
app = app