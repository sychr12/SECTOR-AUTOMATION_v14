"""
Script para substituir literais de cores por constantes AppTheme.
Roda recursivamente em `app/` e edita arquivos .py (fazer backup .bak).
"""
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'app'
HEX_RE = re.compile(r"#([0-9a-fA-F]{6})")

# Categorias
BLUE = {"#2563eb","#3b82f6","#1d4ed8","#0891b2","#06b6d4","#38bdf8","#60a5fa","#2563cb","#2563eb"}
GREEN = {"#22c55e","#16a34a","#10b981","#059669"}
DANGER = {"#ef4444","#dc2626","#b91c1c"}
MUTED = {"#6b7280","#94a3b8","#64748b","#9ca3af"}
LIGHTS = {"#ffffff","#f9fafb","#f3f4f6","#e5e7eb","#f0fdf4"}
DARKS = {"#0f172a","#111827","#020617","#0b1220","#121212","#1e293b","#111c2e","#1a2332","#1e2d42","#242424","#2f2f2f","#1f2937","#1f2933","#273449"}

def replace_colors(text):
    # Ensure AppTheme import
    if 'from theme import AppTheme' not in text and 'import AppTheme' not in text:
        # insert after other imports
        parts = text.splitlines()
        insert_at = 0
        for i,l in enumerate(parts):
            if l.startswith('import') or l.startswith('from'):
                insert_at = i+1
        parts.insert(insert_at, 'from theme import AppTheme')
        text = '\n'.join(parts)

    # Replace text_color assignments (single/double quotes)
    text = re.sub(r'(text_color\s*=\s*)(["\'])(#(?:[0-9a-fA-F]{6}))(\2)', r"\1AppTheme.TXT_MAIN", text)

    # Replace fg_color for known categories
    for hx in BLUE:
        pattern = re.compile(r'(fg_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_PRIMARY", text)
        pattern = re.compile(r'(hover_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_PRIMARY_HOVER", text)

    for hx in GREEN:
        pattern = re.compile(r'(fg_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_SUCCESS", text)
        pattern = re.compile(r'(hover_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_SUCCESS_HOVER", text)

    for hx in DANGER:
        pattern = re.compile(r'(fg_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_DANGER", text)
        pattern = re.compile(r'(hover_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.BTN_DANGER_HOVER", text)

    # Muted text -> TXT_MUTED
    for hx in MUTED.union(LIGHTS):
        pattern = re.compile(r'(text_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        text = pattern.sub(r"\1AppTheme.TXT_MAIN", text)

    # Replace many background/dark hexes used as frames or self.configure -> BG_APP or BG_CARD
    # self.configure(fg_color=...)
    for hx in list(DARKS) + list(LIGHTS):
        pattern = re.compile(r'(self\.configure\(.*?fg_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])(.*?\))', re.DOTALL)
        text = pattern.sub(r"\1AppTheme.BG_APP\5", text)

    # CTkFrame(..., fg_color=hex) -> AppTheme.BG_CARD
    for hx in list(DARKS) + list(LIGHTS):
        pattern = re.compile(r'(fg_color\s*=\s*)(["\'])(' + re.escape(hx) + r')(["\'])')
        # Avoid overwriting buttons handled above by checking if BTN_* not already substituted
        text = pattern.sub(r"\1AppTheme.BG_CARD", text)

    # style.configure replacements common keys
    text = re.sub(r"background\s*=\s*([\"'])#(?:[0-9a-fA-F]{6})\1", "background=AppTheme.BG_CARD", text)
    text = re.sub(r"foreground\s*=\s*([\"'])#(?:[0-9a-fA-F]{6})\1", "foreground=AppTheme.TXT_MAIN", text)
    text = re.sub(r"fieldbackground\s*=\s*([\"'])#(?:[0-9a-fA-F]{6})\1", "fieldbackground=AppTheme.BG_CARD", text)
    text = re.sub(r"background=\[\(\'selected\',\s*#(?:[0-9a-fA-F]{6})\)\]", "background=[('selected', AppTheme.BTN_PRIMARY)]", text)
    text = re.sub(r"foreground=\[\(\'selected\',\s*#(?:[0-9a-fA-F]{6})\)\]", "foreground=[('selected', AppTheme.TXT_MAIN)]", text)

    return text


def process_file(path: Path):
    s = path.read_text(encoding='utf-8')
    if not HEX_RE.search(s):
        return False
    backup = path.with_suffix(path.suffix + '.bak')
    backup.write_text(s, encoding='utf-8')
    new = replace_colors(s)
    path.write_text(new, encoding='utf-8')
    return True

if __name__ == '__main__':
    changed = []
    for p in ROOT.rglob('*.py'):
        try:
            if process_file(p):
                changed.append(str(p.relative_to(ROOT.parent)))
        except Exception as e:
            print('Erro processando', p, e)
    print('Arquivos alterados:', len(changed))
    for c in changed:
        print('-', c)
