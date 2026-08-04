/**
 * dream-loader.js — Parser PGM nativo + render Canvas neón
 * Motor de Imaginación Autónoma v1.0
 *
 * GitHub Pages no sabe servir .pgm como imagen (MIME text/plain),
 * así que parseamos el formato P2 ASCII en el navegador y pintamos
 * los píxeles en un canvas con paleta neón.
 */

const NEON_PALETTE = (v) => {
    // v en [0, 255] → color RGB con gradiente: negro → verde → cian → blanco
    const t = v / 255;
    let r, g, b;
    if (t < 0.33) {
        // negro → verde neón
        const k = t / 0.33;
        r = Math.floor(0 + k * 0);
        g = Math.floor(20 + k * 235);
        b = Math.floor(40 + k * 170);
    } else if (t < 0.66) {
        // verde neón → cian
        const k = (t - 0.33) / 0.33;
        r = Math.floor(0 + k * 0);
        g = Math.floor(255);
        b = Math.floor(210 + k * 45);
    } else {
        // cian → blanco
        const k = (t - 0.66) / 0.34;
        r = Math.floor(k * 255);
        g = Math.floor(255);
        b = Math.floor(255);
    }
    return [r, g, b];
};

function parsePGM(text) {
    // P2 = ASCII greymap. Header: "P2\n# comentarios\nWIDTH HEIGHT\nMAXVAL\n...pixels"
    const tokens = text.split(/\s+/);
    let i = 0;
    if (tokens[i] !== 'P2') throw new Error('No es PGM P2');
    i++;
    // saltar comentarios y headers hasta encontrar WIDTH HEIGHT
    while (tokens[i] && tokens[i].startsWith('#')) i++; // por si hay comentarios
    const w = parseInt(tokens[i++], 10);
    const h = parseInt(tokens[i++], 10);
    const max = parseInt(tokens[i++], 10);
    const pixels = new Uint8ClampedArray(w * h);
    for (let p = 0; p < w * h; p++) {
        // saltar comentarios inline
        while (tokens[i] && tokens[i].startsWith('#')) {
            // saltar hasta fin de línea — pero como split por whitespace,
            // el comentario va a ser un solo token. Lo saltamos.
            i++;
        }
        pixels[p] = Math.floor((parseInt(tokens[i++], 10) / max) * 255);
    }
    return { width: w, height: h, pixels };
}

async function loadDream(filename) {
    const resp = await fetch(`gallery/${filename}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status} en ${filename}`);
    const text = await resp.text();
    const { width, height, pixels } = parsePGM(text);

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    const imgData = ctx.createImageData(width, height);

    for (let p = 0; p < pixels.length; p++) {
        const [r, g, b] = NEON_PALETTE(pixels[p]);
        imgData.data[p * 4] = r;
        imgData.data[p * 4 + 1] = g;
        imgData.data[p * 4 + 2] = b;
        imgData.data[p * 4 + 3] = 255;
    }
    ctx.putImageData(imgData, 0, 0);
    return canvas;
}

async function renderGallery() {
    const gallery = document.getElementById('gallery');
    const status = document.getElementById('status');

    if (status) status.textContent = '⟳ Conectando al repositorio neural...';

    try {
        const resp = await fetch('gallery/INDEX.txt');
        if (!resp.ok) throw new Error('INDEX.txt no encontrado');
        const txt = await resp.text();
        const files = txt.split('\n').map(f => f.trim()).filter(f => f.endsWith('.pgm'));

        if (files.length === 0) {
            gallery.innerHTML = '<p>Galería aún sin sueños. Espera al primer ciclo.</p>';
            if (status) status.remove();
            return;
        }

        if (status) status.textContent = `⟳ Decodificando ${files.length} sueños CPPN...`;

        gallery.innerHTML = '';
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (status) status.textContent = `⟳ Renderizando sueño ${i + 1}/${files.length}...`;

            const wrap = document.createElement('div');
            wrap.className = 'dream';
            wrap.style.setProperty('--i', i);

            const canvas = await loadDream(file);
            wrap.appendChild(canvas);

            const caption = document.createElement('p');
            caption.textContent = file;
            wrap.appendChild(caption);

            gallery.appendChild(wrap);
        }

        if (status) {
            status.textContent = `✓ ${files.length} sueños cultivados`;
            status.style.color = 'var(--neon)';
            status.style.borderColor = 'var(--neon)';
            status.style.animation = 'none';
            setTimeout(() => status.remove(), 3000);
        }
    } catch (err) {
        gallery.innerHTML = `<p style="color:#ff5577">Error: ${err.message}</p>`;
        if (status) status.textContent = '✗ Error de carga';
        console.error('dream-loader:', err);
    }
}

// Auto-init
document.addEventListener('DOMContentLoaded', renderGallery);
