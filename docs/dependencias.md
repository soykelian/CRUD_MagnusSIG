# Dependencias del proyecto

Este documento relaciona cada dependencia instalada con los módulos que la usan. Las dependencias Python se administran en `requirements.txt`; las del frontend, en `package.json` y `package-lock.json`.

## Python y Django

| Dependencia | Uso en MAGNUS SIG |
| --- | --- |
| `Django>=6.1,<6.2` | Proyecto `magnus_sig`, aplicación `productos`, modelos, vistas, formularios, autenticación, permisos, administración, migraciones y pruebas. Los formularios `ProductoForm`, `CategoriaForm`, `ProveedorForm`, `ClienteForm`, `EntradaForm`, `SalidaForm`, `MovimientoForm`, `ServicioForm` y `ConfiguracionForm` usan `django.forms`; no necesitan paquetes adicionales propios. |
| `PyMySQL>=1.1.0` | Conexión de Django con MySQL. `magnus_sig/__init__.py` lo registra como controlador MySQL compatible con Django. |
| `cryptography>=42.0.0` | Soporte de autenticación segura del servidor MySQL para PyMySQL. |
| `openpyxl>=3.1.5` | Generación de hojas de cálculo `.xlsx` desde Reportes. |
| `reportlab>=4.2` | Generación de documentos PDF desde Reportes. |
| `python-docx>=1.1.2` | Generación de documentos Word `.docx` desde Reportes. |

Los módulos de productos (inventario, clientes, proveedores, compras, ventas, servicios, movimientos, roles, stock, admin y comandos de gestión) usan Django y la biblioteca estándar de Python. No requieren paquetes adicionales por cada formulario. Las pruebas actuales usan `django.test.TestCase`, por lo que no requieren pytest.

El archivo de configuración carga variables de `.env` con código propio; no se usa `python-dotenv`. PyMySQL es el controlador elegido, por eso no se instala también `mysqlclient`.

## Frontend

| Dependencia | Tipo | Uso |
| --- | --- | --- |
| `@tailwindcss/cli` | Desarrollo/build | Compila la hoja Tailwind. |
| `tailwindcss` | Desarrollo/build | Framework CSS usado por `frontend/tailwind.css`. |
| `esbuild` | Desarrollo/build | Agrupa y divide el módulo de animaciones y el gráfico 3D. |
| `aos` | Runtime empaquetado | Animaciones de entrada por desplazamiento en `frontend/motion.js`. |
| `gsap` | Runtime empaquetado | Animaciones y ScrollTrigger; también anima el gráfico 3D. |
| `htmx.org` | Runtime empaquetado | Actualizaciones parciales de interfaz. |
| `lenis` | Runtime empaquetado | Desplazamiento suave. |
| `three` | Runtime empaquetado | Gráfico 3D de reportes. |

`productos/static/productos/app.js` usa JavaScript del navegador sin bibliotecas externas. Los archivos `static/productos/build/` son resultados generados; las fuentes que se deben mantener están en `magnus_sig/frontend/`.

## Prototipo de consola archivado

`docs/archivo/prototipo_consola/inventario.py` usa solo la biblioteca estándar de Python y no forma parte de la aplicación web Django.

## Instalación

Desde la raíz del repositorio:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
npm install
```

Después de actualizar dependencias frontend, confirma y sube juntos `package.json` y `package-lock.json`. Para dependencias Python, actualiza `requirements.txt`.

## Validaciones de formularios

Los formularios de clientes y proveedores exigen identificación, razón social, teléfono, correo, dirección y ciudad. Los modelos permiten almacenar vacíos los datos de contacto, pero la regla de captura los hace obligatorios en la interfaz; los registros existentes no se modifican y, al editarlos, se deben completar los datos faltantes. Los formularios de inventario y transacciones mantienen obligatorios sus campos esenciales (relaciones, cantidades, costos y motivos).

- **Cédula de ciudadanía (CC):** solo números, máximo 10 dígitos. Se aceptan identificaciones anteriores con menos dígitos; la Registraduría conserva válidas las cédulas anteriores al NUIP de 10 dígitos ([Registraduría](https://www.registraduria.gov.co/Ahora-la-cedula-es-de-10-digitos.html)).
- **Cédula de extranjería (CE):** solo números, máximo 12 dígitos.
- **NIT:** admite 8 a 10 dígitos base y un dígito de verificación opcional separado por guion. La validación es estructural; no consulta ni calcula el DV. DIAN distingue el número del NIT del dígito de verificación ([DIAN](https://normograma.dian.gov.co/dian/compilacion/docs/resolucion_dian_0032_2021.htm)).
- **Pasaporte:** 5 a 20 caracteres alfanuméricos o guion.
- **Teléfono:** admite 10 dígitos para marcación nacional colombiana, +57 con 10 dígitos o formato internacional de hasta 15 dígitos. La marcación nacional colombiana unificó fijos y móviles a 10 dígitos ([CRC](https://www.crcom.gov.co/es/noticias/comunicado-prensa/proximo-1-septiembre-cambia-forma-hacer-llamadas-desde-y-hacia-telefonos)).
- **Correo:** usa el validador de formato de Django; comprueba la sintaxis, no que el buzón exista o reciba mensajes.
- **Dirección:** mínimo 5 caracteres, debe incluir letras y admite nomenclatura y signos de uso común. No intenta comprobar la existencia de la dirección.
- **Servicio:** rechaza valores negativos y fechas de finalización anteriores a la fecha de inicio.

Estas reglas se aplican al guardar desde los formularios de la aplicación; no modifican el esquema MySQL ni requieren una migración.
