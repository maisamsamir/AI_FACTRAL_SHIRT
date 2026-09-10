# Sakura Fractal — Recursive Cherry Blossom Mandala

A generative art piece that renders a Japanese sakura (cherry blossom) inspired
fractal, designed to double as print-ready artwork (e.g. for apparel).

![Sakura Fractal on a shirt](shirt_mockup.jpeg)

## Fractal Type Implemented

**Custom Iterated Function System (IFS) — "blossom-of-blossoms" fractal.**

A single blossom is defined as *N* petals arranged radially around a center.
At the tip of every petal, a smaller, rotated copy of the *same* blossom is
placed (scaled down by a contraction factor `< 1`), and this rule is applied
recursively for several generations. This is the same self-similarity
principle behind classic fractals like the Sierpinski Triangle or Barnsley
Fern, applied to an original petal-based transformation rather than a
triangle or fern-leaf map — each "generation" is a smaller flower nested at
every petal tip of the flower before it, so the whole composition is
built entirely from one repeated geometric rule (no tree/branch structure
is used).

Each petal is additionally rendered as two nested Bezier shapes (a pale
outer petal + a deeper-toned inner petal) to fake a smooth colour gradient,
and colours shift gradually across generations from a deep rose core to a
pale blush edge.

## Tools, Languages, and Libraries Used

- **Language:** Python 3
- **Libraries:**
  - [`matplotlib`](https://matplotlib.org/) — vector path/Bezier rendering (`matplotlib.path`, `matplotlib.patches`), colour interpolation, and figure export (PNG + SVG)
  - [`numpy`](https://numpy.org/) — geometry/rotation math and randomised stamen placement
  - [`Pillow (PIL)`](https://python-pillow.org/) — post-processing (high-quality resizing, soft bloom/glow effect, colour/contrast enhancement)

## Setup & Run Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/sakura-fractal.git
   cd sakura-fractal
   ```
2. Install dependencies:
   ```bash
   pip install matplotlib numpy pillow
   ```
3. Run the script:
   ```bash
   python3 sakura_fractal.py
   ```
4. Output files are generated in the same folder (or edit the `render()`
   calls at the bottom of `sakura_fractal.py` to change the output path):
   - `sakura_fractal_paper.png` / `.svg` — blossom on a soft paper-toned background
   - `sakura_fractal_transparent.png` / `.svg` — transparent background, ready for printing on any colour fabric

### Adjustable parameters

At the bottom of `sakura_fractal.py`:

```python
PARAMS = dict(max_depth=4, num_petals=5, shrink=0.46, twist=15.0, reach=1.12)
```

| Parameter | Effect |
|---|---|
| `max_depth` | Number of recursive generations (higher = more detail, slower render) |
| `num_petals` | Petals per blossom |
| `shrink` | Scale factor applied to each child generation |
| `twist` | Rotation offset (degrees) applied to each child generation |
| `reach` | How far past the petal tip the next generation is placed |

## Output Preview

| Paper background | Transparent (shirt-ready) |
|---|---|
| ![paper version](sakura_fractal_paper.png) | ![transparent version](sakura_fractal_transparent.png) |

## Author

**Maisam Samir**
Registration Number: **577362**
