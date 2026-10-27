const { chromium } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Julian/AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:960},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/login/',{waitUntil:'networkidle'});
 await page.screenshot({path:'tmp/manual_support/cleanup-login-desktop.png',fullPage:true});
 await page.locator('#id_username').fill('manual_admin');await page.locator('#id_password').fill('ManualDemo-2026!');await page.getByRole('button',{name:'Iniciar sesión'}).click();await page.waitForURL('**/dashboard/');await page.waitForTimeout(300);
 await page.screenshot({path:'tmp/manual_support/cleanup-dashboard-desktop.png',fullPage:true});
 const urls=['/','/productos/','/categorias/','/movimientos/','/entradas/','/salidas/','/proveedores/','/clientes/','/reportes/','/productos/nuevo/','/entradas/nueva/','/salidas/nueva/'];
 const metrics=[];
 for(const url of urls){await page.goto('http://127.0.0.1:8765'+url,{waitUntil:'networkidle'});metrics.push({url,title:await page.title(),h1:await page.locator('h1').first().innerText().catch(()=>''),bodyWidth:await page.locator('body').evaluate(e=>e.scrollWidth),viewport:1440});}
 await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle'});await page.screenshot({path:'tmp/manual_support/cleanup-inventory-desktop.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});
 const mobile=[];
 for(const url of ['/login/','/dashboard/','/','/productos/','/categorias/','/movimientos/','/entradas/','/salidas/','/proveedores/','/clientes/','/reportes/','/productos/nuevo/','/entradas/nueva/','/salidas/nueva/']){
  await page.goto('http://127.0.0.1:8765'+url,{waitUntil:'networkidle'});
  const m=await page.locator('body').evaluate(e=>({scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,scrollHeight:e.scrollHeight}));mobile.push({url,...m});
  if(['/login/','/dashboard/','/','/productos/nuevo/','/reportes/'].includes(url)) await page.screenshot({path:'tmp/manual_support/cleanup-mobile-'+url.replaceAll('/','_')+'.png',fullPage:true});
 }
 await page.goto('http://127.0.0.1:8765/login/',{waitUntil:'networkidle'});await page.locator('#id_username').fill('manual_vendedor');await page.locator('#id_password').fill('ManualDemo-2026!');await page.getByRole('button',{name:'Iniciar sesión'}).click();await page.waitForURL('**/dashboard/');await page.screenshot({path:'tmp/manual_support/cleanup-seller-desktop.png',fullPage:true});
 console.log(JSON.stringify({desktop:metrics,mobile,errors},null,2));await browser.close();
})();
