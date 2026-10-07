
from flask import Flask,send_from_directory,request,redirect,url_for
from datetime import datetime
import smtplib,json,os
from email.mime.text import MIMEText

app=Flask(__name__)
app.secret_key=os.environ.get("DTI_SECRET_KEY","clave_secreta_super_segura")

USUARIO=os.environ.get("DTI_USUARIO","admin")
CLAVE=os.environ.get("DTI_CLAVE","1234")
CORREO_REMITENTE=os.environ.get("DTI_CORREO_REMITENTE","avalvil2818@gmail.com")
CORREO_DESTINO=os.environ.get("DTI_CORREO_DESTINO","avalvil2818@gmail.com")
CORREO_PASSWORD="pbgb wsvn pnzf wmhm"

CARPETA_APP=os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DATOS=os.path.join(CARPETA_APP,"datos_valvulas.json")

estados_iniciales={
    "vs13":"Cerrada",
    "vs14":"Mantenimiento/Reparación",
    "vs15":"Cerrada",
    "vs16":"Cerrada",
    "vs17":"Abierta",
    "vs18":"Abierta",
    "vs19":"Abierta",
    "vs20":"Abierta",
    "vs21":"Abierta",
    "vs22":"Abierta",
    "vs23":"Abierta",
    "vs24":"Abierta",
    "vs25":"Abierta",
    "vs26":"Cerrada",
    "vs27":"Abierta",
    "vs29":"Abierta"
}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS,"w",encoding="utf-8") as archivo:
        json.dump(datos,archivo,indent=4,ensure_ascii=False)


def cargar_datos():

    if os.path.exists(ARCHIVO_DATOS):

        try:

            with open(
                ARCHIVO_DATOS,
                "r",
                encoding="utf-8"
            ) as archivo:

                return json.load(archivo)

        except Exception as e:

            print(
                "Error leyendo datos_valvulas.json:",
                e
            )

    datos={
        v:{
            "estado":e,
            "historial":[]
        }
        for v,e in estados_iniciales.items()
    }

    guardar_datos(datos)

    return datos


datos_valvulas=cargar_datos()


# ============================================================
# ALARMAS ACTUALES
# ============================================================

