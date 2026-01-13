import json
import os
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

DEFAULT_WORK_HHMM = "08:00"

def user_state_path(app_name="TimbratureTool"):
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    folder = os.path.join(base, app_name)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "state.json")

STATE_FILE = user_state_path()

def parse_hhmm_time(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%H:%M").time()
    except ValueError:
        return None

def parse_hhmm_duration(s: str):
    """
    Parse durata in formato HH:MM -> timedelta
    Accetta 0<=HH, 0<=MM<60
    """
    s = s.strip()
    if not s:
        return None
    try:
        parts = s.split(":")
        if len(parts) != 2:
            return None
        hh = int(parts[0])
        mm = int(parts[1])
        if hh < 0 or mm < 0 or mm >= 60:
            return None
        return timedelta(hours=hh, minutes=mm)
    except Exception:
        return None

def fmt_td(td: timedelta) -> str:
    total_minutes = int(td.total_seconds() // 60)
    sign = "-" if total_minutes < 0 else ""
    total_minutes = abs(total_minutes)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{sign}{h:02d}:{m:02d}"

def dt_today(t):
    return datetime.combine(date.today(), t)

def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def today_key():
    return date.today().isoformat()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calcolo uscita (ore giornaliere)")
        self.resizable(False, False)

        self.state_data = load_state()
        self.day = today_key()
        day_state = self.state_data.get(self.day, {})

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, **pad)

        ttk.Label(frm, text=f"Oggi: {self.day}").grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frm, text="Ore giornaliere (HH:MM)").grid(row=1, column=0, sticky="w")
        self.work_var = tk.StringVar(value=day_state.get("ore_giornaliere", DEFAULT_WORK_HHMM))
        ttk.Entry(frm, textvariable=self.work_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Ingresso (HH:MM)").grid(row=2, column=0, sticky="w")
        self.in_var = tk.StringVar(value=day_state.get("ingresso", ""))
        ttk.Entry(frm, textvariable=self.in_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Uscita pranzo (HH:MM)").grid(row=3, column=0, sticky="w")
        self.out_lunch_var = tk.StringVar(value=day_state.get("uscita_pranzo", ""))
        ttk.Entry(frm, textvariable=self.out_lunch_var, width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(frm, text="Rientro pranzo (HH:MM)").grid(row=4, column=0, sticky="w")
        self.in_lunch_var = tk.StringVar(value=day_state.get("rientro_pranzo", ""))
        ttk.Entry(frm, textvariable=self.in_lunch_var, width=10).grid(row=4, column=1, sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Salva", command=self.on_save).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Calcola uscita", command=self.on_calc).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btns, text="Reset oggi", command=self.on_reset_today).grid(row=0, column=2)

        ttk.Separator(frm).grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        self.result_lbl = ttk.Label(frm, text="Uscita prevista: —", font=("Segoe UI", 10, "bold"))
        self.result_lbl.grid(row=7, column=0, columnspan=2, sticky="w")

        self.detail_lbl = ttk.Label(frm, text="", foreground="#555555")
        self.detail_lbl.grid(row=8, column=0, columnspan=2, sticky="w")

        self.try_autocalc()

    def validate_inputs(self):
        work = parse_hhmm_duration(self.work_var.get())
        if work is None or work <= timedelta(0):
            return None, None, None, None, "Inserisci 'Ore giornaliere' valide (HH:MM), es. 08:00."

        t_in = parse_hhmm_time(self.in_var.get())
        t_out_l = parse_hhmm_time(self.out_lunch_var.get())
        t_in_l = parse_hhmm_time(self.in_lunch_var.get())

        if t_in is None:
            return None, None, None, None, "Inserisci un orario di ingresso valido (HH:MM)."

        if (t_out_l is None) ^ (t_in_l is None):
            return None, None, None, None, "Compila entrambi gli orari del pranzo (uscita e rientro) oppure lasciali vuoti."

        if t_out_l and t_in_l:
            dt_in = dt_today(t_in)
            dt_out_l = dt_today(t_out_l)
            dt_in_l = dt_today(t_in_l)
            if not (dt_in <= dt_out_l <= dt_in_l):
                return None, None, None, None, "Gli orari non sono in ordine: ingresso ≤ uscita pranzo ≤ rientro pranzo."

        return work, t_in, t_out_l, t_in_l, None

    def on_save(self):
        work = parse_hhmm_duration(self.work_var.get())
        if work is None or work <= timedelta(0):
            messagebox.showerror("Errore", "Inserisci 'Ore giornaliere' valide (HH:MM), es. 08:00.")
            return

        t_in_raw = self.in_var.get().strip()
        t_out_l_raw = self.out_lunch_var.get().strip()
        t_in_l_raw = self.in_lunch_var.get().strip()

        if parse_hhmm_time(t_in_raw) is None:
            messagebox.showerror("Errore", "Inserisci un orario di ingresso valido (HH:MM).")
            return
        if (t_out_l_raw and parse_hhmm_time(t_out_l_raw) is None) or (t_in_l_raw and parse_hhmm_time(t_in_l_raw) is None):
            messagebox.showerror("Errore", "Formato orario non valido. Usa HH:MM (es. 08:15).")
            return
        if (t_out_l_raw == "" and t_in_l_raw != "") or (t_out_l_raw != "" and t_in_l_raw == ""):
            messagebox.showerror("Errore", "Compila entrambi gli orari del pranzo oppure lasciali vuoti.")
            return

        self.state_data.setdefault(self.day, {})
        self.state_data[self.day]["ore_giornaliere"] = self.work_var.get().strip()
        self.state_data[self.day]["ingresso"] = t_in_raw
        self.state_data[self.day]["uscita_pranzo"] = t_out_l_raw
        self.state_data[self.day]["rientro_pranzo"] = t_in_l_raw
        save_state(self.state_data)

        messagebox.showinfo("Salvato", "Dati salvati.")
        self.try_autocalc()

    def on_calc(self):
        work, t_in, t_out_l, t_in_l, err = self.validate_inputs()
        if err:
            messagebox.showerror("Errore", err)
            return

        dt_in = dt_today(t_in)

        if t_out_l and t_in_l:
            dt_out_l = dt_today(t_out_l)
            dt_in_l = dt_today(t_in_l)

            morning_work = dt_out_l - dt_in
            if morning_work < timedelta(0):
                messagebox.showerror("Errore", "Durata mattina negativa: controlla gli orari.")
                return

            remaining = work - morning_work
            exit_time = dt_in_l + remaining
            pause = dt_in_l - dt_out_l

            self.result_lbl.config(text=f"Uscita prevista: {exit_time.strftime('%H:%M')}")
            self.detail_lbl.config(
                text=f"Target: {fmt_td(work)} | Mattina: {fmt_td(morning_work)} | Pausa: {fmt_td(pause)} | Pomeriggio richiesto: {fmt_td(remaining)}"
            )
        else:
            exit_time = dt_in + work
            self.result_lbl.config(text=f"Uscita prevista (senza pausa): {exit_time.strftime('%H:%M')}")
            self.detail_lbl.config(text=f"Target: {fmt_td(work)} | Inserisci gli orari del pranzo per il calcolo definitivo.")

    def try_autocalc(self):
        work = parse_hhmm_duration(self.work_var.get())
        t_in = parse_hhmm_time(self.in_var.get())
        if not work or not t_in:
            return
        t_out_l = parse_hhmm_time(self.out_lunch_var.get())
        t_in_l = parse_hhmm_time(self.in_lunch_var.get())
        if (t_out_l is None) ^ (t_in_l is None):
            return

        try:
            dt_in = dt_today(t_in)
            if t_out_l and t_in_l:
                dt_out_l = dt_today(t_out_l)
                dt_in_l = dt_today(t_in_l)
                morning_work = dt_out_l - dt_in
                remaining = work - morning_work
                exit_time = dt_in_l + remaining
                pause = dt_in_l - dt_out_l
                self.result_lbl.config(text=f"Uscita prevista: {exit_time.strftime('%H:%M')}")
                self.detail_lbl.config(
                    text=f"Target: {fmt_td(work)} | Mattina: {fmt_td(morning_work)} | Pausa: {fmt_td(pause)} | Pomeriggio richiesto: {fmt_td(remaining)}"
                )
            else:
                exit_time = dt_in + work
                self.result_lbl.config(text=f"Uscita prevista (senza pausa): {exit_time.strftime('%H:%M')}")
                self.detail_lbl.config(text=f"Target: {fmt_td(work)} | Inserisci gli orari del pranzo per il calcolo definitivo.")
        except Exception:
            pass

    def on_reset_today(self):
        if messagebox.askyesno("Reset", "Vuoi cancellare i dati di oggi?"):
            if self.day in self.state_data:
                del self.state_data[self.day]
                save_state(self.state_data)
            self.work_var.set(DEFAULT_WORK_HHMM)
            self.in_var.set("")
            self.out_lunch_var.set("")
            self.in_lunch_var.set("")
            self.result_lbl.config(text="Uscita prevista: —")
            self.detail_lbl.config(text="")

if __name__ == "__main__":
    App().mainloop()
