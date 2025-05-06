
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
from templates.routes.vs_routes import vs_bp

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_d4wn'
app.register_blueprint(vs_bp)

def verificar_usuario_bd(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rank FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def es_usuario_maestro(username, password):
    return username == "ZaKatH" and password == "p0l3ndr4s"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if es_usuario_maestro(username, password):
            session['user'] = 'ZaKatH'
            session['rank'] = 'R6'
            return redirect(url_for('dashboard'))

        rank = verificar_usuario_bd(username, password)
        if rank:
            session['user'] = username
            session['rank'] = rank
            return redirect(url_for('dashboard'))
        else:
            return "⚠️ Usuario o contraseña incorrectos."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'], rank=session['rank'])

@app.route('/registrar', methods=['GET', 'POST'])
def registrar_miembros():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user'] != 'ZaKatH' and session['rank'] not in ['R5', 'R4']:
        return "⛔ Acceso denegado."

    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rank = request.form['rank']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone()
        if exists:
            message = '⚠️ El usuario ya existe.'
        else:
            cursor.execute("INSERT INTO users (username, password, rank) VALUES (?, ?, ?)", (username, password, rank))
            conn.commit()
            message = '✅ Usuario registrado con éxito.'
        conn.close()

    return render_template('registrar.html', message=message)

@app.route('/desert')
def desert():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('seccion.html', titulo="Desert Storm")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
