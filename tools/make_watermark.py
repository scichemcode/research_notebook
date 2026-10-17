"""Render the equation watermark tile used as the notebook background.

Usage:  python tools/make_watermark.py      (writes eq-watermark.svg at the repo root)

The SVG is used as a CSS mask, so only its shape matters; the page supplies the
colour and opacity, which keeps it correct in light and dark mode. Edit EQUATIONS
and re-run to change what appears. Equations use matplotlib mathtext (a LaTeX subset).
"""
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "eq-watermark.svg"
W, H, DPI = 1600, 1100, 100          # tile size in px
MARGIN, ROWS = 36, 8                 # keep glyphs off the edges so the tile repeats cleanly

EQUATIONS = [
    # Quantum mechanics / electronic structure
    r"i\hbar\,\frac{\partial}{\partial t}\Psi(\mathbf{r},t)=\hat{H}\,\Psi(\mathbf{r},t)",
    r"\hat{H}\psi=E\psi",
    r"[\hat{x},\hat{p}\,]=i\hbar",
    r"\Delta x\,\Delta p\geq\frac{\hbar}{2}",
    r"\hat{F}\,\phi_i=\varepsilon_i\,\phi_i",
    r"E[\rho]=T_s[\rho]+\int v(\mathbf{r})\rho(\mathbf{r})\,d\mathbf{r}+J[\rho]+E_{xc}[\rho]",
    r"\langle\psi|\hat{A}|\psi\rangle",
    r"|\Psi\rangle=\sum_n c_n|\phi_n\rangle",
    r"\hat{H}=-\sum_i\frac{\hbar^2}{2m}\nabla_i^2+V(\mathbf{r})",
    # Statistical mechanics / thermodynamics
    r"Z=\sum_i e^{-\beta E_i}",
    r"F=-k_BT\ln Z",
    r"S=k_B\ln\Omega",
    r"\langle A\rangle=\mathrm{Tr}(\hat{\rho}\hat{A})",
    r"\langle e^{-\beta W}\rangle=e^{-\beta\Delta F}",
    r"\Delta G=-RT\ln K",
    r"p_i=\frac{e^{-\beta E_i}}{Z}",
    r"\beta=\frac{1}{k_BT}",
    r"\Delta F=-k_BT\ln\langle e^{-\beta\Delta U}\rangle_0",
    # Molecular simulation
    r"m_i\ddot{\mathbf{r}}_i=-\nabla_i U(\mathbf{r}^N)",
    r"V_{LJ}(r)=4\varepsilon\left[\left(\frac{\sigma}{r}\right)^{12}-\left(\frac{\sigma}{r}\right)^{6}\right]",
    r"\mathbf{r}(t+\Delta t)=2\mathbf{r}(t)-\mathbf{r}(t-\Delta t)+\mathbf{a}(t)\Delta t^2",
    r"P_{acc}=\min\left(1,e^{-\beta\Delta U}\right)",
    r"D=\lim_{t\to\infty}\frac{\langle|\mathbf{r}(t)-\mathbf{r}(0)|^2\rangle}{6t}",
    r"g(r)=\frac{V}{N^2}\left\langle\sum_i\sum_{j\neq i}\delta(r-r_{ij})\right\rangle",
    r"\mathcal{H}=\sum_i\frac{\mathbf{p}_i^2}{2m_i}+U(\mathbf{q})",
    r"\dot{q}=\frac{\partial\mathcal{H}}{\partial p},\;\dot{p}=-\frac{\partial\mathcal{H}}{\partial q}",
]


def main(seed=7):
    rng = random.Random(seed)
    plt.rcParams.update({"mathtext.fontset": "cm", "svg.fonttype": "path"})
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_alpha(0)
    renderer = fig.canvas.get_renderer()

    # Measure every equation at a randomly chosen size.
    eqs = EQUATIONS[:]
    rng.shuffle(eqs)
    items = []
    for eq in eqs:
        size = rng.choice([17, 19, 21, 23, 26])
        t = fig.text(0, 0, f"${eq}$", fontsize=size)
        bb = t.get_window_extent(renderer)
        t.remove()
        items.append((eq, size, bb.width, bb.height))

    # Greedily pack into rows, spreading the leftover space as gaps.
    usable = W - 2 * MARGIN
    rows, row, width = [], [], 0
    for it in items:
        if row and width + it[2] + 70 > usable:
            rows.append(row)
            row, width = [], 0
        row.append(it)
        width += it[2] + 70
    if row:
        rows.append(row)
    rows = rows[:ROWS]

    row_h = (H - 2 * MARGIN) / len(rows)
    for r, row in enumerate(rows):
        total = sum(it[2] for it in row)
        gap = (usable - total) / len(row)
        x = MARGIN + gap / 2 + rng.uniform(-gap / 3, gap / 3) * (0.5 if len(row) > 1 else 0)
        yc = MARGIN + row_h * (r + 0.5)
        for eq, size, w, h in row:
            jitter = rng.uniform(-row_h * 0.18, row_h * 0.18)
            y = H - (yc + jitter)  # figure coords grow upwards
            fig.text(x / W, y / H, f"${eq}$", fontsize=size, va="center", color="black")
            x += w + gap

    fig.savefig(OUT, format="svg", transparent=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {sum(map(len, rows))} equations)")


if __name__ == "__main__":
    main()
