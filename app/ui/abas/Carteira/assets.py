# -*- coding: utf-8 -*-
"""
assets.py — Resolução portátil de assets (imagens, fontes).
Funciona em qualquer máquina, independente do drive/usuário.

Ordem de busca:
  1. Variáveis de ambiente (CARTEIRA_IMG_DIR, CARTEIRA_FONT_PATH)
  2. Pasta 'images/' relativa ao executável / __file__
  3. Pasta 'images/' na raiz do projeto (subindo até 4 níveis)
  4. Paths hardcoded legados (Q:\...)
  5. Fallback: gera imagem placeholder em memória (nunca trava)
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union, Tuple, List

from PIL import Image, ImageDraw, ImageFont


# ── Constantes ───────────────────────────────────────────────────────────────
FRENTE_NAMES: Tuple[str, ...] = ("frente.png", "FRENTE.png", "frente.jpg")
VERSO_NAMES: Tuple[str, ...] = ("verso.png", "VERSO.png", "verso.jpg")
FONT_NAMES: Tuple[str, ...] = ("Roboto-Regular.ttf", "Roboto.ttf", "Arial.ttf")

# ── Paths legados (máquinas originais) ───────────────────────────────────────
_LEGACY_IMG_DIRS = [
    r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images",
    r"C:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images",
    r"D:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images",
]

_LEGACY_FONT_PATHS = [
    r"Q:\ARQUIVOS CPCPR\fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf",
    r"C:\ARQUIVOS CPCPR\fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf",
    r"D:\ARQUIVOS CPCPR\fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf",
]


class AssetNotFoundError(Exception):
    """Exceção customizada para assets não encontrados (opcional)"""
    pass


def _exe_dir() -> Path:
    """Diretório base do executável ou do script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    here = Path(__file__).resolve().parent
    return here


def _candidate_img_dirs() -> List[Path]:
    """Lista diretórios candidatos com deduplicação."""
    candidates: List[Path] = []
    seen = set()

    # 1. Variável de ambiente
    env = os.environ.get("CARTEIRA_IMG_DIR")
    if env:
        path = Path(env).resolve()
        if str(path) not in seen:
            candidates.append(path)
            seen.add(str(path))

    # 2. Busca relativa ao executável
    base = _exe_dir()
    for level in range(5):
        for subdir in ("images", "assets", "resources/images", "static/images"):
            candidate = base / subdir
            if str(candidate) not in seen:
                candidates.append(candidate)
                seen.add(str(candidate))
        base = base.parent

    # 3. Paths legados
    for legacy in _LEGACY_IMG_DIRS:
        path = Path(legacy).resolve()
        if str(path) not in seen:
            candidates.append(path)
            seen.add(str(path))

    return candidates


@lru_cache(maxsize=1)
def _find_img_dir() -> Optional[Path]:
    """Encontra o diretório de imagens."""
    for d in _candidate_img_dirs():
        if d.is_dir():
            # Verifica se tem pelo menos uma das imagens
            for name in FRENTE_NAMES + VERSO_NAMES:
                if (d / name).exists():
                    return d
    return None


def _find_image(names: List[str]) -> Optional[Path]:
    """Busca imagem ignorando case."""
    img_dir = _find_img_dir()
    if img_dir:
        # Primeiro busca exato
        for name in names:
            p = img_dir / name
            if p.exists():
                return p

        # Depois busca case insensitive
        try:
            for file in img_dir.iterdir():
                if file.is_file():
                    file_lower = file.name.lower()
                    if any(file_lower == name.lower() for name in names):
                        return file
        except PermissionError:
            pass

    # Busca em variáveis de ambiente
    for env_key in ("CARTEIRA_IMG_FRENTE", "CARTEIRA_IMG_VERSO"):
        env_val = os.environ.get(env_key)
        if env_val and Path(env_val).exists():
            return Path(env_val)

    return None


@lru_cache(maxsize=1)
def get_img_frente() -> Optional[str]:
    """Retorna caminho da imagem frente."""
    p = _find_image(list(FRENTE_NAMES))
    return str(p) if p else None


@lru_cache(maxsize=1)
def get_img_verso() -> Optional[str]:
    """Retorna caminho da imagem verso."""
    p = _find_image(list(VERSO_NAMES))
    return str(p) if p else None


