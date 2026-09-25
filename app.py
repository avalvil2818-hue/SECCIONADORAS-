from flask import Flask, send_from_directory, request, redirect, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "DTI_SECRET_KEY",
    "clave_secreta_super_segura"
)

USUARIO = os.environ.get("DTI_USUARIO", "admin")
CLAVE = os.environ.get("DTI_CLAVE", "DTI-AguaCF!2026#V7mQ")

CORREO_REMITENTE = os.environ.get(
    "DTI_CORREO_REMITENTE",
    "avalvil2818@gmail.com"
)
CORREO_DESTINO = os.environ.get(
    "DTI_CORREO_DESTINO",
    "avalvil2818@gmail.com"
)
CORREO_PASSWORD = os.environ.get(
    "DTI_CORREO_PASSWORD",
    ""
)


# ============================================================
# DATOS DE LAS VÁLVULAS
# ============================================================

CARPETA_APP = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_DATOS = os.path.join(
    CARPETA_APP,
    "datos_valvulas.json"
)

# Estados iniciales
estados_iniciales = {
    "vs13": "Cerrada",
    "vs14": "Mantenimiento/Reparación",
    "vs15": "Cerrada",
    "vs16": "Cerrada",
    "vs17": "Cerrada",
    "vs18": "Abierta",
    "vs19": "Abierta",
    "vs20": "Abierta",
    "vs21": "Mantenimiento/Reparación",
    "vs22": "Cerrada",
    "vs23": "Abierta",
    "vs24": "Abierta",
    "vs25": "Abierta",
    "vs26": "Cerrada",
    "vs27": "Cerrada",
    "vs29": "Abierta",
}


# ============================================================
# CARGAR DATOS GUARDADOS
# ============================================================

def cargar_datos():

    if os.path.exists(ARCHIVO_DATOS):

        try:

            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)

        except Exception as e:

            print("Error leyendo datos_valvulas.json:", e)


    # Si todavía no existe el archivo,
    # se crean los datos iniciales.

    datos = {}

    for valvula, estado in estados_iniciales.items():

        datos[valvula] = {
            "estado": estado,
            "historial": []
        }

    guardar_datos(datos)

    return datos


# ============================================================
# GUARDAR DATOS
# ============================================================

def guardar_datos(datos):

    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:

        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )


# Cargar los datos cuando inicia Flask
datos_valvulas = cargar_datos()


# ============================================================
# ENVIAR CORREO
# ============================================================

