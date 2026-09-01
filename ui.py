import flet as ft


def construir_interfaz(page: ft.Page, automata, sistema):
    """
    ETAPA 2 - UI RESPONSIVE + SISTEMA VISUAL
    ----------------------------------------
    Esta etapa modifica SOLAMENTE la interfaz.

    Mantiene intactos:
    - automata.py
    - sistema.py
    - flujo y validaciones del prototipo actual

    Cambios visuales:
    - Layout responsive real, sin GridView con alturas rígidas.
    - Tarjetas de producto responsive: 1 / 2 / 3 / 4 columnas.
    - Más aire, separación y jerarquía visual.
    - Paleta moderna azul / rojo con fondos suaves.
    - Gradientes y glows/blurs decorativos compatibles cuando Flet lo permite.
    - Historial responsive en tarjetas: conserva Paso, Estado, Símbolo,
      Transición, Nuevo estado y Explicación sin una tabla rígida.
    - AFD compacto y siempre presente en el panel derecho en escritorio.
    """

    # ======================================================================
    # 1. PALETA Y CONFIGURACIÓN GENERAL
    # ======================================================================
    AZUL_950 = "#082A5E"
    AZUL_900 = "#0B3F86"
    AZUL_800 = "#0E4DA4"
    AZUL_700 = "#1765C1"
    AZUL_600 = "#2379D8"
    AZUL_100 = "#DCEBFF"
    AZUL_50 = "#EEF6FF"

    ROJO_600 = "#EF3E42"
    ROJO_50 = "#FFF1F2"

    VERDE_700 = "#16835A"
    VERDE_50 = "#ECFDF5"

    NARANJA_700 = "#D97706"
    NARANJA_50 = "#FFF7E8"

    TEXTO = "#172033"
    TEXTO_SUAVE = "#66778B"
    BORDE = "#E3EAF2"
    SUPERFICIE = "#FFFFFF"
    FONDO = "#F4F7FB"

    page.title = "Simulador PriceSmart - AFD"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = FONDO

    categorias = sistema.categorias
    productos = sistema.productos
    estados_afd = automata.estados_afd

    # ======================================================================
    # 2. COMPATIBILIDAD VISUAL
    # ======================================================================
    def crear_gradiente(colores, inicio=None, fin=None):
        """Devuelve gradiente si la versión de Flet lo soporta; si no, None."""
        clase = getattr(ft, "LinearGradient", None)
        if clase is None:
            return None

        try:
            return clase(
                begin=inicio or ft.Alignment(-1, -1),
                end=fin or ft.Alignment(1, 1),
                colors=colores,
            )
        except Exception:
            return None

    def crear_blur(sigma=30):
        """Intenta crear blur en distintas firmas de Flet, sin romper la app."""
        clase = getattr(ft, "Blur", None)
        if clase is None:
            return None

        intentos = [
            lambda: clase(sigma_x=sigma, sigma_y=sigma),
            lambda: clase(sigma, sigma),
        ]

        for intento in intentos:
            try:
                return intento()
            except Exception:
                pass

        return None

    def crear_blob(color, ancho, alto, izquierda=None, derecha=None, arriba=None, abajo=None):
        kwargs = {
            "width": ancho,
            "height": alto,
            "border_radius": 999,
            "bgcolor": color,
            "opacity": 0.65,
            "left": izquierda,
            "right": derecha,
            "top": arriba,
            "bottom": abajo,
        }

        blur = crear_blur(45)
        if blur is not None:
            kwargs["blur"] = blur

        return ft.Container(**kwargs)

    # ======================================================================
    # 3. HELPERS GENERALES
    # ======================================================================
    def codigo_estado(estado_completo):
        return estado_completo.split(":", 1)[0].strip()

    def nombre_estado(estado_completo):
        partes = estado_completo.split(":", 1)
        return partes[1].strip() if len(partes) == 2 else estado_completo

    def simbolo_de_evento(evento):
        evento_lower = evento.lower()
        if "validar membresía" in evento_lower:
            return "VM"
        if "registrar producto" in evento_lower:
            return "RP"
        if "finalizar registro" in evento_lower:
            return "FR"
        if "realizar pago" in evento_lower:
            return "PG"
        if "aprobar pago" in evento_lower:
            return "AP"
        return "—"

    def explicacion_evento(simbolo, valido=True):
        explicaciones = {
            "VM": "Validación de membresía",
            "RP": "Registro de producto",
            "FR": "Finalización del registro",
            "PG": "Realización del pago",
            "AP": "Aprobación del pago",
        }
        base = explicaciones.get(simbolo, "Evento del sistema")
        return base if valido else f"{base}: transición no válida"

    def mostrar_alerta(mensaje, color_fondo=ROJO_600):
        page.snack_bar = ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color_fondo,
        )
        page.snack_bar.open = True
        page.update()

    def crear_boton(
        texto,
        color_fondo,
        icono=None,
        accion=None,
        data=None,
        ancho=None,
    ):
        boton = ft.Button(
            texto,
            icon=icono,
            on_click=accion,
            data=data,
            width=ancho,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=color_fondo,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(left=18, top=13, right=18, bottom=13),
            ),
        )
        return boton

    def etiqueta(texto, color_texto, color_fondo):
        return ft.Container(
            bgcolor=color_fondo,
            border_radius=999,
            padding=ft.Padding(left=9, top=4, right=9, bottom=4),
            content=ft.Text(
                texto,
                size=10,
                weight=ft.FontWeight.BOLD,
                color=color_texto,
            ),
        )

    def campo_historial(titulo, valor, col, color_valor=TEXTO, negrita=False):
        return ft.Container(
            col=col,
            padding=ft.Padding(left=4, top=4, right=4, bottom=4),
            content=ft.Column(
                [
                    ft.Text(
                        titulo.upper(),
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO_SUAVE,
                    ),
                    ft.Text(
                        str(valor),
                        size=12,
                        weight=ft.FontWeight.BOLD if negrita else ft.FontWeight.NORMAL,
                        color=color_valor,
                        max_lines=3,
                    ),
                ],
                spacing=3,
                tight=True,
            ),
        )

    # ======================================================================
    # 4. ESTADO VISUAL GENERAL
    # ======================================================================
    txt_total = ft.Text(
        "Q0.00",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=AZUL_950,
    )

    txt_estado_actual = ft.Text(
        nombre_estado(estados_afd[automata.estado_actual_idx]),
        size=18,
        weight=ft.FontWeight.BOLD,
        color=AZUL_950,
    )

    txt_codigo_estado = ft.Text(
        codigo_estado(estados_afd[automata.estado_actual_idx]),
        size=12,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

    badge_estado = ft.Container(
        content=txt_codigo_estado,
        bgcolor=AZUL_700,
        padding=ft.Padding(left=12, top=7, right=12, bottom=7),
        border_radius=999,
    )

    txt_ultimo_evento = ft.Text(
        "Sin eventos todavía",
        size=11,
        color=TEXTO_SUAVE,
        max_lines=2,
    )

    # ======================================================================
    # 5. HISTORIAL RESPONSIVE
    # ======================================================================
    historial_paso = 0

    lista_historial = ft.ListView(
        spacing=10,
        auto_scroll=True,
        height=430,
    )

    def crear_fila_historial(
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
            fondo = "#F8FBFF"
            barra = AZUL_600
            estado_color = AZUL_900
            estado_txt = "INICIAL"
            chip = etiqueta(estado_txt, AZUL_900, AZUL_100)
        elif valida:
            fondo = SUPERFICIE
            barra = VERDE_700
            estado_color = VERDE_700
            estado_txt = "VÁLIDA"
            chip = etiqueta(estado_txt, VERDE_700, VERDE_50)
        else:
            fondo = "#FFFBFB"
            barra = ROJO_600
            estado_color = ROJO_600
            estado_txt = "NO VÁLIDA"
            chip = etiqueta(estado_txt, ROJO_600, ROJO_50)

        contenido = ft.Container(
            padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"Paso {paso}",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=AZUL_950,
                                    ),
                                    chip,
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ResponsiveRow(
                        [
                            campo_historial(
                                "Estado actual",
                                estado_actual,
                                {"xs": 6, "sm": 4, "lg": 2},
                                AZUL_900,
                                True,
                            ),
                            campo_historial(
                                "Símbolo leído",
                                simbolo,
                                {"xs": 6, "sm": 4, "lg": 2},
                                AZUL_900,
                                True,
                            ),
                            campo_historial(
                                "Nuevo estado",
                                nuevo_estado,
                                {"xs": 6, "sm": 4, "lg": 2},
                                estado_color,
                                True,
                            ),
                            campo_historial(
                                "Transición",
                                transicion,
                                {"xs": 12, "sm": 6, "lg": 3},
                                TEXTO,
                            ),
                            campo_historial(
                                "Explicación",
                                explicacion,
                                {"xs": 12, "sm": 6, "lg": 3},
                                TEXTO_SUAVE,
                            ),
                        ],
                        spacing=6,
                        run_spacing=6,
                    ),
                ],
                spacing=10,
            ),
        )

        return ft.Container(
            bgcolor=fondo,
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=8, color="#E7EDF5"),
            content=ft.Row(
                [
                    ft.Container(width=4, bgcolor=barra, border_radius=999),
                    ft.Container(content=contenido, expand=True),
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
            crear_fila_historial(
                paso=0,
                estado_actual="q0",
                simbolo="—",
                transicion="—",
                nuevo_estado="q0",
                explicacion="Estado inicial",
                inicial=True,
            )
        )

    def registrar_historial(evento, estado_anterior, estado_nuevo):
        nonlocal historial_paso
        historial_paso += 1

        q_anterior = codigo_estado(estado_anterior)
        q_nuevo = codigo_estado(estado_nuevo)
        simbolo = simbolo_de_evento(evento)

        lista_historial.controls.append(
            crear_fila_historial(
                paso=historial_paso,
                estado_actual=q_anterior,
                simbolo=simbolo,
                transicion=f"δ({q_anterior}, {simbolo}) = {q_nuevo}",
                nuevo_estado=q_nuevo,
                explicacion=explicacion_evento(simbolo, valido=True),
                valida=True,
            )
        )

    def registrar_intento_invalido(simbolo, explicacion=None):
        nonlocal historial_paso
        historial_paso += 1

        estado = estados_afd[automata.estado_actual_idx]
        q_actual = codigo_estado(estado)

        lista_historial.controls.append(
            crear_fila_historial(
                paso=historial_paso,
                estado_actual=q_actual,
                simbolo=simbolo,
                transicion="No válida",
                nuevo_estado=q_actual,
                explicacion=(
                    explicacion
                    if explicacion is not None
                    else explicacion_evento(simbolo, valido=False)
                ),
                valida=False,
            )
        )
        page.update()

    cargar_estado_inicial_historial()

    # ======================================================================
    # 6. AFD VISUAL COMPACTO
    # ======================================================================
    nodos_afd = []
    flujo_afd = ft.Row(
        wrap=True,
        spacing=7,
        run_spacing=9,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    for i, estado in enumerate(estados_afd):
        q = codigo_estado(estado)
        nombre = nombre_estado(estado)

        nodo = ft.Container(
            padding=ft.Padding(left=12, top=8, right=12, bottom=8),
            border_radius=12,
            bgcolor="#EDF2F7",
            content=ft.Column(
                [
                    ft.Text(q, size=11, weight=ft.FontWeight.BOLD, color=TEXTO),
                    ft.Text(nombre, size=9, color=TEXTO_SUAVE, max_lines=2),
                ],
                spacing=1,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        nodos_afd.append(nodo)
        flujo_afd.controls.append(nodo)

        if i < len(estados_afd) - 1:
            flujo_afd.controls.append(
                ft.Icon(ft.Icons.ARROW_FORWARD, size=15, color="#8CA0B5")
            )

    def actualizar_interfaz_afd(ultimo_evento=None):
        estado_actual = estados_afd[automata.estado_actual_idx]

        txt_codigo_estado.value = codigo_estado(estado_actual)
        txt_estado_actual.value = nombre_estado(estado_actual)

        if ultimo_evento:
            txt_ultimo_evento.value = ultimo_evento

        for i, nodo in enumerate(nodos_afd):
            if i == automata.estado_actual_idx:
                nodo.bgcolor = AZUL_700
                nodo.shadow = ft.BoxShadow(blur_radius=12, color="#BDD5F2")
                nodo.content.controls[0].color = ft.Colors.WHITE
                nodo.content.controls[1].color = ft.Colors.WHITE
            else:
                nodo.bgcolor = "#EDF2F7"
                nodo.shadow = None
                nodo.content.controls[0].color = TEXTO
                nodo.content.controls[1].color = TEXTO_SUAVE

        page.update()

    def intentar_transicion(evento, indice_destino, condicion_valida=True):
        resultado = automata.intentar_transicion(
            evento,
            indice_destino,
            condicion_valida,
        )

        if resultado["valida"]:
            registrar_historial(
                resultado["evento"],
                resultado["estado_anterior"],
                resultado["estado_nuevo"],
            )
            actualizar_interfaz_afd(resultado["evento"])
        else:
            registrar_intento_invalido(
                simbolo_de_evento(evento),
                resultado["mensaje"],
            )
            mostrar_alerta(resultado["mensaje"])

    # ======================================================================
    # 7. MEMBRESÍA - MISMA LÓGICA
    # ======================================================================
    campo_membresia_dialogo = ft.TextField(
        label="Código de membresía",
        hint_text="Ej: PSABC123",
        width=300,
        max_length=8,
        text_align=ft.TextAlign.CENTER,
        capitalization=ft.TextCapitalization.CHARACTERS,
        autofocus=True,
    )

    texto_error_membresia = ft.Text("", color=ROJO_600, size=12)

    def cerrar_dialogo_membresia():
        dialogo_membresia.open = False
        page.update()

    def confirmar_membresia(_):
        codigo = (campo_membresia_dialogo.value or "").strip().upper()

        if not sistema.validar_membresia(codigo):
            texto_error_membresia.value = (
                "Membresía incorrecta. Formato: PS + 3 letras + 3 números. "
                "Intenta nuevamente."
            )
            campo_membresia_dialogo.value = ""
            page.update()
            return

        cerrar_dialogo_membresia()
        intentar_transicion(f"Validar Membresía ({codigo})", 1)

    dialogo_membresia = ft.AlertDialog(
        modal=True,
        title=ft.Text("Validar Membresía"),
        content=ft.Column(
            [
                ft.Text("Ingresa tu código de membresía para continuar."),
                campo_membresia_dialogo,
                texto_error_membresia,
            ],
            tight=True,
            spacing=12,
        ),
        actions=[
            ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo_membresia()),
            ft.Button("Validar", on_click=confirmar_membresia),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_membresia)

    def btn_validar_membresia(_):
        if automata.estado_actual_idx != 0:
            registrar_intento_invalido(
                "VM",
                "La membresía ya fue validada o el proceso ya inició.",
            )
            mostrar_alerta("La membresía ya fue validada o el proceso ya inició.")
            return

        campo_membresia_dialogo.value = ""
        texto_error_membresia.value = ""
        dialogo_membresia.open = True
        page.update()

    # ======================================================================
    # 8. PRODUCTOS / CARRITO - MISMA LÓGICA
    # ======================================================================
    def btn_agregar_producto(e):
        if automata.estado_actual_idx in [1, 2]:
            producto = e.control.data
            sistema.agregar_producto(producto)
            txt_total.value = f"Q{sistema.total_compra:.2f}"
            intentar_transicion("Registrar Producto (r)", 2)
        else:
            registrar_intento_invalido(
                "RP",
                "No se puede registrar un producto antes de validar la membresía.",
            )
            mostrar_alerta("Debes validar tu membresía antes de registrar productos.")

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
        lista_visual = ft.ListView(height=160, spacing=7)

        for p in sistema.productos_agregados:
            lista_visual.controls.append(
                ft.Row(
                    [
                        ft.Text(p["nombre"], expand=True),
                        ft.Text(f"Q{p['precio']:.2f}"),
                    ]
                )
            )

        contenido = ft.Column(
            [
                ft.Text("Revisa tus productos antes de finalizar:", italic=True),
                ft.Container(
                    content=lista_visual,
                    bgcolor="#F7F9FC",
                    padding=12,
                    border_radius=12,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Text("Subtotal:", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Q{sistema.total_compra:.2f}"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        ft.Text("Total:", weight=ft.FontWeight.BOLD, size=18),
                        ft.Text(
                            f"Q{sistema.total_compra:.2f}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_900,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    "¿Estás seguro de que no quieres agregar algún otro producto?",
                    size=11,
                    color=TEXTO_SUAVE,
                ),
            ],
            tight=True,
            width=360,
            spacing=10,
        )

        dialogo_resumen.content = contenido
        dialogo_resumen.open = True
        page.update()

    def btn_finalizar_registro(_):
        if automata.estado_actual_idx == 2:
            if not sistema.productos_agregados:
                mostrar_alerta("No has agregado ningún producto.")
                return
            abrir_dialogo_resumen()
        elif automata.estado_actual_idx > 2:
            registrar_intento_invalido("FR", "El registro de productos ya fue finalizado.")
            mostrar_alerta("El registro ya fue finalizado.")
        else:
            registrar_intento_invalido(
                "FR",
                "No se puede finalizar el registro antes de agregar productos.",
            )
            mostrar_alerta("Debes agregar productos primero.")

    # ======================================================================
    # 9. PAGO - MISMA LÓGICA
    # ======================================================================
    campo_nombre = ft.TextField(label="Nombre Completo", width=320, autofocus=True)
    campo_nit = ft.TextField(label="NIT / DPI", width=320)
    campo_tarjeta = ft.TextField(
        label="Número de Tarjeta",
        hint_text="16 dígitos",
        width=320,
        max_length=16,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    campo_fecha = ft.TextField(
        label="Vencimiento",
        hint_text="MM/YY",
        width=150,
        max_length=5,
    )
    campo_cvv = ft.TextField(
        label="CVV",
        width=150,
        max_length=4,
        password=True,
        can_reveal_password=True,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    texto_error_pago = ft.Text("", color=ROJO_600, size=12)

    def cerrar_dialogo_pago():
        dialogo_pago.open = False
        page.update()

    def procesar_pago(_):
        tarjeta = (campo_tarjeta.value or "").strip()
        fecha = (campo_fecha.value or "").strip()
        cvv = (campo_cvv.value or "").strip()

        valido, mensaje = sistema.validar_pago(
            campo_nombre.value,
            campo_nit.value,
            tarjeta,
            fecha,
            cvv,
        )

        if not valido:
            texto_error_pago.value = mensaje
            page.update()
            return

        texto_error_pago.value = ""
        cerrar_dialogo_pago()

        # MISMA LÓGICA DEL PROTOTIPO ACTUAL.
        intentar_transicion("Realizar Pago (p)", 4)
        intentar_transicion("Aprobar Pago (a)", 5)

        mostrar_alerta(
            "¡Pago aprobado! Compra finalizada exitosamente.",
            color_fondo=VERDE_700,
        )

    dialogo_pago = ft.AlertDialog(
        modal=True,
        title=ft.Text("Facturación y Pago Seguro"),
        content=ft.Column(
            [
                ft.Text("Datos del Titular", weight=ft.FontWeight.BOLD),
                campo_nombre,
                campo_nit,
                ft.Divider(),
                ft.Text("Detalles de la Tarjeta", weight=ft.FontWeight.BOLD),
                campo_tarjeta,
                ft.Row(
                    [campo_fecha, campo_cvv],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=320,
                ),
                texto_error_pago,
            ],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.Button("Cancelar", on_click=lambda _: cerrar_dialogo_pago()),
            ft.Button("Procesar Pago", on_click=procesar_pago),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_pago)

    def btn_pagar(_):
        if automata.estado_actual_idx == 3:
            campo_nombre.value = ""
            campo_nit.value = ""
            campo_tarjeta.value = ""
            campo_fecha.value = ""
            campo_cvv.value = ""
            texto_error_pago.value = ""
            dialogo_pago.open = True
            page.update()
        elif automata.estado_actual_idx == 5:
            registrar_intento_invalido(
                "PG",
                "La compra ya fue finalizada; no puede procesarse otro pago.",
            )
            mostrar_alerta("Esta compra ya fue finalizada. Reinicia el sistema.")
        else:
            registrar_intento_invalido(
                "PG",
                "No se puede realizar el pago antes de finalizar el registro.",
            )
            mostrar_alerta(
                "Debes finalizar el registro (Paso 2) antes de proceder a pagar."
            )

    # ======================================================================
    # 10. REINICIO - MISMA LÓGICA
    # ======================================================================
    def btn_reiniciar(_):
        sistema.reiniciar()
        automata.reiniciar()

        txt_total.value = "Q0.00"
        campo_membresia_dialogo.value = ""
        texto_error_membresia.value = ""
        txt_ultimo_evento.value = "Sistema reiniciado"

        cargar_estado_inicial_historial()
        actualizar_interfaz_afd()

    # ======================================================================
    # 11. CATÁLOGO RESPONSIVE - SIN ALTURAS RÍGIDAS DE GRID
    # ======================================================================
    columna_catalogo = ft.Column(spacing=28)

    def crear_tarjeta_producto(prod):
        if prod.get("imagen"):
            visual = ft.Image(
                src=prod["imagen"],
                height=118,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            visual = ft.Icon(
                ft.Icons.IMAGE_NOT_SUPPORTED,
                size=40,
                color="#B9C6D4",
            )

        boton_agregar = crear_boton(
            "Agregar",
            AZUL_700,
            icono=ft.Icons.ADD,
            accion=btn_agregar_producto,
            data=prod,
            ancho=145,
        )

        tarjeta = ft.Container(
            bgcolor=SUPERFICIE,
            border_radius=18,
            padding=18,
            shadow=ft.BoxShadow(blur_radius=12, color="#E2EAF3"),
            content=ft.Column(
                [
                    ft.Container(
                        height=132,
                        bgcolor="#F8FAFD",
                        border_radius=14,
                        alignment=ft.Alignment(0, 0),
                        padding=10,
                        content=visual,
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
                            etiqueta(prod["categoria"], AZUL_800, AZUL_50),
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
                spacing=14,
            ),
        )

        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4, "xl": 3},
            padding=6,
            content=tarjeta,
        )

    def cargar_productos(categoria_filtro="Todos"):
        columna_catalogo.controls.clear()

        if categoria_filtro == "Todos":
            categorias_presentes = [c for c in categorias if c != "Todos"]
        else:
            categorias_presentes = [categoria_filtro]

        for categoria in categorias_presentes:
            productos_categoria = [
                p for p in productos if p["categoria"] == categoria
            ]
            if not productos_categoria:
                continue

            columna_catalogo.controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    categoria,
                                    size=19,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_950,
                                ),
                                etiqueta(
                                    str(len(productos_categoria)),
                                    AZUL_800,
                                    AZUL_50,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.ResponsiveRow(
                            [crear_tarjeta_producto(p) for p in productos_categoria],
                            spacing=8,
                            run_spacing=8,
                        ),
                    ],
                    spacing=12,
                )
            )

        page.update()

    def cambiar_categoria(e):
        cargar_productos(e.control.value)

    dropdown_categorias = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(key=cat, text=cat) for cat in categorias],
        value="Todos",
        width=280,
    )
    # Compatibilidad con la versión de Flet del proyecto.
    dropdown_categorias.on_change = cambiar_categoria

    # ======================================================================
    # 12. CONTROLES DEL PROCESO
    # ======================================================================
    boton_membresia = crear_boton(
        "1. Validar Membresía",
        AZUL_700,
        icono=ft.Icons.PERSON_OUTLINE,
        accion=btn_validar_membresia,
        ancho=230,
    )
    boton_finalizar_reg = crear_boton(
        "2. Finalizar Registro",
        NARANJA_700,
        icono=ft.Icons.CHECK_CIRCLE_OUTLINE,
        accion=btn_finalizar_registro,
        ancho=230,
    )
    boton_pagar = crear_boton(
        "3. Pagar y Finalizar",
        VERDE_700,
        icono=ft.Icons.PAYMENTS_OUTLINED,
        accion=btn_pagar,
        ancho=230,
    )
    boton_reiniciar = crear_boton(
        "Reiniciar",
        ROJO_600,
        icono=ft.Icons.REFRESH,
        accion=btn_reiniciar,
        ancho=145,
    )

    acciones_responsive = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "sm": 6, "lg": 4},
                alignment=ft.Alignment(0, 0),
                content=boton_membresia,
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "lg": 4},
                alignment=ft.Alignment(0, 0),
                content=boton_finalizar_reg,
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "lg": 4},
                alignment=ft.Alignment(0, 0),
                content=boton_pagar,
            ),
        ],
        spacing=8,
        run_spacing=10,
    )

    # ======================================================================
    # 13. HEADER MODERNO - AÚN CON PLACEHOLDER DE LOGO
    # ======================================================================
    gradiente_header = crear_gradiente(["#FFFFFF", "#F5F9FF", "#EEF5FF"])

    header_contenido = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "md": 7},
                content=ft.Row(
                    [
                        ft.Container(
                            width=58,
                            height=58,
                            border_radius=16,
                            bgcolor=AZUL_800,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                "PS",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "PriceSmart",
                                    size=27,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_950,
                                ),
                                ft.Text(
                                    "Simulador de compra controlado mediante AFD",
                                    size=11,
                                    color=TEXTO_SUAVE,
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            ft.Container(
                col={"xs": 12, "md": 5},
                content=ft.Row(
                    [
                        ft.Container(
                            padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                            border_radius=14,
                            bgcolor="#F7FAFE",
                            content=ft.Column(
                                [
                                    ft.Text("TOTAL ACTUAL", size=9, color=TEXTO_SUAVE),
                                    txt_total,
                                ],
                                spacing=0,
                            ),
                        ),
                        boton_reiniciar,
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=12,
                    wrap=True,
                    run_spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        ],
        spacing=12,
        run_spacing=16,
    )

    header_layers = [
        crear_blob(AZUL_100, 230, 230, derecha=-70, arriba=-120),
        crear_blob("#FFE6E7", 150, 150, derecha=140, abajo=-90),
        ft.Container(
            padding=ft.Padding(left=24, top=20, right=24, bottom=20),
            content=header_contenido,
        ),
    ]

    header_kwargs = {
        "border_radius": 22,
        "bgcolor": SUPERFICIE,
        "shadow": ft.BoxShadow(blur_radius=18, color="#DDE6F0"),
        "clip_behavior": ft.ClipBehavior.HARD_EDGE,
        "content": ft.Stack(header_layers),
    }
    if gradiente_header is not None:
        header_kwargs["gradient"] = gradiente_header

    header = ft.Container(**header_kwargs)

    # ======================================================================
    # 14. PANEL DEL CATÁLOGO
    # ======================================================================
    cabecera_catalogo = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "md": 7},
                content=ft.Column(
                    [
                        ft.Text(
                            "Productos",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_950,
                        ),
                        ft.Text(
                            "Selecciona los productos que deseas registrar en la compra.",
                            size=12,
                            color=TEXTO_SUAVE,
                        ),
                    ],
                    spacing=4,
                ),
            ),
            ft.Container(
                col={"xs": 12, "md": 5},
                alignment=ft.Alignment(1, 0),
                content=dropdown_categorias,
            ),
        ],
        spacing=10,
        run_spacing=12,
    )

    bloque_acciones = ft.Container(
        bgcolor="#F8FAFD",
        border_radius=16,
        padding=16,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TUNE, size=18, color=AZUL_700),
                        ft.Text(
                            "Acciones del proceso",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_950,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "Ejecuta las acciones en orden para observar cómo responde el AFD.",
                    size=10,
                    color=TEXTO_SUAVE,
                ),
                acciones_responsive,
            ],
            spacing=12,
        ),
    )

    panel_sistema_contenido = ft.Column(
        [
            cabecera_catalogo,
            bloque_acciones,
            ft.Container(height=2),
            columna_catalogo,
        ],
        spacing=24,
    )

    panel_sistema_layers = [
        crear_blob("#EAF3FF", 260, 260, izquierda=-150, arriba=40),
        ft.Container(
            padding=ft.Padding(left=22, top=24, right=22, bottom=28),
            content=panel_sistema_contenido,
        ),
    ]

    panel_sistema = ft.Container(
        col={"xs": 12, "md": 7},
        bgcolor="#FCFDFE",
        border_radius=22,
        shadow=ft.BoxShadow(blur_radius=18, color="#DFE7F0"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(panel_sistema_layers),
    )

    # ======================================================================
    # 15. PANEL AFD + HISTORIAL
    # ======================================================================
    gradiente_estado = crear_gradiente(["#E9F4FF", "#F6FAFF", "#EEF4FF"])

    tarjeta_estado_kwargs = {
        "border_radius": 16,
        "padding": 16,
        "bgcolor": AZUL_50,
        "content": ft.Row(
            [
                badge_estado,
                ft.Column(
                    [
                        ft.Text("Estado actual", size=10, color=TEXTO_SUAVE),
                        txt_estado_actual,
                        txt_ultimo_evento,
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    }
    if gradiente_estado is not None:
        tarjeta_estado_kwargs["gradient"] = gradiente_estado

    tarjeta_estado_actual = ft.Container(**tarjeta_estado_kwargs)

    afd_compacto = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=18,
        padding=18,
        shadow=ft.BoxShadow(blur_radius=12, color="#E4EBF3"),
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
                                    "Vista compacta del estado activo",
                                    size=10,
                                    color=TEXTO_SUAVE,
                                ),
                            ],
                            spacing=2,
                        ),
                        etiqueta("EN VIVO", VERDE_700, VERDE_50),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                tarjeta_estado_actual,
                ft.Container(
                    bgcolor="#F8FAFD",
                    border_radius=14,
                    padding=12,
                    content=flujo_afd,
                ),
            ],
            spacing=14,
        ),
    )

    historial_panel = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=18,
        padding=18,
        shadow=ft.BoxShadow(blur_radius=12, color="#E4EBF3"),
        content=ft.Column(
            [
                ft.Column(
                    [
                        ft.Text(
                            "Historial de transiciones",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=AZUL_950,
                        ),
                        ft.Text(
                            "Cada intento conserva estado, símbolo, transición y resultado.",
                            size=10,
                            color=TEXTO_SUAVE,
                        ),
                    ],
                    spacing=3,
                ),
                ft.Divider(height=1, color=BORDE),
                lista_historial,
            ],
            spacing=12,
        ),
    )

    panel_automata = ft.Container(
        col={"xs": 12, "md": 5},
        border_radius=22,
        bgcolor="#F1F5FA",
        padding=14,
        shadow=ft.BoxShadow(blur_radius=18, color="#DFE7F0"),
        content=ft.Column(
            [afd_compacto, historial_panel],
            spacing=14,
        ),
    )

    # ======================================================================
    # 16. LAYOUT FINAL RESPONSIVE
    # ======================================================================
    contenido_principal = ft.ResponsiveRow(
        [panel_sistema, panel_automata],
        spacing=18,
        run_spacing=18,
    )

    cuerpo = ft.Container(
        padding=ft.Padding(left=20, top=18, right=20, bottom=28),
        content=ft.Column(
            [
                header,
                contenido_principal,
                ft.Container(height=2),
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

    # Carga inicial
    cargar_productos()
    actualizar_interfaz_afd()
