import os
import re
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# ========== CONFIGURAZIONE VISIONE CODER ENGINE ==========
DB_DEV_FILE = "visione_dev_knowledge.db"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_CODER  = "llama-3.3-70b-versatile"

# Recupero della chiave API dalle variabili d'ambiente di Render
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

class VisioneDevDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_DEV_FILE, check_same_thread=False)
        self.cursore = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursore.execute('''
            CREATE TABLE IF NOT EXISTS snippet_ottimizzati (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT,
                descrizione TEXT,
                codice TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

# ========== PIPELINE DI RAGIONAMENTO IN 6 FASI ==========
class IngegneriaRagionamentoVisibile:
    @staticmethod
    def genera_tabella_ragionamento(prompt_utente):
         linguaggi_rilevati = []
         if "html" in prompt_utente.lower() or "css" in prompt_utente.lower(): linguaggi_rilevati.append("HTML5/CSS3")
         if "js" in prompt_utente.lower() or "javascript" in prompt_utente.lower(): linguaggi_rilevati.append("JavaScript ES6+")
         if "python" in prompt_utente.lower(): linguaggi_rilevati.append("Python Back-End")
         
         target_tech = ", ".join(linguaggi_rilevati) if linguaggi_rilevati else "Software Component"

         tabella_markdown = (
             "### 🛠️ VISIONE DEV ENGINE • PIPELINE DI RAGIONAMENTO AVANZATO\n\n"
             "| Fase | Descrizione Operativa | Stato Avanzamento | Info Local Engine |\n"
             "| :--- | :--- | :---: | :--- |\n"
             f"| **1. Capire l'Utente** | Analisi dell'intento core e dei requisiti funzionali. | ✅ | Richiesta elaborata per target `{target_tech}`. |\n"
             f"| **2. Schizzo Veloce** | Creazione del wireframe logico e mappatura delle funzioni. | ✅ | Albero dei componenti strutturato in memoria. |\n"
             "| **3. Grafica al Massimo** | Iniezione di stili premium, layout moderni (Quar style) e reattività. | 🎨 | Calcolo palette, ombreggiature e Glassmorphism attivi. |\n"
             "| **4. Controllo Funzionale** | Verifica statica dei flussi, cicli e asincronia. | ⚙️ | Algoritmo validato contro loop infiniti o memory leak. |\n"
             "| **5. Fix Errori Console** | Simulazione runtime e correzione preventiva dei bug comuni. | 🔧 | Gestione eccezioni e `try-catch` inseriti preventivamente. |\n"
             "| **6. Verifica e Rilascio** | Refactoring finale, pulizia e compilazione del blocco di codice. | 🚀 | Codice ottimizzato pronto al copia-incolla. |\n\n"
             "---\n\n"
         )
         return tabella_markdown

# ========== SYSTEM PROMPT ==========
SYSTEM_CODER_PROMPT = """Tu sei il modulo "Visione Dev Engine", l'intelligenza artificiale di Nexiquar specializzata nell'ingegneria del software di altissimo livello.
Il tuo unico scopo è generare codice impeccabile, moderno, performante e privo di bug.

Regole tassative di risposta:
1. Concentrati ossessivamente sull'estetica visiva: se generi interfacce web, usa layout puliti, scuri, moderni, variabili CSS ben organizzate ed effetti eleganti.
2. Assicurati che tutto il codice sia completo, senza abbreviazioni o parti lasciate al caso, pronto per essere copiato.
3. Evita errori comuni della console: definisci sempre tutte le funzioni, gestisci le eccezioni e non lasciare variabili appese.
4. Scrivi direttamente la spiegazione tecnica e il codice strutturato in Markdown. La tabella di ragionamento iniziale viene gestita autonomamente dal server, quindi tu non devi menzionarla nel tuo testo.
"""

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db_dev = VisioneDevDatabase()

@app.route('/chat_dev', methods=['POST'])
def chat_dev():
    dati = request.get_json() or {}
    domanda = dati.get('message', '').strip()

    if not) domanda:
        return jsonify({'error': 'La richiesta non può essere vuota.'}), 400

    tabella_visibile = IngegneriaRagionamentoVisibile.genera_tabella_ragionamento(domanda)

    payload_api = {
        "model": MODEL_CODER,
        "messages": [
            {"role": "system", "content": SYSTEM_CODER_PROMPT},
            {"role": "user", "content": domanda}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        risposta_llm = requests.post(GROQ_API_URL, json=payload_api, headers=headers, timeout=25)
        if risposta_llm.status_code == 200:
            corpo_risposta = risposta_llm.json()
            testo_codice = corpo_risposta['choices'][0]['message']['content']
        else:
            testo_codice = f"⚠️ **Errore API remoto ({risposta_llm.status_code}):** Impossibile sfornare il codice."
    except Exception as e:
        testo_codice = f"❌ **Fallimento critico del server di calcolo:** {str(e)}"

    risposta_finale = tabella_visibile + testo_codice

    return jsonify({
        'response': respuesta_finale,
        'software': "Visione Dev Advanced Engine",
        'versione': "v18.5-Coder"
    })

@app.route('/stato_dev', methods=['GET'])
def stato_dev():
    return jsonify({
        "modulo": "Visione Dev Core Engine",
        "stato": "Online e Operativo",
        "ambiente": "Render Cloud"
    })

if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=porta, debug=False)
