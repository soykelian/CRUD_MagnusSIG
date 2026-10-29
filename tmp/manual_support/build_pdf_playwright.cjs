const fs = require('fs');
const path = require('path');
const marked = require('C:/Users/Julian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked');
const { chromium } = require('C:/Users/Julian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

async function generatePdf() {
    const rootDir = path.resolve(__dirname, '../..');
    const mdPath = path.join(rootDir, 'docs', 'Manual_Usuario_Magnus_SIG.md');
    const outPdf1 = path.join(rootDir, 'output', 'pdf', 'Manual_Usuario_Magnus_SIG.pdf');
    const outPdf2 = path.join(rootDir, 'docs', 'Manual_Usuario_Magnus_SIG.pdf');
    const tempHtmlPath = path.join(rootDir, 'docs', 'manual_temp.html');

    if (!fs.existsSync(mdPath)) {
        console.error('No se encontro el archivo:', mdPath);
        process.exit(1);
    }

    const mdContent = fs.readFileSync(mdPath, 'utf-8');

    // Configure marked
    marked.setOptions({
        gfm: true,
        breaks: true
    });

    const parsedHtml = marked.parse(mdContent);

    const fullHtml = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Manual de Usuario - Magnus SIG</title>
<style>
    @page {
        size: A4;
        margin: 20mm 16mm 22mm 16mm;
    }

    * {
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.55;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }

    /* Cover Page */
    .cover-container {
        page-break-after: always;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 30px 20px;
    }

    .cover-logo {
        max-width: 320px;
        height: auto;
        margin-bottom: 30px;
    }

    .cover-title {
        font-size: 32pt;
        font-weight: 800;
        color: #2e3192;
        letter-spacing: -0.5px;
        margin: 0 0 10px 0;
    }

    .cover-system {
        font-size: 20pt;
        font-weight: 700;
        color: #269dd8;
        margin: 0 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .cover-subtitle {
        font-size: 13pt;
        font-weight: 500;
        color: #475569;
        margin: 0 0 35px 0;
    }

    .cover-badge-container {
        display: flex;
        gap: 15px;
        margin-bottom: 40px;
        justify-content: center;
    }

    .cover-badge {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 9pt;
        color: #334155;
        font-weight: 600;
    }

    .cover-meta {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 35px;
        max-width: 500px;
        width: 100%;
        margin-top: 20px;
        text-align: left;
    }

    .cover-meta table {
        width: 100%;
        border-collapse: collapse;
    }

    .cover-meta td {
        padding: 6px 8px;
        font-size: 9.5pt;
        border: none;
    }

    .cover-meta td.label {
        color: #64748b;
        font-weight: 600;
        width: 40%;
    }

    .cover-meta td.value {
        color: #0f172a;
        font-weight: 600;
    }

    /* Headings */
    h1 {
        color: #2e3192;
        font-size: 18pt;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-top: 28px;
        margin-bottom: 14px;
        page-break-after: avoid;
    }

    h2 {
        color: #1e293b;
        font-size: 14pt;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }

    h3 {
        color: #269dd8;
        font-size: 11.5pt;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 8px;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 10px 0;
        text-align: justify;
    }

    ul, ol {
        margin: 0 0 12px 0;
        padding-left: 24px;
    }

    li {
        margin-bottom: 4px;
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0 20px 0;
        font-size: 8.8pt;
        page-break-inside: avoid;
    }

    th {
        background: #2e3192;
        color: #ffffff;
        font-weight: 600;
        text-align: left;
        padding: 8px 10px;
        border: 1px solid #1e247e;
    }

    td {
        padding: 7px 10px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }

    tr:nth-child(even) td {
        background: #f8fafc;
    }

    /* Images */
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 14px auto 8px auto;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        max-height: 440px;
        object-fit: contain;
        page-break-inside: avoid;
    }

    /* Blockquotes / Callouts */
    blockquote {
        margin: 14px 0;
        padding: 10px 16px;
        background: #f0fdfa;
        border-left: 4px solid #0d9488;
        border-radius: 0 8px 8px 0;
        color: #134e4a;
        font-size: 9.2pt;
    }

    blockquote p {
        margin: 0;
    }

    /* Code blocks */
    pre {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 8.5pt;
        overflow-x: hidden;
        page-break-inside: avoid;
        font-family: Consolas, "Courier New", monospace;
    }

    code {
        font-family: Consolas, "Courier New", monospace;
        font-size: 8.8pt;
        background: #f1f5f9;
        padding: 1px 4px;
        border-radius: 4px;
        color: #0f172a;
    }

    pre code {
        padding: 0;
        background: none;
    }

    hr {
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 22px 0;
    }

    /* Table of contents styling */
    .toc-block {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 25px;
        page-break-after: always;
    }

    .toc-block ul {
        list-style-type: none;
        padding-left: 0;
    }

    .toc-block li {
        margin-bottom: 6px;
        font-size: 9.5pt;
    }

    .toc-block a {
        text-decoration: none;
        color: #2e3192;
        font-weight: 500;
    }

    .page-break {
        page-break-after: always;
    }
</style>
</head>
<body>
${parsedHtml}
</body>
</html>`;

    fs.writeFileSync(tempHtmlPath, fullHtml, 'utf-8');
    console.log('HTML temporal generado:', tempHtmlPath);

    console.log('Iniciando Chromium con Chrome del sistema...');
    const chromePath = fs.existsSync('C:/Program Files/Google/Chrome/Application/chrome.exe')
        ? 'C:/Program Files/Google/Chrome/Application/chrome.exe'
        : 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
    const browser = await chromium.launch({ executablePath: chromePath });
    const page = await browser.newPage();

    await page.goto('file:///' + tempHtmlPath.replace(/\\/g, '/'), {
        waitUntil: 'networkidle'
    });

    console.log('Generando PDF...');
    await page.pdf({
        path: outPdf1,
        format: 'A4',
        printBackground: true,
        margin: {
            top: '20mm',
            bottom: '22mm',
            left: '16mm',
            right: '16mm'
        },
        displayHeaderFooter: true,
        headerTemplate: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 8pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px;">
                <span style="font-weight: 600; color: #2e3192;">MAGNUS SIG &bull; Manual de Usuario</span>
                <span>Sistema de Inventario SG-SST</span>
            </div>
        `,
        footerTemplate: `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 8pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; border-top: 1px solid #f1f5f9; padding-top: 4px;">
                <span>Confidencial &bull; Equipo Magnus SIG</span>
                <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
            </div>
        `
    });

    // Copy to docs folder as well
    fs.copyFileSync(outPdf1, outPdf2);

    await browser.close();

    // Clean up temporary html
    if (fs.existsSync(tempHtmlPath)) {
        fs.unlinkSync(tempHtmlPath);
    }

    console.log('PDF generado exitosamente:');
    console.log('1. ', outPdf1);
    console.log('2. ', outPdf2);
}

generatePdf().catch(err => {
    console.error('Error generando PDF:', err);
    process.exit(1);
});
