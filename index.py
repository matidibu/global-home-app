from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({"status": "Global Home Assist funcionando"})

# Importante para Vercel
app.debug = True