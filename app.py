from flask import Flask, send_from_directory, request
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

USUARIO = "admin"
CLAVE = "1234"

# Estados iniciales
estados = {
    "vs13": "Abierta","vs14": "Abierta","vs15": "Abierta","vs16": "Abierta",
    "vs17": "Abierta","vs18": "Abierta","vs19": "Abierta","vs20": "Abierta",
    "vs21": "Abierta","vs22": "Abierta","vs23": "Abierta","vs24": "Abierta",
    "vs25": "Abierta","vs26": "Abierta","vs27": "Abierta","vs29": "Abierta",
}

# Historial: cada válvula tendrá una lista de registros
historial = {valvula: [] for valvula in estados}

@app.route("/")
def inicio():
    posiciones = {
        "vs22": (351,126,394,181),"vs27": (498,200,550,237),"vs13": (548,457,579,533),
        "vs23": (599,457,626,532),"vs24": (844,579,876,630),"vs14": (443,547,494,576),
        "vs15": (356,487,390,539),"vs16": (229,448,277,477),"vs26": (139,375,169,426),
        "vs21": (228,330,279,359),"vs17": (227,84,280,118),"vs29": (732,122,782,156),
        "vs25": (908,121,960,150),"vs20": (908,537,960,571),"vs19": (825,202,874,233),
        "vs18": (969,32,1000,79),
    }

    overlays = ""
    for valvula, coords in posiciones.items():
        x1,y1,x2,y2 = coords
        if estados[valvula] == "Abierta":
            overlays += f'<a href="/{valvula}" style="position:absolute; left:{x1}px; top:{y1}px; width:{x2-x1}px; height:{y2-y1}px; background:rgba(0,200,0,0.7); border-radius:5px;"></a>'
        else:
            overlays += f'<a href="/{valvula}" style="position:absolute; left:{x1}px; top:{y1}px; width:{x2-x1}px; height:{y2-y1}px;"></a>'

    return f'''
    <html>
    <head>
        <title>Seccionadoras Agua Contra Incendios</title>
        <style>
            body {{
                font-family: Arial;
                margin:0;
                text-align:center;
                background: url('/fondo') no-repeat center center fixed;
                background-size: contain;
            }}
            header {{ background:#2e7d32; color:white; padding:20px; display:flex; align-items:center; }}
            .logo-container {{ background:white; padding:10px; border-radius:8px; margin-right:30px; }}
            .logo {{ height:60px; }}
            h1 {{ flex:1; text-align:center; margin:0; }}
            .contenedor {{ position:relative; display:inline-block; }}
            .imagen-dti {{ display:block; background:white; opacity:0.85; }}
            footer {{ background:#fbc02d; color:black; padding:10px; position:fixed; bottom:0; width:100%; text-align:center; }}
            a {{ text-decoration:none; }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo-container">
                <img src="/logo" class="logo">
            </div>
            <h1>Diagrama - Seccionadoras Agua Contra-incendios</h1>
        </header>
        <main>
            <div class="contenedor">
                <img src="/imagen" class="imagen-dti">
                {overlays}
            </div>
        </main>
        <footer>
            <p>&copy; 2026 Servicios Auxiliares - Proagroindustria</p>
            <p>Desarrollado por Ing. Angel Valdez Martinez</p>
        </footer>
    </body>
    </html>
    '''

@app.route("/imagen")
def servir_imagen():
    return send_from_directory('.', 'seccionadoras.png')

@app.route("/logo")
def logo():
    return send_from_directory('.', 'logo.png')

@app.route("/fondo")
def fondo():
    return send_from_directory('.', 'fondo.png')

@app.route("/<valvula>", methods=["GET", "POST"])
def mostrar_valvula(valvula):
    if valvula not in estados:
        return "<h2>Válvula no encontrada</h2>"

    if request.method == "POST":
        clave = request.form.get("clave")
        comentario = request.form.get("comentario")

        if clave == CLAVE:  # 🔹 solo se valida la contraseña
            estados[valvula] = "Cerrada" if estados[valvula] == "Abierta" else "Abierta"
            registro = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": estados[valvula],
                "motivo": comentario
            }
            historial[valvula].append(registro)
        else:
            return "<h3>Contraseña incorrecta</h3><p><a href='/'>Volver</a></p>"

    estado = estados[valvula]
    registros = historial.get(valvula, [])

    # Construir tabla de historial
    tabla = "<table border='1' style='margin:auto;'><tr><th>Fecha</th><th>Nuevo Estado</th><th>Motivo</th></tr>"
    for r in registros:
        tabla += f"<tr><td>{r['fecha']}</td><td>{r['estado']}</td><td>{r['motivo']}</td></tr>"
    tabla += "</table>" if registros else "<p>No hay cambios registrados aún.</p>"

    return f'''
        <h2>Válvula {valvula.upper()}</h2>
        <p>Estado actual: {estado}</p>
        <form method="post">
            Contraseña: <input type="password" name="clave"><br>
            Motivo del cambio:<br>
            <textarea name="comentario" rows="3" cols="40"></textarea><br>
            <button type="submit">Cambiar Estado</button>
        </form>
        <h3>Historial de cambios</h3>
        {tabla}
        <p><a href="/">Volver al diagrama</a></p>
    '''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)














