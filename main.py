import flet as ft

from automata import AutomataAFD
from sistema import SistemaCompra
from ui import construir_interfaz


def main(page: ft.Page):
    automata = AutomataAFD()
    sistema = SistemaCompra()

    construir_interfaz(
        page,
        automata,
        sistema
    )


ft.run(main)