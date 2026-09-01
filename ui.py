import asyncio
import os
import flet as ft


def construir_interfaz(page: ft.Page, automata, sistema):
    # 1. TOKENS VISUALES
    AZUL_950 = "#072B61"
    AZUL_900 = "#0A3D82"
    AZUL_800 = "#0D4EA5"
    AZUL_700 = "#1769C7"
    AZUL_600 = "#2680DB"
    AZUL_200 = "#BAD7FA"
    AZUL_100 = "#DDEEFF"
    AZUL_50 = "#F1F7FF"

    ROJO_700 = "#D92C34"
    ROJO_600 = "#EE3F46"
    ROJO_100 = "#FFD7DA"
    ROJO_50 = "#FFF2F3"

    VERDE_700 = "#137653"
    VERDE_600 = "#1A9366"
    VERDE_100 = "#CDEEDF"
    VERDE_50 = "#EDFBF4"

    AMBAR_700 = "#B45F06"
    AMBAR_600 = "#D97706"
    AMBAR_100 = "#FFE7B0"
    AMBAR_50 = "#FFF8E8"

    TEXTO = "#162033"
    TEXTO_2 = "#405166"
    TEXTO_SUAVE = "#718297"
    BORDE = "#E3EAF2"
    BORDE_SUAVE = "#EDF2F7"
    SUPERFICIE = "#FFFFFF"
    SUPERFICIE_2 = "#F8FAFD"
    FONDO = "#F2F6FB"

    categorias = sistema.categorias
    productos = sistema.productos
    estados_afd = automata.estados_afd

    page.title = "Simulador PriceSmart - AFD"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = FONDO

    # 2. COMPATIBILIDAD / VENTANA / ANIMACIONES
    def maximizar():
        # API reciente
        try:
            page.window.maximized = True
            return
        except Exception:
            pass

        # API anterior
        try:
            page.window_maximized = True
        except Exception:
            pass

    maximizar()

    def sombra(blur=16, color="#DEE7F0", spread=0):
        try:
            return ft.BoxShadow(
                blur_radius=blur,
                spread_radius=spread,
                color=color,
            )
        except Exception:
            return ft.BoxShadow(
                blur_radius=blur,
                color=color,
            )

    def animar(control, propiedad, duracion=160):
        try:
            setattr(
                control,
                propiedad,
                ft.Animation(duracion, ft.AnimationCurve.EASE_OUT),
            )
            return True
        except Exception:
            return False

    def poner_cursor_click(control):
        try:
            control.mouse_cursor = ft.MouseCursor.CLICK
            return
        except Exception:
            pass
        try:
            control.mouse_cursor = "click"
        except Exception:
            pass

    def gradiente(colores):
        try:
            return ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=colores,
            )
        except Exception:
            return None

    def blur_seguro(sigma=38):
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

    def blob(color, size, left=None, right=None, top=None, bottom=None, opacity=0.40):
        kwargs = {
            "width": size,
            "height": size,
            "bgcolor": color,
            "border_radius": 999,
            "opacity": opacity,
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
        }
        b = blur_seguro()
        if b is not None:
            kwargs["blur"] = b
        return ft.Container(**kwargs)

    def lanzar_tarea(funcion, *args):
        try:
            if hasattr(page, "run_task"):
                page.run_task(funcion, *args)
                return True
        except Exception:
            pass
        return False

    def abrir_dialogo(dialogo):
        try:
            page.open(dialogo)
            return
        except Exception:
            pass

        try:
            dialogo.open = True
            page.update()
        except Exception:
            pass

    def cerrar_dialogo(dialogo):
        try:
            page.close(dialogo)
            return
        except Exception:
            pass

        try:
            dialogo.open = False
            page.update()
        except Exception:
            pass

    # SnackBar robusto para distintas versiones
    def mostrar_alerta(mensaje, color_fondo=ROJO_600):
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color_fondo,
        )

        try:
            page.open(snack)
            return
        except Exception:
            pass

        try:
            page.snack_bar = snack
            snack.open = True
            page.update()
        except Exception:
            pass

    # 3. HELPERS DEL AFD
    def codigo_estado(estado_completo):
        return estado_completo.split(":", 1)[0].strip()

    def nombre_estado(estado_completo):
        partes = estado_completo.split(":", 1)
        if len(partes) == 2:
            return partes[1].strip()
        return estado_completo

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
        if "finalizar compra" in e:
            return "FC"

        return "—"

    def explicacion_evento(simbolo, valida=True):
        textos = {
            "VM": "Se valida la membresía del cliente.",
            "RP": "Se registra un producto en la compra.",
            "FR": "Se cierra el registro de productos.",
            "PG": "Se inicia el procesamiento del pago.",
            "AP": "El pago es aprobado.",
            "FC": "La compra se finaliza después de aprobar el pago.",
        }

        base = textos.get(simbolo, "Evento del sistema.")

        if valida:
            return base

        return base + " El AFD conserva el mismo estado."

    def chip(texto, fg=AZUL_800, bg=AZUL_50):
        return ft.Container(
            bgcolor=bg,
            border_radius=999,
            padding=ft.Padding(left=9, top=4, right=9, bottom=4),
            content=ft.Text(
                texto,
                size=9,
                weight=ft.FontWeight.BOLD,
                color=fg,
            ),
        )

    # 4. ESTADO VISUAL GENERAL
    txt_total = ft.Text(
        "Q0.00",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=AZUL_950,
    )

    txt_carrito = ft.Text(
        "0",
        size=10,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

    txt_membresia = ft.Text(
        "Sin validar",
        size=9,
        color=TEXTO_SUAVE,
    )

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
        color=ft.Colors.WHITE,
    )

    txt_formula = ft.Text(
        "Aún no se ha ejecutado ningún evento.",
        size=10,
        color="#C8D8EB",
    )

    # 5. HISTORIAL - RECONSTRUIDO PARA EVITAR EL PANEL VACÍO
    historial_paso = 0
    txt_cantidad_historial = ft.Text(
        "1 registro",
        size=9,
        color=TEXTO_SUAVE,
    )

    # Column scrollable: más estable que el ListView complejo anterior
    lista_historial = ft.Column(
        spacing=9,
        scroll=ft.ScrollMode.AUTO,
        height=175,
    )

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
            acento = AZUL_600
            fondo = "#F8FBFF"
            etiqueta = chip("INICIAL", AZUL_800, AZUL_100)
        elif valida:
            acento = VERDE_600
            fondo = SUPERFICIE
            etiqueta = chip("VÁLIDA", VERDE_700, VERDE_50)
        else:
            acento = ROJO_600
            fondo = "#FFFBFB"
            etiqueta = chip("NO VÁLIDA", ROJO_700, ROJO_50)

        def dato(titulo, valor, color=TEXTO):
            return ft.Column(
                [
                    ft.Text(
                        titulo.upper(),
                        size=7,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO_SUAVE,
                    ),
                    ft.Text(
                        str(valor),
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        max_lines=2,
                    ),
                ],
                spacing=2,
                tight=True,
            )

        resumen = ft.ResponsiveRow(
            [
                ft.Container(
                    col={"xs": 6, "sm": 3},
                    content=dato("Estado", estado_actual, AZUL_900),
                ),
                ft.Container(
                    col={"xs": 6, "sm": 3},
                    content=dato("Símbolo", simbolo, AZUL_900),
                ),
                ft.Container(
                    col={"xs": 6, "sm": 3},
                    content=dato(
                        "Nuevo",
                        nuevo_estado,
                        VERDE_700 if valida else ROJO_700,
                    ),
                ),
                ft.Container(
                    col={"xs": 6, "sm": 3},
                    content=dato("Paso", paso),
                ),
            ],
            spacing=6,
            run_spacing=6,
        )

        return ft.Container(
            bgcolor=fondo,
            border_radius=15,
            border=ft.Border(
                left=ft.BorderSide(4, acento)
            ),
            padding=ft.Padding(left=13, top=11, right=13, bottom=12),
            shadow=sombra(6, "#E7EDF4"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"Paso {paso}",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=AZUL_950,
                            ),
                            etiqueta,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    resumen,
                    ft.Container(
                        bgcolor=SUPERFICIE_2,
                        border_radius=10,
                        padding=9,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "TRANSICIÓN",
                                    size=7,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXTO_SUAVE,
                                ),
                                ft.Text(
                                    transicion,
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXTO_2,
                                ),
                            ],
                            spacing=2,
                            tight=True,
                        ),
                    ),
                    ft.Text(
                        explicacion,
                        size=9,
                        color=TEXTO_SUAVE,
                        max_lines=3,
                    ),
                ],
                spacing=8,
                tight=True,
            ),
        )

    def refrescar_contador_historial():
        cantidad = len(lista_historial.controls)
        txt_cantidad_historial.value = (
            f"{cantidad} registro"
            if cantidad == 1
            else f"{cantidad} registros"
        )

    def cargar_estado_inicial_historial():
        nonlocal historial_paso

        historial_paso = 0
        lista_historial.controls.clear()

        lista_historial.controls.append(
            crear_item_historial(
                paso=0,
                estado_actual="q0",
                simbolo="—",
                transicion="—",
                nuevo_estado="q0",
                explicacion="Estado inicial del autómata.",
                inicial=True,
            )
        )

        refrescar_contador_historial()

    def registrar_historial(evento, estado_anterior, estado_nuevo):
        nonlocal historial_paso

        historial_paso += 1

        q1 = codigo_estado(estado_anterior)
        q2 = codigo_estado(estado_nuevo)
        s = simbolo_de_evento(evento)

        lista_historial.controls.append(
            crear_item_historial(
                paso=historial_paso,
                estado_actual=q1,
                simbolo=s,
                transicion=f"δ({q1}, {s}) = {q2}",
                nuevo_estado=q2,
                explicacion=explicacion_evento(s, True),
                valida=True,
            )
        )

        refrescar_contador_historial()

        # Si ya está montada, actualizarla directamente.
        try:
            lista_historial.update()
            txt_cantidad_historial.update()
        except Exception:
            pass

    def registrar_invalida(simbolo, explicacion):
        nonlocal historial_paso

        historial_paso += 1
        q = codigo_estado(estados_afd[automata.estado_actual_idx])

        lista_historial.controls.append(
            crear_item_historial(
                paso=historial_paso,
                estado_actual=q,
                simbolo=simbolo,
                transicion="No válida",
                nuevo_estado=q,
                explicacion=explicacion,
                valida=False,
            )
        )

        txt_formula.value = f"{q} + {simbolo} → {q} · transición no válida"
        refrescar_contador_historial()

        try:
            lista_historial.update()
            txt_cantidad_historial.update()
        except Exception:
            pass

        page.update()

    cargar_estado_inicial_historial()

    # 6. AFD VISUAL COMPACTO - TODO VISIBLE SIN SCROLL HORIZONTAL
    nodo_refs = []
    conector_refs = {}

    def crear_nodo(idx):
        estado = estados_afd[idx]
        q = codigo_estado(estado)
        nombre = nombre_estado(estado)
        es_final = idx == len(estados_afd) - 1

        texto_q = ft.Text(
            q,
            size=12,
            weight=ft.FontWeight.BOLD,
            color=AZUL_950,
        )

        circulo_interno = ft.Container(
            width=40,
            height=40,
            border_radius=999,
            bgcolor=SUPERFICIE,
            alignment=ft.Alignment(0, 0),
            content=texto_q,
        )

        circulo_externo = ft.Container(
            width=49,
            height=49,
            border_radius=999,
            bgcolor=AZUL_200 if es_final else "#D9E2EC",
            padding=4 if es_final else 5,
            alignment=ft.Alignment(0, 0),
            content=circulo_interno,
        )

        animar(circulo_externo, "animate_scale", 150)

        nombre_txt = ft.Text(
            nombre,
            size=7,
            color=TEXTO_SUAVE,
            text_align=ft.TextAlign.CENTER,
            max_lines=2,
        )

        controles = []

        if idx == 2:
            controles.append(
                chip("↻ RP", AMBAR_700, AMBAR_50)
            )

        controles.extend(
            [
                circulo_externo,
                nombre_txt,
            ]
        )

        caja = ft.Container(
            width=64,
            content=ft.Column(
                controles,
                spacing=4,
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

        return caja

    def crear_conector(simbolo, direccion="right"):
        evento = chip(simbolo, AZUL_800, AZUL_50)

        flecha_icono = (
            ft.Icons.ARROW_FORWARD
            if direccion == "right"
            else ft.Icons.ARROW_BACK
        )

        linea = ft.Container(
            width=12,
            height=2,
            bgcolor="#A0AFBF",
        )

        flecha = ft.Icon(
            flecha_icono,
            size=16,
            color="#91A2B4",
        )

        trayectoria = ft.Row(
            [linea, flecha],
            spacing=0,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        caja = ft.Container(
            width=34,
            content=ft.Column(
                [
                    evento,
                    trayectoria,
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        conector_refs[simbolo] = {
            "chip": evento,
            "line": linea,
            "arrow": flecha,
        }

        return caja

    def crear_conector_vertical(simbolo):
        evento = chip(simbolo, AZUL_800, AZUL_50)

        linea = ft.Container(
            width=2,
            height=10,
            bgcolor="#A0AFBF",
        )

        flecha = ft.Icon(
            ft.Icons.ARROW_DOWNWARD,
            size=16,
            color="#91A2B4",
        )

        caja = ft.Container(
            width=44,
            content=ft.Column(
                [
                    evento,
                    linea,
                    flecha,
                ],
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        conector_refs[simbolo] = {
            "chip": evento,
            "line": linea,
            "arrow": flecha,
        }

        return caja

    n0, n1, n2, n3, n4, n5, n6 = [
        crear_nodo(i) for i in range(7)
    ]

    c_vm = crear_conector("VM", "right")
    c_rp = crear_conector("RP", "right")
    c_fr = crear_conector_vertical("FR")
    c_pg = crear_conector("PG", "left")
    c_ap = crear_conector("AP", "left")
    c_fc = crear_conector_vertical("FC")

    # Diagrama serpenteante compacto:
    #
    # q0 --VM--> q1 --RP--> q2
    #                    |
    #                    FR
    #                    v
    # q5 <--AP-- q4 <--PG-- q3
    # |
    # FC
    # v
    # q6
    #
    fila_superior = ft.Row(
        [
            n0,
            c_vm,
            n1,
            c_rp,
            n2,
        ],
        spacing=1,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    bajada_fr = ft.Row(
        [
            ft.Container(expand=True),
            c_fr,
            ft.Container(width=12),
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.END,
    )

    fila_media = ft.Row(
        [
            n5,
            c_ap,
            n4,
            c_pg,
            n3,
        ],
        spacing=1,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    bajada_fc = ft.Row(
        [
            ft.Container(width=12),
            c_fc,
            ft.Container(expand=True),
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.START,
    )

    fila_final = ft.Row(
        [
            n6,
            ft.Container(expand=True),
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.START,
    )

    diagrama_contenido = ft.Column(
        [
            fila_superior,
            bajada_fr,
            fila_media,
            bajada_fc,
            fila_final,
        ],
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    async def pulso_nodo(idx):
        try:
            ref = nodo_refs[idx]["outer"]
            ref.scale = 1.10
            ref.update()
            await asyncio.sleep(0.13)
            ref.scale = 1.0
            ref.update()
        except Exception:
            pass

    def actualizar_interfaz_afd(ultimo_evento=None, transicion=None):
        estado = estados_afd[automata.estado_actual_idx]

        txt_codigo_estado.value = codigo_estado(estado)
        txt_estado_actual.value = nombre_estado(estado)

        if transicion is not None:
            q1, s, q2 = transicion
            txt_formula.value = f"δ({q1}, {s}) = {q2}"

        for i, ref in enumerate(nodo_refs):
            activo = i == automata.estado_actual_idx
            es_final = i == len(estados_afd) - 1

            if activo:
                ref["outer"].bgcolor = AZUL_200
                ref["outer"].shadow = sombra(
                    20,
                    "#99C8FA",
                    1,
                )
                ref["inner"].bgcolor = AZUL_700
                ref["q"].color = ft.Colors.WHITE
                ref["name"].color = AZUL_900
                ref["name"].weight = ft.FontWeight.BOLD
            else:
                ref["outer"].bgcolor = (
                    AZUL_200 if es_final else "#D9E2EC"
                )
                ref["outer"].shadow = None
                ref["inner"].bgcolor = SUPERFICIE
                ref["q"].color = AZUL_950
                ref["name"].color = TEXTO_SUAVE
                ref["name"].weight = ft.FontWeight.NORMAL

        # Normalizar conectores
        for _, ref in conector_refs.items():
            try:
                ref["arrow"].color = "#91A2B4"
                ref["line"].bgcolor = "#A0AFBF"
                ref["chip"].bgcolor = AZUL_50
                ref["chip"].content.color = AZUL_800
            except Exception:
                pass

        # Resaltar el evento ejecutado
        if ultimo_evento:
            s = simbolo_de_evento(ultimo_evento)

            if s in conector_refs:
                try:
                    ref = conector_refs[s]
                    ref["arrow"].color = VERDE_600
                    ref["line"].bgcolor = VERDE_600
                    ref["chip"].bgcolor = VERDE_50
                    ref["chip"].content.color = VERDE_700
                except Exception:
                    pass

        lanzar_tarea(
            pulso_nodo,
            automata.estado_actual_idx,
        )

        page.update()

    def ejecutar_evento_ui(simbolo, descripcion=None, mostrar_error=True):
        resultado = automata.ejecutar_evento(
            simbolo,
            descripcion,
        )

        if resultado["valida"]:
            registrar_historial(
                resultado["evento"],
                resultado["estado_anterior"],
                resultado["estado_nuevo"],
            )

            q1 = codigo_estado(resultado["estado_anterior"])
            q2 = codigo_estado(resultado["estado_nuevo"])
            s = resultado["simbolo"]

            actualizar_interfaz_afd(
                resultado["evento"],
                (q1, s, q2),
            )
        else:
            registrar_invalida(
                resultado["simbolo"],
                resultado["mensaje"],
            )

            if mostrar_error:
                mostrar_alerta(
                    resultado["mensaje"]
                )

        return resultado

    # 7. MEMBRESÍA
    campo_membresia = ft.TextField(
        label="Código de membresía",
        hint_text="PSABC123",
        width=320,
        max_length=8,
        text_align=ft.TextAlign.CENTER,
        capitalization=ft.TextCapitalization.CHARACTERS,
        autofocus=True,
    )

    error_membresia = ft.Text(
        "",
        color=ROJO_600,
        size=11,
    )

    def cerrar_membresia(_=None):
        cerrar_dialogo(dialogo_membresia)

    def confirmar_membresia(_):
        codigo = (
            campo_membresia.value or ""
        ).strip().upper()

        if not sistema.validar_membresia(codigo):
            error_membresia.value = (
                "Formato inválido. Usa PS + 3 letras + 3 números."
            )
            campo_membresia.value = ""
            page.update()
            return

        cerrar_membresia()

        resultado = ejecutar_evento_ui(
            "VM",
            f"Validar Membresía ({codigo})",
        )

        if resultado["valida"]:
            txt_membresia.value = "Validada"

    dialogo_membresia = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Validar membresía",
            weight=ft.FontWeight.BOLD,
            color=AZUL_950,
        ),
        content=ft.Column(
            [
                ft.Container(
                    bgcolor=AZUL_50,
                    border_radius=13,
                    padding=12,
                    content=ft.Text(
                        "Formato de prueba: PS + 3 letras + 3 números.",
                        size=10,
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
            ft.Button(
                "Cancelar",
                on_click=cerrar_membresia,
            ),
            ft.Button(
                "Validar",
                on_click=confirmar_membresia,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo_membresia)

    def btn_validar_membresia(_):
        if automata.estado_actual_idx != 0:
            ejecutar_evento_ui(
                "VM",
                "Validar Membresía",
            )
            return

        campo_membresia.value = ""
        error_membresia.value = ""
        abrir_dialogo(dialogo_membresia)

    # 8. CARRITO
    carrito_titulo = ft.Row(spacing=8)
    carrito_cuerpo = ft.Column(spacing=10, tight=True)
    carrito_acciones = ft.Row(
        spacing=10,
        alignment=ft.MainAxisAlignment.END,
        wrap=True,
    )

    carrito_panel = ft.Container(
        width=590,
        bgcolor="#F7F9FC",
        border_radius=28,
        padding=22,
        shadow=sombra(32, "#68788A", 2),
        content=ft.Column(
            [
                carrito_titulo,
                carrito_cuerpo,
                carrito_acciones,
            ],
            spacing=18,
            tight=True,
        ),
    )

    carrito_overlay = ft.Container(
        visible=False,
        expand=True,
        bgcolor="#99000000",
        alignment=ft.Alignment(0, 0),
        padding=18,
        content=carrito_panel,
    )
    page.overlay.append(carrito_overlay)

    def cerrar_carrito(_=None):
        carrito_overlay.visible = False
        page.update()

    def nueva_compra_desde_carrito(_=None):
        # Solo reinicia si el usuario lo pide explícitamente.
        cerrar_carrito()
        btn_reiniciar(None)

    def confirmar_finalizar_registro(_):
        resultado = ejecutar_evento_ui(
            "FR",
            "Finalizar Registro (f)",
        )

        # El resumen permanece abierto, pero cambia de estado y acciones.
        # Ya no se ofrece "Seguir comprando" después de cerrar la selección.
        if resultado["valida"]:
            abrir_carrito()

    def abrir_carrito(_=None):
        items = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=225,
        )

        if not sistema.productos_agregados:
            items.controls.append(
                ft.Container(
                    height=130,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.SHOPPING_CART_OUTLINED,
                                size=34,
                                color="#A8B6C6",
                            ),
                            ft.Text(
                                "Tu carrito está vacío",
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO_2,
                            ),
                            ft.Text(
                                (
                                    "La compra ya fue finalizada."
                                    if automata.estado_actual_idx == 6
                                    else "Agrega productos para continuar."
                                ),
                                size=10,
                                color=TEXTO_SUAVE,
                            ),
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        else:
            for p in sistema.productos_agregados:
                imagen = (
                    ft.Image(
                        src=p["imagen"],
                        fit=ft.BoxFit.CONTAIN,
                    )
                    if p.get("imagen")
                    else ft.Icon(
                        ft.Icons.IMAGE_NOT_SUPPORTED,
                        color="#A8B6C6",
                    )
                )

                items.controls.append(
                    ft.Container(
                        bgcolor=SUPERFICIE_2,
                        border_radius=12,
                        padding=10,
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=44,
                                    height=44,
                                    bgcolor=SUPERFICIE,
                                    border_radius=10,
                                    padding=5,
                                    alignment=ft.Alignment(0, 0),
                                    content=imagen,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            p["nombre"],
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXTO,
                                            max_lines=1,
                                        ),
                                        ft.Text(
                                            p["categoria"],
                                            size=9,
                                            color=TEXTO_SUAVE,
                                        ),
                                    ],
                                    spacing=1,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"Q{p['precio']:.2f}",
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_900,
                                ),
                            ],
                            spacing=10,
                        ),
                    )
                )

        # Acciones del carrito según el estado real del proceso.
        if automata.estado_actual_idx in [0, 1, 2]:
            acciones = [
                ft.Button(
                    "Seguir comprando",
                    on_click=cerrar_carrito,
                )
            ]

        elif automata.estado_actual_idx == 6:
            acciones = [
                ft.Button(
                    "Cerrar",
                    on_click=cerrar_carrito,
                ),
                ft.Button(
                    "Nueva compra",
                    icon=ft.Icons.REFRESH,
                    on_click=nueva_compra_desde_carrito,
                ),
            ]

        else:
            acciones = [
                ft.Button(
                    "Cerrar resumen",
                    on_click=cerrar_carrito,
                )
            ]

        if (
            sistema.productos_agregados
            and automata.estado_actual_idx == 2
        ):
            acciones.append(
                ft.Button(
                    "Finalizar selección",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    on_click=confirmar_finalizar_registro,
                )
            )

        elif automata.estado_actual_idx == 3:
            acciones.append(
                ft.Button(
                    "Proceder al pago",
                    icon=ft.Icons.PAYMENTS_OUTLINED,
                    on_click=btn_pagar,
                )
            )

        elif automata.estado_actual_idx == 5:
            acciones.append(
                ft.Button(
                    "Finalizar compra",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    on_click=finalizar_compra,
                )
            )

        carrito_titulo.controls = [
            ft.Icon(
                ft.Icons.SHOPPING_CART_OUTLINED,
                color=AZUL_700,
            ),
            ft.Text(
                (
                    "Compra finalizada"
                    if automata.estado_actual_idx == 6
                    else "Tu carrito"
                ),
                size=22,
                weight=ft.FontWeight.BOLD,
                color=AZUL_950,
            ),
            chip(
                str(len(sistema.productos_agregados)),
                AZUL_800,
                AZUL_50,
            ),
        ]

        estado_carrito = {
            0: "Valida tu membresía para comenzar.",
            1: "Agrega al menos un producto.",
            2: "Puedes seguir comprando o finalizar la selección.",
            3: "Selección cerrada. Ya no se pueden agregar productos; procede al pago.",
            4: "El pago se está procesando.",
            5: "Pago aprobado. Falta finalizar la compra.",
            6: "Compra finalizada.",
        }.get(automata.estado_actual_idx, "")

        carrito_cuerpo.controls = [
            ft.Container(
                bgcolor=AZUL_50,
                border_radius=11,
                padding=10,
                content=ft.Text(
                    estado_carrito,
                    size=9,
                    color=AZUL_900,
                ),
            ),
            items,
            ft.Divider(color=BORDE),
            ft.Row(
                [
                    ft.Text(
                        "TOTAL",
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO_SUAVE,
                    ),
                    ft.Text(
                        f"Q{sistema.total_compra:.2f}",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=AZUL_950,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

        carrito_acciones.controls = acciones

        carrito_overlay.visible = True
        page.update()

    # 9. PRODUCTOS / FEEDBACK DE CLIC REAL
    async def restaurar_feedback(
        card,
        boton_agregar,
        indicador,
        texto_indicador,
        icono_indicador,
        valido,
    ):
        try:
            await asyncio.sleep(0.75)

            indicador.visible = False
            card.border = None
            card.shadow = sombra(11, "#E1E9F2")

            boton_agregar.scale = 1.0
            boton_agregar.bgcolor = AZUL_700

            texto_indicador.value = "Agregado"
            texto_indicador.color = VERDE_700
            icono_indicador.name = ft.Icons.CHECK_CIRCLE
            icono_indicador.color = VERDE_700

            card.update()
            boton_agregar.update()
            indicador.update()
        except Exception:
            pass

    def feedback_producto(
        info,
        valido,
        mensaje_invalido="Valida membresía",
    ):
        card = info["card"]
        boton_agregar = info["boton"]
        indicador = info["indicador"]
        texto_indicador = info["texto_indicador"]
        icono_indicador = info["icono_indicador"]

        # Feedback inmediato: no depende de que run_task exista.
        indicador.visible = True
        boton_agregar.scale = 0.96

        if valido:
            texto_indicador.value = "Agregado"
            texto_indicador.color = VERDE_700
            icono_indicador.name = ft.Icons.CHECK_CIRCLE
            icono_indicador.color = VERDE_700
            indicador.bgcolor = VERDE_50

            card.border = ft.Border.all(
                1,
                VERDE_100,
            )
            card.shadow = sombra(
                20,
                "#C0E9D8",
                1,
            )
            boton_agregar.bgcolor = VERDE_600
        else:
            texto_indicador.value = mensaje_invalido
            texto_indicador.color = ROJO_700
            icono_indicador.name = ft.Icons.INFO_OUTLINE
            icono_indicador.color = ROJO_700
            indicador.bgcolor = ROJO_50

            card.border = ft.Border.all(
                1,
                ROJO_100,
            )
            card.shadow = sombra(
                20,
                "#F3C4C8",
                1,
            )
            boton_agregar.bgcolor = ROJO_600

        page.update()

        lanzar_tarea(
            restaurar_feedback,
            card,
            boton_agregar,
            indicador,
            texto_indicador,
            icono_indicador,
            valido,
        )

    def agregar_producto(e):
        info = e.control.data
        producto = info["producto"]

        resultado = ejecutar_evento_ui(
            "RP",
            "Registrar Producto (r)",
        )

        if not resultado["valida"]:
            mensajes_por_estado = {
                0: "Valida membresía",
                3: "Selección finalizada",
                4: "Pago en proceso",
                5: "Pago aprobado",
                6: "Compra finalizada",
            }

            feedback_producto(
                info,
                valido=False,
                mensaje_invalido=mensajes_por_estado.get(
                    automata.estado_actual_idx,
                    "Acción no disponible",
                ),
            )
            return

        feedback_producto(
            info,
            valido=True,
        )

        sistema.agregar_producto(producto)

        txt_total.value = (
            f"Q{sistema.total_compra:.2f}"
        )
        txt_carrito.value = str(
            len(sistema.productos_agregados)
        )

        page.update()

    def hover_card(e, card):
        try:
            entrando = str(e.data).lower() == "true"

            card.scale = (
                1.010 if entrando else 1.0
            )

            card.shadow = (
                sombra(20, "#CBD8E6", 1)
                if entrando
                else sombra(11, "#E1E9F2")
            )

            card.update()
        except Exception:
            pass

    def hover_boton_agregar(e, btn):
        try:
            entrando = str(e.data).lower() == "true"

            btn.scale = (
                1.035 if entrando else 1.0
            )

            # Solo azul de hover si no está mostrando feedback rojo/verde.
            if entrando and btn.bgcolor == AZUL_700:
                btn.bgcolor = AZUL_800
            elif not entrando and btn.bgcolor == AZUL_800:
                btn.bgcolor = AZUL_700

            btn.update()
        except Exception:
            pass

    # 10. PAGO
    campo_nombre = ft.TextField(
        label="Nombre completo",
        width=330,
        autofocus=True,
    )

    campo_nit = ft.TextField(
        label="NIT / DPI",
        width=330,
    )

    campo_tarjeta = ft.TextField(
        label="Número de tarjeta",
        hint_text="16 dígitos",
        width=330,
        max_length=16,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    campo_fecha = ft.TextField(
        label="Vencimiento",
        hint_text="MM/YY",
        width=155,
        max_length=5,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def formatear_fecha(e):
        # El usuario escribe solo 4 dígitos: 1227 -> 12/27.
        valor = (e.control.value or "")
        digitos = "".join(c for c in valor if c.isdigit())[:4]

        if len(digitos) <= 2:
            formateado = digitos
        else:
            formateado = digitos[:2] + "/" + digitos[2:]

        if e.control.value != formateado:
            e.control.value = formateado
            try:
                e.control.update()
            except Exception:
                page.update()

    campo_fecha.on_change = formatear_fecha

    campo_cvv = ft.TextField(
        label="CVV",
        width=155,
        max_length=4,
        password=True,
        can_reveal_password=True,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    error_pago = ft.Text(
        "",
        color=ROJO_600,
        size=11,
    )

    dialogo_exito = ft.AlertDialog(
        modal=True,
        content=ft.Text(""),
    )
    page.overlay.append(dialogo_exito)

    dialogo_aprobado = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Pago aprobado",
            weight=ft.FontWeight.BOLD,
            color=AZUL_950,
        ),
        content=ft.Column(
            [
                ft.Container(
                    width=68,
                    height=68,
                    border_radius=999,
                    bgcolor=VERDE_50,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.CHECK_CIRCLE,
                        size=40,
                        color=VERDE_600,
                    ),
                ),
                ft.Text(
                    "El pago fue aprobado.",
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_950,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "El AFD está en q5. Finaliza la compra para llegar al estado de aceptación q6.",
                    size=10,
                    color=TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=11,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dialogo_aprobado)

    def cerrar_exito(_=None):
        cerrar_dialogo(dialogo_exito)
        # El estado q6 permanece visible; para una nueva compra se usa Reiniciar.

    def mostrar_exito(total_final):
        dialogo_exito.title = ft.Text(
            "Compra completada",
            weight=ft.FontWeight.BOLD,
            color=AZUL_950,
        )

        dialogo_exito.content = ft.Container(
            width=380,
            padding=8,
            content=ft.Column(
                [
                    ft.Container(
                        width=70,
                        height=70,
                        border_radius=999,
                        bgcolor=VERDE_50,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=42,
                            color=VERDE_600,
                        ),
                    ),
                    ft.Text(
                        "¡Compra completada!",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=AZUL_950,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Compra finalizada. El carrito se limpió, pero el AFD permanece en q6 hasta reiniciar.",
                        size=10,
                        color=TEXTO_SUAVE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        bgcolor=SUPERFICIE_2,
                        border_radius=14,
                        padding=14,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            "TOTAL",
                                            size=8,
                                            color=TEXTO_SUAVE,
                                        ),
                                        ft.Text(
                                            f"Q{total_final:.2f}",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=AZUL_950,
                                        ),
                                    ],
                                    spacing=1,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "ESTADO",
                                            size=8,
                                            color=TEXTO_SUAVE,
                                        ),
                                        ft.Text(
                                            "q6 · Compra finalizada",
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=VERDE_700,
                                        ),
                                    ],
                                    spacing=1,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        dialogo_exito.actions = [
            ft.Button(
                "Cerrar",
                on_click=cerrar_exito,
            )
        ]

        dialogo_exito.actions_alignment = (
            ft.MainAxisAlignment.CENTER
        )

        abrir_dialogo(dialogo_exito)

    def finalizar_compra(_=None):
        # Evita ejecutar FC dos veces si el usuario hace doble clic.
        if automata.estado_actual_idx == 6:
            cerrar_dialogo(dialogo_aprobado)
            cerrar_carrito()
            return

        if automata.estado_actual_idx != 5:
            return

        total_final = sistema.total_compra

        cerrar_dialogo(dialogo_aprobado)
        cerrar_carrito()

        resultado = ejecutar_evento_ui(
            "FC",
            "Finalizar Compra (c)",
        )

        if resultado["valida"]:
            # Reinicia únicamente los datos de compra. El autómata NO se
            # reinicia: q6 debe permanecer visible como estado de aceptación.
            sistema.reiniciar()
            txt_total.value = "Q0.00"
            txt_carrito.value = "0"

            page.update()
            mostrar_exito(total_final)

    def mostrar_pago_aprobado():
        dialogo_aprobado.actions = [
            ft.Button(
                "Finalizar compra",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                on_click=finalizar_compra,
            )
        ]
        abrir_dialogo(dialogo_aprobado)

    async def aprobar_pago_despues():
        # q4 permanece visible brevemente antes de la aprobación simulada.
        await asyncio.sleep(0.35)

        resultado = ejecutar_evento_ui(
            "AP",
            "Aprobar Pago (a)",
        )

        if resultado["valida"]:
            mostrar_pago_aprobado()

    def cerrar_pago(_=None):
        cerrar_dialogo(dialogo_pago)

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

        resultado = ejecutar_evento_ui(
            "PG",
            "Realizar Pago (p)",
        )

        if not resultado["valida"]:
            return

        # La aprobación se simula como un segundo evento del AFD.
        if not lanzar_tarea(aprobar_pago_despues):
            resultado_ap = ejecutar_evento_ui(
                "AP",
                "Aprobar Pago (a)",
            )

            if resultado_ap["valida"]:
                mostrar_pago_aprobado()

    dialogo_pago = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Facturación y pago",
            weight=ft.FontWeight.BOLD,
            color=AZUL_950,
        ),
        content=ft.Column(
            [
                ft.Text(
                    "Datos del titular",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO_2,
                ),
                campo_nombre,
                campo_nit,
                ft.Divider(color=BORDE),
                ft.Text(
                    "Tarjeta",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO_2,
                ),
                campo_tarjeta,
                ft.Row(
                    [
                        campo_fecha,
                        campo_cvv,
                    ],
                    spacing=12,
                    wrap=True,
                ),
                error_pago,
            ],
            spacing=10,
            tight=True,
        ),
        actions=[
            ft.Button(
                "Cancelar",
                on_click=cerrar_pago,
            ),
            ft.Button(
                "Procesar pago",
                on_click=procesar_pago,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo_pago)

    def btn_pagar(_):
        if automata.estado_actual_idx == 3:
            cerrar_carrito()

            for campo in [
                campo_nombre,
                campo_nit,
                campo_tarjeta,
                campo_fecha,
                campo_cvv,
            ]:
                campo.value = ""

            error_pago.value = ""
            abrir_dialogo(dialogo_pago)
            return

        # Si el pago ya fue aprobado pero aún falta FC, recuperar la pantalla.
        if automata.estado_actual_idx == 5:
            mostrar_pago_aprobado()
            return

        if automata.estado_actual_idx == 6:
            mostrar_alerta(
                "Esta compra ya fue finalizada. Reinicia el sistema."
            )
            return

        ejecutar_evento_ui(
            "PG",
            "Realizar Pago (p)",
        )

    # 11. FINALIZAR / REINICIAR
    def btn_finalizar_registro(_):
        if automata.estado_actual_idx == 2:
            abrir_carrito()
            return

        ejecutar_evento_ui(
            "FR",
            "Finalizar Registro (f)",
        )

    def btn_reiniciar(_):
        sistema.reiniciar()
        automata.reiniciar()

        txt_total.value = "Q0.00"
        txt_carrito.value = "0"
        txt_membresia.value = "Sin validar"
        txt_formula.value = (
            "Sistema reiniciado. El AFD volvió a q0."
        )

        campo_membresia.value = ""
        error_membresia.value = ""

        cargar_estado_inicial_historial()
        actualizar_interfaz_afd()

    # 13. CATÁLOGO
    columna_catalogo = ft.Column(
        spacing=28,
        scroll=ft.ScrollMode.AUTO,
        height=525,
    )

    campo_busqueda = ft.TextField(
        hint_text="Buscar productos...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=14,
        height=48,
        value="",
        bgcolor=SUPERFICIE,
        border_color=BORDE,
        focused_border_color=AZUL_600,
        cursor_color=AZUL_700,
    )

    dropdown_categoria = ft.Dropdown(
        label="Categoría",
        options=[
            ft.dropdown.Option(
                key=c,
                text=c,
            )
            for c in categorias
        ],
        value="Todos",
        width=230,
    )

    def crear_tarjeta_producto(prod):
        visual = (
            ft.Image(
                src=prod["imagen"],
                height=120,
                fit=ft.BoxFit.CONTAIN,
            )
            if prod.get("imagen")
            else ft.Icon(
                ft.Icons.IMAGE_NOT_SUPPORTED,
                size=42,
                color="#A9B7C7",
            )
        )

        icono_indicador = ft.Icon(
            ft.Icons.CHECK_CIRCLE,
            size=12,
            color=VERDE_700,
        )

        texto_indicador = ft.Text(
            "Agregado",
            size=8,
            weight=ft.FontWeight.BOLD,
            color=VERDE_700,
        )

        indicador = ft.Container(
            visible=False,
            bgcolor=VERDE_50,
            border_radius=999,
            padding=ft.Padding(
                left=7,
                top=4,
                right=7,
                bottom=4,
            ),
            content=ft.Row(
                [
                    icono_indicador,
                    texto_indicador,
                ],
                spacing=4,
                tight=True,
            ),
        )

        texto_btn = ft.Text(
            "Agregar",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )

        icono_btn = ft.Icon(
            ft.Icons.ADD,
            size=17,
            color=ft.Colors.WHITE,
        )

        boton_agregar = ft.Container(
            bgcolor=AZUL_700,
            border_radius=12,
            padding=ft.Padding(
                left=12,
                top=9,
                right=12,
                bottom=9,
            ),
            content=ft.Row(
                [
                    icono_btn,
                    texto_btn,
                ],
                spacing=5,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # Ripple si la versión lo soporta
        try:
            boton_agregar.ink = True
        except Exception:
            pass

        poner_cursor_click(boton_agregar)
        animar(
            boton_agregar,
            "animate_scale",
            120,
        )
        animar(
            boton_agregar,
            "animate",
            140,
        )

        card = ft.Container(
            bgcolor=SUPERFICIE,
            border_radius=20,
            padding=15,
            shadow=sombra(11, "#E1E9F2"),
            content=ft.Column(
                [
                    ft.Stack(
                        [
                            ft.Container(
                                height=145,
                                border_radius=16,
                                bgcolor="#F7F9FC",
                                alignment=ft.Alignment(0, 0),
                                padding=12,
                                content=visual,
                            ),
                            ft.Container(
                                top=9,
                                right=9,
                                content=indicador,
                            ),
                        ]
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                prod["nombre"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                max_lines=2,
                            ),
                            chip(
                                prod["categoria"],
                                AZUL_800,
                                AZUL_50,
                            ),
                        ],
                        spacing=7,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"Q{prod['precio']:.2f}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AZUL_950,
                            ),
                            boton_agregar,
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

        animar(
            card,
            "animate_scale",
            170,
        )

        try:
            card.on_hover = (
                lambda e, c=card:
                hover_card(e, c)
            )
        except Exception:
            pass

        try:
            boton_agregar.on_hover = (
                lambda e, b=boton_agregar:
                hover_boton_agregar(e, b)
            )
        except Exception:
            pass

        boton_agregar.data = {
            "producto": prod,
            "card": card,
            "boton": boton_agregar,
            "indicador": indicador,
            "texto_indicador": texto_indicador,
            "icono_indicador": icono_indicador,
        }

        boton_agregar.on_click = agregar_producto

        # Más aire: 3 por fila en desktop normal.
        return ft.Container(
            col={
                "xs": 12,
                "sm": 6,
                "lg": 4,
                "xl": 3,
            },
            padding=7,
            content=card,
        )

    def cargar_productos(e=None):
        # Algunas versiones de Flet disparan Dropdown mediante on_select y
        # otras mediante on_change. Siempre tomamos el valor real del control.
        valor_evento = None
        try:
            valor_evento = e.control.value
        except Exception:
            pass

        categoria = str(
            valor_evento
            or dropdown_categoria.value
            or "Todos"
        ).strip()

        busqueda = (
            campo_busqueda.value
            or ""
        ).strip().casefold()

        if categoria not in categorias:
            categoria = "Todos"

        categorias_a_mostrar = (
            [c for c in categorias if c != "Todos"]
            if categoria == "Todos"
            else [categoria]
        )

        nuevos_controles = []
        cantidad_total = 0

        for cat in categorias_a_mostrar:
            cat_norm = cat.strip().casefold()

            lista = [
                p
                for p in productos
                if str(p.get("categoria", "")).strip().casefold() == cat_norm
                and (
                    not busqueda
                    or busqueda in str(p.get("nombre", "")).casefold()
                )
            ]

            if not lista:
                continue

            cantidad_total += len(lista)

            nuevos_controles.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    cat,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_950,
                                ),
                                chip(
                                    str(len(lista)),
                                    AZUL_800,
                                    AZUL_50,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.ResponsiveRow(
                            [
                                crear_tarjeta_producto(p)
                                for p in lista
                            ],
                            spacing=8,
                            run_spacing=8,
                        ),
                    ],
                    spacing=12,
                )
            )

        if cantidad_total == 0:
            nuevos_controles.append(
                ft.Container(
                    height=210,
                    bgcolor=SUPERFICIE_2,
                    border_radius=18,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.SEARCH,
                                size=38,
                                color="#A9B7C7",
                            ),
                            ft.Text(
                                "No encontramos productos",
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO_2,
                            ),
                            ft.Text(
                                "Prueba con otra búsqueda o categoría.",
                                size=10,
                                color=TEXTO_SUAVE,
                            ),
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        # Reemplazar el contenido completo es más consistente que clear/append
        # en la versión de Flet usada por el proyecto.
        columna_catalogo.controls = nuevos_controles

        try:
            columna_catalogo.scroll_to(offset=0, duration=150)
        except Exception:
            pass

        page.update()

    # Compatibilidad con distintas versiones de Dropdown/TextField.
    campo_busqueda.on_change = cargar_productos
    dropdown_categoria.on_change = cargar_productos
    try:
        dropdown_categoria.on_select = cargar_productos
    except Exception:
        pass

    # 14. HEADER
    def hover_icono(e, control, color_hover=None, color_normal=None):
        try:
            entrando = str(e.data).lower() == "true"

            control.scale = (
                1.045 if entrando else 1.0
            )

            if color_hover and color_normal:
                control.bgcolor = (
                    color_hover
                    if entrando
                    else color_normal
                )

            control.update()
        except Exception:
            pass

    # Logo: si luego colocas assets/pricesmart_logo.png, se usa solo.
    ruta_logo = os.path.join(
        "assets",
        "pricesmart_logo.png",
    )

    if os.path.exists(ruta_logo):
        logo_control = ft.Image(
            src=ruta_logo,
            width=145,
            height=46,
            fit=ft.BoxFit.CONTAIN,
        )

        marca = ft.Row(
            [logo_control],
            spacing=0,
        )
    else:
        marca = ft.Row(
            [
                ft.Container(
                    width=50,
                    height=50,
                    border_radius=14,
                    bgcolor=AZUL_800,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "PS",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ),
                ft.Column(
                    [
                        ft.Text(
                            "PriceSmart",
                            size=23,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_950,
                        ),
                        ft.Text(
                            "Compra simulada · AFD en tiempo real",
                            size=9,
                            color=TEXTO_SUAVE,
                        ),
                    ],
                    spacing=1,
                ),
            ],
            spacing=11,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    boton_usuario = ft.Container(
        width=44,
        height=44,
        border_radius=13,
        bgcolor=AZUL_50,
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(
            ft.Icons.PERSON_OUTLINE,
            color=AZUL_800,
        ),
    )
    boton_usuario.on_click = btn_validar_membresia
    poner_cursor_click(boton_usuario)
    animar(boton_usuario, "animate_scale", 130)
    try:
        boton_usuario.on_hover = (
            lambda e:
            hover_icono(
                e,
                boton_usuario,
                AZUL_100,
                AZUL_50,
            )
        )
    except Exception:
        pass

    boton_carrito = ft.Container(
        width=46,
        height=46,
        border_radius=14,
        bgcolor=AZUL_950,
        alignment=ft.Alignment(0, 0),
        content=ft.Stack(
            [
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.SHOPPING_CART_OUTLINED,
                        color=ft.Colors.WHITE,
                        size=20,
                    ),
                ),
                ft.Container(
                    right=3,
                    top=3,
                    width=19,
                    height=19,
                    border_radius=999,
                    bgcolor=ROJO_600,
                    alignment=ft.Alignment(0, 0),
                    content=txt_carrito,
                ),
            ],
        ),
    )
    boton_carrito.on_click = abrir_carrito
    poner_cursor_click(boton_carrito)
    animar(boton_carrito, "animate_scale", 130)
    try:
        boton_carrito.on_hover = (
            lambda e:
            hover_icono(
                e,
                boton_carrito,
                AZUL_900,
                AZUL_950,
            )
        )
    except Exception:
        pass

    boton_reset = ft.Container(
        width=44,
        height=44,
        border_radius=13,
        bgcolor=ROJO_50,
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(
            ft.Icons.REFRESH,
            color=ROJO_600,
        ),
    )
    boton_reset.on_click = btn_reiniciar
    poner_cursor_click(boton_reset)
    animar(boton_reset, "animate_scale", 130)

    header_busqueda = ft.Container(
        border_radius=15,
        padding=2,
        content=campo_busqueda,
    )

    header_acciones = ft.Row(
        [
            ft.Column(
                [
                    ft.Text(
                        "TOTAL",
                        size=7,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO_SUAVE,
                    ),
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
        wrap=False,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    header_row = ft.ResponsiveRow(
        [
            ft.Container(
                col={
                    "xs": 12,
                    "md": 3,
                    "lg": 3,
                },
                content=marca,
            ),
            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                    "lg": 5,
                },
                content=header_busqueda,
            ),
            ft.Container(
                col={
                    "xs": 12,
                    "md": 3,
                    "lg": 4,
                },
                alignment=ft.Alignment(1, 0),
                content=header_acciones,
            ),
        ],
        spacing=12,
        run_spacing=12,
    )

    header_kwargs = {
        "border_radius": 24,
        "bgcolor": SUPERFICIE,
        "shadow": sombra(20, "#D7E2ED"),
        "clip_behavior": ft.ClipBehavior.HARD_EDGE,
        "content": ft.Stack(
            [
                blob(
                    AZUL_100,
                    220,
                    right=-70,
                    top=-120,
                    opacity=0.48,
                ),
                blob(
                    ROJO_100,
                    135,
                    right=180,
                    bottom=-90,
                    opacity=0.28,
                ),
                ft.Container(
                    padding=ft.Padding(
                        left=22,
                        top=17,
                        right=22,
                        bottom=17,
                    ),
                    content=header_row,
                ),
            ]
        ),
    }

    grad = gradiente(
        [
            "#FFFFFF",
            "#F7FAFF",
            "#EEF5FF",
        ]
    )

    if grad is not None:
        header_kwargs["gradient"] = grad

    header = ft.Container(
        **header_kwargs
    )

    # 15. PANEL CATÁLOGO
    cabecera_catalogo = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "md": 7},
                content=ft.Column(
                    [
                        ft.Text(
                            "Productos",
                            size=25,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_950,
                        ),
                        ft.Text(
                            "Valida tu membresía desde el icono de usuario y agrega los productos que deseas comprar.",
                            size=10,
                            color=TEXTO_SUAVE,
                        ),
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
        col={
            "xs": 12,
            "lg": 8,
        },
        bgcolor="#FCFDFE",
        border_radius=24,
        shadow=sombra(18, "#DCE5EF"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            [
                blob(
                    "#EAF3FF",
                    270,
                    left=-160,
                    top=70,
                    opacity=0.28,
                ),
                ft.Container(
                    padding=ft.Padding(
                        left=22,
                        top=22,
                        right=22,
                        bottom=30,
                    ),
                    content=ft.Column(
                        [
                            cabecera_catalogo,
                            columna_catalogo,
                        ],
                        spacing=28,
                    ),
                ),
            ]
        ),
    )

    # 16. PANEL AFD
    tarjeta_estado = ft.Container(
        border_radius=16,
        padding=14,
        bgcolor="#0A315F",
        gradient=gradiente([
            "#082B57",
            "#123E73",
        ]),
        shadow=sombra(10, "#D9E5F1"),
        content=ft.Row(
            [
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=999,
                    bgcolor="#1E67B7",
                    alignment=ft.Alignment(0, 0),
                    content=txt_codigo_estado,
                ),
                ft.Column(
                    [
                        ft.Text(
                            "ESTADO ACTUAL",
                            size=7,
                            weight=ft.FontWeight.BOLD,
                            color="#9EB7D3",
                        ),
                        txt_estado_actual,
                        txt_formula,
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=11,
        ),
    )

    afd_card = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=20,
        padding=14,
        shadow=sombra(12, "#E2EAF2"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "AFD en tiempo real",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_950,
                                ),
                                ft.Text(
                                    "El estado activo y el evento ejecutado se resaltan.",
                                    size=8,
                                    color=TEXTO_SUAVE,
                                ),
                            ],
                            spacing=1,
                        ),
                        chip(
                            "EN VIVO",
                            VERDE_700,
                            VERDE_50,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                tarjeta_estado,
                ft.Container(
                    bgcolor=SUPERFICIE_2,
                    border_radius=16,
                    padding=ft.Padding(
                        left=7,
                        top=8,
                        right=7,
                        bottom=8,
                    ),
                    content=diagrama_contenido,
                ),
                ft.Text(
                    "El recorrido se actualiza en tiempo real. ↻ RP es la autotransición de registro de productos.",
                    size=8,
                    color=TEXTO_SUAVE,
                ),
            ],
            spacing=12,
        ),
    )

    # 17. HISTORIAL
    historial_card = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=20,
        padding=16,
        shadow=sombra(12, "#E2EAF2"),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "Historial de transiciones",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_950,
                                ),
                                txt_cantidad_historial,
                            ],
                            spacing=1,
                        ),
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=11,
                            bgcolor=AZUL_50,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.HISTORY,
                                color=AZUL_700,
                                size=19,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(
                    height=1,
                    color=BORDE,
                ),
                lista_historial,
            ],
            spacing=11,
        ),
    )

    panel_afd = ft.Container(
        col={
            "xs": 12,
            "lg": 4,
        },
        bgcolor="#F1F5FA",
        border_radius=24,
        padding=13,
        shadow=sombra(18, "#DCE5EF"),
        content=ft.Column(
            [
                afd_card,
                historial_card,
            ],
            spacing=13,
        ),
    )

    # 18. LAYOUT FINAL
    contenido = ft.ResponsiveRow(
        [
            panel_catalogo,
            panel_afd,
        ],
        spacing=18,
        run_spacing=18,
    )

    cuerpo = ft.Container(
        padding=ft.Padding(
            left=18,
            top=18,
            right=18,
            bottom=28,
        ),
        content=ft.Column(
            [
                header,
                contenido,
            ],
            spacing=18,
        ),
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

    # Reintento después de montar la página.
    maximizar()
    page.update()