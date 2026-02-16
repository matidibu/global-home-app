# ... (mantener imports y config inicial)

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        dest, nac, estilo = data.get('destino'), data.get('nacionalidad'), data.get('estilo')
        idioma, moneda = data.get('idioma'), data.get('moneda')
        
        prompt = f"""
        Actúa como un Concierge VIP. Genera una guía en {idioma} para {dest}.
        Estilo: {estilo}. Moneda: {moneda}.
        
        Para cada punto de interés, necesito:
        1. El nombre oficial.
        2. El costo en: Local / {moneda} / USD.
        3. El 'slug' o nombre de búsqueda para GetYourGuide.
        
        Responde en JSON:
        {{
            "b": "Bienvenida",
            "requisitos": "Trámites legales",
            "puntos": [
                {{
                    "n": "Nombre del lugar",
                    "h": "Horarios",
                    "p": "Precios triple moneda",
                    "t": "Transporte",
                    "s": "Tip experto",
                    "oficial": "URL de google search del sitio oficial",
                    "gyg_query": "Nombre exacto en inglés para afiliado"
                }}
            ]
        }}
        """
        # ... (mantener llamada a Groq y return jsonify)