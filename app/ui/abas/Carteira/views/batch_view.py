# views/batch_view.py
# -*- coding: utf-8 -*-
"""
batch_view.py — Aba de geração em LOTE de carteiras digitais.
"""
import os
import re
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from app.theme import AppTheme
from ..utils.constants import VERDE, VERDE_HOVER, AZUL, AZUL_HOVER, MUTED, VERMELHO, AMBER
from .batch_controller import BatchCarteiraController


# ── Cores ─────────────────────────────────────────────────────────────────────
_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_AMBER   = "#f59e0b"
_AMBER_H = "#d97706"
_VERM    = "#ef4444"
_MUTED   = "#64748b"

_LOG_CORES = {
    "sucesso": _VERDE,
    "erro":    _VERM,
    "aviso":   _AMBER,
    "info":    _MUTED,
}


class BatchCarteiraView(ctk.CTkFrame):
    """Aba de geração em lote — integrada ao CTkTabview ou ttk.Notebook."""

    def __init__(self, master, usuario: str, repo, sefaz_repo):
        super().__init__(master, fg_color="transparent")
        self.usuario   = usuario
        self._ctrl     = BatchCarteiraController(usuario, repo, sefaz_repo)
        self._arquivos: list = []

        self._build()
        
    # ── Layout principal ──────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=32, pady=24)

        # Cabeçalho
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            hdr, text="Gerar Carteiras em Lote",
            font=("Segoe UI", 22, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(side="left")

        ctk.CTkLabel(
            hdr,
            text="Nome do PDF deve ser o CPF sem formatação  (ex: 01234567890.pdf)",
            font=("Segoe UI", 11),
            text_color=_MUTED,
        ).pack(side="right", pady=(6, 0))

        ctk.CTkFrame(wrap, height=1,
                     fg_color=AppTheme.BG_CARD).pack(fill="x", pady=(0, 20))

        # Duas colunas
        cols = ctk.CTkFrame(wrap, fg_color="transparent")
        cols.pack(fill="both", expand=True)
        cols.grid_columnconfigure(0, weight=2)
        cols.grid_columnconfigure(1, weight=3)
        cols.grid_rowconfigure(0, weight=1)

        self._build_esquerda(cols)
        self._build_direita(cols)

    # ── Coluna esquerda: seleção + lista + controles ──────────────────────────
    def _build_esquerda(self, parent):
        col = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                           corner_radius=16)
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(
            col, text="Arquivos Selecionados",
            font=("Segoe UI", 13, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w", padx=20, pady=(20, 12))

        # Botões de seleção
        sel = ctk.CTkFrame(col, fg_color="transparent")
        sel.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkButton(
            sel, text="📄 Selecionar PDFs",
            height=38, corner_radius=10,
            fg_color=_AZUL, hover_color=_AZUL_H,
            font=("Segoe UI", 12, "bold"), text_color="#fff",
            command=self._selecionar_pdfs,
        ).pack(side="left")

        ctk.CTkButton(
            sel, text="📁 Selecionar Pasta",
            height=38, corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
            command=self._selecionar_pasta,
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            sel, text="✕ Limpar",
            height=38, corner_radius=10, width=80,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 11), text_color=_MUTED,
            command=self._limpar_lista,
        ).pack(side="right")

        # Contador
        self._lbl_count = ctk.CTkLabel(
            col, text="0 arquivo(s)",
            font=("Segoe UI", 11), text_color=_MUTED)
        self._lbl_count.pack(anchor="w", padx=20, pady=(0, 8))

        # Treeview
        frame_tree = ctk.CTkFrame(col, fg_color=AppTheme.BG_INPUT,
                                  corner_radius=12)
        frame_tree.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Batch.Treeview",
                        background=AppTheme.BG_INPUT,
                        fieldbackground=AppTheme.BG_INPUT,
                        foreground=AppTheme.TXT_MAIN,
                        rowheight=30, font=("Segoe UI", 11),
                        borderwidth=0)
        style.configure("Batch.Treeview.Heading",
                        background=AppTheme.BG_CARD,
                        foreground=_MUTED,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Batch.Treeview",
                  background=[("selected", "#1e3a5f")])

        self._tree = ttk.Treeview(
            frame_tree,
            columns=("cpf", "nome", "status"),
            show="headings",
            style="Batch.Treeview",
            selectmode="browse",
        )
        for col_id, titulo, w, stretch in [
            ("cpf",    "CPF",     120, False),
            ("nome",   "Arquivo", 180, True),
            ("status", "Status",   90, False),
        ]:
            self._tree.heading(col_id, text=titulo)
            self._tree.column(col_id, width=w, minwidth=60, stretch=stretch)

        vsb = ttk.Scrollbar(frame_tree, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=6)
        self._tree.pack(fill="both", expand=True, padx=6, pady=6)

        # Tags de cor por status
        self._tree.tag_configure("ok",       foreground=_VERDE)
        self._tree.tag_configure("erro",     foreground=_VERM)
        self._tree.tag_configure("aviso",    foreground=_AMBER)
        self._tree.tag_configure("pendente", foreground=_MUTED)

        # Progresso
        prog = ctk.CTkFrame(col, fg_color="transparent")
        prog.pack(fill="x", padx=20, pady=(0, 8))
        self._lbl_prog = ctk.CTkLabel(
            prog, text="",
            font=("Segoe UI", 11), text_color=_MUTED)
        self._lbl_prog.pack(anchor="w")

        self._progress = ctk.CTkProgressBar(
            col, height=8, corner_radius=4,
            progress_color=_VERDE)
        self._progress.set(0)
        self._progress.pack(fill="x", padx=20, pady=(0, 12))

        # Botões ação
        self._btn_gerar = ctk.CTkButton(
            col, text="🚀 Gerar Carteiras",
            height=46, corner_radius=14,
            fg_color=_VERDE, hover_color=_VERDE_H,
            font=("Segoe UI", 14, "bold"), text_color="#fff",
            command=self._iniciar,
        )
        self._btn_gerar.pack(fill="x", padx=20, pady=(0, 8))

        self._btn_parar = ctk.CTkButton(
            col, text="⛔ Parar",
            height=40, corner_radius=12,
            fg_color=_VERM, hover_color="#dc2626",
            font=("Segoe UI", 12), text_color="#fff",
            state="disabled",
            command=self._parar,
        )
        self._btn_parar.pack(fill="x", padx=20, pady=(0, 20))

    # ── Coluna direita: log ───────────────────────────────────────────────────
    def _build_direita(self, parent):
        col = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                           corner_radius=16)
        col.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        hdr = ctk.CTkFrame(col, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            hdr, text="Log de Processamento",
            font=("Segoe UI", 13, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(side="left")

        ctk.CTkButton(
            hdr, text="Limpar Log",
            height=28, width=90, corner_radius=8,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 10), text_color=_MUTED,
            command=self._limpar_log,
        ).pack(side="right")

        # Resumo (3 mini-stats)
        resumo = ctk.CTkFrame(col, fg_color=AppTheme.BG_INPUT,
                              corner_radius=10)
        resumo.pack(fill="x", padx=20, pady=(0, 12))
        for i in range(3):
            resumo.grid_columnconfigure(i, weight=1)

        self._sc_sucesso  = self._mini_stat(resumo, "✓ Sucesso",   "0", _VERDE, 0)
        self._sc_erro     = self._mini_stat(resumo, "✕ Erros",     "0", _VERM,  1)
        self._sc_ignorado = self._mini_stat(resumo, "⊘ Ignorados", "0", _AMBER, 2)

        # Log textbox
        self._log_box = ctk.CTkTextbox(
            col,
            fg_color="transparent",
            text_color=AppTheme.TXT_MAIN,
            font=("Consolas", 11),
            state="disabled",
            border_width=0,
        )
        self._log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    @staticmethod
    def _mini_stat(parent, titulo, valor, cor, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, padx=8, pady=8)
        ctk.CTkLabel(f, text=titulo,
                     font=("Segoe UI", 9), text_color=_MUTED).pack()
        lbl = ctk.CTkLabel(f, text=valor,
                           font=("Segoe UI", 18, "bold"),
                           text_color=cor)
        lbl.pack()
        return lbl

    # ── Seleção de arquivos ───────────────────────────────────────────────────
    def _selecionar_pdfs(self):
        caminhos = filedialog.askopenfilenames(
            title="Selecionar PDFs (nome = CPF sem formatação)",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        )
        if caminhos:
            self._adicionar_arquivos(list(caminhos))

    def _selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecionar pasta com PDFs")
        if not pasta:
            return
        caminhos = [
            os.path.join(pasta, f)
            for f in os.listdir(pasta)
            if f.lower().endswith(".pdf")
        ]
        if not caminhos:
            messagebox.showwarning("Aviso", "Nenhum PDF encontrado na pasta.")
            return
        self._adicionar_arquivos(caminhos)

    def _adicionar_arquivos(self, caminhos: list):
        existentes = {a["caminho"] for a in self._arquivos}
        invalidos  = []

        for caminho in caminhos:
            if caminho in existentes:
                continue
            nome = os.path.basename(caminho)
            cpf  = BatchCarteiraController.cpf_do_arquivo(nome)
            if not cpf:
                invalidos.append(nome)
                continue
            self._arquivos.append({
                "caminho": caminho,
                "nome":    nome,
                "cpf":     BatchCarteiraController.formatar_cpf(cpf),
                "status":  "pendente",
            })

        self._renderizar_lista()

        if invalidos:
            messagebox.showwarning(
                "Arquivos ignorados",
                f"{len(invalidos)} arquivo(s) ignorado(s) "
                "(o nome deve ser exatamente 11 dígitos numéricos):\n\n" +
                "\n".join(invalidos[:10]) +
                (f"\n... e mais {len(invalidos) - 10}" if len(invalidos) > 10 else ""),
            )

    def _limpar_lista(self):
        if self._ctrl.esta_rodando():
            messagebox.showwarning("Aviso", "Aguarde o processamento terminar.")
            return
        self._arquivos.clear()
        self._renderizar_lista()

    def _renderizar_lista(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        for a in self._arquivos:
            self._tree.insert("", "end",
                              values=(a["cpf"], a["nome"], a["status"].upper()),
                              tags=(a["status"],))
        n = len(self._arquivos)
        self._lbl_count.configure(
            text=f"{n} arquivo(s)",
            text_color=AppTheme.TXT_MAIN if n else _MUTED,
        )

    def _atualizar_status_arquivo(self, nome: str, status: str):
        for i, a in enumerate(self._arquivos):
            if a["nome"] == nome:
                a["status"] = status
                items = self._tree.get_children()
                if i < len(items):
                    self._tree.item(items[i],
                                    values=(a["cpf"], a["nome"],
                                            status.upper()),
                                    tags=(status,))
                break

    # ── Iniciar / Parar ───────────────────────────────────────────────────────
    def _iniciar(self):
        if not self._arquivos:
            messagebox.showwarning("Aviso", "Adicione PDFs antes de gerar.")
            return
        if self._ctrl.esta_rodando():
            messagebox.showwarning("Aviso", "Processamento já em andamento.")
            return

        # Reset visual
        self._progress.set(0)
        self._progress.configure(progress_color=_VERDE)
        self._limpar_log()
        self._sc_sucesso.configure(text="0")
        self._sc_erro.configure(text="0")
        self._sc_ignorado.configure(text="0")
        self._btn_gerar.configure(state="disabled", text="Gerando...",
                                   fg_color=_MUTED)
        self._btn_parar.configure(state="normal")

        # Resetar status na lista
        for a in self._arquivos:
            a["status"] = "pendente"
        self.after(0, self._renderizar_lista)

        caminhos = [a["caminho"] for a in self._arquivos]
        self._ctrl.executar_lote(
            caminhos_pdf = caminhos,
            log_cb       = self._on_log,
            progress_cb  = self._on_progress,
            concluido_cb = self._on_concluido,
        )

    def _parar(self):
        self._ctrl.parar()
        self._btn_parar.configure(state="disabled")
        self._log("Parando após o arquivo atual...", "aviso")

    # ── Callbacks do controller ───────────────────────────────────────────────
    def _on_log(self, msg: str, tipo: str = "info"):
        self.after(0, self._log, msg, tipo)

        # Atualizar status na árvore conforme tipo do log
        m = re.match(r"\[\d+/\d+\] (.+?) — (.+)", msg)
        if m:
            cpf_txt = m.group(1)
            status  = "ok" if tipo == "sucesso" else tipo
            for a in self._arquivos:
                if a["cpf"] == cpf_txt or cpf_txt in a["nome"]:
                    self.after(0, self._atualizar_status_arquivo,
                               a["nome"], status)
                    break

    def _on_progress(self, atual: int, total: int, nome: str):
        pct = atual / total if total else 0
        self.after(0, lambda: self._progress.set(pct))
        self.after(0, lambda: self._lbl_prog.configure(
            text=f"{atual}/{total}  —  {nome}"))

    def _on_concluido(self, sucesso: int, erro: int, ignorado: int):
        self.after(0, lambda: self._sc_sucesso.configure(text=str(sucesso)))
        self.after(0, lambda: self._sc_erro.configure(text=str(erro)))
        self.after(0, lambda: self._sc_ignorado.configure(text=str(ignorado)))
        self.after(0, lambda: self._progress.set(1.0))
        cor_prog = _VERDE if erro == 0 else _AMBER
        self.after(0, lambda: self._progress.configure(progress_color=cor_prog))
        self.after(0, lambda: self._lbl_prog.configure(
            text=f"Concluído — {sucesso} salvo(s)"))
        self.after(0, lambda: self._btn_gerar.configure(
            state="normal", text="🚀 Gerar Carteiras", fg_color=_VERDE))
        self.after(0, lambda: self._btn_parar.configure(state="disabled"))

        if erro == 0:
            self.after(0, messagebox.showinfo,
                       "Concluído",
                       f"Lote finalizado!\n\n"
                       f"✓ Sucesso:    {sucesso}\n"
                       f"⊘ Ignorados: {ignorado}\n"
                       f"✕ Erros:      {erro}")
        else:
            self.after(0, messagebox.showwarning,
                       "Concluído com erros",
                       f"Lote finalizado com erros.\n\n"
                       f"✓ Sucesso:    {sucesso}\n"
                       f"⊘ Ignorados: {ignorado}\n"
                       f"✕ Erros:      {erro}\n\n"
                       f"Verifique o log para detalhes.")

    # ── Log ───────────────────────────────────────────────────────────────────
    def _log(self, msg: str, tipo: str = "info"):
        self._log_box.configure(state="normal")
        tag = f"_t_{tipo}"
        self._log_box.tag_config(tag, foreground=_LOG_CORES.get(tipo, _MUTED))
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_box.insert("end", f"[{ts}] {msg}\n", tag)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _limpar_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")