from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)

# Clave secreta para sesiones - cámbiala por algo seguro
app.secret_key = "IDC-buscaunaagujaenunpajar"

# Archivo para almacenar mensajes
DB_FILE = "mensajes.json"

# Función de cifrado César
def cifrar_cesar(mensaje, clave):
    resultado = ""
    for letra in mensaje:
        if letra.isalpha():
            base = ord('A') if letra.isupper() else ord('a')
            resultado += chr((ord(letra) - base + clave) % 26 + base)
        else:
            resultado += letra
    return resultado

# Descifrado por fuerza bruta: intenta todas las claves
def fuerza_bruta(mensaje):
    resultados = []
    for clave in range(26):
        descifrado = cifrar_cesar(mensaje, -clave)
        resultados.append(f"Clave {clave:02d}: {descifrado}")
    return resultados

# Cargar mensajes desde archivo JSON
def cargar_mensajes():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Guardar nuevo mensaje en JSON
def guardar_mensaje(nombre, mensaje):
    mensajes = cargar_mensajes()
    mensajes.append({"nombre": nombre, "mensaje": mensaje})
    with open(DB_FILE, "w") as f:
        json.dump(mensajes, f, indent=2)

# Ruta pública: formulario para enviar mensaje cifrado
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para recibir datos POST del formulario
@app.route("/enviar", methods=["POST"])
def enviar():
    nombre = request.form["nombre"]
    mensaje = request.form["mensaje"]
    guardar_mensaje(nombre, mensaje)
    return redirect(url_for("index"))

# Login para administrador (GET muestra formulario, POST verifica clave)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        clave = request.form.get("clave")
        if clave == "12345":  # Cambia esta contraseña
            session["autenticado"] = True
            return redirect(url_for("bandeja"))
        else:
            return render_template("admin_login.html", error=True)
    return render_template("admin_login.html", error=False)

# Bandeja de mensajes (solo si está autenticado)
@app.route("/bandeja")
def bandeja():
    if not session.get("autenticado"):
        return redirect(url_for("admin"))
    mensajes = cargar_mensajes()
    return render_template("admin.html", mensajes=mensajes, fuerza_bruta=fuerza_bruta)

# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("autenticado", None)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    # Ejecuta la app en 0.0.0.0 puerto 3000 con debug activado
    app.run(host="0.0.0.0", port=3000, debug=True)