def enviar_alerta(
    valvula,
    estado_anterior,
    estado_nuevo,
    motivo
):

    fecha = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    texto = f"""
ALERTA DE VÁLVULA

Válvula:
{valvula.upper()}

Estado anterior:
{estado_anterior}

Nuevo estado:
{estado_nuevo}

Motivo:
{motivo}

Fecha:
{fecha}

Registro para agregar al historial de datos_valvulas.json:

{{
    "fecha": "{fecha}",
    "estado": "{estado_nuevo}",
    "motivo": "{motivo}"
}}
"""

    msg = MIMEText(texto)

    msg["Subject"] = (
        f"Alerta: Válvula {valvula.upper()} "
        f"→ {estado_nuevo}"
    )

    msg["From"] = CORREO_REMITENTE
    msg["To"] = CORREO_DESTINO


    try:

        if not CORREO_PASSWORD:
            print(
                "Correo no enviado: falta DTI_CORREO_PASSWORD."
            )
            return

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                CORREO_REMITENTE,
                CORREO_PASSWORD
            )

            server.send_message(msg)

        print(
            f"Correo enviado: {valvula.upper()}"
        )

    except Exception as e:

        print(
            "Error enviando correo:",
            e
        )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def inicio():

    posiciones = {

        "vs27": (497, 202, 550, 237),
        "vs29": (725, 204, 777, 242),
        "vs19": (914, 198, 967, 236),
        "vs23": (596, 455, 626, 536),
        "vs13": (550, 457, 579, 534),
        "vs20": (908, 535, 960, 572),
        "vs24": (841, 577, 877, 629),
        "vs14": (443, 544, 493, 579),
        "vs15": (357, 488, 389, 540),
        "vs16": (227, 445, 279, 479),
        "vs26": (136, 374, 170, 427),
        "vs17": (228, 85, 278, 119),
        "vs22": (355, 127, 390, 180),
        "vs25": (1048, 161, 1100, 199),
        "vs21": (229, 327, 281, 362),
        "vs18": (896, 26, 947, 61),

    }


    overlays = ""


    for valvula, coords in posiciones.items():

        x1, y1, x2, y2 = coords

        estado_actual = datos_valvulas[valvula]["estado"]


        # -------------------------------
        # COLOR SEGÚN ESTADO
        # -------------------------------

        if estado_actual == "Abierta":

            color = "rgba(0,200,0,0.7)"


        elif estado_actual == "Mantenimiento/Reparación":

            color = "rgba(255,165,0,0.9)"


        elif estado_actual == "Cerrada":

            color = "rgba(200,0,0,0.7)"


        else:

            color = "rgba(100,100,100,0.5)"


        overlays += f'''
        <a
            href="/{valvula}"
            title="Válvula {valvula.upper()} - {estado_actual}"
            style="
                position:absolute;
                left:{x1}px;
                top:{y1}px;
                width:{x2-x1}px;
                height:{y2-y1}px;
                background:{color};
                border-radius:5px;
            "
        ></a>
        '''


    return f'''
    <html>

    <head>

        <title>
            SECCIONADORAS DE AGUA CONTRA-INCENDIO
        </title>


        <style>

            body {{
                font-family: Arial;
                margin: 0;
                text-align: center;
                background: #eeeeee;
            }}


            /* -------------------------------
               FONDO
            -------------------------------- */

            .fondo {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url('/fondo');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
                z-index: -1;
            }}


            /* -------------------------------
               ENCABEZADO
            -------------------------------- */

            header {{
                background: #2e7d32;
                color: white;
                padding: 20px;
                display: flex;
                align-items: center;
            }}


            .logo-container {{
                background: white;
                padding: 10px;
                border-radius: 8px;
                margin-right: 30px;
            }}


            .logo {{
                height: 60px;
            }}


            h1 {{
                flex: 1;
                text-align: center;
                margin: 0;
            }}


            /* -------------------------------
               DTI
            -------------------------------- */

            .contenedor {{
                position: relative;
                display: inline-block;
                margin-top: 20px;
            }}


            .imagen-dti {{
                display: block;
                background: white;
                opacity: 0.85;
            }}


            /* -------------------------------
               SIMBOLOGÍA
            -------------------------------- */

            .simbologia {{

                background: white;

                border: 1px solid #ccc;

                padding: 10px 20px;

                border-radius: 8px;

                text-align: left;

                margin: 20px auto 100px auto;

                width: fit-content;

                box-shadow: 0 2px 6px rgba(0,0,0,0.2);

            }}


            .simbologia h3 {{
                text-align: center;
                margin-top: 5px;
            }}


            .cuadro {{
                display: inline-block;
                width: 20px;
                height: 20px;
                margin-right: 5px;
                vertical-align: middle;
                border-radius: 3px;
            }}


            /* -------------------------------
               PIE DE PÁGINA
            -------------------------------- */

            footer {{
                background: #fbc02d;
                color: black;
                padding: 10px;
                position: fixed;
                bottom: 0;
                width: 100%;
                text-align: center;
                z-index: 10;
            }}


            footer p {{
                margin: 3px;
            }}


            a {{
                text-decoration: none;
            }}

        </style>

    </head>


    <body>

        <div class="fondo"></div>


        <!-- ENCABEZADO -->

        <header>

            <div class="logo-container">

                <img
                    src="/logo"
                    class="logo"
                >

            </div>


            <h1>
                SECCIONADORAS DE AGUA CONTRA-INCENDIO
            </h1>

        </header>


        <!-- DTI -->

        <main>

            <div class="contenedor">

                <img
                    src="/imagen"
                    usemap="#mapa"
                    class="imagen-dti"
                >

                {overlays}


                <map name="mapa">

                    <area
                        alt="Torre de enfriamiento norte"
                        title="Torre de enfriamiento norte"
                        href=""
                        coords="405,260,485,341"
                        shape="rect"
                    >

                    <area
                        alt="Torre de enfriamiento sur"
                        title="Torre de enfriamiento sur"
                        href=""
                        coords="401,383,491,465"
                        shape="rect"
                    >

                    <area
                        alt="Llenaderas"
                        title="Llenaderas"
                        href=""
                        coords="825,375,961,425"
                        shape="rect"
                    >

                    <area
                        alt="Caldera 3"
                        title="Caldera 3"
                        href=""
                        coords="846,271,924,333"
                        shape="rect"
                    >

                    <area
                        alt="PTA"
                        title="PTA"
                        href=""
                        coords="235,488,289,539"
                        shape="rect"
                    >

                    <area
                        alt="Caldera 1"
                        title="Caldera 1"
                        href=""
                        coords="285,358,328,394"
                        shape="rect"
                    >

                    <area
                        alt="Caldera 2"
                        title="Caldera 2"
                        href=""
                        coords="287,415,327,447"
                        shape="rect"
                    >

                    <area
                        alt="Urea 1"
                        title="Urea 1"
                        href=""
                        coords="240,131,276,268"
                        shape="rect"
                    >

                    <area
                        alt="Urea 2"
                        title="Urea 2"
                        href=""
                        coords="832,51,879,166"
                        shape="rect"
                    >

                    <area
                        alt="Dirección de operaciones"
                        title="Dirección de operaciones"
                        href=""
                        coords="454,120,657,173"
                        shape="rect"
                    >

<area
    alt="Muelle"
    title="Muelle"
    href=""
    coords="998,48,1150,119"
    shape="rect">


 
<area
    alt="Entrada sur"
    title="Entrada sur"
    href=""
    coords="38,542,96,635"
    shape="rect">
    

                </map>

            </div>


            <!-- SIMBOLOGÍA -->

            <div class="simbologia">

                <h3>
                    Simbología
                </h3>


                <p>

                    <span
                        class="cuadro"
                        style="background:rgba(0,200,0,0.7);"
                    ></span>

                    Abierta

                </p>


                <p>

                    <span
                        class="cuadro"
                        style="background:rgba(200,0,0,0.7);"
                    ></span>

                    Cerrada

                </p>


                <p>

                    <span
                        class="cuadro"
                        style="background:rgba(255,165,0,0.9);"
                    ></span>

                    Mantenimiento/Reparación

                </p>

                <p style="text-align:center; margin-top:15px;">
                    <a href="/descargar_datos">
                        Descargar respaldo de datos
                    </a>
                </p>

            </div>

        </main>


        <!-- PIE DE PÁGINA -->

        <footer>

            <p>
                &copy; 2026 Servicios Auxiliares - Proagroindustria
            </p>

            <p>
                Desarrollado por Ing. Angel Valdez Martinez
            </p>

        </footer>


    </body>

    </html>
    '''


