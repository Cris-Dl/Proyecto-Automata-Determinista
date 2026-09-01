import asyncio
import flet as ft


def construir_interfaz(page: ft.Page, automata, sistema):
    """
    ETAPA 4 - UI MODERNA / TIENDA + AFD VISUAL
    --------------------------------------------
    Esta versión modifica SOLAMENTE ui.py.

    NO cambia:
    - automata.py
    - sistema.py
    - main.py
    - estados ni flujo del prototipo actual

    Objetivos de esta etapa:
    - Dar más aire visual a toda la aplicación.
    - Mejorar el responsive interno, no solo el layout exterior.
    - Convertir el encabezado en una barra de tienda online.
    - Agregar búsqueda visual y contador de carrito.
    - Mejorar hover y feedback de "Agregar".
    - Rediseñar el AFD como diagrama real, no como una fila de botones.
    - Mantener el historial como elemento académico principal.
    - Modernizar modales y pantalla de confirmación.
    """

    # ==================================================================
    # 1. TOKENS VISUALES
    # ==================================================================
    AZUL_950 = "#072B61"
    AZUL_900 = "#0A3D82"
    AZUL_800 = "#0D4EA5"
    AZUL_700 = "#1668C7"
    AZUL_600 = "#247FE0"
    AZUL_200 = "#BCD7F8"
    AZUL_100 = "#DCEBFF"
    AZUL_50 = "#F0F6FF"

    ROJO_700 = "#D92C34"
    ROJO_600 = "#EF3E42"
    ROJO_100 = "#FFD9DB"
    ROJO_50 = "#FFF3F4"

    VERDE_700 = "#167A55"
    VERDE_600 = "#1D9667"
    VERDE_100 = "#CDEFE1"
    VERDE_50 = "#EEFBF5"

    AMBAR_700 = "#B86108"
    AMBAR_600 = "#D97706"
    AMBAR_100 = "#FFE7B7"
    AMBAR_50 = "#FFF8E9"

    TEXTO = "#172033"
    TEXTO_2 = "#435368"
    TEXTO_SUAVE = "#738397"
    BORDE = "#E3EAF2"
    BORDE_SUAVE = "#EDF1F6"
    SUPERFICIE = "#FFFFFF"
    SUPERFICIE_2 = "#F8FAFD"
    FONDO = "#F2F6FB"

    page.title = "Simulador PriceSmart - AFD"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = FONDO

    categorias = sistema.categorias
    productos = sistema.productos
    estados_afd = automata.estados_afd

    # ==================================================================
    # 2. HELPERS DE COMPATIBILIDAD / ANIMACIÓN
    # ==================================================================
    def animar(control, propiedad, duracion=180):
        try:
            setattr(
                control,
                propiedad,
                ft.Animation(duracion, ft.AnimationCurve.EASE_OUT),
            )
            return True
        except Exception:
            return False

    def sombra(blur=18, color="#DDE6F0", spread=0):
        try:
            return ft.BoxShadow(
                blur_radius=blur,
                spread_radius=spread,
                color=color,
            )
        except Exception:
            return ft.BoxShadow(blur_radius=blur, color=color)

    def gradiente(colores, begin=None, end=None):
        clase = getattr(ft, "LinearGradient", None)
        if clase is None:
            return None
        try:
            return clase(
                begin=begin or ft.Alignment(-1, -1),
                end=end or ft.Alignment(1, 1),
                colors=colores,
            )
        except Exception:
            return None

    def blur_seguro(sigma=35):
        clase = getattr(ft, "Blur", None)
        if clase is None:
            return None
        for creador in (
            lambda: clase(sigma_x=sigma, sigma_y=sigma),
            lambda: clase(sigma, sigma),
        ):
            try:
                return creador()
            except Exception:
                pass
        return None

    def blob(color, size, left=None, right=None, top=None, bottom=None, opacity=0.55):
        kwargs = dict(
            width=size,
            height=size,
            bgcolor=color,
            border_radius=999,
            opacity=opacity,
            left=left,
            right=right,
            top=top,
            bottom=bottom,
        )
        b = blur_seguro(48)
        if b is not None:
            kwargs["blur"] = b
        return ft.Container(**kwargs)

    def lanzar_tarea(funcion, *args):
        """Ejecuta microanimación si la versión de Flet ofrece page.run_task."""
        try:
            if hasattr(page, "run_task"):
                page.run_task(funcion, *args)
        except Exception:
            pass

    # ==================================================================
    # 3. HELPERS DE TEXTO / AFD
    # ==================================================================
    def codigo_estado(estado_completo):
        return estado_completo.split(":", 1)[0].strip()

    def nombre_estado(estado_completo):
        partes = estado_completo.split(":", 1)
        return partes[1].strip() if len(partes) == 2 else estado_completo

    def simbolo_de_evento(evento):
        e = evento.lower()
        if "validar membresía" in e:
            return "VM"
        if "registrar producto" in e:
            return "RP"
        if "finalizar registro" in e:
            return "FR"
        if "realizar pago" in e:
            return "PG"
        if "aprobar pago" in e:
            return "AP"
        return "—"

    def explicacion_evento(simbolo, valido=True):
        textos = {
            "VM": "Se valida la membresía del cliente.",
            "RP": "Se registra un producto en la compra.",
            "FR": "Se cierra el registro de productos.",
            "PG": "Se procesa la información de pago.",
            "AP": "El pago es aprobado y finaliza la compra.",
        }
        base = textos.get(simbolo, "Evento del sistema.")
        return base if valido else f"{base} El AFD conserva el estado actual."

    def mostrar_alerta(mensaje, color_fondo=ROJO_600):
        page.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color_fondo,
        )
        page.snack_bar.open = True
        page.update()

    def chip(texto, fg=AZUL_800, bg=AZUL_50, icono=None):
        controles = []
        if icono is not None:
            controles.append(ft.Icon(icono, size=12, color=fg))
        controles.append(
            ft.Text(texto, size=9, weight=ft.FontWeight.BOLD, color=fg)
        )
        return ft.Container(
            bgcolor=bg,
            border_radius=999,
            padding=ft.Padding(left=9, top=5, right=9, bottom=5),
            content=ft.Row(controles, spacing=5, tight=True),
        )

    def boton(texto, color, accion, icono=None, data=None, width=None):
        b = ft.Button(
            texto,
            icon=icono,
            on_click=accion,
            data=data,
            width=width,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(left=16, top=12, right=16, bottom=12),
            ),
        )
        return b

    # ==================================================================
    # 4. ESTADO VISUAL COMPARTIDO
    # ==================================================================
    txt_total = ft.Text("Q0.00", size=22, weight=ft.FontWeight.BOLD, color=AZUL_950)
    txt_carrito = ft.Text("0", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    txt_membresia = ft.Text("Sin validar", size=10, color=TEXTO_SUAVE)

    txt_codigo_estado = ft.Text(
        codigo_estado(estados_afd[automata.estado_actual_idx]),
        size=12,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )
    txt_estado_actual = ft.Text(
        nombre_estado(estados_afd[automata.estado_actual_idx]),
        size=18,
        weight=ft.FontWeight.BOLD,
        color=AZUL_950,
    )
    txt_formula = ft.Text(
        "Aún no se ha ejecutado ningún evento.",
        size=11,
        color=TEXTO_SUAVE,
    )

    # ==================================================================
    # 5. HISTORIAL RESPONSIVE
    # ==================================================================
    historial_paso = 0
    lista_historial = ft.ListView(spacing=9, auto_scroll=True, height=420)

    def crear_item_historial(
        paso,
        estado_actual,
        simbolo,
        transicion,
        nuevo_estado,
        explicacion,
        valida=True,
        inicial=False,
    ):
        if inicial:
            acento, fondo, estado_chip = AZUL_600, "#F8FBFF", chip("INICIAL", AZUL_800, AZUL_100)
        elif valida:
            acento, fondo, estado_chip = VERDE_600, SUPERFICIE, chip("VÁLIDA", VERDE_700, VERDE_50)
        else:
            acento, fondo, estado_chip = ROJO_600, "#FFFBFB", chip("NO VÁLIDA", ROJO_700, ROJO_50)

        def campo(titulo, valor, col, color=TEXTO):
            return ft.Container(
                col=col,
                content=ft.Column(
                    [
                        ft.Text(titulo.upper(), size=8, weight=ft.FontWeight.BOLD, color=TEXTO_SUAVE),
                        ft.Text(str(valor), size=11, weight=ft.FontWeight.BOLD, color=color, max_lines=3),
                    ],
                    spacing=2,
                    tight=True,
                ),
            )

        contenido = ft.Container(
            expand=True,
            padding=ft.Padding(left=14, top=12, right=14, bottom=12),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(f"Paso {paso}", size=12, weight=ft.FontWeight.BOLD, color=AZUL_950),
                            estado_chip,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ResponsiveRow(
                        [
                            campo("Estado", estado_actual, {"xs": 6, "sm": 3, "lg": 2}, AZUL_900),
                            campo("Símbolo", simbolo, {"xs": 6, "sm": 3, "lg": 2}, AZUL_900),
                            campo("Nuevo", nuevo_estado, {"xs": 6, "sm": 3, "lg": 2}, VERDE_700 if valida else ROJO_700),
                            campo("Transición", transicion, {"xs": 12, "sm": 6, "lg": 3}),
                            campo("Explicación", explicacion, {"xs": 12, "sm": 6, "lg": 3}, TEXTO_2),
                        ],
                        spacing=8,
                        run_spacing=8,
                    ),
                ],
                spacing=9,
            ),
        )

        return ft.Container(
            bgcolor=fondo,
            border_radius=14,
            shadow=sombra(7, "#E7EDF4"),
            content=ft.Row(
                [
                    ft.Container(width=4, bgcolor=acento, border_radius=999),
                    contenido,
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    def cargar_estado_inicial_historial():
        nonlocal historial_paso
        historial_paso = 0
        lista_historial.controls.clear()
        lista_historial.controls.append(
            crear_item_historial(
                0, "q0", "—", "—", "q0", "Estado inicial del autómata.", inicial=True
            )
        )

    def registrar_historial(evento, estado_anterior, estado_nuevo):
        nonlocal historial_paso
        historial_paso += 1
        q1 = codigo_estado(estado_anterior)
        q2 = codigo_estado(estado_nuevo)
        s = simbolo_de_evento(evento)
        lista_historial.controls.append(
            crear_item_historial(
                historial_paso,
                q1,
                s,
                f"δ({q1}, {s}) = {q2}",
                q2,
                explicacion_evento(s, True),
                valida=True,
            )
        )

    def registrar_invalida(simbolo, explicacion):
        nonlocal historial_paso
        historial_paso += 1
        q = codigo_estado(estados_afd[automata.estado_actual_idx])
        lista_historial.controls.append(
            crear_item_historial(
                historial_paso,
                q,
                simbolo,
                "No válida",
                q,
                explicacion,
                valida=False,
            )
        )
        txt_formula.value = f"{q} + {simbolo} → {q}  ·  transición no válida"
        page.update()

    cargar_estado_inicial_historial()

    # ==================================================================
    # 6. AFD VISUAL - DIAGRAMA SERPENTEANTE
    # ==================================================================
    nodo_refs = []
    conector_refs = {}

    def crear_nodo(idx):
        estado = estados_afd[idx]
        q = codigo_estado(estado)
        nombre = nombre_estado(estado)

        texto_q = ft.Text(q, size=14, weight=ft.FontWeight.BOLD, color=AZUL_950)
        circulo_interno = ft.Container(
            width=58,
            height=58,
            border_radius=999,
            bgcolor=SUPERFICIE,
            alignment=ft.Alignment(0, 0),
            content=texto_q,
        )
        circulo_externo = ft.Container(
            width=68,
            height=68,
            border_radius=999,
            bgcolor="#D9E2EC" if idx != len(estados_afd) - 1 else AZUL_200,
            padding=5 if idx != len(estados_afd) - 1 else 4,
            alignment=ft.Alignment(0, 0),
            content=circulo_interno,
        )
        animar(circulo_externo, "animate_scale", 180)

        nombre_txt = ft.Text(
            nombre,
            size=9,
            color=TEXTO_SUAVE,
            text_align=ft.TextAlign.CENTER,
            max_lines=2,
        )

        loop = None
        if idx == 2:
            loop = chip("↻ RP", AMBAR_700, AMBAR_50)

        elementos = []
        if loop is not None:
            elementos.append(loop)
        elementos.extend([circulo_externo, nombre_txt])

        control = ft.Container(
            width=96,
            content=ft.Column(
                elementos,
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        nodo_refs.append(
            {
                "outer": circulo_externo,
                "inner": circulo_interno,
                "q": texto_q,
                "name": nombre_txt,
            }
        )
        return control

    def crear_conector(simbolo, direccion="right"):
        color = "#91A2B4"
        icono = ft.Icons.ARROW_FORWARD if direccion == "right" else ft.Icons.ARROW_BACK
        evento_chip = chip(simbolo, AZUL_800, AZUL_50)
        flecha = ft.Icon(icono, size=20, color=color)
        caja = ft.Container(
            width=62,
            content=ft.Column(
                [evento_chip, flecha],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        conector_refs[simbolo] = {"box": caja, "chip": evento_chip, "arrow": flecha}
        return caja

    def crear_conector_vertical(simbolo):
        evento_chip = chip(simbolo, AZUL_800, AZUL_50)
        flecha = ft.Icon(ft.Icons.ARROW_DOWNWARD, size=20, color="#91A2B4")
        caja = ft.Container(
            width=90,
            content=ft.Column(
                [evento_chip, flecha],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        conector_refs[simbolo] = {"box": caja, "chip": evento_chip, "arrow": flecha}
        return caja

    n0, n1, n2, n3, n4, n5 = [crear_nodo(i) for i in range(6)]
    c_vm = crear_conector("VM", "right")
    c_rp = crear_conector("RP", "right")
    c_fr = crear_conector_vertical("FR")
    c_pg = crear_conector("PG", "left")
    c_ap = crear_conector("AP", "left")

    fila_superior = ft.Row(
        [n0, c_vm, n1, c_rp, n2],
        spacing=2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    fila_intermedia = ft.Row(
        [ft.Container(width=350), c_fr],
        spacing=0,
    )
    fila_inferior = ft.Row(
        [n5, c_ap, n4, c_pg, n3],
        spacing=2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    diagrama_contenido = ft.Container(
        width=590,
        padding=ft.Padding(left=8, top=8, right=8, bottom=8),
        content=ft.Column(
            [fila_superior, fila_intermedia, fila_inferior],
            spacing=1,
        ),
    )

    diagrama_scroll = ft.Row(
        [diagrama_contenido],
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
    )

    async def pulso_nodo(idx):
        try:
            ref = nodo_refs[idx]["outer"]
            ref.scale = 1.10
            ref.update()
            await asyncio.sleep(0.16)
            ref.scale = 1.0
            ref.update()
        except Exception:
            pass

    def actualizar_interfaz_afd(ultimo_evento=None, transicion=None):
        estado = estados_afd[automata.estado_actual_idx]
        q = codigo_estado(estado)
        txt_codigo_estado.value = q
        txt_estado_actual.value = nombre_estado(estado)

        if transicion is not None:
            q1, s, q2 = transicion
            txt_formula.value = f"δ({q1}, {s}) = {q2}"

        for i, ref in enumerate(nodo_refs):
            activo = i == automata.estado_actual_idx
            final = i == len(estados_afd) - 1
            if activo:
                ref["outer"].bgcolor = AZUL_200
                ref["outer"].shadow = sombra(18, "#9CC8F6", 1)
                ref["inner"].bgcolor = AZUL_700
                ref["q"].color = ft.Colors.WHITE
                ref["name"].color = AZUL_900
                ref["name"].weight = ft.FontWeight.BOLD
            else:
                ref["outer"].bgcolor = AZUL_200 if final else "#D9E2EC"
                ref["outer"].shadow = None
                ref["inner"].bgcolor = SUPERFICIE
                ref["q"].color = AZUL_950
                ref["name"].color = TEXTO_SUAVE
                ref["name"].weight = ft.FontWeight.NORMAL

        # Normalizar conectores
        for s, ref in conector_refs.items():
            try:
                ref["arrow"].color = "#91A2B4"
                ref["chip"].bgcolor = AZUL_50
                ref["chip"].content.controls[-1].color = AZUL_800
            except Exception:
                pass

        if ultimo_evento:
            s = simbolo_de_evento(ultimo_evento)
            if s in conector_refs:
                try:
                    ref = conector_refs[s]
                    ref["arrow"].color = VERDE_600
                    ref["chip"].bgcolor = VERDE_50
                    ref["chip"].content.controls[-1].color = VERDE_700
                except Exception:
                    pass

        lanzar_tarea(pulso_nodo, automata.estado_actual_idx)
        page.update()

    def intentar_transicion(evento, indice_destino, condicion_valida=True):
        resultado = automata.intentar_transicion(evento, indice_destino, condicion_valida)
        if resultado["valida"]:
            registrar_historial(
                resultado["evento"],
                resultado["estado_anterior"],
                resultado["estado_nuevo"],
            )
            q1 = codigo_estado(resultado["estado_anterior"])
            q2 = codigo_estado(resultado["estado_nuevo"])
            s = simbolo_de_evento(resultado["evento"])
            actualizar_interfaz_afd(resultado["evento"], (q1, s, q2))
        else:
            s = simbolo_de_evento(evento)
            registrar_invalida(s, resultado["mensaje"])
            mostrar_alerta(resultado["mensaje"])

    # ==================================================================
    # 7. MEMBRESÍA
    # ==================================================================
    campo_membresia = ft.TextField(
        label="Código de membresía",
        hint_text="PSABC123",
        width=320,
        max_length=8,
        text_align=ft.TextAlign.CENTER,
        capitalization=ft.TextCapitalization.CHARACTERS,
        autofocus=True,
    )
    error_membresia = ft.Text("", color=ROJO_600, size=11)

    def cerrar_membresia(_=None):
        dialogo_membresia.open = False
        page.update()

    def confirmar_membresia(_):
        codigo = (campo_membresia.value or "").strip().upper()
        if not sistema.validar_membresia(codigo):
            error_membresia.value = "Formato inválido. Usa PS + 3 letras + 3 números."
            campo_membresia.value = ""
            page.update()
            return
        cerrar_membresia()
        txt_membresia.value = "Validada"
        intentar_transicion(f"Validar Membresía ({codigo})", 1)

    dialogo_membresia = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(
                    width=38,
                    height=38,
                    border_radius=12,
                    bgcolor=AZUL_50,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.PERSON_OUTLINE, color=AZUL_700),
                ),
                ft.Column(
                    [
                        ft.Text("Validar membresía", weight=ft.FontWeight.BOLD, color=AZUL_950),
                        ft.Text("Identifica al cliente antes de registrar productos.", size=10, color=TEXTO_SUAVE),
                    ],
                    spacing=1,
                ),
            ],
            spacing=10,
        ),
        content=ft.Column(
            [
                ft.Container(
                    bgcolor=AZUL_50,
                    border_radius=14,
                    padding=14,
                    content=ft.Text(
                        "Código de prueba esperado: PS + 3 letras + 3 números.",
                        size=11,
                        color=AZUL_900,
                    ),
                ),
                campo_membresia,
                error_membresia,
            ],
            spacing=12,
            tight=True,
        ),
        actions=[
            ft.Button("Cancelar", on_click=cerrar_membresia),
            ft.Button("Validar", on_click=confirmar_membresia),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_membresia)

    def btn_validar_membresia(_):
        if automata.estado_actual_idx != 0:
            registrar_invalida("VM", "La membresía ya fue validada o el proceso ya inició.")
            mostrar_alerta("La membresía ya fue validada o el proceso ya inició.")
            return
        campo_membresia.value = ""
        error_membresia.value = ""
        dialogo_membresia.open = True
        page.update()

    # ==================================================================
    # 8. CARRITO / PRODUCTOS
    # ==================================================================
    dialogo_carrito = ft.AlertDialog(
        modal=True,
        content=ft.Text(""),
    )
    page.overlay.append(dialogo_carrito)

    def cerrar_carrito(_=None):
        dialogo_carrito.open = False
        page.update()

    def confirmar_finalizar_registro(_):
        dialogo_carrito.open = False
        page.update()
        intentar_transicion("Finalizar Registro (f)", 3)

    def abrir_carrito(_=None):
        items = ft.ListView(height=220, spacing=8)
        if not sistema.productos_agregados:
            items.controls.append(
                ft.Container(
                    height=130,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=34, color="#A9B7C7"),
                            ft.Text("Tu carrito está vacío", weight=ft.FontWeight.BOLD, color=TEXTO_2),
                            ft.Text("Agrega productos para continuar.", size=10, color=TEXTO_SUAVE),
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
            )
        else:
            for p in sistema.productos_agregados:
                items.controls.append(
                    ft.Container(
                        bgcolor=SUPERFICIE_2,
                        border_radius=12,
                        padding=10,
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=42,
                                    height=42,
                                    border_radius=10,
                                    bgcolor=SUPERFICIE,
                                    alignment=ft.Alignment(0, 0),
                                    content=(
                                        ft.Image(src=p["imagen"], fit=ft.BoxFit.CONTAIN)
                                        if p.get("imagen")
                                        else ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color="#A9B7C7")
                                    ),
                                ),
                                ft.Column(
                                    [
                                        ft.Text(p["nombre"], size=11, weight=ft.FontWeight.BOLD, color=TEXTO, max_lines=1),
                                        ft.Text(p["categoria"], size=9, color=TEXTO_SUAVE),
                                    ],
                                    spacing=1,
                                    expand=True,
                                ),
                                ft.Text(f"Q{p['precio']:.2f}", weight=ft.FontWeight.BOLD, color=AZUL_900),
                            ],
                            spacing=10,
                        ),
                    )
                )

        acciones = [ft.Button("Seguir comprando", on_click=cerrar_carrito)]
        if sistema.productos_agregados and automata.estado_actual_idx == 2:
            acciones.append(ft.Button("Finalizar registro", on_click=confirmar_finalizar_registro))

        dialogo_carrito.title = ft.Row(
            [
                ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=AZUL_700),
                ft.Text("Tu carrito", weight=ft.FontWeight.BOLD, color=AZUL_950),
                chip(str(len(sistema.productos_agregados)), AZUL_800, AZUL_50),
            ],
            spacing=8,
        )
        dialogo_carrito.content = ft.Column(
            [
                items,
                ft.Divider(color=BORDE),
                ft.Row(
                    [
                        ft.Text("TOTAL", size=10, weight=ft.FontWeight.BOLD, color=TEXTO_SUAVE),
                        ft.Text(f"Q{sistema.total_compra:.2f}", size=20, weight=ft.FontWeight.BOLD, color=AZUL_950),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            width=420,
            tight=True,
            spacing=10,
        )
        dialogo_carrito.actions = acciones
        dialogo_carrito.actions_alignment = ft.MainAxisAlignment.END
        dialogo_carrito.open = True
        page.update()

    async def pulso_producto(card, indicador):
        try:
            indicador.visible = True
            card.scale = 1.025
            card.shadow = sombra(20, "#BFEAD8", 1)
            card.update()
            await asyncio.sleep(0.20)
            card.scale = 1.0
            card.update()
            await asyncio.sleep(0.65)
            indicador.visible = False
            card.shadow = sombra(12, "#E1E9F2")
            card.update()
        except Exception:
            pass

    def agregar_producto(e):
        if automata.estado_actual_idx not in [1, 2]:
            registrar_invalida("RP", "No se puede registrar un producto antes de validar la membresía.")
            mostrar_alerta("Debes validar tu membresía antes de registrar productos.")
            return

        info = e.control.data
        producto = info["producto"]
        sistema.agregar_producto(producto)
        txt_total.value = f"Q{sistema.total_compra:.2f}"
        txt_carrito.value = str(len(sistema.productos_agregados))
        intentar_transicion("Registrar Producto (r)", 2)
        lanzar_tarea(pulso_producto, info["card"], info["indicador"])

    # ==================================================================
    # 9. PAGO / CHECKOUT
    # ==================================================================
    campo_nombre = ft.TextField(label="Nombre completo", width=330, autofocus=True)
    campo_nit = ft.TextField(label="NIT / DPI", width=330)
    campo_tarjeta = ft.TextField(
        label="Número de tarjeta",
        hint_text="16 dígitos",
        width=330,
        max_length=16,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_fecha = ft.TextField(label="Vencimiento", hint_text="MM/YY", width=155, max_length=5)
    campo_cvv = ft.TextField(
        label="CVV",
        width=155,
        max_length=4,
        password=True,
        can_reveal_password=True,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    error_pago = ft.Text("", color=ROJO_600, size=11)

    dialogo_exito = ft.AlertDialog(
        modal=True,
        content=ft.Text(""),
    )
    page.overlay.append(dialogo_exito)

    def cerrar_exito(_=None):
        dialogo_exito.open = False
        page.update()

    def mostrar_exito():
        dialogo_exito.title = None
        dialogo_exito.content = ft.Container(
            width=390,
            padding=10,
            content=ft.Column(
                [
                    ft.Container(
                        width=74,
                        height=74,
                        border_radius=999,
                        bgcolor=VERDE_50,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=42, color=VERDE_600),
                    ),
                    ft.Text("¡Compra completada!", size=23, weight=ft.FontWeight.BOLD, color=AZUL_950),
                    ft.Text(
                        "El pago fue procesado y el AFD llegó a su estado final.",
                        size=11,
                        color=TEXTO_SUAVE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        bgcolor=SUPERFICIE_2,
                        border_radius=16,
                        padding=16,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("TOTAL", size=9, color=TEXTO_SUAVE),
                                        ft.Text(f"Q{sistema.total_compra:.2f}", size=19, weight=ft.FontWeight.BOLD, color=AZUL_950),
                                    ],
                                    spacing=1,
                                ),
                                ft.Column(
                                    [
                                        ft.Text("ESTADO", size=9, color=TEXTO_SUAVE),
                                        ft.Text("q5 · Finalizada", size=12, weight=ft.FontWeight.BOLD, color=VERDE_700),
                                    ],
                                    spacing=1,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ),
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        dialogo_exito.actions = [ft.Button("Cerrar", on_click=cerrar_exito)]
        dialogo_exito.actions_alignment = ft.MainAxisAlignment.CENTER
        dialogo_exito.open = True
        page.update()

    def cerrar_pago(_=None):
        dialogo_pago.open = False
        page.update()

    def procesar_pago(_):
        valido, mensaje = sistema.validar_pago(
            campo_nombre.value,
            campo_nit.value,
            (campo_tarjeta.value or "").strip(),
            (campo_fecha.value or "").strip(),
            (campo_cvv.value or "").strip(),
        )
        if not valido:
            error_pago.value = mensaje
            page.update()
            return

        error_pago.value = ""
        cerrar_pago()
        # Se conserva exactamente la lógica del prototipo actual.
        intentar_transicion("Realizar Pago (p)", 4)
        intentar_transicion("Aprobar Pago (a)", 5)
        mostrar_exito()

    dialogo_pago = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=12,
                    bgcolor=VERDE_50,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.PAYMENTS_OUTLINED, color=VERDE_700),
                ),
                ft.Column(
                    [
                        ft.Text("Facturación y pago", weight=ft.FontWeight.BOLD, color=AZUL_950),
                        ft.Text("Datos ficticios para la simulación.", size=10, color=TEXTO_SUAVE),
                    ],
                    spacing=1,
                ),
            ],
            spacing=10,
        ),
        content=ft.Column(
            [
                ft.Text("Datos del titular", size=11, weight=ft.FontWeight.BOLD, color=TEXTO_2),
                campo_nombre,
                campo_nit,
                ft.Divider(color=BORDE),
                ft.Text("Tarjeta", size=11, weight=ft.FontWeight.BOLD, color=TEXTO_2),
                campo_tarjeta,
                ft.Row([campo_fecha, campo_cvv], spacing=12, wrap=True),
                error_pago,
            ],
            spacing=10,
            tight=True,
        ),
        actions=[
            ft.Button("Cancelar", on_click=cerrar_pago),
            ft.Button("Procesar pago", on_click=procesar_pago),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_pago)

    def btn_pagar(_):
        if automata.estado_actual_idx == 3:
            for c in [campo_nombre, campo_nit, campo_tarjeta, campo_fecha, campo_cvv]:
                c.value = ""
            error_pago.value = ""
            dialogo_pago.open = True
            page.update()
        elif automata.estado_actual_idx == 5:
            registrar_invalida("PG", "La compra ya fue finalizada; no puede procesarse otro pago.")
            mostrar_alerta("Esta compra ya fue finalizada. Reinicia el sistema.")
        else:
            registrar_invalida("PG", "No se puede pagar antes de finalizar el registro de productos.")
            mostrar_alerta("Debes finalizar el registro antes de proceder al pago.")

    # ==================================================================
    # 10. FINALIZAR REGISTRO / REINICIO
    # ==================================================================
    def btn_finalizar_registro(_):
        if automata.estado_actual_idx == 2:
            if not sistema.productos_agregados:
                mostrar_alerta("No has agregado ningún producto.")
                return
            abrir_carrito()
        elif automata.estado_actual_idx > 2:
            registrar_invalida("FR", "El registro de productos ya fue finalizado.")
            mostrar_alerta("El registro ya fue finalizado.")
        else:
            registrar_invalida("FR", "Debes registrar al menos un producto antes de finalizar.")
            mostrar_alerta("Debes agregar productos primero.")

    def btn_reiniciar(_):
        sistema.reiniciar()
        automata.reiniciar()
        txt_total.value = "Q0.00"
        txt_carrito.value = "0"
        txt_membresia.value = "Sin validar"
        txt_formula.value = "Sistema reiniciado. El AFD volvió a q0."
        campo_membresia.value = ""
        error_membresia.value = ""
        cargar_estado_inicial_historial()
        actualizar_interfaz_afd()

    # ==================================================================
    # 11. CATÁLOGO: BUSCADOR + CARDS
    # ==================================================================
    columna_catalogo = ft.Column(spacing=30)

    campo_busqueda = ft.TextField(
        hint_text="Buscar productos...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=14,
        height=48,
        value="",
    )

    dropdown_categoria = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(key=c, text=c) for c in categorias],
        value="Todos",
        width=230,
    )

    def hover_card(e, card):
        try:
            entrando = str(e.data).lower() == "true"
            card.scale = 1.012 if entrando else 1.0
            card.bgcolor = "#FFFFFF" if entrando else SUPERFICIE
            card.shadow = sombra(20, "#CBD8E6", 1) if entrando else sombra(11, "#E1E9F2")
            card.update()
        except Exception:
            pass

    def crear_tarjeta_producto(prod):
        visual = (
            ft.Image(src=prod["imagen"], height=130, fit=ft.BoxFit.CONTAIN)
            if prod.get("imagen")
            else ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=42, color="#A9B7C7")
        )

        indicador = ft.Container(
            visible=False,
            bgcolor=VERDE_50,
            border_radius=999,
            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=12, color=VERDE_700),
                    ft.Text("Agregado", size=9, weight=ft.FontWeight.BOLD, color=VERDE_700),
                ],
                spacing=4,
                tight=True,
            ),
        )

        btn = boton("Agregar", AZUL_700, agregar_producto, ft.Icons.ADD)

        card = ft.Container(
            bgcolor=SUPERFICIE,
            border_radius=20,
            padding=16,
            shadow=sombra(11, "#E1E9F2"),
            content=ft.Column(
                [
                    ft.Stack(
                        [
                            ft.Container(
                                height=150,
                                border_radius=16,
                                bgcolor="#F7F9FC",
                                alignment=ft.Alignment(0, 0),
                                padding=12,
                                content=visual,
                            ),
                            ft.Container(top=10, right=10, content=indicador),
                        ]
                    ),
                    ft.Column(
                        [
                            ft.Text(prod["nombre"], size=14, weight=ft.FontWeight.BOLD, color=TEXTO, max_lines=2),
                            chip(prod["categoria"], AZUL_800, AZUL_50),
                        ],
                        spacing=7,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(
                        [
                            ft.Text(f"Q{prod['precio']:.2f}", size=18, weight=ft.FontWeight.BOLD, color=AZUL_950),
                            btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                        spacing=8,
                        run_spacing=8,
                    ),
                ],
                spacing=13,
            ),
        )
        animar(card, "animate_scale", 180)
        try:
            card.on_hover = lambda e, c=card: hover_card(e, c)
        except Exception:
            pass

        btn.data = {"producto": prod, "card": card, "indicador": indicador}

        return ft.Container(
            col={"xs": 12, "sm": 6, "lg": 4, "xl": 3},
            padding=6,
            content=card,
        )

    def cargar_productos(_=None):
        categoria = dropdown_categoria.value or "Todos"
        busqueda = (campo_busqueda.value or "").strip().lower()
        columna_catalogo.controls.clear()

        categorias_a_mostrar = [c for c in categorias if c != "Todos"] if categoria == "Todos" else [categoria]
        cantidad_total = 0

        for cat in categorias_a_mostrar:
            lista = [
                p for p in productos
                if p["categoria"] == cat
                and (not busqueda or busqueda in p["nombre"].lower())
            ]
            if not lista:
                continue
            cantidad_total += len(lista)
            columna_catalogo.controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(cat, size=18, weight=ft.FontWeight.BOLD, color=AZUL_950),
                                chip(str(len(lista)), AZUL_800, AZUL_50),
                            ],
                            spacing=8,
                        ),
                        ft.ResponsiveRow(
                            [crear_tarjeta_producto(p) for p in lista],
                            spacing=8,
                            run_spacing=8,
                        ),
                    ],
                    spacing=12,
                )
            )

        if cantidad_total == 0:
            columna_catalogo.controls.append(
                ft.Container(
                    height=220,
                    bgcolor=SUPERFICIE_2,
                    border_radius=18,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SEARCH, size=38, color="#A9B7C7"),
                            ft.Text("No encontramos productos", weight=ft.FontWeight.BOLD, color=TEXTO_2),
                            ft.Text("Prueba con otra búsqueda o categoría.", size=10, color=TEXTO_SUAVE),
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
            )
        page.update()

    campo_busqueda.on_change = cargar_productos
    dropdown_categoria.on_change = cargar_productos

    # ==================================================================
    # 12. CONTROLES ACADÉMICOS DEL PROCESO
    # ==================================================================
    b_membresia = boton("VM · Validar membresía", AZUL_700, btn_validar_membresia, ft.Icons.PERSON_OUTLINE)
    b_finalizar = boton("FR · Finalizar registro", AMBAR_600, btn_finalizar_registro, ft.Icons.CHECK_CIRCLE_OUTLINE)
    b_pagar = boton("PG · Pagar", VERDE_700, btn_pagar, ft.Icons.PAYMENTS_OUTLINED)

    barra_proceso = ft.Container(
        bgcolor=SUPERFICIE_2,
        border_radius=17,
        padding=14,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TUNE, size=17, color=AZUL_700),
                        ft.Text("Eventos del AFD", size=13, weight=ft.FontWeight.BOLD, color=AZUL_950),
                        chip("Demostración", AZUL_800, AZUL_50),
                    ],
                    spacing=7,
                    wrap=True,
                ),
                ft.Text(
                    "Los botones se mantienen disponibles para poder demostrar también transiciones no válidas.",
                    size=9,
                    color=TEXTO_SUAVE,
                ),
                ft.ResponsiveRow(
                    [
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=b_membresia),
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=b_finalizar),
                        ft.Container(col={"xs": 12, "sm": 6, "lg": 4}, content=b_pagar),
                    ],
                    spacing=8,
                    run_spacing=8,
                ),
            ],
            spacing=9,
        ),
    )

    # ==================================================================
    # 13. HEADER - TIENDA ONLINE
    # ==================================================================
    boton_usuario = ft.Container(
        width=46,
        height=46,
        border_radius=14,
        bgcolor=AZUL_50,
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(ft.Icons.PERSON_OUTLINE, color=AZUL_800),
    )
    boton_usuario.on_click = btn_validar_membresia

    boton_carrito = ft.Container(
        height=46,
        border_radius=14,
        bgcolor=AZUL_950,
        padding=ft.Padding(left=13, top=0, right=13, bottom=0),
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=ft.Colors.WHITE, size=19),
                ft.Container(
                    width=22,
                    height=22,
                    border_radius=999,
                    bgcolor=ROJO_600,
                    alignment=ft.Alignment(0, 0),
                    content=txt_carrito,
                ),
            ],
            spacing=7,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    boton_carrito.on_click = abrir_carrito

    boton_reset = ft.Container(
        width=46,
        height=46,
        border_radius=14,
        bgcolor=ROJO_50,
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(ft.Icons.REFRESH, color=ROJO_600),
    )
    boton_reset.on_click = btn_reiniciar

    marca = ft.Row(
        [
            ft.Container(
                width=52,
                height=52,
                border_radius=15,
                bgcolor=AZUL_800,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("PS", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ),
            ft.Column(
                [
                    ft.Text("PriceSmart", size=24, weight=ft.FontWeight.BOLD, color=AZUL_950),
                    ft.Text("Compra simulada · AFD en tiempo real", size=10, color=TEXTO_SUAVE),
                ],
                spacing=1,
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    header_busqueda = ft.Container(
        bgcolor="#FFFFFFCC",
        border_radius=16,
        padding=4,
        content=campo_busqueda,
    )

    header_acciones = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("TOTAL", size=8, weight=ft.FontWeight.BOLD, color=TEXTO_SUAVE),
                    txt_total,
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Column(
                [
                    boton_usuario,
                    txt_membresia,
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            boton_carrito,
            boton_reset,
        ],
        spacing=10,
        wrap=True,
        run_spacing=8,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    header_row = ft.ResponsiveRow(
        [
            ft.Container(col={"xs": 12, "md": 3}, content=marca),
            ft.Container(col={"xs": 12, "md": 5}, content=header_busqueda),
            ft.Container(col={"xs": 12, "md": 4}, content=header_acciones),
        ],
        spacing=12,
        run_spacing=14,
    )

    grad_header = gradiente(["#FFFFFF", "#F5F9FF", "#EEF5FF"])
    header_kwargs = dict(
        border_radius=24,
        bgcolor=SUPERFICIE,
        shadow=sombra(20, "#D7E2ED"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            [
                blob(AZUL_100, 220, right=-70, top=-120, opacity=0.55),
                blob(ROJO_100, 140, right=180, bottom=-90, opacity=0.35),
                ft.Container(padding=ft.Padding(left=22, top=18, right=22, bottom=18), content=header_row),
            ]
        ),
    )
    if grad_header is not None:
        header_kwargs["gradient"] = grad_header
    header = ft.Container(**header_kwargs)

    # ==================================================================
    # 14. PANEL CATÁLOGO
    # ==================================================================
    cabecera_catalogo = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "md": 7},
                content=ft.Column(
                    [
                        ft.Text("Productos", size=25, weight=ft.FontWeight.BOLD, color=AZUL_950),
                        ft.Text("Selecciona productos; cada clic genera el evento RP cuando corresponde.", size=11, color=TEXTO_SUAVE),
                    ],
                    spacing=3,
                ),
            ),
            ft.Container(
                col={"xs": 12, "md": 5},
                alignment=ft.Alignment(1, 0),
                content=dropdown_categoria,
            ),
        ],
        spacing=10,
        run_spacing=10,
    )

    panel_catalogo = ft.Container(
        col={"xs": 12, "md": 8},
        bgcolor="#FCFDFE",
        border_radius=24,
        shadow=sombra(18, "#DCE5EF"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            [
                blob("#EAF3FF", 270, left=-160, top=70, opacity=0.35),
                ft.Container(
                    padding=ft.Padding(left=22, top=22, right=22, bottom=28),
                    content=ft.Column(
                        [
                            cabecera_catalogo,
                            barra_proceso,
                            columna_catalogo,
                        ],
                        spacing=24,
                    ),
                ),
            ]
        ),
    )

    # ==================================================================
    # 15. PANEL AFD + HISTORIAL
    # ==================================================================
    tarjeta_estado = ft.Container(
        border_radius=16,
        padding=15,
        bgcolor=AZUL_50,
        content=ft.Row(
            [
                ft.Container(
                    width=42,
                    height=42,
                    border_radius=999,
                    bgcolor=AZUL_700,
                    alignment=ft.Alignment(0, 0),
                    content=txt_codigo_estado,
                ),
                ft.Column(
                    [
                        ft.Text("ESTADO ACTUAL", size=8, weight=ft.FontWeight.BOLD, color=TEXTO_SUAVE),
                        txt_estado_actual,
                        txt_formula,
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=12,
        ),
    )

    afd_card = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=20,
        padding=17,
        shadow=sombra(12, "#E2EAF2"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("AFD en tiempo real", size=18, weight=ft.FontWeight.BOLD, color=AZUL_950),
                                ft.Text("Diagrama del flujo implementado", size=9, color=TEXTO_SUAVE),
                            ],
                            spacing=1,
                        ),
                        chip("EN VIVO", VERDE_700, VERDE_50),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                tarjeta_estado,
                ft.Container(
                    bgcolor=SUPERFICIE_2,
                    border_radius=16,
                    padding=10,
                    content=diagrama_scroll,
                ),
                ft.Text(
                    "↻ RP representa el registro repetido de productos mientras el AFD permanece en q2.",
                    size=8,
                    color=TEXTO_SUAVE,
                ),
            ],
            spacing=13,
        ),
    )

    historial_card = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=20,
        padding=17,
        shadow=sombra(12, "#E2EAF2"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Historial de transiciones", size=19, weight=ft.FontWeight.BOLD, color=AZUL_950),
                                ft.Text("Cada evento muestra estado, símbolo y resultado.", size=9, color=TEXTO_SUAVE),
                            ],
                            spacing=1,
                        ),
                        ft.Icon(ft.Icons.HISTORY, color=AZUL_700),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1, color=BORDE),
                lista_historial,
            ],
            spacing=11,
        ),
    )

    panel_afd = ft.Container(
        col={"xs": 12, "md": 4},
        bgcolor="#F1F5FA",
        border_radius=24,
        padding=13,
        shadow=sombra(18, "#DCE5EF"),
        content=ft.Column([afd_card, historial_card], spacing=13),
    )

    # ==================================================================
    # 16. LAYOUT FINAL
    # ==================================================================
    contenido = ft.ResponsiveRow(
        [panel_catalogo, panel_afd],
        spacing=18,
        run_spacing=18,
    )

    cuerpo = ft.Container(
        padding=ft.Padding(left=18, top=18, right=18, bottom=28),
        content=ft.Column([header, contenido], spacing=18),
    )

    raiz = ft.Column(
        [cuerpo],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.add(raiz)

    cargar_productos()
    actualizar_interfaz_afd()