@lru_cache(maxsize=1)
def get_font_path() -> Optional[str]:
    """Retorna caminho da fonte."""
    # 1. Variável de ambiente
    env = os.environ.get("CARTEIRA_FONT_PATH")
    if env and Path(env).exists():
        return env

    # 2. Relativo ao projeto
    base = _exe_dir()
    for _ in range(5):
        for name in FONT_NAMES:
            for sub in ("fonts", "assets", "resources", "."):
                p = base / sub / name
                if p.exists():
                    return str(p)
        base = base.parent

    # 3. Paths legados
    for p in _LEGACY_FONT_PATHS:
        if Path(p).exists():
            return p

    # 4. Fontes do sistema (Windows)
    win_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in FONT_NAMES:
        p = win_fonts / name
        if p.exists():
            return str(p)

    # 5. Fontes do sistema (Linux/Mac)
    for sys_dir in ["/usr/share/fonts", "/usr/local/share/fonts",
                    os.path.expanduser("~/.fonts"),
                    "/Library/Fonts", "/System/Library/Fonts"]:
        for name in FONT_NAMES:
            p = Path(sys_dir) / name
            if p.exists():
                return str(p)

    return None


def assets_status(verbose: bool = False) -> dict:
    """Retorna status de todos os assets para diagnóstico."""
    status = {
        "img_frente": get_img_frente(),
        "img_verso": get_img_verso(),
        "font_path": get_font_path(),
        "img_dir_found": str(_find_img_dir()) if _find_img_dir() else None,
    }

    if verbose:
        # Adiciona informações de debug
        status.update({
            "candidate_dirs": [str(d) for d in _candidate_img_dirs()[:5]],
            "exe_dir": str(_exe_dir()),
            "sys_frozen": getattr(sys, "frozen", False),
        })

    return status


def make_placeholder_image(
    width: int = 420,
    height: int = 240,
    label: str = "SEM IMAGEM",
    bg_color: Union[str, Tuple[int, int, int]] = (220, 220, 230),
    border_color: Union[str, Tuple[int, int, int]] = (150, 150, 170),
    text_color: Union[str, Tuple[int, int, int]] = (120, 120, 140)
) -> Image.Image:
    """
    Gera imagem placeholder quando o arquivo real não é encontrado.

    Args:
        width: Largura da imagem
        height: Altura da imagem
        label: Texto a ser exibido
        bg_color: Cor de fundo
        border_color: Cor da borda
        text_color: Cor do texto
    """
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Desenha borda
    draw.rectangle(
        [2, 2, width - 3, height - 3],
        outline=border_color,
        width=2
    )

    # Tenta usar fonte com tamanho dinâmico
    font_size = min(width, height) // 10
    font = None
    try:
        font = get_pil_font(font_size)
    except Exception:
        pass

    # Calcula posição central
    if font:
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), label, fill=text_color, font=font)
    else:
        draw.text((width // 2, height // 2), label, fill=text_color, anchor="mm")

    return img


def open_image(
    path: Optional[str],
    fallback_label: str = "SEM IMAGEM",
    resize_to: Optional[Tuple[int, int]] = None,
    convert_mode: Optional[str] = None
) -> Image.Image:
    """
    Abre imagem do path ou retorna placeholder. Nunca lança exceção.

    Args:
        path: Caminho da imagem
        fallback_label: Texto do placeholder
        resize_to: (width, height) para redimensionar
        convert_mode: Modo de conversão ('RGB', 'RGBA', etc)
    """
    img = None

    if path and os.path.exists(path):
        try:
            img = Image.open(path)
        except Exception:
            pass

    if img is None:
        img = make_placeholder_image(label=fallback_label)

    # Aplica conversão se necessário
    if convert_mode and img.mode != convert_mode:
        img = img.convert(convert_mode)

    # Aplica redimensionamento
    if resize_to:
        img = img.resize(resize_to, Image.Resampling.LANCZOS)

    return img


def get_pil_font(size: int) -> Optional[Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]]:
    """Retorna ImageFont com o tamanho pedido, com fallback seguro."""
    font_path = get_font_path()
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass

    # Fallback: fonte bitmap padrão do PIL
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def reload_assets() -> dict:
    """Força recarregamento de todos os assets (útil para desenvolvimento)."""
    _find_img_dir.cache_clear()
    get_img_frente.cache_clear()
    get_img_verso.cache_clear()
    get_font_path.cache_clear()

    # Recarrega e retorna novo status
    return assets_status(verbose=True)