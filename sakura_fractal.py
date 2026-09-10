"""
SAKURA FRACTAL v2 — smoother curves, layered gradients, glowing stamens,
and a soft bloom finish.

Still a true IFS fractal: a blossom's petals each carry a smaller, rotated
copy of the same blossom at their tip, repeated for several generations.
No trunk, no branches.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from PIL import Image, ImageFilter, ImageChops, ImageEnhance

Path = mpath.Path

# ----------------------------------------------------------------------
# 1. Petal geometry — smooth, rounded sakura petal (no hard notch),
#    built from symmetric cubic beziers for a soft, silky contour
# ----------------------------------------------------------------------
def petal_local_path(length, width):
    verts = [
        (0.0, 0.06 * length),                                                       # base
        (-width, length * 0.30), (-width * 0.92, length * 0.72), (-width * 0.18, length * 0.97),  # left side up
        (-width * 0.055, length * 1.015), (width * 0.055, length * 1.015), (width * 0.18, length * 0.97),  # rounded tip arc
        (width * 0.92, length * 0.72), (width, length * 0.30), (0.0, 0.06 * length),  # right side down
    ]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CURVE4, Path.CURVE4, Path.CURVE4]
    # NOTE: CURVE4 groups must come in complete triples following the start
    return verts, codes


def _rot_transform(cx, cy, angle_deg):
    a = np.radians(angle_deg)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])

    def T(p):
        return tuple(rot.dot(np.array(p)) + np.array([cx, cy]))
    return T


def make_petal_path(cx, cy, length, width, angle_deg):
    T = _rot_transform(cx, cy, angle_deg)
    verts_local = [
        (0.0, 0.06 * length),
        (-width, length * 0.30), (-width * 0.92, length * 0.72), (-width * 0.18, length * 0.97),
        (-width * 0.055, length * 1.015), (width * 0.055, length * 1.015), (width * 0.18, length * 0.97),
        (width * 0.92, length * 0.72), (width, length * 0.30), (0.0, 0.06 * length),
    ]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CURVE4, Path.CURVE4, Path.CURVE4]
    verts = [T(p) for p in verts_local]
    return Path(verts, codes)


def add_petal(ax, cx, cy, length, width, angle_deg, facecolor, alpha, zorder,
              edgecolor=None, lw=0.0):
    path = make_petal_path(cx, cy, length, width, angle_deg)
    patch = mpatches.PathPatch(path, facecolor=facecolor, edgecolor=edgecolor,
                                linewidth=lw, alpha=alpha, zorder=zorder,
                                joinstyle='round', capstyle='round',
                                antialiased=True)
    ax.add_patch(patch)
    return path


# ----------------------------------------------------------------------
# 2. Colour palette — soft pastel gradient, deep rose core -> blush edge
# ----------------------------------------------------------------------
CORE_DEEP    = "#c81457"   # deep rose (petal base, innermost generation)
CORE_LIGHT   = "#ff9dbd"   # lighter rose (petal edge, innermost generation)
MID_DEEP     = "#e8558c"
MID_LIGHT    = "#ffc3d8"
OUTER_DEEP   = "#f593b4"
OUTER_LIGHT  = "#ffe6ef"
STAMEN_CORE  = "#fff3c4"
STAMEN_EDGE  = "#ffb94d"
SOFT_OUTLINE = "#ffffff"

deep_cmap  = mcolors.LinearSegmentedColormap.from_list("deep",  [CORE_DEEP, MID_DEEP, OUTER_DEEP])
light_cmap = mcolors.LinearSegmentedColormap.from_list("light", [CORE_LIGHT, MID_LIGHT, OUTER_LIGHT])


def depth_colors(depth, max_depth):
    t = depth / max(max_depth, 1)
    return deep_cmap(t), light_cmap(t)


# ----------------------------------------------------------------------
# 3. Recursive blossom — each petal is now TWO nested shapes (a soft pale
#    outer petal + a deeper-toned inner petal) which reads as a smooth
#    gradient from base to tip without needing per-pixel shading
# ----------------------------------------------------------------------
def draw_blossom(ax, cx, cy, size, angle_offset, depth, max_depth,
                  num_petals=5, shrink=0.46, twist=15.0, reach=1.12, glow_halo=True):
    deep, light = depth_colors(depth, max_depth)
    fade = 1.0 - 0.05 * depth
    width = size * 0.26

    # soft halo glow behind the blossom (cheap concentric fade, adds a
    # dreamy soft-focus backdrop on a solid background). Skipped for the
    # transparent cutout since translucent light-on-nothing reads as a
    # muddy smudge once placed on a dark shirt.
    if glow_halo:
        for r_mult, a in ((1.05, 0.05), (0.75, 0.06), (0.5, 0.05)):
            ax.add_patch(mpatches.Circle((cx, cy), size * r_mult, facecolor=light,
                                          edgecolor=None, alpha=a * fade,
                                          zorder=depth * 3 - 0.5, linewidth=0))

    for i in range(num_petals):
        petal_angle = angle_offset + i * (360.0 / num_petals)

        # outer pale petal (slightly larger) -> reads as the light edge
        add_petal(ax, cx, cy, size, width, petal_angle,
                   facecolor=light, alpha=0.95 * fade, zorder=depth * 3,
                   edgecolor=SOFT_OUTLINE, lw=max(0.10, 0.55 - 0.08 * depth))
        # inner deep petal (smaller, base-anchored) -> reads as gradient
        add_petal(ax, cx, cy, size * 0.62, width * 0.72, petal_angle,
                   facecolor=deep, alpha=0.85 * fade, zorder=depth * 3 + 0.2)
        # faint centre vein for a touch of botanical realism
        a = np.radians(petal_angle)
        vx = cx - size * 0.85 * np.sin(a)
        vy = cy + size * 0.85 * np.cos(a)
        ax.plot([cx, vx], [cy, vy], color=SOFT_OUTLINE, lw=0.25, alpha=0.35 * fade,
                 zorder=depth * 3 + 0.3, solid_capstyle='round')

        if depth < max_depth:
            tip_x = cx - size * reach * np.sin(a)
            tip_y = cy + size * reach * np.cos(a)
            child_twist = twist if depth % 2 == 0 else -twist
            draw_blossom(ax, tip_x, tip_y, size * shrink,
                         petal_angle + child_twist, depth + 1, max_depth,
                         num_petals=num_petals, shrink=shrink, twist=twist,
                         reach=reach, glow_halo=glow_halo)

    # glowing stamen cluster: layered soft circles + fine radiating threads
    stamen_r = size * 0.11
    for r_mult, col, a in ((2.0, STAMEN_EDGE, 0.18), (1.35, STAMEN_EDGE, 0.55), (0.7, STAMEN_CORE, 0.95)):
        ax.add_patch(mpatches.Circle((cx, cy), stamen_r * r_mult, facecolor=col,
                                      edgecolor=None, alpha=a * fade,
                                      zorder=depth * 3 + 0.6, linewidth=0))
    seed = abs(depth * 97 + int(cx * 131) + int(cy * 71)) % (2**31 - 1)
    rng = np.random.default_rng(seed)
    for _ in range(7):
        ang = rng.uniform(0, 2 * np.pi)
        r = stamen_r * rng.uniform(1.5, 2.6)
        ex, ey = cx + r * np.cos(ang), cy + r * np.sin(ang)
        ax.plot([cx, ex], [cy, ey], color=STAMEN_EDGE,
                 lw=max(0.25, 0.7 - 0.1 * depth), alpha=0.8 * fade,
                 zorder=depth * 3 + 0.6, solid_capstyle='round')
        ax.add_patch(mpatches.Circle((ex, ey), stamen_r * 0.22, facecolor=STAMEN_CORE,
                                      edgecolor=None, alpha=0.9 * fade, zorder=depth * 3 + 0.7))


# ----------------------------------------------------------------------
# 4. Compose + soft-focus post-processing for a smoother, dreamier finish
# ----------------------------------------------------------------------
def render(max_depth=4, num_petals=5, shrink=0.46, twist=15.0, reach=1.12,
           transparent=False, filename="sakura_fractal", supersample=2):
    base_dpi = 300
    fig, ax = plt.subplots(figsize=(10, 10), dpi=base_dpi * supersample)
    ax.set_aspect('equal')
    ax.axis('off')

    if not transparent:
        n = 700
        xx, yy = np.meshgrid(np.linspace(-1, 1, n), np.linspace(-1, 1, n))
        rr = np.sqrt(xx ** 2 + yy ** 2)
        bg = np.clip(1 - rr ** 1.3 * 0.6, 0, 1)
        bg_cmap = mcolors.LinearSegmentedColormap.from_list(
            "paper", ["#fffaf7", "#fdeaf0", "#fbdfe9"]
        )
        ax.imshow(bg, extent=[-2.6, 2.6, -2.6, 2.6], cmap=bg_cmap,
                  origin='lower', zorder=-10, interpolation='bicubic')

    draw_blossom(ax, 0, 0, 1.0, 90, 0, max_depth,
                 num_petals=num_petals, shrink=shrink, twist=twist, reach=reach,
                 glow_halo=not transparent)

    lim = 2.1
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    tmp_png = f"/home/claude/_tmp_{filename}.png"
    fig.savefig(tmp_png, dpi=base_dpi * supersample, transparent=transparent,
                bbox_inches='tight', pad_inches=0.15)
    fig.savefig(f"/mnt/user-data/outputs/{filename}.svg",
                transparent=transparent, bbox_inches='tight', pad_inches=0.15)
    plt.close(fig)

    # ---- post-process: downsample with high-quality filtering ----
    img = Image.open(tmp_png).convert("RGBA")
    target_w = 3000
    target_h = int(img.height * target_w / img.width)
    img = img.resize((target_w, target_h), Image.LANCZOS)

    if not transparent:
        # bloom: blur a brightened copy and screen-blend it back on top.
        # Safe here because the canvas is fully opaque (no alpha edges
        # to bleed black into).
        rgb = img.convert("RGB")
        bright = ImageEnhance.Brightness(rgb).enhance(1.35)
        blurred = bright.filter(ImageFilter.GaussianBlur(radius=target_w * 0.006))
        screened = ImageChops.screen(rgb, blurred)
        blended_rgb = Image.blend(rgb, screened, 0.35)
        r, g, b = blended_rgb.split()
        final = Image.merge("RGBA", (r, g, b, img.split()[3]))
    else:
        # transparent cutout: only sharpen colour/contrast, no blur —
        # blurring here would bleed the (undefined) RGB of fully
        # transparent pixels into the visible edge as a dark fringe.
        final = img

    final = ImageEnhance.Color(final).enhance(1.08)
    final = ImageEnhance.Contrast(final).enhance(1.04)

    final.save(f"/mnt/user-data/outputs/{filename}.png")
    print(f"Saved {filename}.png ({final.size[0]}x{final.size[1]}) and {filename}.svg")


if __name__ == "__main__":
    PARAMS = dict(max_depth=4, num_petals=5, shrink=0.46, twist=15.0, reach=1.12)
    render(**PARAMS, transparent=False, filename="sakura_fractal_paper")
    render(**PARAMS, transparent=True, filename="sakura_fractal_transparent")
