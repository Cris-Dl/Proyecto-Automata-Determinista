import re
import requests

class SistemaCompra:
    """Datos y validaciones del módulo de compra extraídos del prototipo original."""

    categorias = ["Todos", "Alimentos", "Accesorios"]

    PATRON_MEMBRESIA = re.compile(r"^PS[A-Za-z]{3}[0-9]{3}$")
    PATRON_TARJETA = re.compile(r"^\d{16}$")
    PATRON_FECHA = re.compile(r"^(0[1-9]|1[0-2])\/\d{2}$")
    PATRON_CVV = re.compile(r"^\d{3,4}$")

    def __init__(self):
        self.productos = self.obtener_productos_api()
        self.total_compra = 0.0
        self.productos_agregados = []

    @staticmethod
    def obtener_productos_api():
        productos_api = []
        try:
            res_alimentos = requests.get(
                "https://dummyjson.com/products/category/groceries",
                timeout=5,
            )
            if res_alimentos.status_code == 200:
                for item in res_alimentos.json()["products"]:
                    productos_api.append({
                        "nombre": item["title"][:18] + "..." if len(item["title"]) > 18 else item["title"],
                        "precio": float(item["price"]) * 8.0,
                        "categoria": "Alimentos",
                        "imagen": item["thumbnail"],
                    })

            res_accesorios = requests.get(
                "https://dummyjson.com/products/category/smartphones",
                timeout=5,
            )
            if res_accesorios.status_code == 200:
                for item in res_accesorios.json()["products"]:
                    productos_api.append({
                        "nombre": item["title"][:18] + "..." if len(item["title"]) > 18 else item["title"],
                        "precio": float(item["price"]) * 8.0,
                        "categoria": "Accesorios",
                        "imagen": item["thumbnail"],
                    })

            if len(productos_api) > 0:
                return productos_api

        except Exception:
            pass

        return [
            {"nombre": "Arroz 5kg", "precio": 45.00, "categoria": "Alimentos", "imagen": None},
            {"nombre": "Frijol 4kg", "precio": 35.00, "categoria": "Alimentos", "imagen": None},
            {"nombre": "TV Smart 50\"", "precio": 2500.00, "categoria": "Accesorios", "imagen": None},
            {"nombre": "Audífonos Bluetooth", "precio": 300.00, "categoria": "Accesorios", "imagen": None},
        ]

    def validar_membresia(self, codigo):
        return bool(self.PATRON_MEMBRESIA.match(codigo))

    def agregar_producto(self, producto):
        self.productos_agregados.append(producto)
        self.total_compra += producto["precio"]

    def validar_pago(self, nombre, nit, tarjeta, fecha, cvv):
        if not nombre or not nit:
            return False, "Ingresa tus datos personales (Nombre y NIT/DPI)."

        if not self.PATRON_TARJETA.match(tarjeta):
            return False, "Tarjeta inválida. Deben ser exactamente 16 dígitos numéricos."

        if not self.PATRON_FECHA.match(fecha):
            return False, "Fecha inválida. Usa el formato MM/YY (Ej. 12/25)."

        if not self.PATRON_CVV.match(cvv):
            return False, "CVV inválido. Deben ser 3 o 4 dígitos."

        return True, ""

    def reiniciar(self):
        self.total_compra = 0.0
        self.productos_agregados.clear()