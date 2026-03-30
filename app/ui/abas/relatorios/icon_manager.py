# -*- coding: utf-8 -*-
"""Gerenciador de ícones para relatórios"""
import os
from PIL import Image
import customtkinter as ctk


class IconManager:
    """Gerenciador de ícones para a interface de relatórios"""
    
    def __init__(self):
        self.icons = {}
        self.icons_dir = self._find_icons_path()
        self._setup_icons()
        
    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "..", "..", "images", "icons", "relatorios"),
            os.path.join(current_dir, "..", "..", "..", "images", "icons", "relatorios"),
            r"C:\Users\Administrador\Documents\SECTOR AUTOMATION_v14\images\icons\relatorios",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"[IconManager] ✅ Ícones encontrados em: {path}")
                return path
        
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada")
        return possible_paths[0]
        
    def load_icon(self, filename, size=(32, 32), colorize_to=None):
        """Carrega um ícone e opcionalmente aplica cor"""
        try:
            path = os.path.join(self.icons_dir, filename)
            if not os.path.exists(path):
                return None
                
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            if colorize_to:
                img = self._colorize_image(img, colorize_to)
            
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"[IconManager] Erro ao carregar {filename}: {e}")
            return None
    
    def _colorize_image(self, img, color):
        """Aplica cor a uma imagem"""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        if isinstance(color, str):
            color = self._hex_to_rgb(color)
        
        data = img.getdata()
        new_data = []
        for r, g, b, a in data:
            if a > 0:
                new_data.append((color[0], color[1], color[2], a))
            else:
                new_data.append((r, g, b, a))
        
        img.putdata(new_data)
        return img
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Converte hex para RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _setup_icons(self):
        """Configura todos os ícones necessários"""
        icons_config = {
            "total": ("paste.png", (32, 32), "#3b82f6"),
            "municipios": ("mapa.png", (32, 32), "#f59e0b"),
            "inscricoes": ("pen.png", (32, 32), "#10b981"),
            "renovacoes": ("pen.png", (32, 32), "#ef4444"),
            "history": ("history.png", (24, 24), None),
            "reload": ("reload.png", (24, 24), None),
            "settings": ("settings.png", (24, 24), None),
            "paste": ("paste.png", (20, 20), None),
        }
        
        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)
    
    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)