from flask import Flask, send_from_directory, request
from datetime import datetime

app = Flask(__name__)

# Estados iniciales de todas las válvulas
estados = {
    "vs13": "Abierta",
    "vs14": "Abierta",
    "vs15": "Abierta",
    "vs16": "Abierta",
    "vs17": "Abierta",
    "vs18": "Abierta",
    "vs19": "Abierta",
    "vs20": "Abierta",
    "vs21": "Abierta",
    "vs22": "Abierta",
    "vs23": "Abierta",
    "vs24": "Abierta",
    "vs25": "Abierta",
    "vs26": "Abierta",
    "vs27": "Abierta",
    "vs29": "Abierta",
}

# Historial de cambios
historial = {}

@app.route("/")
def inicio():
    return '''
        <h1>Diagrama - Seccionadoras Agua Contra Incendios</h1>
        <img src="/imagen" usemap="#mapaDTI" 
             style="max-width:80%; height:auto; display:block; margin:auto;">

        <map name="mapaDTI">
            <area target="_self" alt="VS-22" title="VS-22" href="/vs22" coords="394,181,351,126" shape="rect">
            <area target="_self" alt="VS-27" title="VS-27" href="/vs27" coords="550,237,498,200" shape="rect">
            <area target="_self" alt="VS-13" title="VS-13" href="/vs13" coords="548,457,579,533" shape="rect">
            <area target="_self" alt="VS-23" title="VS-23" href="/vs23" coords="599,457,626,532" shape="rect">
            <area target="_self" alt="VS-24" title="VS-24" href="/vs24" coords="844,579,876,630" shape="rect">
            <area target="_self" alt="VS-14" title="VS-14" href="/vs14" coords="443,547,494,576" shape="rect">
            <area target="_self" alt="VS-15" title="VS-15" href="/vs15" coords="356,487,390,539" shape="rect">
            <area target="_self" alt="VS-16" title="VS-16" href="/vs16" coords="229,448,277,477" shape="rect">
            <area target="_self" alt="VS-26" title="VS-26" href="/vs26" coords="139,375,169,426" shape="rect">
            <area target="_self" alt="VS-21" title="VS-21" href="/vs21" coords="228,330,279,359" shape="rect">
            <area target="_self" alt="VS-17" title="VS-17" href="/vs17" coords="227,84,280,118" shape="rect">
            <area target="_self" alt="VS-29" title="VS-29" href="/vs29" coords="732,122,782,156" shape="rect">
            <area target="_self" alt="VS-25" title="VS-25" href="/vs25" coords="908,121,960,150" shape="rect">
            <area target="_self" alt="VS-20" title="VS-20" href="/vs20" coords="908,537,960,571" shape="rect">
            <area target="_self" alt="VS-19" title="VS-19" href="/vs19" coords="825,202,874,233" shape="rect">
            <area target="_self" alt="VS-18" title="VS-18" href="/vs18" coords="969,79,1000,32" shape="rect">
        </map>
    '''

@app.route("/imagen")
def servir_imagen():
    return send_from_directory('.', 'seccionadoras.png')

# Ruta genérica para todas las válvulas
@app.route("/<valvula>", methods=["GET", "POST"])
def mostrar_valvula(valvula):
    if valvula not in estados:
        return "<h2>Válvula no encontrada</h2>"

    if request.method == "POST":
        # Cambiar estado
        estados[valvula] = "Cerrada" if estados[valvula] == "Abierta" else "Abierta"
        historial[valvula] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    estado = estados[valvula]
    ultima = historial.get(valvula, "Nunca")
    return f'''
        <h2>Válvula {valvula.upper()}</h2>
        <p>Estado actual: {estado}</p>
        <p>Último cambio: {ultima}</p>
        <form method="post">
            <button type="submit">Cambiar Estado</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True, port=5001)




