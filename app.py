from flask import Flask, send_from_directory, request, redirect, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

USUARIO = "admin"
CLAVE = "1234"

# Estados iniciales
estados = {
    "vs13": "Cerrada","vs14": "Mantenimiento/Reparación","vs15": "Cerrada","vs16": "Cerrada",
    "vs17": "Cerrada","vs18": "Abierta","vs19": "Abierta","vs20": "Abierta",
    "vs21": "Mantenimiento/Reparación","vs22": "Cerrada","vs23": "Abierta","vs24": "Abierta",
    "vs25": "Abierta","vs26": "Cerrada","vs27": "Cerrada","vs29": "Abierta",
}

# Historial
historial = {valvula: [] for valvula in estados}

# 🔹 Función para enviar alertas por correo
def enviar_alerta(valvula, estado, motivo):
    msg = MIMEText(f"La válvula {valvula} cambió a estado {estado}. Motivo: {motivo}")
    msg["Subject"] = f"Alerta: Válvula {valvula} en {estado}"
    msg["From"] = "avalvil2818@gmail.com"
    msg["To"] = "avalvil2818@gmail.com"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("avalvil2818@gmail.com", "ymnh gkfc kthk stfq")  # Contraseña de aplicación
            server.send_message(msg)
    except Exception as e:
        print("Error enviando correo:", e)

@app.route("/")
def inicio():
    posiciones = {
        "vs27": (497,202,550,237),
        "vs29": (733,121,784,156),
        "vs19": (824,200,875,235),
        "vs23": (596,455,626,536),
        "vs13": (550,457,579,534),
        "vs20": (908,535,960,572),
        "vs24": (841,577,877,629),
        "vs14": (443,544,493,579),
        "vs15": (357,488,389,540),
        "vs16": (227,445,279,479),
        "vs26": (136,374,170,427),
        "vs17": (228,85,278,119),
        "vs22": (355,127,390,180),
        "vs25": (905,120,959,153),
        "vs21": (229,327,281,362),
        "vs18": (967,28,1001,83),
    }

    overlays = ""
    for valvula, coords in posiciones.items():
        x1,y1,x2,y2 = coords
        if estados[valvula] == "Abierta":
            color = "rgba(0,200,0,0.7)"   # verde
        elif estados[valvula] == "Mantenimiento/Reparación":
            color = "rgba(255,165,0,0.9)" # naranja
        elif estados[valvula] == "Cerrada":
             color = "rgba(0,0,0,0)"       # transparente
        else:
            color = None
        if color:
            overlays += f'<a href="/{valvula}" style="position:absolute; left:{x1}px; top:{y1}px; width:{x2-x1}px; height:{y2-y1}px; background:{color}; border-radius:5px;"></a>'

    return f'''
    <html>
    <head>
        <title>SECCIONADORAS DE AGUA CONTRA-INCENDIO</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial;
                margin:0;
                text-align:center;
                background: url('/fondo') no-repeat center center fixed;
                background-size: cover;
            }}
            header {{ background:#2e7d32; color:white; padding:20px; display:flex; align-items:center; flex-wrap:wrap; }}
            .logo-container {{ background:white; padding:10px; border-radius:8px; margin-right:30px; }}
            .logo {{ height:60px; }}
            h1 {{ flex:1; text-align:center; margin:0; font-size:1.2em; }}
            .contenedor {{ position:relative; display:inline-block; max-width:100%; }}
            .imagen-dti {{ display:block; max-width:100%; height:auto; background:white; opacity:0.85; }}
            footer {{ background:#fbc02d; color:black; padding:10px; width:100%; text-align:center; position:relative; }}
            a {{ text-decoration:none; }}
            .simbologia {{
                position:relative;
                margin:20px auto;
                background:white;
                border:1px solid #ccc;
                padding:10px;
                border-radius:8px;
                text-align:left;
                max-width:300px;
            }}
            .cuadro {{ display:inline-block; width:20px; height:20px; margin-right:5px; }}
            table {{ width:95%; border-collapse:collapse; margin:auto; }}
            td, th {{ padding:5px; text-align:center; }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo-container">
                <img src="/logo" class="logo">
            </div>
            <h1>SECCIONADORAS DE AGUA CONTRA-INCENDIO</h1>
        </header>
        <main>
            <div class="contenedor">
                <img src="/imagen" usemap="#mapa" class="imagen-dti">
                {overlays}
            </div>
            <div class="simbologia">
                <h3>Simbología</h3>
                <p><span class="cuadro" style="background:rgba(0,200,0,0.7);"></span> Abierta</p>
                <p><span class="cuadro" style="background:rgba(200,0,0,0.7);"></span> Cerrada</p>
                <p><span class="cuadro" style="background:rgba(255,165,0,0.9);"></span> Mantenimiento/Reparación</p>
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

@app.route("/<nombre>.png")
def servir_imagen_valvula(nombre):
    return send_from_directory('.', f"{nombre}.png")

@app.route("/<valvula>", methods=["GET", "POST"])
def mostrar_valvula(valvula):
    if valvula not in estados:
        return "<h2>Válvula no encontrada</h2>"

    if request.method == "POST":
        clave = request.form.get("clave")
        comentario = request.form.get("comentario")
        nuevo_estado = request.form.get("estado")

        if clave == CLAVE:
            estados[valvula] = nuevo_estado if nuevo_estado else estados[valvula]
            registro = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": estados[valvula],
                "motivo": comentario
            }
            historial[valvula].append(registro)
            enviar_alerta(valvula, estados[valvula], comentario)
            return redirect(url_for("mostrar_valvula", valvula=valvula))
        else:
            return "<h3>Contraseña incorrecta</h3><p><a href='/'>Volver</a></p>"

    estado = estados[valvula]
    registros = historial.get(valvula, [])

    if registros:
        tabla = "<table border='1'><tr><th>Fecha</th><th>Nuevo Estado</th><th>Motivo</th></tr>"
        for r in registros:
            tabla += f"<tr><td>{r['fecha']}</td><td>{r['estado']}</td><td>{r['motivo']}</td></tr>"
        tabla += "</table>"
    else:
        tabla = "<p>No hay cambios registrados aún.</p>"

    return f'''
        <h2>VÁLVULA {valvula.upper()}</h2>
        <p>Estado actual: {estado}</p>
                <img src="/{valvula}.png" alt="Imagen {valvula.upper()}"  
               style="max-width:300px; margin:10px auto; display:block;">
        <form method="post">
            Contraseña: <input type="password" name="clave"><br>
            Nuevo estado:
            <select name="estado">
                 <option value="Abierta">Abierta</option>
                 <option value="Cerrada">Cerrada</option>
                 <option value="Mantenimiento/Reparación">Mantenimiento/Reparación</option>
            </select><br>
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




    
















