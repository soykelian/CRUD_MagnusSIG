const { chromium } = require('C:/Users/Julian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'), path=require('path');
const out=path.resolve('tmp/manual_support/screens');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Julian/AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe'});
 const context=await browser.newContext({viewport:{width:1440,height:960},deviceScaleFactor:1});
 const page=await context.newPage(); page.setDefaultTimeout(15000);
 page.on('pageerror',e=>console.log('PAGEERROR',e.message));
 async function shot(name,full=true){await page.waitForTimeout(500); await page.screenshot({path:path.join(out,name+'.png'),fullPage:full}); console.log('CAPTURE',name,page.url())}
 async function adminLogin(){await page.goto('http://127.0.0.1:8765/login/'); await page.locator('#id_username').fill('manual_admin'); await page.locator('#id_password').fill('ManualDemo-2026!'); await page.locator('button[type=submit]').click(); await page.waitForURL('**/dashboard/');}
 async function sellerLogin(){await page.goto('http://127.0.0.1:8765/login/'); await page.locator('#id_username').fill('manual_vendedor'); await page.locator('#id_password').fill('ManualDemo-2026!'); await page.locator('button[type=submit]').click(); await page.waitForURL('**/dashboard/');}
 await page.goto('http://127.0.0.1:8765/login/'); await shot('01-login');
 await adminLogin(); await shot('02-dashboard-admin');
 await page.goto('http://127.0.0.1:8765/'); await shot('03-inventario');
 await page.goto('http://127.0.0.1:8765/productos/'); await shot('04-catalogo-productos');
 await page.goto('http://127.0.0.1:8765/categorias/'); await shot('05-categorias');
 await page.goto('http://127.0.0.1:8765/categorias/nueva/'); await shot('06-form-categoria');
 await page.locator('#nombre').fill('Protección ocular demo'); await page.locator('#descripcion').fill('Gafas y visores de seguridad para la demostración del manual.'); await shot('07-categoria-completada');
 await page.locator('.form-card form button[type=submit]').click(); await page.waitForURL('**/categorias/'); await shot('08-categoria-guardada');
 await page.goto('http://127.0.0.1:8765/productos/nuevo/'); await shot('09-form-producto');
 await page.locator('#id_codigo').fill('EPP-GAF-01'); await page.locator('#id_nombre').fill('Gafas de seguridad antiempañantes'); await page.locator('#id_descripcion').fill('Protección ocular para actividades de mantenimiento.'); await page.locator('#id_id_categoria').selectOption({label:'Protección ocular demo'}); await page.locator('#id_unidad_medida').fill('Unidad'); await page.locator('#id_precio_compra').fill('24000'); await page.locator('#id_precio_venta').fill('36000'); await page.locator('#id_cantidad').fill('12'); await page.locator('#id_stock_minimo').fill('4'); await page.locator('#id_ubicacion').fill('Bodega principal - Estante B2'); await shot('10-producto-completado');
 await page.locator('.form-card form button[type=submit]').click(); await page.waitForURL('http://127.0.0.1:8765/'); await shot('11-producto-en-inventario');
 await page.goto('http://127.0.0.1:8765/productos/'); await page.getByText('Gafas de seguridad antiempañantes',{exact:false}).first().click(); await page.waitForTimeout(300); await shot('12-detalle-producto');
 await page.goto('http://127.0.0.1:8765/movimientos/'); await shot('13-movimientos');
 await page.goto('http://127.0.0.1:8765/entradas/'); await shot('14-entradas');
 await page.goto('http://127.0.0.1:8765/entradas/nueva/'); await shot('15-form-entrada');
 await page.locator('#id_proveedor').selectOption({label:'Suministros Seguros Demo'}); await page.locator('#id_producto').selectOption({label:'Casco de seguridad clase E'}); await page.locator('input[name=cantidad]').fill('6'); await page.locator('input[name=costo_unitario]').fill('52000'); await page.locator('input[name=numero_factura]').fill('FAC-MANUAL-001'); await shot('16-entrada-completada');
 await page.locator('.form-card form button[type=submit]').click(); await page.waitForURL('**/entradas/'); await shot('17-entrada-pendiente');
 await page.getByRole('button',{name:'Confirmar recepción'}).first().click(); await page.waitForURL('**/entradas/'); await shot('18-entrada-recibida');
 await page.goto('http://127.0.0.1:8765/proveedores/'); await shot('19-proveedores');
 await page.goto('http://127.0.0.1:8765/clientes/'); await shot('20-clientes');
 await page.goto('http://127.0.0.1:8765/servicios/'); await shot('21-servicios');
 await page.goto('http://127.0.0.1:8765/reportes/'); await shot('22-reportes');
 await page.goto('http://127.0.0.1:8765/configuracion/'); await shot('23-configuracion');
 await page.goto('http://127.0.0.1:8765/admin/'); await shot('24-admin-django');
 await page.goto('http://127.0.0.1:8765/logout/').catch(()=>{});
 await sellerLogin(); await shot('25-dashboard-vendedor');
 await page.goto('http://127.0.0.1:8765/'); await shot('26-inventario-vendedor');
 await page.goto('http://127.0.0.1:8765/salidas/'); await shot('27-salidas-vendedor');
 await page.goto('http://127.0.0.1:8765/salidas/nueva/'); await shot('28-form-salida');
 await page.locator('#id_cliente').selectOption({label:'Proyecto de demostración'}); await page.locator('#id_producto').selectOption({label:'Casco de seguridad clase E'}); await page.locator('input[name=cantidad]').fill('3'); await page.locator('input[name=precio_unitario]').fill('78000'); await shot('29-salida-completada');
 await page.locator('.form-card form button[type=submit]').click(); await page.waitForURL('**/salidas/'); await shot('30-salida-pendiente');
 await page.getByRole('button',{name:'Despachar'}).first().click(); await page.waitForURL('**/salidas/'); await shot('31-salida-despachada');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

