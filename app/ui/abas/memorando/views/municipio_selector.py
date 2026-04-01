# -*- coding: utf-8 -*-
import customtkinter as ctk


class MunicipioSelector(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        values,
        default=None,
        width=220,
        height=44,
        corner_radius=12,
        fg_color="#f8fafc",
        text_color="#1f2937",
        button_color="#f8fafc",
        button_hover_color="#eef2f7",
        dropdown_fg_color="#ffffff",
        border_color="#dbe2ea",
        font=("Segoe UI", 13),
        placeholder="Selecione...",
        command=None,
        border_width=1,
    ):
        super().__init__(parent, fg_color="transparent")

        self.values = list(values or [])
        self.filtered_values = self.values[:]
        self.command = command
        self.placeholder = placeholder
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.fg_color = fg_color
        self.text_color = text_color
        self.button_color = button_color
        self.button_hover_color = button_hover_color
        self.dropdown_fg_color = dropdown_fg_color
        self.border_color = border_color
        self.border_width = border_width
        self.font = font

        self._selected = default if default in self.values else (self.values[0] if self.values else "")
        self._popup = None
        self._scroll = None
        self._search_var = None
        self._search_entry = None
        self._trace_id = None
        self._closing_popup = False
        self._click_outside_bind_id = None
        
        self._build_main()

    def _build_main(self):
        self.grid_columnconfigure(0, weight=1)

        self._button = ctk.CTkButton(
            self,
            text=self._selected if self._selected else self.placeholder,
            width=self.width,
            height=self.height,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            font=self.font,
            anchor="w",
            border_width=self.border_width,
            border_color=self.border_color,
            command=self._toggle_popup,
        )
        self._button.grid(row=0, column=0, sticky="ew")
        
    def _toggle_popup(self):
        if self._popup and self._popup.winfo_exists():
            self._close_popup()
        else:
            self._open_popup()

    def _open_popup(self):
        if self._popup and self._popup.winfo_exists():
            return

        self._closing_popup = False
        self._popup = ctk.CTkToplevel(self)
        self._popup.overrideredirect(True)
        self._popup.attributes("-topmost", True)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        popup_width = max(self.width, 280)
        popup_height = 320

        self._popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        self._popup.configure(fg_color=self.dropdown_fg_color)

        container = ctk.CTkFrame(
            self._popup,
            fg_color=self.dropdown_fg_color,
            border_width=1,
            corner_radius=self.corner_radius,
            border_color=self.border_color,
        )
        container.pack(fill="both", expand=True)

        self._search_var = ctk.StringVar()
        self._trace_id = self._search_var.trace_add("write", self._on_search)

        self._search_entry = ctk.CTkEntry(
            container,
            textvariable=self._search_var,
            placeholder_text="Buscar município...",
            height=38,
            corner_radius=self.corner_radius,
            fg_color=self.fg_color,
            border_color=self.border_color,
            border_width=self.border_width,
            text_color="#1f2937",
            font=("Segoe UI", 12),
        )
        self._search_entry.pack(fill="x", padx=12, pady=(12, 8))
        self._search_entry.focus()

        self._scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8",
        )
        self._scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.filtered_values = self.values[:]
        self._render_options()

        self._popup.bind("<Escape>", lambda e: self._close_popup())

        self._bind_mousewheel()
        self.after(50, self._bind_click_outside)

    def _bind_mousewheel(self):
        try:
            if self._popup and self._popup.winfo_exists():
                self._popup.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
                self._popup.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
                self._popup.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")
        except Exception:
            pass

    def _unbind_mousewheel(self):
        try:
            if self._popup:
                self._popup.unbind_all("<MouseWheel>")
                self._popup.unbind_all("<Button-4>")
                self._popup.unbind_all("<Button-5>")
        except Exception:
            pass

    def _on_mousewheel(self, event):
        try:
            if self._closing_popup:
                return
            if not self._popup or not self._popup.winfo_exists():
                return
            if not self._scroll or not self._scroll.winfo_exists():
                return

            canvas = self._scroll._parent_canvas
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _on_mousewheel_linux(self, event):
        try:
            if self._closing_popup:
                return
            if not self._popup or not self._popup.winfo_exists():
                return
            if not self._scroll or not self._scroll.winfo_exists():
                return

            canvas = self._scroll._parent_canvas
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _on_search(self, *_):
        try:
            if self._closing_popup:
                return
            if not self._popup or not self._popup.winfo_exists():
                return
            if not self._scroll or not self._scroll.winfo_exists():
                return
            if self._search_var is None:
                return

            termo = self._search_var.get().strip().lower()

            if not termo:
                self.filtered_values = self.values[:]
            else:
                self.filtered_values = [
                    item for item in self.values
                    if termo in item.lower()
                ]

            self._render_options()
        except Exception:
            pass

    def _render_options(self):
        try:
            if self._closing_popup:
                return
            if not self._scroll or not self._scroll.winfo_exists():
                return

            # limpa itens antigos
            for w in self._scroll.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass

            # sem resultados
            if not self.filtered_values:
                ctk.CTkLabel(
                    self._scroll,
                    text="Nenhum município encontrado",
                    text_color="#64748b",
                    font=("Segoe UI", 12),
                ).pack(pady=16)

                self.after(10, self._scroll_to_top)
                return

            # recria a lista
            for item in self.filtered_values:
                btn = ctk.CTkButton(
                    self._scroll,
                    text=item,
                    anchor="w",
                    height=36,
                    corner_radius=self.corner_radius - 2 if self.corner_radius > 2 else self.corner_radius,
                    fg_color="transparent",
                    hover_color=self.button_hover_color,
                    text_color="#1f2937",
                    font=("Segoe UI", 12),
                    command=lambda v=item: self.set(v, trigger=True),
                )
                btn.pack(fill="x", padx=6, pady=2)

            # sobe o scroll depois que os widgets existirem
            self.after(10, self._scroll_to_top)

        except Exception as e:
            print(f"[MunicipioSelector] erro em _render_options: {e}")

    def _close_popup_safe(self):
        try:
            if self._popup and self._popup.winfo_exists():
                self.after(80, self._close_popup)
        except Exception:
            pass

    def _close_popup(self):
        if self._closing_popup:
            return

        self._closing_popup = True

        try:
            self._unbind_mousewheel()

            if self._trace_id and self._search_var is not None:
                try:
                    self._search_var.trace_remove("write", self._trace_id)
                except Exception:
                    pass
                self._trace_id = None

            if self._search_entry is not None:
                try:
                    self._search_entry.configure(textvariable=None)
                except Exception:
                    pass

            if self._popup and self._popup.winfo_exists():
                self._popup.destroy()

        except Exception:
            pass
        finally:
            self._popup = None
            self._scroll = None
            self._search_entry = None
            self._search_var = None
            self._closing_popup = False
            
        try:
            top = self.winfo_toplevel()
            if self._click_outside_bind_id is not None:
                top.unbind("<Button-1>", self._click_outside_bind_id)
                self._click_outside_bind_id = None
        except Exception:
            pass

    def get(self):
        return self._selected

    def set(self, value, trigger=False):
        if value not in self.values:
            return
        self._selected = value
        self._button.configure(text=value if value else self.placeholder)
        self._close_popup()
        if trigger and callable(self.command):
            self.command(value)

    def configure_values(self, values, default=None):
        self.values = list(values or [])
        self.filtered_values = self.values[:]

        if default in self.values:
            self._selected = default
        elif self._selected not in self.values:
            self._selected = self.values[0] if self.values else ""

        self._button.configure(text=self._selected if self._selected else self.placeholder)
        
    def _scroll_to_top(self):
        try:
            if self._scroll and self._scroll.winfo_exists():
                self._scroll._parent_canvas.yview_moveto(0)
        except Exception as e:
            print(f"[MunicipioSelector] erro ao rolar para o topo: {e}")
            
    def _bind_click_outside(self):
        try:
            top = self.winfo_toplevel()
            if self._click_outside_bind_id is None:
                self._click_outside_bind_id = top.bind("<Button-1>", self._on_click_outside, add="+")
        except Exception:
            pass
        
    def _is_child_of(self, widget, parent):
        try:
            while widget:
                if widget == parent:
                    return True
                widget = widget.master
        except Exception:
            pass
        return False
        
    def _on_click_outside(self, event):
        try:
            if self._closing_popup:
                return
            if not self._popup or not self._popup.winfo_exists():
                return

            widget = event.widget

            # verifica se clicou dentro do popup
            if self._is_child_of(widget, self._popup):
                return

            # verifica se clicou no botão do selector
            if self._is_child_of(widget, self):
                return

            # clicou fora → fecha
            self._close_popup()

        except Exception:
            pass
        
        
    