# ============================================================
# IMAGEN DEL DTI
# ============================================================

@app.route("/imagen")
def servir_imagen():

    return send_from_directory(
        ".",
        "seccionadoras.png"
    )


# ============================================================
# LOGO
# ============================================================

@app.route("/logo")
def logo():

    return send_from_directory(
        ".",
        "logo.png"
    )


# ============================================================
# FONDO
# ============================================================

@app.route("/fondo")
def fondo():

    return send_from_directory(
        ".",
        "fondo.png"
    )


# ============================================================
# DESCARGAR RESPALDO DEL JSON
# ============================================================

@app.route("/descargar_datos", methods=["GET", "POST"])
def descargar_datos():

    if request.method == "GET":

        return """
        <html>
        <head>
            <title>Descargar respaldo</title>
        </head>
        <body style="font-family:Arial;text-align:center;margin-top:80px;">

            <h2>Descargar respaldo de datos</h2>

            <form method="post">

                <p>Introduzca la contraseña:</p>

                <input
                    type="password"
                    name="clave"
                    required
                >

                <br><br>

                <button type="submit">
                    Descargar datos_valvulas.json
                </button>

            </form>

            <br>

            <a href="/">← Volver al diagrama</a>

        </body>
        </html>
        """

    clave = request.form.get("clave", "")

    if clave != CLAVE:

        return """
        <script>
            alert("Contraseña incorrecta.");
            history.back();
        </script>
        """

    # Guardamos la versión más reciente antes de descargarla.
    guardar_datos(datos_valvulas)

    return send_from_directory(
        CARPETA_APP,
        "datos_valvulas.json",
        as_attachment=True
    )


# ============================================================
# IMÁGENES INDIVIDUALES DE LAS VÁLVULAS
# ============================================================

@app.route("/<nombre>.png")
def servir_imagen_valvula(nombre):

    return send_from_directory(
        ".",
        f"{nombre}.png"
    )


# ============================================================
# PÁGINA DE CADA VÁLVULA
# ============================================================

