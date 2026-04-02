# -*- coding: utf-8 -*-
"""
assets.py — Resolução portátil de assets (imagens, fontes).

Estrutura real da tabela Imagens (banco bancocpp):
    Id          INT IDENTITY PK
    NomeImagem  VARCHAR(100)   → 'frente.png' ou 'verso.png'
    Imagem      VARBINARY(MAX) → conteúdo binário da imagem
    TipoArquivo VARCHAR(50)    → 'image/png', etc.
    DataCadastro DATETIME

Ordem de busca das imagens frente/verso:
  1. Banco de dados SQL Server (bancocpp.dbo.Imagens) ← PRIORIDADE
  2. Variáveis de ambiente (CARTEIRA_IMG_DIR)
  3. Pasta 'images/' relativa ao executável / __file__
  4. Paths hardcoded legados (Q:\...)
  5. Fallback: placeholder gerado em memória (nunca trava)
"""
from __future__ import annotations

import os
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union, Tuple, List

from PIL import Image, ImageDraw, ImageFont


# ── Constantes ───────────────────────────────────────────────────────────────
FRENTE_NAMES: Tuple[str, ...] = ("frente.png", "FRENTE.png", "frente.jpg")
VERSO_NAMES: Tuple[str, ...]  = ("verso.png",  "VERSO.png",  "verso.jpg")
FONT_NAMES:  Tuple[str, ...]  = ("Roboto-Regular.ttf", "Roboto.ttf", "Arial.ttf")

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


# ── Busca no Banco de Dados ───────────────────────────────────────────────────

