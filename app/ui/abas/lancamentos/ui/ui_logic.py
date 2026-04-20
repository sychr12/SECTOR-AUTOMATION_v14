# -*- coding: utf-8 -*-
"""
ui_logic.py — Lógica de negócio da UI (PyQt6).

Contém os carregadores de dados, preenchimento das tabelas
e atualização de contadores. Não cria widgets nem responde
a eventos de formulário diretamente.
"""

from PyQt6.QtWidgets import QMessageBox, QLabel, QTableWidgetItem

from app.theme import AppTheme

_VERDE = "#22c55e"
_AZUL  = "#3b82f6"
_VERM  = "#ef4444"
_MUTED = "#64748b"


class LancamentoLogic:
    """
    Mixin de lógica — herdado por LancamentoUI.

    Depende de atributos criados por LancamentoLayout e pelo __init__
    de LancamentoUI.
    """

    # =========================================================================
    # Helpers
    # =========================================================================
    def _clear_container_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_container_layout(child_layout)

    def _show_layout_message(self, layout, text, color=_MUTED, size=12):
        self._clear_container_layout(layout)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                background: transparent;
                padding: 20px;
            }}
        """)
        layout.insertWidget(0, lbl)

    # =========================================================================
    # Stats
    # =========================================================================
    def _atualizar_stats(self):
        try:
            s = self.controller.estatisticas()
        except Exception:
            s = {}

        pendentes  = s.get("pendentes", 0)
        lancados   = s.get("lancados", 0)
        urgentes   = s.get("urgentes", 0)
        devolucoes = s.get("devolucoes", 0)
        renovacoes = s.get("renovacoes", 0)
        inscricoes = s.get("inscricoes", 0)

        def _safe_set(lbl, val):
            try:
                if lbl is not None:
                    lbl.setText(str(val))
            except Exception:
                pass

        _safe_set(self._lbl_pendentes, pendentes)
        _safe_set(self._lbl_lancados, lancados)
        _safe_set(self._lbl_urgentes, urgentes)
        _safe_set(getattr(self, "_lbl_devolucoes", None), devolucoes)
        _safe_set(getattr(self, "_lbl_renovacoes", None), renovacoes)
        _safe_set(getattr(self, "_lbl_inscricoes", None), inscricoes)

    # =========================================================================
    # Filtro por tipo
    # =========================================================================
    def _filtrar_por_tipo(self, modo: str, tipo: str):
        """Filtra a tabela pelo tipo/status selecionado."""
        if not hasattr(self, "_filtro_tipo"):
            self._filtro_tipo = {}

        self._filtro_tipo[modo] = tipo

        dados_brutos = getattr(self, f"_dados_{modo}", [])
        layout = getattr(self, f"_tabela_{modo}_layout", None)

        if layout is None:
            return

        self._clear_container_layout(layout)

        if tipo == "TODOS":
            filtrados = dados_brutos
        else:
            filtrados = [
                r for r in dados_brutos
                if (r.get("status") or "").upper() == tipo
                or (r.get("tipo") or "").upper() == tipo
            ]

        if not filtrados:
            tipo_label = {
                "RENOVACAO": "Renovação",
                "INSCRICAO": "Inscrição",
                "DEVOLUCAO": "Devolução",
            }.get(tipo, tipo)
            self._show_layout_message(
                layout,
                f"Nenhum processo do tipo «{tipo_label}» encontrado."
            )
            layout.addStretch()
            return

        for reg in filtrados:
            self._criar_linha(reg, getattr(self, f"_tabela_{modo}", None), modo)

        layout.addStretch()

    # =========================================================================
    # Aba Lista — Falta Revisar / Renovação / Inscrição / Prontos / Devoluções
    # =========================================================================
    def _carregar_modo(self, modo: str):
        if modo == "revisar":
            self._carregar_revisar()
        elif modo == "renovacao":
            self._carregar_renovacao()
        elif modo == "inscricao":
            self._carregar_inscricao()
        elif modo == "prontos":
            self._carregar_prontos()
        else:
            self._carregar_devolucoes()

    def _carregar_revisar(self):
        self._limpar_tabela("revisar")
        self._worker_carregar("revisar")

    def _carregar_renovacao(self):
        self._limpar_tabela("renovacao")
        self._worker_carregar("renovacao")

    def _carregar_inscricao(self):
        self._limpar_tabela("inscricao")
        self._worker_carregar("inscricao")

    def _carregar_prontos(self):
        self._limpar_tabela("prontos")
        self._worker_carregar("prontos")

    def _carregar_devolucoes(self):
        self._limpar_tabela("devolucoes")
        self._worker_carregar("devolucoes")

    def _filtrar_devolucoes(self):
        """Filtra a tabela de devoluções em tempo real pelo termo digitado."""
        entry = getattr(self, "_dev_busca", None)
        termo = entry.text().lower().strip() if entry is not None else ""
        dados = getattr(self, "_dados_devolucoes", [])
        layout = getattr(self, "_tabela_devolucoes_layout", None)

        if layout is None:
            return

        self._clear_container_layout(layout)

        filtrados = dados
        if termo:
            filtrados = [
                r for r in dados
                if termo in (r.get("nome_pdf") or "").lower()
                or termo in (r.get("cpf") or "").lower()
                or termo in (r.get("motivo") or "").lower()
                or termo in (r.get("analisado_por") or "").lower()
            ]

        if not filtrados:
            self._show_layout_message(layout, "Nenhum processo encontrado.")
            layout.addStretch()
            return

        for reg in filtrados:
            self._criar_linha(reg, getattr(self, "_tabela_devolucoes", None), "devolucoes")

        layout.addStretch()

    def _limpar_tabela(self, modo: str):
        layout = getattr(self, f"_tabela_{modo}_layout", None)
        if layout is not None:
            self._show_layout_message(layout, "Carregando...")
            layout.addStretch()

        self._selecionado = None
        self._linha_sel = None
        self._linha_sel_reg = None

    def _worker_carregar(self, modo: str):
        try:
            if modo == "revisar":
                dados = self.controller.carregar_para_revisar()
            elif modo == "renovacao":
                dados = self.controller.carregar_por_tipo("RENOVACAO")
            elif modo == "inscricao":
                dados = self.controller.carregar_por_tipo("INSCRICAO")
            elif modo == "prontos":
                dados = self.controller.carregar_prontos()
            else:
                dados = self.controller.carregar_devolucoes()

            self._preencher_tabela(dados, modo)

        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar:\n{exc}")

    def _preencher_tabela(self, dados: list, modo: str):
        layout = getattr(self, f"_tabela_{modo}_layout", None)
        if layout is None:
            return

        self._clear_container_layout(layout)

        if modo == "revisar":
            self._dados_revisar = dados
        elif modo == "renovacao":
            self._dados_renovacao = dados
        elif modo == "inscricao":
            self._dados_inscricao = dados
        elif modo == "prontos":
            self._dados_prontos = dados
        else:
            self._dados_devolucoes = dados

        self._selecionado = None
        self._linha_sel = None
        self._linha_sel_reg = None

        if not dados:
            msg = (
                "Nenhum processo aguardando revisão."
                if modo == "revisar"
                else "Nenhum processo pronto para impressão."
                if modo == "prontos"
                else "Nenhuma devolução encontrada."
            )
            self._show_layout_message(layout, msg, _MUTED, 13)
            layout.addStretch()
            self._atualizar_stats()
            return

        filtro_ativo = getattr(self, "_filtro_tipo", {}).get(modo, "TODOS")
        if filtro_ativo != "TODOS":
            dados_render = [
                r for r in dados
                if (r.get("status") or "").upper() == filtro_ativo
                or (r.get("tipo") or "").upper() == filtro_ativo
            ]
        else:
            dados_render = dados

        if not dados_render:
            self._show_layout_message(layout, "Nenhum processo encontrado.", _MUTED, 13)
            layout.addStretch()
            self._atualizar_stats()
            return

        for reg in dados_render:
            self._criar_linha(reg, getattr(self, f"_tabela_{modo}", None), modo)

        layout.addStretch()
        self._atualizar_stats()

    # =========================================================================
    # Aba Histórico
    # =========================================================================
    def _carregar_historico(self):
        try:
            self._hist_dados = self.controller.historico()
            self._filtrar_historico()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", str(exc))

    def _filtrar_historico(self):
        termo = self._hist_busca.text().lower().strip() if self._hist_busca else ""
        dados = getattr(self, "_hist_dados", [])

        if termo:
            dados = [
                d for d in dados
                if termo in (d.get("nome_pdf") or "").lower()
                or termo in (d.get("lancado_por") or "").lower()
                or termo in (d.get("analisado_por") or "").lower()
                or termo in (d.get("cpf") or "").lower()
            ]

        self._hist_tree.setRowCount(0)

        for i, r in enumerate(dados):
            row = self._hist_tree.rowCount()
            self._hist_tree.insertRow(row)

            valores = [
                r.get("nome_pdf", "—"),
                r.get("cpf", "—"),
                r.get("analisado_por", "—"),
                r.get("lancado_por", "—"),
                r.get("criado_em", "—"),
            ]

            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                self._hist_tree.setItem(row, col, item)

    def _limpar_cpp(self):
        """Placeholder — lógica de CPP gerenciada pelo módulo bancoantigo."""
        pass