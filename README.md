# Timbrature Tool 🕒

Piccola applicazione desktop per il **calcolo dell’orario di uscita giornaliero** in base alle timbrature effettuate durante la giornata lavorativa.

Pensata per chi:
- timbra l’ingresso manualmente
- **non può consultare l’orario di ingresso dal gestionale fino al giorno successivo**
- vuole sapere con precisione **a che ora uscire per completare le ore giornaliere**

---

## ✨ Funzionalità

- Inserimento:
  - Orario di ingresso
  - Orario di uscita per pausa pranzo
  - Orario di rientro dalla pausa pranzo
  - **Ore lavorative giornaliere** (es. `08:00`, `07:30`, ecc.)
- Calcolo automatico dell’**orario di uscita previsto**
- Persistenza dei dati **giornalieri**
  - Inserisci l’ingresso al mattino
  - Completa i dati dopo la pausa pranzo
- Interfaccia grafica **semplice e minimale**
- Nessun bisogno di diritti di amministratore
- Applicazione **portabile** (un singolo `.exe`)

---

## 🖥️ Interfaccia

GUI realizzata con **Tkinter**:
- input manuale in formato `HH:MM`
- messaggi di errore chiari
- calcolo immediato quando i dati sono completi

---

## 💾 Persistenza dei dati

I dati vengono salvati localmente in un file JSON nella cartella utente:
```bash
%LOCALAPPDATA%\TimbratureTool\state.json
```
Questo garantisce:
- nessun bisogno di permessi amministrativi
- separazione dei dati per giorno (`YYYY-MM-DD`)

---

## ⚙️ Tecnologie utilizzate

- **Python 3**
- **Tkinter** (GUI)
- **PyInstaller** (creazione eseguibile Windows)
- JSON per la persistenza

---

## 🪟 Creazione dell’eseguibile (.exe)

> ⚠️ PyInstaller **non supporta il cross-compiling**  
> L’eseguibile Windows deve essere generato **su Windows**.

### Build su Windows
```bash
pip install pyinstaller
pyinstaller --onefile --windowed timbrature.py
```

L’eseguibile finale si troverà in:
```bash
dist/timbrature.exe
```

---

## 🍎 macOS e Linux
	•	Su macOS viene generata un’app .app
	•	Su Linux un binario ELF
	•	Per ottenere un .exe da macOS:
	•	usare una VM Windows
	•	oppure GitHub Actions con runner Windows

---

## 🤖 Progetto realizzato con AI

Questo progetto è stato progettato e sviluppato con il supporto di un’Intelligenza Artificiale (ChatGPT), utilizzata come:
	•	assistente alla progettazione
	•	supporto allo sviluppo del codice
	•	revisore logico e funzionale

Le scelte architetturali e funzionali sono state guidate da esigenze reali dell’utente finale e validate manualmente.

---

## 📌 Note
	•	Il progetto è pensato per uso personale
	•	Non interagisce con sistemi aziendali o gestionali
	•	Nessun dato viene inviato all’esterno

---

## 📄 Licenza

Uso personale / interno.
Adattabile e modificabile liberamente.

---
