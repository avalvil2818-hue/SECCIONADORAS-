import json
from collections import Counter
from sklearn.ensemble import RandomForestClassifier


ARCHIVO_ENTRENAMIENTO = "datos_entrenamiento.json"

VALVULAS = [
    "vs13", "vs14", "vs15", "vs16", "vs17", "vs18",
    "vs19", "vs20", "vs21", "vs22", "vs23", "vs24",
    "vs25", "vs26", "vs27", "vs29"
]

ESTADOS = {
    "Abierta": 0,
    "Cerrada": 1,
    "Mantenimiento/Reparación": 2
}

# Normalizamos solamente las respuestas que sí equivalen
# a las dos categorías que queremos utilizar.
# "Suministro comprometido" NO se usa para entrenar esa zona.
NORMALIZACION = {
    "Normal": "Tiene suministro",
    "Tiene suministro": "Tiene suministro",
    "Sin suministro": "Sin suministro"
}


class ModeloSuministro:

    def __init__(self, archivo=ARCHIVO_ENTRENAMIENTO):
        self.archivo = archivo
        self.datos = self._cargar_datos()
        self.modelos = {}
        self.ejemplos_exactos = {}
        self.entrenar()

    def _cargar_datos(self):
        with open(self.archivo, "r", encoding="utf-8") as f:
            return json.load(f)

    def _vectorizar_valvulas(self, valvulas):
        return [
            ESTADOS.get(valvulas.get(v, "Abierta"), 0)
            for v in VALVULAS
        ]

    def _clave_escenario(self, valvulas):
        return tuple(
            ESTADOS.get(valvulas.get(v, "Abierta"), 0)
            for v in VALVULAS
        )

    def entrenar(self):
        # Primero guardamos los ejercicios conocidos.
        # Así, si aparece exactamente uno que ya fue validado,
        # devolvemos exactamente la respuesta registrada.
        for ejercicio in self.datos:
            clave = self._clave_escenario(ejercicio["valvulas"])
            self.ejemplos_exactos[clave] = ejercicio["resultado"]

        # Reunimos todas las zonas presentes en el archivo.
        zonas = set()
        for ejercicio in self.datos:
            zonas.update(ejercicio.get("resultado", {}).keys())

        # Un modelo independiente por zona.
        for zona in sorted(zonas):
            X = []
            y = []

            for ejercicio in self.datos:
                resultado = ejercicio.get("resultado", {}).get(zona)
                resultado = NORMALIZACION.get(resultado)

                # Ignoramos "Suministro comprometido" porque el modelo
                # debe aprender únicamente:
                # 0 = Sin suministro
                # 1 = Tiene suministro
                if resultado not in ("Sin suministro", "Tiene suministro"):
                    continue

                X.append(self._vectorizar_valvulas(ejercicio["valvulas"]))
                y.append(0 if resultado == "Sin suministro" else 1)

            # No entrenamos una zona si no existen ambas clases.
            if len(set(y)) < 2 or len(y) < 5:
                continue

            modelo = RandomForestClassifier(
                n_estimators=300,
                max_depth=8,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42
            )

            modelo.fit(X, y)

            self.modelos[zona] = modelo

    def predecir(self, valvulas):
        clave = self._clave_escenario(valvulas)

        # 1. Si el escenario ya existe, usamos el dato real registrado.
        if clave in self.ejemplos_exactos:
            resultado_original = self.ejemplos_exactos[clave]
            resultado = {}

            for zona, valor in resultado_original.items():
                valor = NORMALIZACION.get(valor)
                if valor in ("Sin suministro", "Tiene suministro"):
                    resultado[zona] = valor

            sin_suministro = [
                zona for zona, valor in resultado.items()
                if valor == "Sin suministro"
            ]

            return {
                "metodo": "Coincidencia exacta con ejercicio validado",
                "confianza": 1.0,
                "resultado": resultado,
                "sin_suministro": sin_suministro
            }

        # 2. Si es un escenario nuevo, usamos los modelos ML.
        X = [self._vectorizar_valvulas(valvulas)]
        resultado = {}
        confianzas = []

        for zona, modelo in self.modelos.items():
            probabilidades = modelo.predict_proba(X)[0]
            prediccion = int(modelo.predict(X)[0])

            confianza = float(max(probabilidades))
            confianzas.append(confianza)

            # Para evitar afirmar algo con demasiada seguridad cuando
            # todavía faltan ejemplos, marcamos como No determinado.
            if confianza < 0.65:
                resultado[zona] = "No determinado"
            else:
                resultado[zona] = (
                    "Tiene suministro"
                    if prediccion == 1
                    else "Sin suministro"
                )

        sin_suministro = [
            zona for zona, valor in resultado.items()
            if valor == "Sin suministro"
        ]

        confianza_general = (
            sum(confianzas) / len(confianzas)
            if confianzas else 0
        )

        return {
            "metodo": "Modelo Random Forest",
            "confianza": confianza_general,
            "resultado": resultado,
            "sin_suministro": sin_suministro
        }

    def generar_escenario(self, cantidad_cambios=None):
        """
        Genera un escenario nuevo para probar el modelo.
        Todas las válvulas empiezan abiertas y después se cambian
        aleatoriamente algunas a Cerrada o Mantenimiento/Reparación.
        """
        if cantidad_cambios is None:
            cantidad_cambios = random.randint(1, 6)

        valvulas = {v: "Abierta" for v in VALVULAS}

        seleccionadas = random.sample(
            VALVULAS,
            min(cantidad_cambios, len(VALVULAS))
        )

        for v in seleccionadas:
            valvulas[v] = random.choice([
                "Cerrada",
                "Mantenimiento/Reparación"
            ])

        return valvulas

    def nuevo_ejercicio(self):
        valvulas = self.generar_escenario()
        prediccion = self.predecir(valvulas)

        return {
            "valvulas": valvulas,
            "prediccion": prediccion
        }


if __name__ == "__main__":

    modelo = ModeloSuministro()

    print("\nMODELO DE SUMINISTRO DE AGUA CONTRA-INCENDIO")
    print("---------------------------------------------")
    print(f"Ejemplos utilizados: {len(modelo.datos)}")
    print(f"Modelos por zona entrenados: {len(modelo.modelos)}")

    ejercicio = modelo.nuevo_ejercicio()

    print("\nNUEVO ESCENARIO")
    for valvula, estado in ejercicio["valvulas"].items():
        print(f"{valvula.upper()}: {estado}")

    print("\nÁREAS SIN SUMINISTRO:")
    sin_suministro = ejercicio["prediccion"]["sin_suministro"]

    if sin_suministro:
        for zona in sin_suministro:
            print(f" - {zona}")
    else:
        print(" - Ninguna detectada")

    print(
        f"\nMétodo: {ejercicio['prediccion']['metodo']}"
    )
    print(
        f"Confianza general: "
        f"{ejercicio['prediccion']['confianza']:.1%}"
    )
