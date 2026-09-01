class AutomataAFD:
    """Lógica del AFD extraída del prototipo original, sin cambiar su comportamiento."""

    def __init__(self):
        self.estados_afd = [
            "q0: Inicio",
            "q1: Membresía validada",
            "q2: Registrando",
            "q3: Esperando pago",
            "q4: Pago aprobado",
            "q5: Finalizada",
        ]
        self.estado_actual_idx = 0
        self.historial = []

    def intentar_transicion(self, evento, indice_destino, condicion_valida=True):
        if condicion_valida:
            estado_anterior = self.estados_afd[self.estado_actual_idx]
            self.estado_actual_idx = indice_destino
            estado_nuevo = self.estados_afd[self.estado_actual_idx]

            transicion = {
                "evento": evento,
                "estado_anterior": estado_anterior,
                "estado_nuevo": estado_nuevo,
            }
            self.historial.append(transicion)

            return {
                "valida": True,
                **transicion,
            }

        return {
            "valida": False,
            "mensaje": (
                "Transición no válida en el estado actual "
                f"({self.estados_afd[self.estado_actual_idx]})."
            ),
        }

    def reiniciar(self):
        self.estado_actual_idx = 0
        self.historial.clear()
