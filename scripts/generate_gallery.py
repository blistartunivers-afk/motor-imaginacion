import math
import random
import os
from datetime import datetime

def generate_cppn_image(width=256, height=256, seed=None):
    if seed is not None:
        random.seed(seed)
    
    # Pesos de la red CPPN de 3 capas
    w1 = [[random.uniform(-2, 2) for _ in range(4)] for _ in range(8)]
    w2 = [[random.uniform(-2, 2) for _ in range(8)] for _ in range(8)]
    w3 = [[random.uniform(-2, 2) for _ in range(8)] for _ in range(3)]
    
    funcs = [math.sin, math.cos, math.tanh, lambda v: math.exp(-v*v)]
    
    pixels = [[None] * width for _ in range(height)]
    histogram = [0] * 256
    
    for py in range(height):
        y = (py / height) * 2.0 - 1.0
        for px in range(width):
            x = (px / width) * 2.0 - 1.0
            r = math.sqrt(x*x + y*y)
            
            inp = [x, y, r, 1.0]
            l1 = []
            for node_weights in w1:
                val = sum(w * i for w, i in zip(node_weights, inp))
                fn = funcs[hash((py, px, 0)) % 4]
                try:
                    l1.append(fn(val))
                except Exception:
                    l1.append(0.0)
            
            l2 = []
            for node_weights in w2:
                val = sum(w * i for w, i in zip(node_weights, l1))
                fn = funcs[hash((py, px, 1)) % 4]
                try:
                    l2.append(fn(val))
                except Exception:
                    l2.append(0.0)
            
            rgb = []
            for node_weights in w3:
                val = sum(w * i for w, i in zip(node_weights, l2))
                channel = int((math.tanh(val) + 1.0) * 0.5 * 255)
                rgb.append(max(0, min(255, channel)))
            
            pixels[py][px] = tuple(rgb)
            gray = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
            histogram[gray] += 1

    # Entropia de Shannon
    total_pixels = width * height
    entropy = 0.0
    for count in histogram:
        if count > 0:
            p = count / total_pixels
            entropy -= p * math.log2(p)

    return pixels, entropy

def save_pgm(pixels, filename, width, height):
    with open(filename, 'w') as f:
        f.write("P2\n")
        f.write(f"{width} {height}\n")
        f.write("255\n")
        for row in pixels:
            row_strs = []
            for (r, g, b) in row:
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                row_strs.append(str(gray))
            f.write(" ".join(row_strs) + "\n")

if __name__ == "__main__":
    os.makedirs("gallery", exist_ok=True)
    seed = int(datetime.now().timestamp())
    pixels, entropy = generate_cppn_image(256, 256, seed=seed)
    filename = f"gallery/dream_{seed}.pgm"
    save_pgm(pixels, filename, 256, 256)
    print(f"Generada {filename} con entropia = {entropy:.2f} bits")
    
    # Actualizar indice para el frontend
    gallery_files = sorted([f for f in os.listdir("gallery") if f.endswith(".pgm")])
    with open("gallery/INDEX.txt", "w") as f:
        f.write("\n".join(gallery_files))
    print(f"Indice con {len(gallery_files)} suenos")