@app.route(
    "/<valvula>",
    methods=["GET", "POST"]
)
def mostrar_valvula(valvula):

    # Verificar que exista la válvula

    if valvula not in datos_valvulas:

        return """
        <h2>Válvula no encontrada</h2>
        <p>
            <a href="/">Volver al diagrama</a>
        </p>
        """


    # ========================================================
    # CAMBIO DE ESTADO
    # ========================================================

    if request.method == "POST":

        clave = request.form.get("clave")

        comentario = request.form.get(
            "comentario",
            ""
        )

        nuevo_estado = request.form.get(
            "estado"
        )


        # -----------------------------------------------
        # COMPROBAR CONTRASEÑA
        # -----------------------------------------------

        if clave == CLAVE:

            # Estado que tenía antes

            estado_anterior = (
                datos_valvulas[valvula]["estado"]
            )


            # -----------------------------------------------
            # ACTUALIZAR ESTADO
            # -----------------------------------------------

            if nuevo_estado:

                datos_valvulas[valvula]["estado"] = (
                    nuevo_estado
                )


            estado_actual = (
                datos_valvulas[valvula]["estado"]
            )


            # -----------------------------------------------
            # CREAR REGISTRO
            # -----------------------------------------------

            registro = {

                "fecha":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "estado":
                    estado_actual,

                "motivo":
                    comentario

            }


            # -----------------------------------------------
            # AGREGAR AL HISTORIAL
            # -----------------------------------------------

            datos_valvulas[valvula]["historial"].append(
                registro
            )


            # -----------------------------------------------
            # GUARDAR EN JSON
            # -----------------------------------------------

            guardar_datos(
                datos_valvulas
            )


            # -----------------------------------------------
            # ENVIAR CORREO
            # -----------------------------------------------

            enviar_alerta(

                valvula,

                estado_anterior,

                estado_actual,

                comentario  )

            # -----------------------------------------------
            # REGRESAR A LA VÁLVULA
            # -----------------------------------------------

            return redirect(
                url_for(
                    "mostrar_valvula",
                    valvula=valvula
                )
            )

        else:

            return """
            <h3>
                Contraseña incorrecta
            </h3>

            <p>
                <a href="/">
                    Volver
                </a>
            </p>
            """

    # ========================================================
    # MOSTRAR INFORMACIÓN
    # ========================================================

    estado = datos_valvulas[valvula]["estado"]

    registros = datos_valvulas[valvula]["historial"]


    # ========================================================
    # CREAR TABLA DEL HISTORIAL
    # ========================================================

    if registros:

        tabla = """
        <table
            border="1"
            cellpadding="8"
            cellspacing="0"
            style="margin:auto;"
        >

            <tr>
                <th>Fecha</th>
                <th>Nuevo Estado</th>
                <th>Motivo</th>
            </tr>
        """

        for registro in registros:

            tabla += f"""
            <tr>

                <td>
                    {registro["fecha"]}
                </td>

                <td>
                    {registro["estado"]}
                </td>

                <td>
                    {registro["motivo"]}
                </td>

            </tr>
            """


        tabla += """
        </table>
        """

    else:

        tabla = """
        <p>
            No hay cambios registrados aún.
        </p>
        """


    # ========================================================
    # PÁGINA
    # ========================================================

    return f'''
    <html>

    <head>

        <title>
            Válvula {valvula.upper()}
        </title>


        <style>

            body {{
                font-family: Arial;
                text-align: center;
                background: #eeeeee;
                margin: 30px;
            }}


            .contenedor {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                max-width: 900px;
                margin: auto;
                box-shadow:
                    0 2px 10px
                    rgba(0,0,0,0.15);
            }}


            .estado {{
                font-size: 24px;
                font-weight: bold;
                margin: 20px;
            }}


            table {{
                background: white;
                border-collapse: collapse;
                width: 90%;
            }}


            th {{
                background: #2e7d32;
                color: white;
            }}


            td, th {{
                padding: 8px;
            }}


            input, select, textarea {{
                margin: 5px;
                padding: 8px;
            }}


            button {{
                padding: 10px 20px;
                background: #2e7d32;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}


            button:hover {{
                background: #1b5e20;
            }}


        </style>

    </head>

    <body>

        <div class="contenedor">


            <h2>
                VÁLVULA {valvula.upper()}
            </h2>


            <div class="estado">

                Estado actual:

                <br>

                {estado}

            </div>

            <img
                src="/{valvula}.png"
                alt="Imagen {valvula.upper()}"
                style="
                    max-width:300px;
                    margin:10px auto;
                    display:block;
                "
            >

            <hr>

            <h3>
                Cambiar estado
            </h3>


            <form method="post">


                Contraseña:

                <br>

                <input
                    type="password"
                    name="clave"
                    required
                >

                <br>

                Nuevo estado:

                <br>

                <select name="estado">

                    <option value="Abierta">
                        Abierta
                    </option>

                    <option value="Cerrada">
                        Cerrada
                    </option>

                    <option value="Mantenimiento/Reparación">
                        Mantenimiento/Reparación
                    </option>

                </select>

                <br>

                Motivo del cambio:

                <br>

                <textarea
                    name="comentario"
                    rows="3"
                    cols="40"
                    placeholder="Escriba el motivo del cambio..."
                ></textarea>

                <br>

                <button type="submit">
                    Cambiar Estado
                </button>

            </form>

            <hr>

            <h3>
                Historial de cambios
            </h3>

            {tabla}

            <br>

            <p>

                <a href="/">
                    ← Volver al diagrama
                </a>

            </p>

        </div>

    </body>

    </html>
    '''


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5001)

    
















