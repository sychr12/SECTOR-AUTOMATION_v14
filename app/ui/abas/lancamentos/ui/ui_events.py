# -*- coding: utf-8 -*-
"""
ui_events.py — Handlers de eventos e ações disparadas pelo usuário (PyQt6).
"""

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QLabel
from PyQt6.QtCore import Qt

_VERDE = "#22c55e"
_VERM  = "#ef4444"
_MUTED = "#64748b"


class LancamentoEvents:

    # =========================================================================
    # Navegação entre abas
    # =========================================================================
    def _on_tab(self):
        try:
            idx = self._nb.currentIndex()
            text = self._nb.tabText(idx).strip()

            if "Revisar" in text or idx == 0:
                self._carregar_revisar()
            elif "Renova" in text or idx == 1:
                self._carregar_renovacao()
            elif "Inscri" in text or idx == 2:
                self._carregar_inscricao()
            elif "Devolu" in text or idx == 3:
                self._carregar_devolucoes()
            elif "Hist" in text or idx == 5:
                self._carregar_historico()
        except Exception:
            pass

    # =========================================================================
    # Seleção de linha na tabela
    # =========================================================================
    def _selecionar_linha(self, reg: dict, frame):
        from app.theme import AppTheme

        if self._linha_sel is not None:
            try:
                reg_ant = self._linha_sel_reg or {}
                urg_ant = reg_ant.get("urgencia", False)
                lan_ant = bool(reg_ant.get("lancado_por"))
                bg_ant = "#1c1007" if urg_ant and not lan_ant else AppTheme.BG_CARD
                self._linha_sel.setStyleSheet(f"background-color: {bg_ant}; border-radius: 10px;")
            except Exception:
                pass

        self._selecionado = reg
        self._linha_sel = frame
        self._linha_sel_reg = reg

        try:
            frame.setStyleSheet("background-color: #1e3a5f; border-radius: 10px;")
        except Exception:
            pass

    # =========================================================================
    # Pasta de origem
    # =========================================================================
    def _selecionar_pasta(self):
        from app.theme import AppTheme

        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de PDFs")
        if pasta:
            self._pasta_origem = pasta
            nome = os.path.basename(pasta)

            for attr in ("_lbl_pasta_revisar", "_lbl_pasta_prontos", "_lbl_pasta_devolucoes"):
                lbl = getattr(self, attr, None)
                if lbl is not None:
                    try:
                        lbl.setText(nome)
                        lbl.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
                    except Exception:
                        pass

    # =========================================================================
    # PDF
    # =========================================================================
    def _abrir_pdf(self, analise_id: int):
        ok, msg = self.controller.abrir_pdf(analise_id)
        if not ok:
            QMessageBox.critical(self, "Erro", msg)

    # =========================================================================
    # Lançamento
    # =========================================================================
    def _lancar_por_cpf(self, event=None):
        cpf_txt = self._entry_cpf.text().strip()
        if not cpf_txt:
            return

        ok, msg = self.controller.registrar_por_cpf(cpf_txt)
        cor = _VERDE if ok else _VERM

        try:
            self._lbl_cpf_status.setText(msg)
            self._lbl_cpf_status.setStyleSheet(f"color: {cor};")
        except Exception:
            pass

        if ok:
            try:
                self._entry_cpf.clear()
            except Exception:
                pass

            self._carregar_revisar()
            self._carregar_prontos()
            self._atualizar_stats()

    def _lancar_linha(self, reg: dict):
        ok, msg = self.controller.enviar_para_impressao(
            analise_id=reg["id"],
            nome_pdf=reg["nome_pdf"],
            pasta_origem=self._pasta_origem,
        )

        if ok:
            self._carregar_revisar()
            self._carregar_prontos()
            self._atualizar_stats()
            QMessageBox.information(self, "Sucesso", msg)
        else:
            QMessageBox.critical(self, "Erro", msg)

    def _enviar_impressao(self):
        if not self._selecionado:
            QMessageBox.warning(self, "Atenção", "Selecione um processo na tabela.")
            return
        self._lancar_linha(self._selecionado)

    # =========================================================================
    # Consulta CPF — eventos de formulário
    # =========================================================================
    def _mascara_consulta_cpf(self):
        if self._aplicando_consulta_cpf:
            return

        self._aplicando_consulta_cpf = True
        try:
            t = self._entry_consulta.text()
            d = "".join(c for c in t if c.isdigit())[:11]

            if len(d) <= 3:
                r = d
            elif len(d) <= 6:
                r = d[:3] + "." + d[3:]
            elif len(d) <= 9:
                r = d[:3] + "." + d[3:6] + "." + d[6:]
            else:
                r = d[:3] + "." + d[3:6] + "." + d[6:9] + "-" + d[9:]

            if r != t:
                self._entry_consulta.blockSignals(True)
                self._entry_consulta.setText(r)
                self._entry_consulta.blockSignals(False)
                self._entry_consulta.setCursorPosition(len(r))
        finally:
            self._aplicando_consulta_cpf = False

    def _executar_consulta_cpf(self, event=None):
        cpf_txt = self._entry_consulta.text().strip()
        if not cpf_txt:
            return

        layout = getattr(self, "_consulta_resultado_layout", None)
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.deleteLater()
                elif child_layout is not None:
                    self._clear_container_layout(child_layout)

            lbl = QLabel("Consultando...")
            lbl.setStyleSheet(f"color: {_MUTED}; font-size: 12px; padding: 20px;")
            layout.insertWidget(0, lbl)
            layout.addStretch()

        resultado = self.controller.consultar_cpf(cpf_txt)
        self._exibir_consulta(resultado, cpf_txt)

    def _limpar_consulta(self):
        try:
            self._entry_consulta.clear()
        except Exception:
            pass

        layout = getattr(self, "_consulta_resultado_layout", None)
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.deleteLater()
                elif child_layout is not None:
                    self._clear_container_layout(child_layout)

            lbl = QLabel("Digite um CPF acima e clique em Consultar.")
            lbl.setStyleSheet(f"color: {_MUTED}; font-size: 13px; padding: 40px;")
            layout.insertWidget(0, lbl)
            layout.addStretch()

    # =========================================================================
    # Máscara CPF — aba registro
    # =========================================================================
    def _mascara_cpf(self):
        if self._aplicando_cpf:
            return

        self._aplicando_cpf = True
        try:
            t = self._entry_cpf.text()
            d = "".join(c for c in t if c.isdigit())[:11]

            if len(d) <= 3:
                r = d
            elif len(d) <= 6:
                r = d[:3] + "." + d[3:]
            elif len(d) <= 9:
                r = d[:3] + "." + d[3:6] + "." + d[6:]
            else:
                r = d[:3] + "." + d[3:6] + "." + d[6:9] + "-" + d[9:]

            if r != t:
                self._entry_cpf.blockSignals(True)
                self._entry_cpf.setText(r)
                self._entry_cpf.blockSignals(False)
                self._entry_cpf.setCursorPosition(len(r))
        finally:
            self._aplicando_cpf = False