def _buscar_imagens_do_banco() -> Tuple[Optional[bytes], Optional[bytes]]:
    """
    Busca as imagens frente e verso na tabela bancocpp.dbo.Imagens.

    Estrutura da tabela:
        NomeImagem  VARCHAR(100)   → 'frente.png' | 'verso.png'
        Imagem      VARBINARY(MAX) → bytes da imagem

    Retorna:
        (frente_bytes, verso_bytes) — qualquer um pode ser None.
    """
    try:
        from services.database import get_connection
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT NomeImagem, Imagem
                FROM   bancocpp.dbo.Imagens
                WHERE  NomeImagem IN ('frente.png', 'verso.png')
                   AND Imagem IS NOT NULL;
            """)
            rows = cursor.fetchall()
            cursor.close()
        finally:
            try:
                conn.close()
            except Exception:
                pass

        frente_bytes: Optional[bytes] = None
        verso_bytes:  Optional[bytes] = None

        for row in rows:
            nome  = (row[0] or "").lower().strip()
            dados = row[1]
            if dados:
                blob = bytes(dados) if not isinstance(dados, bytes) else dados
                if "frente" in nome:
                    frente_bytes = blob
                    print(f"[Assets] frente carregada do banco ({len(blob):,} bytes).")
                elif "verso" in nome:
                    verso_bytes = blob
                    print(f"[Assets] verso carregada do banco ({len(blob):,} bytes).")

        if not frente_bytes:
            print("[Assets] 'frente.png' não encontrada na tabela Imagens.")
        if not verso_bytes:
            print("[Assets] 'verso.png' não encontrada na tabela Imagens.")

        return frente_bytes, verso_bytes

    except ImportError:
        print("[Assets] services.database não disponível — ignorando busca no banco.")
        return None, None
    except Exception as e:
        print(f"[Assets] Erro ao buscar imagens no banco: {type(e).__name__}: {e}")
        return None, None


def _bytes_para_arquivo_temp(data: bytes, suffix: str = ".png") -> Optional[str]:
    """Salva bytes em arquivo temporário e retorna o caminho."""
    try:
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix="carteira_img_"
        )
        tmp.write(data)
        tmp.flush()
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"[Assets] Erro ao criar arquivo temporário: {e}")
        return None


# Cache das imagens vindas do banco
_cache_db: dict = {}


def _carregar_cache_banco() -> None:
    """Carrega (uma única vez) as imagens do banco."""
    if _cache_db:
        return

    frente_bytes, verso_bytes = _buscar_imagens_do_banco()

    _cache_db["frente_bytes"] = frente_bytes
    _cache_db["verso_bytes"]  = verso_bytes
    _cache_db["frente_path"]  = _bytes_para_arquivo_temp(frente_bytes) if frente_bytes else None
    _cache_db["verso_path"]   = _bytes_para_arquivo_temp(verso_bytes)  if verso_bytes  else None


# ── Helpers de diretório ─────────────────────────────────────────────────────

def _exe_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _candidate_img_dirs() -> List[Path]:
    candidates: List[Path] = []
    seen: set = set()

    env = os.environ.get("CARTEIRA_IMG_DIR")
    if env:
        p = Path(env).resolve()
        if str(p) not in seen:
            candidates.append(p); seen.add(str(p))

    base = _exe_dir()
    for _ in range(5):
        for sub in ("images", "assets", "resources/images", "static/images"):
            c = base / sub
            if str(c) not in seen:
                candidates.append(c); seen.add(str(c))
        base = base.parent

    for legacy in _LEGACY_IMG_DIRS:
        p = Path(legacy).resolve()
        if str(p) not in seen:
            candidates.append(p); seen.add(str(p))

    return candidates


@lru_cache(maxsize=1)
def _find_img_dir() -> Optional[Path]:
    for d in _candidate_img_dirs():
        if d.is_dir():
            for name in FRENTE_NAMES + VERSO_NAMES:
                if (d / name).exists():
                    return d
    return None


def _find_image_on_disk(names: List[str]) -> Optional[Path]:
    img_dir = _find_img_dir()
    if img_dir:
        for name in names:
            p = img_dir / name
            if p.exists():
                return p
        try:
            for f in img_dir.iterdir():
                if f.is_file() and any(f.name.lower() == n.lower() for n in names):
                    return f
        except PermissionError:
            pass
    return None


# ── API pública ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_img_frente() -> Optional[str]:
    """
    Retorna o caminho da imagem frente (arquivo temporário gerado a partir
    do banco, ou arquivo em disco como fallback).
    """
    _carregar_cache_banco()
    if _cache_db.get("frente_path"):
        return _cache_db["frente_path"]
    p = _find_image_on_disk(list(FRENTE_NAMES))
    return str(p) if p else None


@lru_cache(maxsize=1)
def get_img_verso() -> Optional[str]:
    """
    Retorna o caminho da imagem verso (arquivo temporário gerado a partir
    do banco, ou arquivo em disco como fallback).
    """
    _carregar_cache_banco()
    if _cache_db.get("verso_path"):
        return _cache_db["verso_path"]
    p = _find_image_on_disk(list(VERSO_NAMES))
    return str(p) if p else None


def get_img_frente_bytes() -> Optional[bytes]:
    """Retorna bytes brutos da imagem frente (sem gravar arquivo)."""
    _carregar_cache_banco()
    return _cache_db.get("frente_bytes")


def get_img_verso_bytes() -> Optional[bytes]:
    """Retorna bytes brutos da imagem verso (sem gravar arquivo)."""
    _carregar_cache_banco()
    return _cache_db.get("verso_bytes")


@lru_cache(maxsize=1)
def get_font_path() -> Optional[str]:
    """Retorna caminho da fonte."""
    env = os.environ.get("CARTEIRA_FONT_PATH")
    if env and Path(env).exists():
        return env

    base = _exe_dir()
    for _ in range(5):
        for name in FONT_NAMES:
            for sub in ("fonts", "assets", "resources", "."):
                p = base / sub / name
                if p.exists():
                    return str(p)
        base = base.parent

    for p in _LEGACY_FONT_PATHS:
        if Path(p).exists():
            return p

    win_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in FONT_NAMES:
        p = win_fonts / name
        if p.exists():
            return str(p)

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
    _carregar_cache_banco()
    status = {
        "img_frente":       get_img_frente(),
        "img_verso":        get_img_verso(),
        "font_path":        get_font_path(),
        "img_dir_found":    str(_find_img_dir()) if _find_img_dir() else None,
        "frente_do_banco":  _cache_db.get("frente_bytes") is not None,
        "verso_do_banco":   _cache_db.get("verso_bytes")  is not None,
        "frente_tam_bytes": len(_cache_db["frente_bytes"]) if _cache_db.get("frente_bytes") else 0,
        "verso_tam_bytes":  len(_cache_db["verso_bytes"])  if _cache_db.get("verso_bytes")  else 0,
    }
    if verbose:
        status.update({
            "candidate_dirs": [str(d) for d in _candidate_img_dirs()[:5]],
            "exe_dir":        str(_exe_dir()),
            "sys_frozen":     getattr(sys, "frozen", False),
        })
    return status


# ── Utilitários de imagem ─────────────────────────────────────────────────────

def make_placeholder_image(
    width: int = 420,
    height: int = 240,
    label: str = "SEM IMAGEM",
    bg_color: Union[str, Tuple[int, int, int]] = (220, 220, 230),
    border_color: Union[str, Tuple[int, int, int]] = (150, 150, 170),
    text_color: Union[str, Tuple[int, int, int]] = (120, 120, 140),
) -> Image.Image:
    img  = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, width - 3, height - 3], outline=border_color, width=2)

    font_size = min(width, height) // 10
    font = None
    try:
        font = get_pil_font(font_size)
    except Exception:
        pass

    if font:
        bbox = draw.textbbox((0, 0), label, font=font)
        x = (width  - (bbox[2] - bbox[0])) // 2
        y = (height - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), label, fill=text_color, font=font)
    else:
        draw.text((width // 2, height // 2), label, fill=text_color, anchor="mm")

    return img


def open_image(
    path: Optional[str],
    fallback_label: str = "SEM IMAGEM",
    resize_to: Optional[Tuple[int, int]] = None,
    convert_mode: Optional[str] = None,
) -> Image.Image:
    """Abre imagem do path ou retorna placeholder. Nunca lança exceção."""
    img = None
    if path and os.path.exists(path):
        try:
            img = Image.open(path)
        except Exception:
            pass
    if img is None:
        img = make_placeholder_image(label=fallback_label)
    if convert_mode and img.mode != convert_mode:
        img = img.convert(convert_mode)
    if resize_to:
        img = img.resize(resize_to, Image.Resampling.LANCZOS)
    return img


def get_pil_font(size: int) -> Optional[Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]]:
    font_path = get_font_path()
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def reload_assets() -> dict:
    """Força recarregamento completo dos assets."""
    global _cache_db
    _cache_db = {}
    _find_img_dir.cache_clear()
    get_img_frente.cache_clear()
    get_img_verso.cache_clear()
    get_font_path.cache_clear()
    return assets_status(verbose=True)