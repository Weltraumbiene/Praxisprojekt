# core/css_checker.py
import tinycss2
import re

def parse_color(value: str):
    value = value.strip().lower()
    if value.startswith("#"):
        hex_color = value.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    rgb_match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", value)
    if rgb_match:
        return tuple(int(rgb_match.group(i)) for i in range(1, 4))

    raise ValueError(f"Unbekanntes Farbformat: {value}")

def relative_luminance(rgb):
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * to_linear(r) + 0.7152 * to_linear(g) + 0.0722 * to_linear(b)

def contrast_ratio(rgb1, rgb2):
    lum1 = relative_luminance(rgb1)
    lum2 = relative_luminance(rgb2)
    L1, L2 = max(lum1, lum2), min(lum1, lum2)
    return (L1 + 0.05) / (L2 + 0.05)

def check_css_contrast(css: str) -> list[str]:
    errors = []

    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)
    for rule in rules:
        if rule.type != 'qualified-rule':
            continue

        declarations = tinycss2.parse_declaration_list(rule.content)
        color = None
        background = None

        for decl in declarations:
            if decl.type != 'declaration':
                continue
            name = decl.name.lower()
            value = "".join([token.serialize() for token in decl.value]).strip()

            if name == "color":
                color = value
            elif name in ("background-color", "background"):  # <– Erweiterung hier!
                background = value

        if color and background:
            try:
                rgb_fg = parse_color(color)
                rgb_bg = parse_color(background)
                ratio = contrast_ratio(rgb_fg, rgb_bg)

                if ratio < 4.5:
                    errors.append(
                        f"Niedriger Kontrast ({ratio:.2f}:1) zwischen Textfarbe {color} und Hintergrundfarbe {background}"
                    )
            except Exception as e:
                errors.append(f"Fehler bei Farben {color} / {background}: {str(e)}")

    return errors

