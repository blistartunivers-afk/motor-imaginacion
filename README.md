# Motor de Imaginación 🌌

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Autonomous Dreamer](https://github.com/blistartunivers-afk/motor-imaginacion/actions/workflows/dream-gallery.yml/badge.svg)](https://github.com/blistartunivers-afk/motor-imaginacion/actions)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen)](https://blistartunivers-afk.github.io/motor-imaginacion/)

Un explorador visual autónomo de patrones neuronales generativos en tiempo real, basado en **CPPN (Compositional Pattern Producing Networks)** con pesos aleatorios no entrenados y funciones de activación estocásticas.

---

## 🔬 Fundamento Matemático

El sistema explota el **Teorema de Aproximación Universal** utilizando redes neuronales artificiales no entrenadas con activaciones compuestas:

$$f_k(x, y, r) = \\tanh(W_4 \\cdot \\phi(W_3 \\cdot \\phi(W_2 \\cdot \\phi(W_1 \\cdot [x, y, r, 1]))))$$

Donde:
- $x, y \\in [-1, 1]$ son coordenadas cartesianas normalizadas.
- $r = \\sqrt{x^2 + y^2}$ introduce simetría radial.
- $\\phi_i \\in \\{\\sin, \\cos, \\tanh, \\text{gauss}, \\text{softsign}\\}$ se selecciona estocásticamente por neurona.

---

## 🛠️ Autonomía del Proyecto

Este repositorio funciona de manera **100% autodependiente**:
1. **Página Interactiva (Canvas2D):** Renderizado en tiempo real en navegador sin dependencias de servidor.
2. **Generador Autónomo (GitHub Actions):** Tarea programada que ejecuta la simulación, analiza la entropía de Shannon y actualiza la galería semanalmente.
3. **Tests de Diversidad:** Suite de pruebas continuas que asegura que la entropía visual se mantenga por encima de los umbrales de variedad aceptables.

---

## 📜 Licencia

MIT License © 2026 blistartunivers-afk
