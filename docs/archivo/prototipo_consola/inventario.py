"""MVP de inventario por consola para la entrega 2.

Los productos se guardan únicamente en memoria y se pierden al salir.
Este programa no usa Django ni una base de datos.
"""

from decimal import Decimal, InvalidOperation


def leer_cantidad():
    """Solicita una cantidad entera no negativa sin cerrar el programa."""
    while True:
        try:
            cantidad = int(input("Cantidad en stock: "))
        except ValueError:
            print("Ingresa un número entero válido.")
            continue
        if cantidad < 0:
            print("La cantidad no puede ser negativa.")
            continue
        return cantidad


def leer_precio():
    """Solicita un precio positivo y conserva su precisión decimal."""
    while True:
        try:
            precio = Decimal(input("Precio: ").strip().replace(",", "."))
        except InvalidOperation:
            print("Ingresa un precio válido, por ejemplo 12500.50.")
            continue
        if not precio.is_finite() or precio <= 0:
            print("El precio debe ser mayor que cero.")
            continue
        if precio.as_tuple().exponent < -2:
            print("El precio puede tener máximo dos decimales.")
            continue
        return precio


def agregar_producto(inventario):
    """Solicita y agrega un producto a la lista en memoria."""
    print("\nAgregar producto")
    nombre = input("Nombre del producto: ").strip()
    while not nombre:
        print("El nombre del producto es obligatorio.")
        nombre = input("Nombre del producto: ").strip()
    cantidad = leer_cantidad()
    precio = leer_precio()

    inventario.append({
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio,
    })
    print("Producto agregado correctamente.")


def visualizar_inventario(inventario):
    """Muestra todos los productos registrados."""
    print("\nInventario")
    if not inventario:
        print("El inventario está vacío.")
        return

    for numero, producto in enumerate(inventario, start=1):
        print(
            f"{numero}. {producto['nombre']} | "
            f"Stock: {producto['cantidad']} | "
            f"Precio: ${producto['precio']:.2f}"
        )


def buscar_producto(inventario):
    """Busca productos por coincidencia parcial en el nombre."""
    termino = input("Nombre del producto que buscas: ").strip().casefold()
    if not termino:
        print("Escribe un nombre o parte del nombre para buscar.")
        return
    resultados = [
        producto for producto in inventario
        if termino in producto["nombre"].casefold()
    ]

    if not resultados:
        print("No se encontraron productos con ese nombre.")
        return

    print("\nResultados")
    for producto in resultados:
        print(
            f"{producto['nombre']} | Stock: {producto['cantidad']} | "
            f"Precio: ${producto['precio']:.2f}"
        )


def mostrar_menu():
    """Imprime las opciones disponibles."""
    print("\n=== Magnus SIG · Inventario por consola ===")
    print("1. Agregar producto")
    print("2. Visualizar inventario")
    print("3. Buscar producto")
    print("4. Salir")


def main():
    """Mantiene el menú activo hasta que el usuario elija salir."""
    inventario = []

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            agregar_producto(inventario)
        elif opcion == "2":
            visualizar_inventario(inventario)
        elif opcion == "3":
            buscar_producto(inventario)
        elif opcion == "4":
            print("Hasta luego.")
            break
        else:
            print("Opción no reconocida. Elige una opción del 1 al 4.")


if __name__ == "__main__":
    main()
