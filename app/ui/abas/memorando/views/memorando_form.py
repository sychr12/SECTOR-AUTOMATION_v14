# -*- coding: utf-8 -*-
"""Views para Memorando de Saída — formulário e histórico"""

import customtkinter as ctk
from app.theme import AppTheme
from .municipio_selector import MunicipioSelector
from app.ui.abas.memorando.style import (
    FILTER_RADIUS,
    FILTER_BORDER,
    FILTER_HOVER,
    FILTER_INPUT_BG,
    FILTER_DROPDOWN_BG,
)
class MemorandoFormView(ctk.CTkFrame):

    def __init__(self, parent, controller, on_gerar=None, on_historico=None,
                 icons=None, unloc_list=None, unloc_dict=None):
        super().__init__(parent, fg_color="transparent")
        self.controller   = controller
        self.on_gerar     = on_gerar
        self.on_historico = on_historico
        self.icons        = icons or {}
        self.unloc_list   = unloc_list or []
        self.unloc_dict   = unloc_dict or {}
        self._aplicando_mascara = False
        self._create_widgets()

    def _create_widgets(self):
        card = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD, corner_radius=16)
        card.pack(fill="x")
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        campos = [
            (0, "Nº Memo Saída", "Ex: 001", "entry"),
            (1, "Data", "DD/MM/AAAA", "entry"),
            (2, "Município", "Selecione o município", "combo"),
            (3, "Nº Memo Entrada", "Ex: 045", "entry"),
        ]

        self._entries = {}

        for col, label, placeholder, tipo in campos:
            label_frame = ctk.CTkFrame(card, fg_color="transparent")
            label_frame.grid(row=0, column=col, padx=(20, 8), pady=(24, 4), sticky="w")

            ctk.CTkLabel(
                label_frame,
                text=label,
                font=("Segoe UI", 11, "bold"),
                text_color=AppTheme.TXT_MUTED,
                anchor="w"
            ).pack(side="left")

            if tipo == "combo":
                entry = MunicipioSelector(
                    card,
                    values=self.unloc_list,
                    default="MAO - MANAUS" if "MAO - MANAUS" in self.unloc_list else (self.unloc_list[0] if self.unloc_list else ""),
                    width=220,
                    height=44,
                    corner_radius=FILTER_RADIUS,
                    fg_color=FILTER_INPUT_BG,
                    text_color=AppTheme.TXT_MAIN,
                    button_color=FILTER_INPUT_BG,
                    button_hover_color=FILTER_HOVER,
                    dropdown_fg_color=FILTER_DROPDOWN_BG,
                    border_color=FILTER_BORDER,
                    border_width=1,
                    font=("Segoe UI", 13),
                    placeholder="Selecione o município",
                )
            else:
                entry = ctk.CTkEntry(
                    card,
                    placeholder_text=placeholder,
                    fg_color=FILTER_INPUT_BG,
                    text_color=AppTheme.TXT_MAIN,
                    placeholder_text_color="#4b5563",
                    height=44,
                    corner_radius=FILTER_RADIUS,
                    border_color=FILTER_BORDER,
                    border_width=1,
                    font=("Segoe UI", 13),
                )
                
                if label == "Data":
                    self._data_var = ctk.StringVar()
                    entry.configure(textvariable=self._data_var)
                    self._data_var.trace_add("write", self._mascara_data)

            entry.grid(
                row=1, column=col,
                padx=(20, 8) if col == 0 else (8, 20) if col == 3 else (8, 8),
                pady=(0, 24),
                sticky="ew"
            )

            self._entries[col] = entry

        self.nmemosaidaentry   = self._entries[0]
        self.dataemissaoentry  = self._entries[1]
        self.unlocentry        = self._entries[2]
        self.nmemoentradaentry = self._entries[3]

        separator = ctk.CTkFrame(card, height=1, fg_color=AppTheme.BG_INPUT)
        separator.grid(row=2, column=0, columnspan=4, padx=20, pady=(0, 20), sticky="ew")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=(0, 24), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        if self.on_gerar:
            self.btn_gerar = ctk.CTkButton(
                btn_frame,
                text=" Gerar e Salvar",
                image=self.icons.get("save"),
                compound="left",
                height=48,
                corner_radius=FILTER_RADIUS,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                font=("Segoe UI", 13, "bold"),
                text_color="#ffffff",
                command=self._on_gerar
            )
            self.btn_gerar.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        if self.on_historico:
            self.btn_historico = ctk.CTkButton(
                btn_frame,
                text=" Histórico",
                image=self.icons.get("history"),
                compound="left",
                height=48,
                corner_radius=FILTER_RADIUS,
                fg_color=FILTER_INPUT_BG,
                hover_color=FILTER_HOVER,
                font=("Segoe UI", 13),
                text_color=AppTheme.TXT_MAIN,
                command=self.on_historico
            )
            self.btn_historico.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _mascara_data(self, *_):
        if self._aplicando_mascara:
            return
        self._aplicando_mascara = True
        try:
            texto = self._data_var.get()
            digitos = "".join(c for c in texto if c.isdigit())[:8]

            if len(digitos) <= 2:
                fmt = digitos
            elif len(digitos) <= 4:
                fmt = digitos[:2] + "/" + digitos[2:]
            else:
                fmt = digitos[:2] + "/" + digitos[2:4] + "/" + digitos[4:]

            if fmt != texto:
                self._data_var.set(fmt)
                self.dataemissaoentry.after(0, lambda: self.dataemissaoentry.icursor("end"))
        finally:
            self._aplicando_mascara = False

    def _on_gerar(self):
        if self.on_gerar:
            self.on_gerar(self.get_form_data())

    def get_form_data(self):
        return {
            "numero":       self.nmemosaidaentry.get().strip(),
            "data":         self.dataemissaoentry.get().strip(),
            "unloc":        self.unlocentry.get().strip(),
            "memo_entrada": self.nmemoentradaentry.get().strip(),
        }

    def get_unloc_codigo(self):
        valor = self.unlocentry.get().strip()
        if " - " in valor:
            return valor.split(" - ")[0]
        return valor

    def clear_form(self):
        self.nmemosaidaentry.delete(0, "end")
        self._data_var.set("")

        if "MAO - MANAUS" in self.unloc_list:
            self.unlocentry.set("MAO - MANAUS")
        elif self.unloc_list:
            self.unlocentry.set(self.unloc_list[0])

        self.nmemoentradaentry.delete(0, "end")
        self.nmemosaidaentry.focus()