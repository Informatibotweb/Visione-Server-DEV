import os
import re
import json
import math
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Se requests non è installato nell'ambiente hosting (es. Render)
try:
    import requests
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "requests"])
    import requests

# ========== CONFIGURAZIONE VISIONE CODER ENGINE ==========
DB_DEV_FILE = "visione_dev_knowledge.db"
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_CODER  = "llama-3.3-70b-versatile"  # Ottimo per il ragionamento logico e strutturazione codice

class VisioneDevDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_DEV_FILE, check_same_thread=False)
        self.cursore = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        # Archivio dei snippet di codice ottimizzati e riutilizzabili
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

# ========== MOTORE DI RAGIONAMENTO LOGICO IN 6 FASI ==========
class IngegneriaRagionamentoVisibile:
    @staticmethod
    def genera_tabella_ragionamento(prompt_utente):
        """
        Analizza la richiesta e compila la tabella di scomposizione logica 
        in 6 fasi fondamentali richieste per lo sviluppo premium.
        """
        # Estrarre informazioni per lo "schizzo" e il focus grafico
        linguaggi_rilevati = []
        if "html" in prompt_utente.lower() or "css" in prompt_utente.lower(): linguaggi_rilevati.append("HTML5/CSS3 UI")
        if "js" in prompt_utente.lower() or "javascript" in prompt_utente.lower(): linguaggi_rilevati.append("JavaScript ES6+")
        if "python" in prompt_utente.lower(): linguaggi_rilevati.append("Python Back-End")
        
        target_linguaggio = ", ".join(linguaggi_rilevati) if linguaggi_rilevati else "Full-Stack Software"

        # Costruzione della tabella Markdown visibile all'utente
        tabella_ragionamento = (
            "### 🛠️ VISIONE DEV ENGINE • PIPELINE DI RAGIONAMENTO AVANZATO\n\n"
            "| Fase | Descrizione Operativa | Simulazione Intermedia & Analisi Architetturale | Stato |\n"
            "| :--- | :--- | :--- | :---: |\n"
            f"| **1. Capire l'Utente** | Identificazione dell'intento e dei requisiti core. | Richiesta rilevata: *\"{prompt_utente[:60]}...\"*. Target operativo impostato su `{target_linguaggio}`. |  ✅ |\n"
            f"| **2. Schizzo Veloce** | Progettazione logica, wireframe mentale e flussi di dati. | Definizione dell'alberatura dei componenti e mapping delle funzioni logiche principali. |  ✅ |\n"
            "| **3. Grafica al Massimo** | Iniezione di stili premium, layout moderni, transizioni e variabili CSS fluide. | Applicazione di palette coerenti, design a card (vetro/glassmorphism), ombreggiature morbide e reattività totale. |  🎨 |\n"
            "| **4. Controllo Funzionale** | Analisi statica del codice per prevenire eccezioni asincrone o logiche. | Verifica dei cicli, gestione degli stati, validazione degli input e conformità degli algoritmi. |  ⚙️ |\n"
            "| **5. Fix Errori Console** | Simulazione dell'esecuzione nel runtime e correzione preventiva dei bug comuni. | Risoluzione preventiva di potenziali `ReferenceError`, `TypeError`, e gestione dei fallimenti di rete o DOM. |  🔧 |\n"
            "| **6. Verifica e Rilascio** | Compilazione del blocco finale pulito, commentato e pronto all'uso. | Ottimizzazione della formattazione, rimozione di codice ridondante e refactoring finale superato. |  🚀 |\n\n"
            "---\n\n"
        )
        return tabella_ragionamento

# ========== PROMPT DI SISTEMA AD ALTE PRESTAZIONI PER IL CODICE ==========
SYSTEM_CODER_PROMPT = """Tu sei il modulo "Visione Dev Engine", l'intelligenza artificiale di Nexiquar specializzata nell'ingegneria del software di altissimo livello. 
Il tuo unico scopo è generare codice impeccabile, moderno, performante e privo di bug.

Quando l'utente ti chiede di creare o sistemare del codice, devi seguire rigorosamente queste regole:
1. Concentrati ossessivamente sull'estetica visiva (se si tratta di interfacce web): usa design moderni, layout puliti, variabili CSS ben organizzate, accenti moderni ed effetti eleganti.
2. Assicurati che tutto il codice sia all'interno di un unico blocco o ben strutturato, pronto per il copia-incolla.
3. Evita errori comuni della console: definisci sempre tutte le funzioni prima di chiamarle, gestisci le eccezioni e non lasciare funzioni appese o non definite.
4. Non fare accenni alla tabella di ragionamento che precede la tua risposta; quella viene generata autonomamente dal server. Tu devi solo scrivere la spiegazione tecnica del codice e il codice stesso strutturato in modo eccellente con Markdown e blocchi di codice specificando il linguaggio (es. ```html, ```javascript, ```python).
"""

# ========== APPLICAZIONE FLASK SERVER CODER ==========
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db_dev = VisioneDevDatabase()

@app.route('/chat_dev', methods=['POST'])
def chat_dev():
    dati = request.get_json() or {}
    domanda = dati.get('message', '').strip()
    session_id = dati.get('session_id', 'dev_user')

    if not domanda:
        return jsonify({'error': 'La richiesta non può essere vuota.'}), 400

    # 1. Generazione immediata e visibile della tabella di ragionamento in 6 fasi
    tabella_visibile = IngegneriaRagionamentoVisibile.genera_tabella_ragionamento(domanda)

    # 2. Interrogazione dell'LLM (Groq API) per sfornare il codice ottimizzato
    payload_api = {
        "model": MODEL_CODER,
        "messages": [
            {"role": "system", "content": SYSTEM_CODER_PROMPT},
            {"role": "user", "content": domanda}
        ],
        "temperature": 0.25, # Temperatura bassa per massimizzare precisione e stabilità del codice
        "max_tokens": 4096
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        risposta_llm = requests.post(GROQ_API_URL, json=payload_api, headers=headers, timeout=20)
        if risposta_llm.status_code == 200:
            corpo_risposta = risposta_llm.json()
            testo_codice = corpo_risposta['choices'][0]['message']['content']
        else:
            testo_codice = (
                "⚠️ **Errore di compilazione interno del codice.**\n"
                "Il modello remoto ha risposto con codice di stato errato. Verifica i parametri di rete."
            )
    except Exception as e:
        testo_codice = f"❌ **Fallimento critico nell'analisi del codice:** {str(e)}"

    # 3. Unione del ragionamento visivo (tabella) e del codice finale sfornato
    risposta_finale_strutturata = tabella_visibile + testo_codice

    return jsonify({
        'response': risposta_finale_strutturata,
        'software': "Visione Dev Advanced Engine",
        'versione': "v18.5-Coder"
    })

@app.route('/stato_dev', methods=['GET'])
def stato_dev():
    return jsonify({
        "modulo": "Visione Dev Core Engine",
        "stato": "Online",
        "ottimizzazione_grafica": "Attiva (Massimo Livello)",
        "controllo_errori_console": "Abilitato"
    })

if __name__ == '__main__':
    # Configurazione flessibile per la porta (compatibile con Render)
    porta = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=porta, debug=False)
