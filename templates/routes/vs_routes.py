from flask import Blueprint, render_template, session, redirect, url_for, request
import sqlite3
from datetime import datetime, timedelta, date

vs_bp = Blueprint('vs', __name__)

@vs_bp.route('/vs', methods=["GET", "POST"])
def vs():
    if 'user' not in session:
        return redirect(url_for('login'))

    puntuaciones = {}
    semana_fechas = []

    if request.method == "POST":
        mes = request.form.get("mes")
        dia = request.form.get("dia")
        if mes and dia:
            try:
                lunes_date = datetime.strptime(f"2025-{mes}-{dia}", "%Y-%m-%d")
                semana_fechas = [lunes_date + timedelta(days=i) for i in range(5)]
            except ValueError:
                return "Fecha inválida", 400

            dias_texto = ["lunes", "martes", "miercoles", "jueves", "viernes"]
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            for key in request.form:
                if key.endswith("_score_lunes"):
                    username = key.split("_score_lunes")[0]
                    for i, dia_nombre in enumerate(dias_texto):
                        puntuacion = request.form.get(f"{username}_score_{dia_nombre}")
                        if puntuacion is not None:
                            try:
                                puntuacion_int = int(puntuacion)
                                fecha = semana_fechas[i].strftime('%Y-%m-%d')
                                c.execute("INSERT OR REPLACE INTO puntuaciones (usuario, fecha, puntuacion) VALUES (?, ?, ?)",
                                          (username, fecha, puntuacion_int))
                            except ValueError:
                                pass

            conn.commit()
            conn.close()
            return redirect(url_for('vs.vs', mes=mes, dia=dia))

    mes = request.args.get("mes")
    dia = request.args.get("dia")

    if mes and dia:
        try:
            lunes_date = datetime.strptime(f"2025-{mes}-{dia}", "%Y-%m-%d")
        except ValueError:
            lunes_date = date.today() - timedelta(days=date.today().weekday())
    else:
        lunes_date = date.today() - timedelta(days=date.today().weekday())
        mes = lunes_date.strftime('%m')
        dia = lunes_date.strftime('%d')

    semana_fechas = [lunes_date + timedelta(days=i) for i in range(5)]

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, rank FROM users ORDER BY username ASC")
    members = c.fetchall()

    for fecha in semana_fechas:
        fecha_str = fecha.strftime('%Y-%m-%d')
        c.execute("SELECT usuario, puntuacion FROM puntuaciones WHERE fecha = ?", (fecha_str,))
        for usuario, puntuacion in c.fetchall():
            puntuaciones[(usuario, fecha_str)] = puntuacion

    # Imprimir las fechas y puntuaciones para depuración
    print("Fechas generadas:")
    for fecha in semana_fechas:
        print(fecha.strftime('%Y-%m-%d'))

    print("Puntuaciones cargadas:")
    for key, value in puntuaciones.items():
        print(f"{key} => {value}")

    conn.close()

    return render_template(
        'vs.html',
        members=members,
        semana_fechas=semana_fechas,
        puntuaciones=puntuaciones,
        mes_seleccionado=mes,
        dia_seleccionado=dia
    )
