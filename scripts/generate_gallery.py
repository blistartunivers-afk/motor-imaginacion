"""
Motor de Imaginación — Generador autónomo de sueños CPPN.

Genera una o varias imágenes (PNG/PGM) a partir de una red CPPN
(Compositional Pattern Producing Network) con activaciones compuestas
y selección estocástica por neurona.

Uso:
    python scripts/generate_gallery.py                       # 1 sueño PNG, 256x256
    python scripts/generate_gallery.py --count 8             # 8 sueños (workflow)
    python scripts/generate_gallery.py --format pgm          # retrocompat .pgm
    python scripts/generate_gallery.py --width 512 --height 512
"""
import argparse
import math
import os
import random
import sys
from datetime import datetime

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # Se permite .pgm puro sin Pillow


# ---------------------------------------------------------------------------
# Núcleo CPPN
# ---------------------------------------------------------------------------

def _softsign(v):
    return v / (1.0 + abs(v))


def _gauss(v):
    return math.exp(-v * v)


# Catálogo de funciones de activación (cumple lo prometido en el README).
ACTIVATIONS = [math.sin, math.cos, math.tanh, _gauss, _softsign]


def generate_cppn_image(width=256, height=256, seed=None):
    """Genera una imagen CPPN con `width x height` pixeles RGB y devuelve
    (pixels, entropy_shannon, metadata) donde:
      - pixels: list[list[tuple[int,int,int]]]
      - entropy_shannon: float
      - metadata: dict con seed y estadisticas basicas
    """
    if seed is not None:
        random.seed(seed)

    # Pesos de la red CPPN: 4 -> 8 -> 8 -> 3
    w1 = [[random.uniform(-2, 2) for _ in range(4)] for _ in range(8)]
    w2 = [[random.uniform(-2, 2) for _ in range(8)] for _ in range(8)]
    w3 = [[random.uniform(-2, 2) for _ in range(8)] for _ in range(3)]

    pixels = [[None] * width for _ in range(height)]
    histogram = [0] * 256

    # Selección determinista de funciones por capa (estable y reproducible).
    l1_funcs = [ACTIVATIONS[hash((0, i)) % len(ACTIVATIONS)] for i in range(8)]
    l2_funcs = [ACTIVATIONS[hash((1, i)) % len(ACTIVATIONS)] for i in range(8)]

    for py in range(height):
        y = (py / height) * 2.0 - 1.0
        for px in range(width):
            x = (px / width) * 2.0 - 1.0
            r = math.sqrt(x * x + y * y)

            inp = [x, y, r, 1.0]

            # Capa 1
            l1 = []
            for i, node_weights in enumerate(w1):
                val = sum(w * iv for w, iv in zip(node_weights, inp))
                try:
                    l1.append(l1_funcs[i](val))
                except Exception:
                    l1.append(0.0)

            # Capa 2
            l2 = []
            for i, node_weights in enumerate(w2):
                val = sum(w * iv for w, iv in zip(node_weights, l1))
                try:
                    l2.append(l2_funcs[i](val))
                except Exception:
                    l2.append(0.0)

            # Capa 3 (salida RGB)
            rgb = []
            for node_weights in w3:
                val = sum(w * iv for w, iv in zip(node_weights, l2))
                channel = int((math.tanh(val) + 1.0) * 0.5 * 255)
                rgb.append(max(0, min(255, channel)))

            pixels[py][px] = tuple(rgb)
            gray = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
            histogram[gray] += 1

    # Entropía de Shannon
    total = width * height
    entropy = 0.0
    for count in histogram:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    metadata = {
        "seed": seed,
        "width": width,
        "height": height,
        "entropy_shannon": entropy,
        "unique_grays": sum(1 for c in histogram if c > 0),
    }
    return pixels, entropy, metadata


# ---------------------------------------------------------------------------
# Exportadores
# ---------------------------------------------------------------------------

def save_pgm(pixels, filename, width, height):
    """Guarda en formato PGM (P2, ASCII). Retrocompatibilidad."""
    with open(filename, "w") as f:
        f.write("P2\n")
        f.write(f"{width} {height}\n")
        f.write("255\n")
        for row in pixels:
            row_strs = []
            for (r, g, b) in row:
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                row_strs.append(str(gray))
            f.write(" ".join(row_strs) + "\n")


def save_png(pixels, filename, width, height):
    """Guarda en formato PNG RGB. Requiere Pillow."""
    if Image is None:
        raise RuntimeError(
            "Pillow no está instalado. Ejecuta: pip install -r requirements.txt"
        )
    img = Image.new("RGB", (width, height))
    img.putdata([px for row in pixels for px in row])
    img.save(filename, format="PNG", optimize=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Generador autónomo de sueños CPPN."
    )
    p.add_argument("--count", type=int, default=1,
                   help="Número de sueños a generar (default: 1).")
    p.add_argument("--width", type=int, default=256,
                   help="Ancho en píxeles (default: 256).")
    p.add_argument("--height", type=int, default=256,
                   help="Alto en píxeles (default: 256).")
    p.add_argument("--out-dir", default="gallery",
                   help="Directorio de salida (default: gallery).")
    p.add_argument("--format", choices=("png", "pgm"), default="png",
                   help="Formato de imagen (default: png).")
    p.add_argument("--seed-base", type=int, default=None,
                   help="Seed base. Si se omite, usa timestamp.")
    p.add_argument("--update-index", action="store_true",
                   help="Reescribir gallery/INDEX.txt con todos los archivos.")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    base_seed = args.seed_base or int(datetime.now().timestamp())
    written = []
    entropies = []

    for i in range(args.count):
        # Cada sueño tiene seed determinista derivada del base + índice.
        seed = base_seed + i
        pixels, entropy, meta = generate_cppn_image(
            args.width, args.height, seed=seed
        )
        ext = "png" if args.format == "png" else "pgm"
        filename = f"dream_{seed}.{ext}"
        filepath = os.path.join(args.out_dir, filename)

        if args.format == "png":
            save_png(pixels, filepath, args.width, args.height)
        else:
            save_pgm(pixels, filepath, args.width, args.height)

        written.append(filename)
        entropies.append(entropy)
        print(
            f"  [+] {filename}  "
            f"entropy={entropy:.3f}  "
            f"unique_grays={meta['unique_grays']}"
        )

    avg_entropy = sum(entropies) / max(1, len(entropies))
    print(f"\n✓ {len(written)} sueños generados en '{args.out_dir}/'")
    print(f"  Entropía promedio: {avg_entropy:.3f}")

    if args.update_index:
        index_path = os.path.join(args.out_dir, "INDEX.txt")
        # Listar todos los archivos existentes (incluyendo legacy .pgm).
        existing = sorted(
            f for f in os.listdir(args.out_dir)
            if f.startswith("dream_") and (f.endswith(".png") or f.endswith(".pgm"))
        )
        with open(index_path, "w") as f:
            f.write("\n".join(existing) + "\n")
        print(f"  Índice actualizado: {index_path} ({len(existing)} archivos)")

    return 0 if all(e > 3.0 for e in entropies) else 1


if __name__ == "__main__":
    sys.exit(main())
