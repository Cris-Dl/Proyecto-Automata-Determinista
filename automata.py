class AutomataAFD:
    ESTADOS = {
        "q0": "Inicio",
        "q1": "Membresía validada",
        "q2": "Registrando productos",
        "q3": "Esperando pago",
        "q4": "Procesando pago",
        "q5": "Pago aprobado",
        "q6": "Compra finalizada",
    }

    ALFABETO = ("VM", "RP", "FR", "PG", "AP", "FC")

    ESTADO_INICIAL = "q0"

    ESTADOS_FINALES = {"q6"}

    # Transiciones válidas de δ.
    TRANSICIONES = {
        ("q0", "VM"): "q1",
        ("q1", "RP"): "q2",
        ("q2", "RP"): "q2",
        ("q2", "FR"): "q3",
        ("q3", "PG"): "q4",
        ("q4", "AP"): "q5",
        ("q5", "FC"): "q6",
    }

    MENSAJES_INVALIDOS = {
        "VM": "La membresía solo puede validarse desde el estado Inicio.",
        "RP": "No se pueden registrar productos en el estado actual.",
        "FR": "El registro solo puede finalizarse mientras se están registrando productos.",
        "PG": "El pago solo puede iniciarse cuando el sistema está esperando pago.",
        "AP": "El pago solo puede aprobarse después de haber iniciado su procesamiento.",
        "FC": "La compra solo puede finalizarse después de que el pago haya sido aprobado.",
    }

    def __init__(self):
        self.estados_afd = [
            f"{codigo}: {nombre}"
            for codigo, nombre in self.ESTADOS.items()
        ]

        self.estado_actual = self.ESTADO_INICIAL
        self.historial = []

    @property
    def estado_actual_idx(self):
        """Índice del estado actual, conservado para compatibilidad con la UI."""
        return list(self.ESTADOS.keys()).index(self.estado_actual)

    def delta(self, estado, simbolo):
        """
        Función de transición δ.

        Si el par (estado, símbolo) corresponde a una transición válida,
        devuelve el nuevo estado.

        Si el evento no es válido desde ese estado, conserva el mismo
        estado. La UI puede mostrar que el intento fue no válido.
        """
        return self.TRANSICIONES.get((estado, simbolo), estado)

    def es_transicion_valida(self, estado, simbolo):
        return (estado, simbolo) in self.TRANSICIONES

    def ejecutar_evento(self, simbolo, descripcion=None):
        """
        Ejecuta un símbolo del alfabeto desde el estado actual.

        La UI únicamente envía el símbolo; el AFD determina el estado
        destino mediante δ. La interfaz ya no decide directamente a qué
        índice debe avanzar.
        """
        simbolo = str(simbolo).upper().strip()

        if simbolo not in self.ALFABETO:
            raise ValueError(
                f"El símbolo {simbolo!r} no pertenece al alfabeto del AFD."
            )

        estado_anterior = self.estado_actual
        valida = self.es_transicion_valida(estado_anterior, simbolo)
        estado_nuevo = self.delta(estado_anterior, simbolo)

        if valida:
            self.estado_actual = estado_nuevo

        evento = descripcion or simbolo

        registro = {
            "valida": valida,
            "simbolo": simbolo,
            "evento": evento,
            "estado_anterior": self._estado_completo(estado_anterior),
            "estado_nuevo": self._estado_completo(estado_nuevo),
        }

        if not valida:
            registro["mensaje"] = self.MENSAJES_INVALIDOS.get(
                simbolo,
                "Transición no válida en el estado actual.",
            )

        self.historial.append(registro)

        return registro

    def _estado_completo(self, codigo):
        return f"{codigo}: {self.ESTADOS[codigo]}"

    def reiniciar(self):
        self.estado_actual = self.ESTADO_INICIAL
        self.historial.clear()

    def definicion_formal(self):
        """Devuelve los cinco componentes de M para fines académicos."""
        return {
            "Q": set(self.ESTADOS.keys()),
            "Sigma": set(self.ALFABETO),
            "delta": dict(self.TRANSICIONES),
            "q0": self.ESTADO_INICIAL,
            "F": set(self.ESTADOS_FINALES),
        }