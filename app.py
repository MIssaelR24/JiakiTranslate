from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "jiaki_secret_key_2026"


# ----------------------------
# ARCHIVOS
# ----------------------------
PALABRAS = "palabras.json"
USUARIOS = "usuarios.json"


# ----------------------------
# CREAR usuarios.json SI NO EXISTE
# ----------------------------
if not os.path.exists(USUARIOS):
    with open(USUARIOS, "w", encoding="utf-8") as f:
        json.dump({}, f)


# ----------------------------
# CARGAR JSON
# ----------------------------
def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


diccionario = cargar_json(PALABRAS)


# ----------------------------
# BUSQUEDA INTELIGENTE
# ----------------------------
def buscar_inteligente(texto):
    texto = texto.lower().strip()
    resultados = []

    if not texto:
        return []

    for esp, yaq in diccionario.items():
        esp_l = esp.lower()
        yaq_l = yaq.lower()

        score = 0

        if texto == esp_l or texto == yaq_l:
            score = 100
        elif esp_l.startswith(texto) or yaq_l.startswith(texto):
            score = 90
        elif texto in esp_l or texto in yaq_l:
            score = 70

        if score > 0:
            resultados.append((score, f"{esp} -> {yaq}"))

    resultados.sort(reverse=True)

    return [r[1] for r in resultados[:5]]


# ----------------------------
# PAGINA PRINCIPAL
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""

    if request.method == "POST":
        palabra = request.form["palabra"].lower().strip()

        if palabra in diccionario:
            resultado = f"Yaqui: {diccionario[palabra]}"
        else:
            for esp, yaq in diccionario.items():
                if palabra == yaq:
                    resultado = f"Español: {esp}"
                    break
            else:
                resultado = "No encontrado"

    usuario = session.get("usuario")

    return render_template(
        "index.html",
        resultado=resultado,
        usuario=usuario
    )


# ----------------------------
# AUTOCOMPLETE API
# ----------------------------
@app.route("/buscar")
def buscar():
    texto = request.args.get("q", "")
    return jsonify(buscar_inteligente(texto))


# ----------------------------
# REGISTRO
# ----------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        password = request.form["password"].strip()

        usuarios = cargar_json(USUARIOS)

        if usuario in usuarios:
            return "Ese usuario ya existe"

        usuarios[usuario] = password

        with open(USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)

        return redirect("/login")

    return render_template("registro.html")


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        password = request.form["password"].strip()

        usuarios = cargar_json(USUARIOS)

        if usuario in usuarios and usuarios[usuario] == password:
            session["usuario"] = usuario
            return redirect("/")

        return "Datos incorrectos"

    return render_template("login.html")


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#@app.route("/agregar", methods=["POST"])
#def agregar():
    if "usuario" not in session:
        return redirect("/login")

    esp = request.form["esp"].lower().strip()
    yaqui = request.form["yaqui"].lower().strip()

    pendientes = cargar_json(pendientes)

    #  todo va a revisión SIEMPRE
    pendientes[esp] = {
        "yaqui": yaqui,
        "usuario": session["usuario"]
    }

    with open(pendientes, "w", encoding="utf-8") as f:
        json.dump(pendientes, f, indent=4, ensure_ascii=False)

    return "Enviado a revisión del administrador"
#@app.route("/admin")
#def admin():
    if session.get("usuario") != "admin":
        return "No autorizado"

    pendientes = cargar_json(pendientes)
    return pendientes

#@app.route("/admin/aceptar/<esp>")
#def aceptar(esp):
    if session.get("usuario") != "admin":
        return "No autorizado"

    diccionario = cargar_json(PALABRAS)
    pendientes = cargar_json(pendientes)

    if esp in pendientes:
        diccionario[esp] = pendientes[esp]["yaqui"]
        del pendientes[esp]

        with open(PALABRAS, "w", encoding="utf-8") as f:
            json.dump(diccionario, f, indent=4, ensure_ascii=False)

        with open(pendientes, "w", encoding="utf-8") as f:
            json.dump(pendientes, f, indent=4, ensure_ascii=False)

    return redirect("/admin")
# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)