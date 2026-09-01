import re
import flet as ft
import requests


def main(page: ft.Page):
    page.title = "Simulador PriceSmart - AFD"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    def crear_boton(texto, color_fondo, icono=None, accion=None, data=None):
        return ft.Button(
            texto,
            icon=icono,
            on_click=accion,
            data=data,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color_fondo,
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

    # --- 2. EXTRACCIÓN DE DATOS MEDIANTE API ---
    categorias = ["Todos", "Alimentos", "Accesorios"]

    def obtener_productos_api():
        productos_api = []
        try:
            res_alimentos = requests.get("https://dummyjson.com/products/category/groceries", timeout=5)
            if res_alimentos.status_code == 200:
                for item in res_alimentos.json()["products"]:
                    productos_api.append({
                        "nombre": item["title"][:18] + "..." if len(item["title"]) > 18 else item["title"],
                        "precio": float(item["price"]) * 8.0,
                        "categoria": "Alimentos",
                        "imagen": item["thumbnail"]
                    })

            res_accesorios = requests.get("https://dummyjson.com/products/category/smartphones", timeout=5)
            if res_accesorios.status_code == 200:
                for item in res_accesorios.json()["products"]:
                    productos_api.append({
                        "nombre": item["title"][:18] + "..." if len(item["title"]) > 18 else item["title"],
                        "precio": float(item["price"]) * 8.0,
                        "categoria": "Accesorios",
                        "imagen": item["thumbnail"]
                    })

            if len(productos_api) > 0:
                return productos_api

        except Exception:
            pass

        return [
            {"nombre": "Arroz 5kg", "precio": 45.00, "categoria": "Alimentos", "imagen": None},
            {"nombre": "Frijol 4kg", "precio": 35.00, "categoria": "Alimentos", "imagen": None},
            {"nombre": "TV Smart 50\"", "precio": 2500.00, "categoria": "Accesorios", "imagen": None},
            {"nombre": "Audífonos Bluetooth", "precio": 300.00, "categoria": "Accesorios", "imagen": None}
        ]

    productos = obtener_productos_api()

    # --- EXPRESIONES REGULARES DE VALIDACIÓN ---
    PATRON_MEMBRESIA = re.compile(r"^PS[A-Za-z]{3}[0-9]{3}$")
    PATRON_TARJETA = re.compile(r"^\d{16}$")
    PATRON_FECHA = re.compile(r"^(0[1-9]|1[0-2])\/\d{2}$")
    PATRON_CVV = re.compile(r"^\d{3,4}$")

    # --- 3. ESTADOS Y LÓGICA DEL AFD ---
    estados_afd = ["q0: Inicio", "q1: Membresía validada", "q2: Registrando", "q3: Esperando pago", "q4: Pago aprobado",
                   "q5: Finalizada"]
    estado_actual_idx = 0

    nodos_afd = []
    historial_text = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    total_compra = 0.0
    productos_agregados = []

    txt_total = ft.Text(f"Total: Q0.00", size=20, weight=ft.FontWeight.BOLD)

    def registrar_historial(evento, estado_anterior, estado_nuevo):
        historial_text.controls.append(ft.Text(f"{estado_anterior} --[{evento}]--> {estado_nuevo}"))
        page.update()

    def actualizar_interfaz_afd():
        for i, n_actual in enumerate(nodos_afd):
            if i == estado_actual_idx:
                n_actual.bgcolor = ft.Colors.GREEN_400
                n_actual.shadow = ft.BoxShadow(spread_radius=2, blur_radius=5, color=ft.Colors.GREEN_700)
            else:
                n_actual.bgcolor = ft.Colors.BLUE_GREY_100
                n_actual.shadow = None
        page.update()

    def intentar_transicion(evento, indice_destino, condicion_valida=True):
        nonlocal estado_actual_idx
        if condicion_valida:
            estado_anterior = estados_afd[estado_actual_idx]
            estado_actual_idx = indice_destino
            estado_nuevo = estados_afd[estado_actual_idx]

            registrar_historial(evento, estado_anterior, estado_nuevo)
            actualizar_interfaz_afd()
        else:
            mostrar_alerta(f"Transición no válida en el estado actual ({estados_afd[estado_actual_idx]}).")

    def mostrar_alerta(mensaje, color_fondo=ft.Colors.RED_700):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=color_fondo)
        page.snack_bar.open = True
        page.update()

    # --- 4. FUNCIONES DE INTERACCIÓN ---

    # 4.1 VALIDACIÓN DE MEMBRESÍA
    campo_membresia_dialogo = ft.TextField(
        label="Código de membresía", hint_text="Ej: PSABC123", width=280, max_length=8,
        text_align=ft.TextAlign.CENTER, capitalization=ft.TextCapitalization.CHARACTERS, autofocus=True,
    )
    texto_error_membresia = ft.Text("", color=ft.Colors.RED_600, size=12)

    def cerrar_dialogo_membresia():
        dialogo_membresia.open = False
        page.update()

    def confirmar_membresia(_):
        codigo = (campo_membresia_dialogo.value or "").strip().upper()

        if not PATRON_MEMBRESIA.match(codigo):
            texto_error_membresia.value = "Membresía incorrecta. Formato: PS + 3 letras + 3 números. Intenta nuevamente."
            campo_membresia_dialogo.value = ""
            page.update()
            return

        cerrar_dialogo_membresia()
        intentar_transicion(f"Validar Membresía ({codigo})", 1)

    dialogo_membresia = ft.AlertDialog(
        modal=True, title=ft.Text("Validar Membresía"),
        content=ft.Column(
            [ft.Text("Ingresa tu código de membresía para continuar."), campo_membresia_dialogo, texto_error_membresia],
            tight=True, spacing=10),
        actions=[ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo_membresia()),
                 ft.Button("Validar", on_click=confirmar_membresia)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_membresia)

    def btn_validar_membresia(_):
        if estado_actual_idx != 0:
            mostrar_alerta("La membresía ya fue validada o el proceso ya inició.")
            return
        campo_membresia_dialogo.value = ""
        texto_error_membresia.value = ""
        dialogo_membresia.open = True
        page.update()

    # 4.2 AGREGAR PRODUCTOS Y RESUMEN
    def btn_agregar_producto(e):
        nonlocal total_compra
        if estado_actual_idx in [1, 2]:
            producto = e.control.data
            productos_agregados.append(producto)
            total_compra += producto["precio"]
            txt_total.value = f"Total: Q{total_compra:.2f}"
            intentar_transicion("Registrar Producto (r)", 2)
        else:
            mostrar_alerta("Debes validar tu membresía antes de registrar productos.")
            btn_validar_membresia(None)

    def cerrar_dialogo_resumen(_):
        dialogo_resumen.open = False
        page.update()

    def confirmar_finalizar_registro(_):
        dialogo_resumen.open = False
        page.update()
        intentar_transicion("Finalizar Registro (f)", 3)

    dialogo_resumen = ft.AlertDialog(
        modal=True,
        title=ft.Text("Resumen de tu carrito"),
        actions=[
            ft.Button("Quiero agregar más", on_click=cerrar_dialogo_resumen),
            ft.Button("Confirmar y Finalizar", on_click=confirmar_finalizar_registro),
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
    page.overlay.append(dialogo_resumen)

    def abrir_dialogo_resumen():
        lista_visual = ft.ListView(expand=True, spacing=5)
        for p in productos_agregados:
            lista_visual.controls.append(
                ft.Row([ft.Text(p["nombre"], expand=True), ft.Text(f"Q{p['precio']:.2f}")])
            )

        contenido = ft.Column([
            ft.Text("Revisa tus productos antes de finalizar:", italic=True),
            ft.Container(content=lista_visual, height=150, bgcolor=ft.Colors.GREY_100, padding=10, border_radius=8),
            ft.Divider(),
            ft.Row([ft.Text("Subtotal:", weight=ft.FontWeight.BOLD), ft.Text(f"Q{total_compra:.2f}")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, size=18),
                    ft.Text(f"Q{total_compra:.2f}", size=18, color=ft.Colors.GREEN_700)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("¿Estás seguro de que no quieres agregar algún otro producto?", size=12,
                    color=ft.Colors.BLUE_GREY_600)
        ], tight=True, width=350)

        dialogo_resumen.content = contenido
        dialogo_resumen.open = True
        page.update()

    def btn_finalizar_registro(_):
        if estado_actual_idx == 2:
            if not productos_agregados:
                mostrar_alerta("No has agregado ningún producto.")
                return
            abrir_dialogo_resumen()
        elif estado_actual_idx > 2:
            mostrar_alerta("El registro ya fue finalizado.")
        else:
            mostrar_alerta("Debes agregar productos primero.")

    # 4.3 PAGO CON TARJETA (NUEVA LÓGICA)
    campo_nombre = ft.TextField(label="Nombre Completo", width=300, autofocus=True)
    campo_nit = ft.TextField(label="NIT / DPI", width=300)
    campo_tarjeta = ft.TextField(label="Número de Tarjeta", hint_text="16 dígitos", width=300, max_length=16,
                                 keyboard_type=ft.KeyboardType.NUMBER)
    campo_fecha = ft.TextField(label="Vencimiento", hint_text="MM/YY", width=140, max_length=5)
    campo_cvv = ft.TextField(label="CVV", width=140, max_length=4, password=True, can_reveal_password=True,
                             keyboard_type=ft.KeyboardType.NUMBER)
    texto_error_pago = ft.Text("", color=ft.Colors.RED_600, size=12)

    def cerrar_dialogo_pago():
        dialogo_pago.open = False
        page.update()

    def procesar_pago(_):
        if not campo_nombre.value or not campo_nit.value:
            texto_error_pago.value = "Ingresa tus datos personales (Nombre y NIT/DPI)."
            page.update()
            return

        tarjeta = (campo_tarjeta.value or "").strip()
        fecha = (campo_fecha.value or "").strip()
        cvv = (campo_cvv.value or "").strip()

        if not PATRON_TARJETA.match(tarjeta):
            texto_error_pago.value = "Tarjeta inválida. Deben ser exactamente 16 dígitos numéricos."
            page.update()
            return

        if not PATRON_FECHA.match(fecha):
            texto_error_pago.value = "Fecha inválida. Usa el formato MM/YY (Ej. 12/25)."
            page.update()
            return

        if not PATRON_CVV.match(cvv):
            texto_error_pago.value = "CVV inválido. Deben ser 3 o 4 dígitos."
            page.update()
            return

        # Si todo es correcto, procesamos en el AFD
        texto_error_pago.value = ""
        cerrar_dialogo_pago()
        intentar_transicion("Realizar Pago (p)", 4)
        intentar_transicion("Aprobar Pago (a)", 5)
        mostrar_alerta("¡Pago aprobado! Compra finalizada exitosamente.", color_fondo=ft.Colors.GREEN_700)

    dialogo_pago = ft.AlertDialog(
        modal=True,
        title=ft.Text("Facturación y Pago Seguro"),
        content=ft.Column([
            ft.Text("Datos del Titular", weight=ft.FontWeight.BOLD),
            campo_nombre,
            campo_nit,
            ft.Divider(),
            ft.Text("Detalles de la Tarjeta", weight=ft.FontWeight.BOLD),
            campo_tarjeta,
            ft.Row([campo_fecha, campo_cvv], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            texto_error_pago
        ], tight=True, spacing=10),
        actions=[
            ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo_pago()),
            ft.Button("Procesar Pago", on_click=procesar_pago),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_pago)

    def btn_pagar(_):
        if estado_actual_idx == 3:
            # Limpiar campos de pago por si acaso
            campo_nombre.value = ""
            campo_nit.value = ""
            campo_tarjeta.value = ""
            campo_fecha.value = ""
            campo_cvv.value = ""
            texto_error_pago.value = ""

            dialogo_pago.open = True
            page.update()
        elif estado_actual_idx == 5:
            mostrar_alerta("Esta compra ya fue finalizada. Reinicia el sistema.")
        else:
            mostrar_alerta("Debes finalizar el registro (Paso 2) antes de proceder a pagar.")

    def btn_reiniciar(_):
        nonlocal estado_actual_idx, total_compra
        total_compra = 0.0
        productos_agregados.clear()
        txt_total.value = f"Total: Q0.00"
        historial_text.controls.clear()
        historial_text.controls.append(ft.Text("--- Sistema Reiniciado ---", italic=True))
        estado_actual_idx = 0
        campo_membresia_dialogo.value = ""
        texto_error_membresia.value = ""
        actualizar_interfaz_afd()

    # --- 5. CONSTRUCCIÓN DE LA INTERFAZ ---
    columna_afd = ft.Column(expand=1, alignment=ft.MainAxisAlignment.START, spacing=15)
    columna_afd.controls.append(ft.Text("Diagrama del AFD", size=24, weight=ft.FontWeight.BOLD))

    for estado in estados_afd:
        nodo = ft.Container(
            content=ft.Text(estado, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            padding=10,
            alignment=ft.Alignment(0, 0),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_GREY_100,
            width=200
        )
        nodos_afd.append(nodo)
        columna_afd.controls.append(nodo)

        if estado != estados_afd[-1]:
            columna_afd.controls.append(ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.BLUE_GREY_400))

    columna_afd.controls.append(ft.Divider())
    columna_afd.controls.append(ft.Text("Historial de Transiciones", size=20, weight=ft.FontWeight.BOLD))

    contenedor_historial = ft.Container(
        content=historial_text,
        bgcolor=ft.Colors.GREY_100,
        border_radius=5,
        padding=10,
        expand=True
    )
    columna_afd.controls.append(contenedor_historial)

    columna_catalogo = ft.Column(expand=True, spacing=10, scroll=ft.ScrollMode.AUTO)

    def crear_tarjeta_producto(prod):
        elementos_tarjeta = []
        if prod.get("imagen"):
            elementos_tarjeta.append(ft.Image(src=prod["imagen"], height=90, fit=ft.BoxFit.CONTAIN))

        elementos_tarjeta.extend([
            ft.Text(prod["nombre"], weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text(prod["categoria"], size=11, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_GREY_400,
                padding=ft.Padding(left=8, top=2, right=8, bottom=2),
                border_radius=12,
            ),
            ft.Text(f"Q{prod['precio']:.2f}", color=ft.Colors.GREEN_700),
            crear_boton("Agregar", ft.Colors.BLUE_GREY_600, accion=btn_agregar_producto, data=prod)
        ])

        return ft.Card(
            content=ft.Container(
                padding=10,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    elementos_tarjeta,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

    def cargar_productos(categoria_filtro="Todos"):
        columna_catalogo.controls.clear()

        if categoria_filtro == "Todos":
            categorias_presentes = [c for c in categorias if c != "Todos"]
            for categoria in categorias_presentes:
                productos_categoria = [p for p in productos if p["categoria"] == categoria]
                if not productos_categoria:
                    continue

                columna_catalogo.controls.append(
                    ft.Text(categoria, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800)
                )

                grid = ft.GridView(
                    max_extent=200,
                    child_aspect_ratio=0.8,
                    spacing=10,
                    run_spacing=10,
                    height=260,
                )
                grid.controls = [crear_tarjeta_producto(p) for p in productos_categoria]
                columna_catalogo.controls.append(grid)
        else:
            productos_categoria = [p for p in productos if p["categoria"] == categoria_filtro]
            columna_catalogo.controls.append(
                ft.Text(categoria_filtro, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800)
            )
            grid = ft.GridView(
                height=550,
                max_extent=200,
                child_aspect_ratio=0.8,
                spacing=10,
                run_spacing=10,
            )
            grid.controls = [crear_tarjeta_producto(p) for p in productos_categoria]
            columna_catalogo.controls.append(grid)

        page.update()

    def cambiar_categoria(e):
        cargar_productos(e.control.value)

    dropdown_categorias = ft.Dropdown(
        label="Buscar por Categoría",
        options=[ft.dropdown.Option(key=cat, text=cat) for cat in categorias],
        value="Todos",
        width=250
    )
    dropdown_categorias.on_change = cambiar_categoria

    boton_membresia = crear_boton("1. Validar Membresía", ft.Colors.BLUE_600, accion=btn_validar_membresia)
    boton_finalizar_reg = crear_boton("2. Finalizar Registro", ft.Colors.ORANGE_600, accion=btn_finalizar_registro)
    boton_pagar = crear_boton("3. Pagar y Finalizar", ft.Colors.GREEN_600, accion=btn_pagar)

    fila_controles = ft.Row(
        [boton_membresia, boton_finalizar_reg, boton_pagar],
        wrap=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    boton_reiniciar = crear_boton("Reiniciar Sistema", ft.Colors.RED_600, icono=ft.Icons.REFRESH, accion=btn_reiniciar)

    columna_sistema = ft.Column(expand=2, spacing=20)
    columna_sistema.controls.extend([
        ft.Text("Módulo de Caja - PriceSmart", size=28, weight=ft.FontWeight.BOLD),
        fila_controles,
        ft.Divider(),
        dropdown_categorias,
        columna_catalogo,
        ft.Divider(),
        ft.Row([txt_total, boton_reiniciar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])

    page.add(
        ft.Row(
            [columna_sistema, ft.VerticalDivider(), columna_afd],
            expand=True
        )
    )

    cargar_productos()
    actualizar_interfaz_afd()


ft.run(main)