REGLAS_ALARMA = {

    # =========================================================
    # 1. PTA
    # =========================================================
    "PTA": {
        "combinaciones": [

             ["vs16", "vs15", "vs21", "vs22", "vs27"],
             ["vs26", "vs13", "vs21", "vs22", "vs27"],
             ["vs17", "vs13", "vs22", "vs27"],
             ["vs16", "vs15", "vs17", "vs22", "vs27"],
             ["vs16", "vs14", "vs21", "vs22", "vs27"],
             ["vs14", "vs18", "vs29"],
            ["vs20", "vs14"],

            # ["vsXX"],
            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "PTA",
        "mensaje":
        "Sin suministro de agua contra-incendio a PTA."
    },


    # =========================================================
    # 2. ESFERAS
    # =========================================================
    "Esferas": {
        "combinaciones": [
            ["vs16", "vs26", "vs15", "vs14"],
            ["vs13", "vs26", "vs15", "vs16"],
            ["vs17", "vs22", "vs27", "vs14"],
            ["vs17", "vs22", "vs27", "vs13"],
            ["vs14", "vs18", "vs29"],
            ["vs20", "vs14"],

        

            # Agregar otras combinaciones si se confirman
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Esferas",
        "mensaje":
        "Sin suministro de agua contra-incendio a Esferas."
    },


    # =========================================================
    # 3. TORRES NORTE / SUR
    # =========================================================
    "Torres Norte/Sur": {
        "combinaciones": [

            ["vs17", "vs15", "vs22", "vs27","vs16","vs26"],
            ["vs17", "vs15", "vs22", "vs27","vs16","vs21"],
            ["vs17", "vs14", "vs22", "vs27"],
            ["vs16", "vs15", "vs21", "vs22", "vs27"],
            ["vs16", "vs14", "vs21", "vs22", "vs27"],
            [ "vs14", "vs18", "vs29"],
            ["vs20", "vs14"],

            # ["vsXX"],
            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Torres Norte/Sur",
        "mensaje":
        "Sin suministro de agua contra-incendio a Torres Norte/Sur."
    },


    # =========================================================
    # 4. CALDERA 1
    # =========================================================
    "Caldera 1": {
        "combinaciones": [

            ["vs27", "vs22", "vs17", "vs15", "vs26", "vs16"],
            ["vs27", "vs22", "vs17", "vs14"],
            ["vs14", "vs18", "vs19"],
            ["vs20", "vs18", "vs19"],
            ["vs20", "vs14"],
            
            # ["vsXX"],
            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Caldera 1",
        "mensaje":
        "Sin suministro de agua contra-incendio a Caldera 1."
    },


    # =========================================================
    # 5. CALDERA 2
    # =========================================================
    "Caldera 2": {
        "combinaciones": [
            ["vs16", "vs26", "vs14"],
            ["vs17", "vs14", "vs22", "vs27"],
            [ "vs14", "vs18", "vs29"],
            ["vs20", "vs14"],

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Caldera 2",
        "mensaje":
        "Sin suministro de agua contra-incendio a Caldera 2."
    },


    # =========================================================
    # 6. CALDERA 3
    # =========================================================
    "Caldera 3": {
        "combinaciones": [
            ["vs19", "vs29"],
            ["vs20", "vs29","vs18"],
            ["vs23", "vs29","vs18"],
            ["vs20", "vs14"],

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Caldera 3",
        "mensaje":
        "Sin suministro de agua contra-incendio a Caldera 3."
    },


    # =========================================================
    # 7. MUELLE
    # =========================================================
    "Muelle": {
        "combinaciones": [
            ["vs25"],
            ["vs19", "vs29"],
            ["vs20", "vs29","vs18"],
            ["vs23", "vs29","vs18"],
            ["vs20", "vs14"],

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Muelle",
        "mensaje":
        "Sin suministro de agua contra-incendio al Muelle."
    },


    # =========================================================
    # 8. LLENADERAS
    # =========================================================
    "Llenaderas": {
        "combinaciones": [
            ["vs19", "vs29"],
            ["vs20", "vs29","vs18"],
           ["vs23", "vs29","vs18"],
            ["vs20", "vs14"],

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Llenaderas",
        "mensaje":
        "Sin suministro de agua contra-incendio a Llenaderas."
    },


    # =========================================================
    # 9. PLANTA UREA 1
    # =========================================================
    "Planta Urea 1": {
        "combinaciones": [

            ["vs21", "vs17","vs26", "vs15", "vs27", "vs22" ],
            ["vs21", "vs17","vs26", "vs14", "vs27", "vs22" ],
            ["vs21", "vs17","vs26", "vs16", "vs27", "vs22" ],
            [ "vs14", "vs18", "vs29"],
            ["vs20", "vs14"],

            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Planta Urea 1",
        "mensaje":
        "Sin suministro de agua contra-incendio a Planta Urea 1."
    },


    # =========================================================
    # 10. PLANTA UREA 2
    # =========================================================
    "Planta Urea 2": {
        "combinaciones": [
            ["vs19", "vs29"],
            ["vs20","vs27", "vs22", "vs17"],
            ["vs19","vs27", "vs22", "vs17", "vs18" ],
            ["vs19","vs27", "vs22", "vs17", "vs20" ],
            ["vs20", "vs14"],

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Planta Urea 2",
        "mensaje":
        "Suministro de agua contra-incendio comprometido en Planta Urea 2."
    },


    # =========================================================
    # 11. LABORATORIO / TALLER DE MANTENIMIENTO
    # =========================================================
    "Laboratorio / Taller de mantenimiento": {
        "combinaciones": [

            ["vs27", "vs22", "vs17", "vs18","vs29"],
            ["vs27", "vs22", "vs17", "vs18","vs19"],
            [ "vs14", "vs18", "vs29"],
            [ "vs14", "vs18", "vs19"],
            [ "vs15","vs16","vs26", "vs18", "vs29"],
            [ "vs15","vs16","vs26", "vs18", "vs19"],
            ["vs20", "vs14"],

            # ["vsXX"],
            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Laboratorio / Taller de mantenimiento",
        "mensaje":
        "Sin suministro de agua contra-incendio al Laboratorio / Taller de mantenimiento."
    },


    # =========================================================
    # 12. SUBESTACIÓN / RH / ESTACIONAMIENTO
    # =========================================================
    "Sub-estación eléctrica / Recursos humanos / Estacionamiento": {
        "combinaciones": [
            ["vs24"],
            ["vs23", "vs20"],
            ["vs23", "vs19", "vs18"],
            ["vs23", "vs29", "vs18"],
            

            # Posibles combinaciones adicionales
            # ["vsXX", "vsXX"],
        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Sub-estación eléctrica / Recursos humanos / Estacionamiento",
        "mensaje":
        "Sin suministro de agua contra-incendio al área."
    },


    # =========================================================
    # 13. ESTACIÓN DE REGULACIÓN DE GAS NATURAL
    # =========================================================
    "Estación de regulación de gas natural": {
        "combinaciones": [

             ["vs23", "vs20"],
             ["vs13", "vs20","vs23"],
             ["vs23", "vs19", "vs18"],
             ["vs23", "vs29", "vs18"],
            # ["vsXX"],
            # ["vsXX", "vsXX"],
            # ["vsXX", "vsXX", "vsXX"],

        ],
        "estados": [
            "Cerrada",
            "Mantenimiento/Reparación"
        ],
        "prioridad": "Alta",
        "zona": "Estación de regulación de gas natural",
        "mensaje":
        "Sin suministro de agua contra-incendio a la Estación de regulación de gas natural."
    },


"Circuito interno": {
    "combinaciones": [
        ["vs23", "vs13"],
        ["vs23", "vs14"],
        ["vs13","vs20"],
        
    ],
    "estados": [
        "Cerrada",
        "Mantenimiento/Reparación"
    ],
    "prioridad": "Alta",
    "zona": "Circuito interno",
    "mensaje": "Sin suministro de agua contra-incendio al circuito interno."
},
}


def obtener_alarmas():

    alarmas_agrupadas = {}

    for nombre, regla in REGLAS_ALARMA.items():

        # ====================================================
        # REVISAR LAS COMBINACIONES DE ESTA ZONA
        # ====================================================

        for combinacion in regla["combinaciones"]:

            condiciones = []

            for valvula in combinacion:

                estado = datos_valvulas.get(
                    valvula,
                    {}
                ).get("estado")

                condiciones.append(
                    estado in regla["estados"]
                )

            # =================================================
            # SI TODA LA COMBINACIÓN ESTÁ INDISPONIBLE
            # =================================================

            if all(condiciones):

                # Ordenamos las válvulas para que:
                #
                # [vs16, vs26, vs15, vs14]
                #
                # y
                #
                # [vs14, vs15, vs16, vs26]
                #
                # sean consideradas la misma combinación.

                clave_combinacion = tuple(
                    sorted(combinacion)
                )

                # =================================================
                # SI YA EXISTE ESTA MISMA COMBINACIÓN
                # AGRUPAMOS LA ZONA
                # =================================================

                if clave_combinacion in alarmas_agrupadas:

                    alarma = alarmas_agrupadas[
                        clave_combinacion
                    ]

                    alarma["zonas"].append(
                        regla["zona"]
                    )

                # =================================================
                # SI ES UNA COMBINACIÓN NUEVA
                # =================================================

                else:

                    estados_actuales = []

                    for valvula in combinacion:

                        estado = datos_valvulas.get(
                            valvula,
                            {}
                        ).get("estado")

                        estados_actuales.append(
                            f"{valvula.upper()}: {estado}"
                        )

                    alarmas_agrupadas[
                        clave_combinacion
                    ] = {

                        "equipo":
                        " + ".join(
                            v.upper()
                            for v in combinacion
                        ),

                        "prioridad":
                        regla["prioridad"],

                        "zonas": [
                            regla["zona"]
                        ],

                        "mensaje":
                        regla["mensaje"],

                        "estado":
                        " | ".join(
                            estados_actuales
                        )
                    }

                # Ya encontramos una combinación activa
                # para esta zona.
                break


    # ========================================================
    # CONVERTIR LAS ALARMAS AGRUPADAS AL FORMATO DEL SISTEMA
    # ========================================================

    alarmas = []

    for alarma in alarmas_agrupadas.values():

        alarmas.append({

            "equipo":
            alarma["equipo"],

            "prioridad":
            alarma["prioridad"],

            "zona":
            " + ".join(
                alarma["zonas"]
            ),

            "mensaje":
            alarma["mensaje"],

            "estado":
            alarma["estado"]
        })

    return alarmas
# ============================================================
# CORREO
# ============================================================

def enviar_alerta(
    valvula,
    estado_anterior,
    estado_nuevo,
    motivo
):

    fecha=datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    texto=f"""ALERTA DE VÁLVULA

Válvula: {valvula.upper()}
Estado anterior: {estado_anterior}
Nuevo estado: {estado_nuevo}
Motivo: {motivo}
Fecha: {fecha}

Registro:
{{
    "fecha":"{fecha}",
    "estado":"{estado_nuevo}",
    "motivo":"{motivo}"
}}"""

    msg=MIMEText(texto)

    msg["Subject"]=(
        f"Alerta: Válvula "
        f"{valvula.upper()} → {estado_nuevo}"
    )

    msg["From"]=CORREO_REMITENTE
    msg["To"]=CORREO_DESTINO

    try:

        if not CORREO_PASSWORD:

            print(
                "Correo no enviado: "
                "falta DTI_CORREO_PASSWORD."
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
# VÁLVULAS Y ZONAS
# ============================================================

VALVULAS=list(
    estados_iniciales.keys()
)

ZONAS=[

    "PTA",

    "Esferas",

    "Torres Norte/Sur",

    "Caldera 1 ",

    "Caldera 2 ",

    "Caldera 3",

    "Muelle",

    "Llenaderas",

    "Planta Urea 1",

    "Planta Urea 2",

    "Laboratorio / Taller de mantenimiento",

    "Sub-estación eléctrica / Recursos humanos / Estacionamiento",

    "Estación de regulación de gas natural "
]


# ============================================================
# POSICIONES DE LAS VÁLVULAS
# ============================================================

POSICIONES={

    "vs27":(497,202,550,237),

    "vs29":(725,204,777,242),

    "vs19":(914,198,967,236),

    "vs23":(660,473,695,527),

    "vs13":(616,473,649,527),

    "vs20":(968,487,1002,542),

    "vs24":(841,577,877,629),

    "vs14":(443,544,493,579),

    "vs15":(354,506,392,559),

    "vs16":(282,403,335,437),

    "vs26":(133,331,169,383),

    "vs17":(228,85,278,119),

    "vs22":(355,127,390,180),

    "vs25":(1048,161,1100,199),

    "vs21":(228,269,282,304),

    "vs18":(896,26,947,61)
}


def color_estado(estado):

    return {

        "Abierta":
        "rgba(0,200,0,0.70)",

        "Cerrada":
        "rgba(200,0,0,0.75)",

        "Mantenimiento/Reparación":
        "rgba(255,165,0,0.90)"

    }.get(
        estado,
        "rgba(100,100,100,0.50)"
    )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def inicio():

    alarmas=obtener_alarmas()

    posiciones=POSICIONES

    if alarmas:

        panel_alarmas=f"""
        <div class="panel-alarmas">

        <div class="titulo-alarmas">
        🚨 ALARMAS ACTIVAS
        <span>{len(alarmas)}</span>
        </div>
        """

        for alarma in alarmas:

            panel_alarmas+=f"""

            <div class="alarma">

            <div class="alarma-cabecera">

            <span>
            🔴 {alarma["equipo"]}
            </span>

            <b>
            {alarma["prioridad"]}
            </b>

            </div>

            <div class="alarma-zona">

            📍 Zona afectada:
            <strong>
            {alarma["zona"]}
            </strong>

            </div>

            <div class="alarma-estado">

            Estado actual:
            <strong>
            {alarma["estado"]}
            </strong>

            </div>

            <div class="alarma-mensaje">

            {alarma["mensaje"]}

            </div>

            <div class="alarma-fecha">

            Detectada:
            {datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )}

            </div>

            </div>
            """

        panel_alarmas+="</div>"

    else:

        panel_alarmas="""

        <div class="panel-normal">

        🟢 SISTEMA NORMAL

        <span>
        No hay alarmas activas
        </span>

        </div>
        """

    overlays=""

    for valvula,(x1,y1,x2,y2) in posiciones.items():

        estado=datos_valvulas[valvula]["estado"]

        color=color_estado(estado)

        overlays+=f"""

        <a
        href="/{valvula}"
        title="Válvula {valvula.upper()} - {estado}"

        style="
        position:absolute;
        left:{x1}px;
        top:{y1}px;
        width:{x2-x1}px;
        height:{y2-y1}px;
        background:{color};
        border-radius:5px;
        ">

        </a>
        """

    return f"""
<html>

<head>

<title>
SECCIONADORAS DE AGUA CONTRA-INCENDIO
</title>

<style>

body{{
    font-family:Arial;
    margin:0;
    text-align:center;
    background:#eeeeee
}}

.fondo{{
    position:fixed;
    inset:0;
    background-image:url('/fondo');
    background-repeat:no-repeat;
    background-position:center;
    background-size:cover;
    z-index:-1
}}

header{{
    background:#2e7d32;
    color:white;
    padding:20px;
    display:flex;
    align-items:center
}}

.logo-container{{
    background:white;
    padding:10px;
    border-radius:8px;
    margin-right:30px
}}

.logo{{
    height:60px
}}

h1{{
    flex:1;
    text-align:center;
    margin:0
}}

.panel-alarmas{{
    width:90%;
    max-width:1000px;
    margin:20px auto;
    background:#ffebee;
    border:3px solid #c62828;
    border-radius:10px;
    padding:15px;
    box-sizing:border-box;
    box-shadow:0 4px 12px rgba(0,0,0,.25)
}}

.titulo-alarmas{{
    background:#c62828;
    color:white;
    font-size:21px;
    font-weight:bold;
    padding:12px;
    border-radius:7px;
    margin-bottom:10px
}}

.titulo-alarmas span{{
    background:white;
    color:#c62828;
    border-radius:20px;
    padding:3px 10px;
    margin-left:5px
}}

.alarma{{
    background:#fff;
    border:2px solid #ef5350;
    border-left:8px solid #c62828;
    padding:12px;
    margin-top:10px;
    text-align:left;
    border-radius:7px;
    box-shadow:0 2px 6px rgba(0,0,0,.15)
}}

.alarma-cabecera{{
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:#b71c1c;
    font-size:18px;
    font-weight:bold
}}

.alarma-cabecera b{{
    background:#c62828;
    color:white;
    padding:4px 10px;
    border-radius:4px;
    font-size:12px
}}

.alarma-zona{{
    background:#fff3cd;
    border:1px solid #ffc107;
    color:#856404;
    padding:8px;
    margin-top:8px;
    border-radius:5px;
    font-size:14px
}}

.alarma-estado{{
    margin-top:8px;
    color:#b71c1c;
    font-size:14px
}}

.alarma-mensaje{{
    color:#333;
    margin-top:8px;
    font-size:15px
}}

.alarma-fecha{{
    color:#777;
    font-size:11px;
    margin-top:8px
}}

.panel-normal{{
    width:90%;
    max-width:1000px;
    margin:20px auto;
    padding:15px;
    box-sizing:border-box;
    background:#e8f5e9;
    border:2px solid #2e7d32;
    border-radius:10px;
    color:#1b5e20;
    font-weight:bold;
    box-shadow:0 3px 8px rgba(0,0,0,.15)
}}

.panel-normal span{{
    display:block;
    font-size:13px;
    font-weight:normal;
    margin-top:5px
}}

.contenedor{{
    position:relative;
    display:inline-block;
    margin-top:10px
}}

.imagen-dti{{
    display:block;
    background:white;
    opacity:.85
}}

.simbologia{{
    background:white;
    border:1px solid #ccc;
    padding:10px 20px;
    border-radius:8px;
    text-align:left;
    margin:20px auto 100px auto;
    width:fit-content;
    box-shadow:0 2px 6px rgba(0,0,0,.2)
}}

.simbologia h3{{
    text-align:center;
    margin-top:5px
}}

.cuadro{{
    display:inline-block;
    width:20px;
    height:20px;
    margin-right:5px;
    vertical-align:middle;
    border-radius:3px
}}

footer{{
    background:#fbc02d;
    color:black;
    padding:10px;
    position:fixed;
    bottom:0;
    width:100%;
    text-align:center;
    z-index:10
}}

footer p{{
    margin:3px
}}

a{{
    text-decoration:none
}}

</style>

</head>

<body>

<div class="fondo"></div>

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

<main>

{panel_alarmas}

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
coords="396,266,493,355"
shape="rect"
>

<area
alt="Torre de enfriamiento sur"
title="Torre de enfriamiento sur"
href=""
coords="399,392,490,478"
shape="rect"
>

<area
alt="Esferas A/B/C"
title="Esferas A/B/C"
href=""
coords="170,459,233,533"
shape="rect"
>

<area
alt="Sub-estación eléctrica / Recursos humanos / Estacionamiento "
title="Sub-estación eléctrica / Recursos humanos / Estacionamiento "
href=""
coords="563,600,752,659"
shape="rect"
>

<area
alt="Estación de regulación de gas natural"
title="Estación de regulación de gas natural"
href=""
coords="1005,601,1054,654"
shape="rect"
>

<area
alt="Tanque de agua Contra-Incendio"
title="Tanque de agua Contra-Incendio"
href=""
coords="586,263,726,436"
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
coords="285,447,346,505"
shape="rect"
>

<area
alt="Caldera 1"
title="Caldera 1"
href=""
coords="290,307,341,350"
shape="rect"
>

<area
alt="Caldera 2"
title="Caldera 2"
href=""
coords="224,353,271,399"
shape="rect"
>

<area
alt="Planta Urea 1"
title="Planta Urea 1"
href=""
coords="240,131,276,268"
shape="rect"
>

<area
alt="Planta Urea 2"
title="Planta Urea 2"
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
shape="rect"
>

<area
alt="Portada 1"
title="Portada 1"
href=""
coords="38,542,96,635"
shape="rect"
>

</map>

</div>

<div class="simbologia">

<h3>
Simbología
</h3>

<p>

<span
class="cuadro"
style="background:rgba(0,200,0,.7);">
</span>

Abierta

</p>

<p>

<span
class="cuadro"
style="background:rgba(200,0,0,.7);">
</span>

Cerrada

</p>

<p>

<span
class="cuadro"
style="background:rgba(255,165,0,.9);">
</span>

Mantenimiento/Reparación

</p>

<p
style="text-align:center;margin-top:15px"
>

<a href="/descargar_datos">
Descargar respaldo de datos
</a>

</p>

</div>

</main>

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
"""


# ============================================================
# ARCHIVOS
# ============================================================

@app.route("/imagen")
def servir_imagen():

    return send_from_directory(
        ".",
        "seccionadoras.png"
    )


@app.route("/logo")
def logo():

    return send_from_directory(
        ".",
        "logo.png"
    )


@app.route("/fondo")
def fondo():

    return send_from_directory(
        ".",
        "fondo.png"
    )


@app.route("/<nombre>.png")
def servir_imagen_valvula(nombre):

    return send_from_directory(
        ".",
        f"{nombre}.png"
    )


# ============================================================
# DESCARGAR DATOS
# ============================================================

@app.route(
    "/descargar_datos",
    methods=["GET","POST"]
)
def descargar_datos():

    if request.method=="GET":

        return """

        <html>

        <head>

        <title>
        Descargar respaldo
        </title>

        </head>

        <body
        style="
        font-family:Arial;
        text-align:center;
        margin-top:80px
        ">

        <h2>
        Descargar respaldo de datos
        </h2>

        <form method="post">

        <p>
        Introduzca la contraseña:
        </p>

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

        <a href="/">
        ← Volver al diagrama
        </a>

        </body>

        </html>
        """

    if request.form.get(
        "clave",
        ""
    )!=CLAVE:

        return """

        <script>

        alert(
            "Contraseña incorrecta."
        );

        history.back();

        </script>
        """

    guardar_datos(
        datos_valvulas
    )

    return send_from_directory(
        CARPETA_APP,
        "datos_valvulas.json",
        as_attachment=True
    )


# ============================================================
# PÁGINA DE VÁLVULA
# ============================================================

@app.route(
    "/<valvula>",
    methods=["GET","POST"]
)
def mostrar_valvula(valvula):

    if valvula not in datos_valvulas:

        return """

        <h2>
        Válvula no encontrada
        </h2>

        <p>

        <a href="/">
        Volver al diagrama
        </a>

        </p>
        """

    if request.method=="POST":

        clave=request.form.get(
            "clave"
        )

        comentario=request.form.get(
            "comentario",
            ""
        )

        nuevo_estado=request.form.get(
            "estado"
        )

        if clave!=CLAVE:

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

        estado_anterior=datos_valvulas[
            valvula
        ]["estado"]

        if nuevo_estado:

            datos_valvulas[
                valvula
            ]["estado"]=nuevo_estado

        estado_actual=datos_valvulas[
            valvula
        ]["estado"]

        datos_valvulas[
            valvula
        ]["historial"].append({

            "fecha":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "estado":
            estado_actual,

            "motivo":
            comentario
        })

        guardar_datos(
            datos_valvulas
        )

        enviar_alerta(
            valvula,
            estado_anterior,
            estado_actual,
            comentario
        )

        return redirect(
            url_for(
                "mostrar_valvula",
                valvula=valvula
            )
        )

    estado=datos_valvulas[
        valvula
    ]["estado"]

    registros=datos_valvulas[
        valvula
    ]["historial"]

    if registros:

        tabla="""

        <table
        border="1"
        cellpadding="8"
        cellspacing="0"
        style="margin:auto">

        <tr>

        <th>
        Fecha
        </th>

        <th>
        Nuevo Estado
        </th>

        <th>
        Motivo
        </th>

        </tr>
        """

        for registro in registros:

            tabla+=f"""

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

        tabla+="</table>"

    else:

        tabla="""

        <p>
        No hay cambios registrados aún.
        </p>
        """

    return f"""

<html>

<head>

<title>
Válvula {valvula.upper()}
</title>

<style>

body{{
    font-family:Arial;
    text-align:center;
    background:#eeeeee;
    margin:30px
}}

.contenedor{{
    background:white;
    padding:30px;
    border-radius:10px;
    max-width:900px;
    margin:auto;
    box-shadow:0 2px 10px rgba(0,0,0,.15)
}}

.estado{{
    font-size:24px;
    font-weight:bold;
    margin:20px
}}

table{{
    background:white;
    border-collapse:collapse;
    width:90%
}}

th{{
    background:#2e7d32;
    color:white
}}

td,th{{
    padding:8px
}}

input,select,textarea{{
    margin:5px;
    padding:8px
}}

button{{
    padding:10px 20px;
    background:#2e7d32;
    color:white;
    border:none;
    border-radius:5px;
    cursor:pointer
}}

button:hover{{
    background:#1b5e20
}}

</style>

</head>

<body>

<div class="contenedor">

<h2>
VÁLVULA {valvula.upper()}
</h2>

<div class="estado">

Estado actual:<br>

{estado}

</div>

<img
src="/{valvula}.png"
alt="Imagen {valvula.upper()}"
style="
max-width:300px;
margin:10px auto;
display:block
"
>

<hr>

<h3>
Cambiar estado
</h3>

<form method="post">

Contraseña:<br>

<input
type="password"
name="clave"
required
>

<br>

Nuevo estado:<br>

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

Motivo del cambio:<br>

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
"""


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__=="__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5001
    )