from flask import Flask, render_template, request, jsonify
from groq import Groq
from supabase import create_client
import os
import json

# 1. Configuración de la App con ruta de templates corregida
app = Flask(__name__, template_folder='../templates')
app.debug = True

# 2. Inicialización de clientes (Vercel lee estas variables de 'Environment Variables')
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""), 
        os.getenv("SUPABASE_KEY", "")
    )
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error configurando clientes: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        destino = data.get('destino')
        nacionalidad = data.get('nacionalidad')
        
        # El "System Prompt" que define la personalidad de tu marca
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
        
        return jsonify(json.loads(completion.choices[0].message.content))
    except Exception as e:
        # Si algo falla, el error aparecerá en los logs de Vercel
        return jsonify({"error": str(e)}), 500

# 3. EL TRUCO PARA VERCEL: Exportar la instancia de la app
# Esto asegura que Vercel encuentre el servidor Flask
app = app