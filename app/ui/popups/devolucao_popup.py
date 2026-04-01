# -*- coding: utf-8 -*-
"""
Popup para seleção de motivo de devolução
"""
import customtkinter as ctk
from tkinter import messagebox, StringVar


class DevolucaoPopup(ctk.CTkToplevel):
    """Janela popup para selecionar motivo de devolução"""

    def __init__(self, parent, on_confirmar):
        super().__init__(parent)

        # ---------------- JANELA ----------------
        self.transient(parent)
        self.grab_set()
        self.focus_force()

        # FECHAR CORRETAMENTE PELO X
        self.protocol("WM_DELETE_WINDOW", self._fechar)

        self.on_confirmar = on_confirmar
        self.motivos = self._carregar_motivos()
        self.radio_buttons = []

        self.title("Motivo da Devolução")
        self.geometry("1100x520")
        self.resizable(False, False)

        self.motivo_var = StringVar(value="")

        self._criar_layout()

        # 🔒 GARANTE QUE O LAYOUT EXISTE
        self.update_idletasks()

        # 🔒 PRECARREGA PRIMEIRA CATEGORIA
        if self.motivos:
            primeira = next(iter(self.motivos))
            self.after(100, lambda: self._mostrar_motivos(primeira))

    # ======================================================
    # DADOS
    # ======================================================
    def _carregar_motivos(self):
        """Carrega os motivos de devolução organizados por categoria"""
        return {
            "Endereço": [
                "NOME DA COMUNIDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "CORRIGIR A COORDENADAS, NÃO SÃO DO ENDEREÇO DESCRITO;",
                "ENDEREÇO INCOMPLETO, FALTA A COMUNIDADE OU SE É PRODUTOR ISOLADO;",
                "ENVIAR COMO ALTERAÇÃO DE ENDEREÇO;",
                "FALTA O KM DA RODOVIA;",
                "FALTA O KM DA ESTRADA;",
                "FALTA O KM DO RAMAL;",
                "FALTA O KM DA VICINAL;",
                "COORDENADAS E ENDEREÇO ESTÃO DIVERGENTES;",
                "ENDEREÇO ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "COORDENADAS INVÁLIDAS, CORRIGIR;",
                "O ENDEREÇO DA ÁREA DA PESCA ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "AS COORDENADAS ESTÃO INCORRETAS;",
                "FALTA A COMUNIDADE NA DECLARAÇÃO;",
                "ENDEREÇO DIVERGENTE DA CPP, CORRIGIR OU ENVIAR COMO ALTERAÇÃO;"
            ],
            "Documentos": [
                "ENVIAR OUTRO DOCUMENTO DE IDENTIFICAÇÃO, RG, OU HABILITAÇÃO, ETC;",
                "FALTA UM DOCUMENTO DE IDENTIFICAÇÃO COM FOTO;",
                "NA RG ELE NÃO ASSINA E ASSINOU NA FAC, ENTÃO APRESENTAR UM DOCUMENTO DE IDENTIDADE COM ASSINATURA;",
                "CORRIGIR O NÚMERO DO RG NA FAC;",
                "NÚMERO DO RG DIVERGENTE DO DOCUMENTO;",
                "NOME ESTÁ DIVERGENTE ENTRE RG E CPF, ATUALIZAR DOCUMENTOS;",
                "CORRIGIR, DIVERGENTE DA RG;",
                "FRENTE DO RG ESTÁ ILEGÍVEL;",
                "FALTA O RG NA DECLARAÇÃO;",
                "COPIA DO RG ESTÁ ILEGÍVEL;",
                "ASSINATURA NA RG ESTÁ ILEGÍVEL;",
                "FALTA A AUTENTICAÇÃO DO CONTRATO;",
                "CORRIGIR CPF, DIVERGENTE DOS DOCUMENTOS PESSOAIS;",
                "CONTRATO DE COMODATO NÃO PODE SER POR TEMPO INDETERMINADO, PRECISA TER UM PRAZO ESTIPULADO;",
                "COM A NOVA DATA DE VALIDADE DA CPP DE 4 ANOS, DESSA FORMA, OS CONTRATOS DEVEM TER O PRAZO DE NO MÍNIMO 4 ANOS DE VALIDADE;",
                "FALTA O TERMO DE EXTRATIVISMO;",
                "ENVIAR O COMPROVANTE DA SITUAÇÃO CADASTRAL NO CPF (DO SITE DA RECEITA FEDERAL);",
                "A SITUAÇÃO CADASTRAL ESTÁ 'SUSPENSA', REGULARIZAR O CPF PERANTE A RECEITA FEDERAL;",
                "ENVIAR CÓPIA DE UMA DOCUMENTAÇÃO COM FOTO E ASSINATURA;",
                "NECESSITA DO BOLETIM DE OCORRÊNCIA EMITIDO PELA POLICIA CIVIL (SECRETARIA DE SEGURANÇA PÚBLICA);",
                "FALTA A FOLHA DE SOLICITAÇÃO DE BAIXA DE INCRIÇÃO ESTADUAL;",
                "CARTEIRA DE TRABALHO TRANSCRITA A MÃO, NÃO É VÁLIDA;"
            ],
            "Cadastro": [
                "CORRIGIR O NOME DA PRODUTORA NA DECLARAÇÃO;",
                "JÁ POSSUI CADASTRO, ENVIAR COMO ALTERAÇÃO OU RENOVAÇÃO, ENVIAR A CÓPIA DA CPP OU O B.O.;",
                "CORRIGIR A DATA NA DECLARAÇÃO;",
                "ENVIAR TAMBEM A FAC DIGITALIZADA;",
                "ENVIAR COMO ALTERAÇÃO, ENVIAR A CÓPIA DA CPP OU O BO;",
                "MANTER O Nº DE CONTROLE JÁ UTILIZADO 0000;",
                "ENVIADO NO MEMO Nº;",
                "ATUALIZAR A FAC E A DECLARAÇÃO, ESTÃO COM DATA SUPERIOR A 6 MESES;",
                "NÚMERO DE CONTROLE DIVERGENTE DA CPP;",
                "NÚMERO DE CONTROLE DIVERGENTE NA DECLARAÇÃO;",
                "NÚMERO DE CONTROLE ESTÁ DIVERGENTE ENTRE DECLARAÇÃO E FAC;",
                "ESTÁ SEM O NÚMERO DE CONTROLE;",
                "NOME DA PROPRIEDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "NOME DA PROPRIEDADE ESTÁ DIVERGENTE DA CPP;",
                "ESPECIFICAR A CULTURA SECUNDÁRIA;",
                "ESPECIFICAR A CULTURA; ESPECIFICAR 1ª CULTURA; ESPECIFICAR 2ª CULTURA;",
                "AS DUAS ATIVIDADES ESTÃO DIVERGENTES ENTRE FAC E DECLARAÇÃO;",
                "COLOCAR A COMUNIDADE NA DECLARAÇÃO;",
                "COMUNIDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "DIVERGENTE DA CPP;",
                "CORRIGIR O ANO EM QUE O PRODUTOR COMEÇOU A SER ASSISTIDO, NO ANO EM QUESTÃO ELE ERA DE MENOR;",
                "NÚMERO DE CONTROLE NÃO SEQUENCIAL, É UMA INSCRIÇÃO;",
                "ENVIAR COMO ALTERAÇÃO, HOUVE MUDANÇA NO SOBRENOME;",
                "ENVIAR COMO ALTERAÇÃO DE ATIVIDADE;",
                "ENVIAR COMO ALTERAÇÃO;",
                "ENVIAR A FAC DE ALTERAÇÃO DE SIGLA E Nº DE CONTROLE;",
                "FALTA O NOME DA PROPRIEDADE NA DECLARAÇÃO;",
                "FALTA O CARIMBO DO GERENTE;",
                "FALTA A ASSINATURA DO GERENTE;",
                "FALTA A ASSINATURA DO PRODUTOR NA FAC;",
                "NOME INCOMPLETO NA DECLARAÇÃO;",
                "NOME DO PRODUTOR ESTÁ DIVERGENTE ENTRE DECLARAÇÃO E FAC;",
                "FALTA A ASSINATURA DA PRODUTORA NA FAC;",
                "CORRIGIR A SIGLA DO MUNICIPIO;",
                "ASSINATURA DO PRODUTOR ESTÁ DIVERGENTE DA RG;",
                "ATUALIZAR A DATA NA DECLARAÇÃO, ESTÁ SUPERIOR A 6 MESES;",
                "A PRODUÇÃO TOTAL ESTÁ DIVERGENTE COM A QUANTIDADE TOTAL DE PEIXES, CORRIGIR;",
                "SEM ASSINATURA E CARIMBO DO GERENTE E TÉCNICO;",
                "APAGAR O NUMERO DA INSCRIÇÃO ESTADUAL NA FAC, É UMA INSCRIÇÃO;"
            ],
            "Pesca": [
                "REGISTRO DE PESCADOR NÃO ENCONTRADO NO SITE DO MINISTÉRIO DA PESCA E AGRICULTURA, APRESENTAR A CARTEIRA DE PESCADOR ATUAL;",
                "ESPECIFICAR AS ESPÉCIES E AS QUANTIDADES DE PEIXES E A ÁREA DA PISCICULTURA;",
                "FALTA A ÁREA DA PISCICULTURA;"
            ],
            "Simples Nacional": [
                "FALTA DAR A BAIXA;",
                "SIMPLES NACIONAL ATIVO;",
                "SIMPLES NACIONAL SUSPENSO;"
            ],
            "Animais": [
                "FALTA A QUANTIDADE DE FRANGOS;",
                "FALTA A QUANTIDADE E AS ESPÉCIES DE PEIXES;",
                "ENVIAR O COMPROVANTE DE SITUAÇÃO CADASTRAL NO CPF (DO SITE DA RECEITA FEDERAL) E ANEXAR AOS PROCESSOS DOS PRODUTORES;"
            ]
        }

    # ======================================================
    # LAYOUT
    # ======================================================
    def _criar_layout(self):
        """Cria o layout do popup"""
        container = ctk.CTkFrame(self, corner_radius=14)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container,
            text="Selecione o motivo da devolução",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w", pady=(0, 16))

        corpo = ctk.CTkFrame(container, fg_color="transparent")
        corpo.pack(fill="both", expand=True)

        # Coluna de categorias
        col_cat = ctk.CTkFrame(corpo, width=260, corner_radius=12)
        col_cat.pack(side="left", fill="y", padx=(0, 14))
        col_cat.pack_propagate(False)

        ctk.CTkLabel(
            col_cat,
            text="Categoria",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.lista_categorias = ctk.CTkScrollableFrame(col_cat, corner_radius=10)
        self.lista_categorias.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        for categoria in self.motivos:
            ctk.CTkButton(
                self.lista_categorias,
                text=categoria,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="#1f2937",
                hover_color="#374151",
                command=lambda c=categoria: self._mostrar_motivos(c),
            ).pack(fill="x", pady=4)

        # Coluna de motivos
        col_mot = ctk.CTkFrame(corpo, corner_radius=12)
        col_mot.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            col_mot,
            text="Motivo",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.scroll_motivos = ctk.CTkScrollableFrame(col_mot, corner_radius=10)
        self.scroll_motivos.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Rodapé
        rodape = ctk.CTkFrame(container, fg_color="transparent")
        rodape.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            rodape,
            text="Confirmar",
            height=38,
            corner_radius=8,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self._confirmar,
        ).pack(side="right")

        ctk.CTkButton(
            rodape,
            text="Cancelar",
            height=38,
            corner_radius=8,
            fg_color="#64748b",
            hover_color="#475569",
            command=self._fechar,
        ).pack(side="right", padx=(0, 10))

    # ======================================================
    # AÇÕES
    # ======================================================
    def _mostrar_motivos(self, categoria):
        """Exibe os motivos de uma categoria"""
        # Limpa a seleção atual
        self.motivo_var.set("")

        # Remove referências antigas dos RadioButtons
        self.radio_buttons.clear()

        # Remove todos os widgets anteriores de forma segura
        try:
            for w in self.scroll_motivos.winfo_children():
                try:
                    w.pack_forget()
                    w.destroy()
                except:
                    pass
        except:
            pass

        # Força atualização
        self.scroll_motivos.update_idletasks()

        # Adiciona os novos motivos
        motivos_list = self.motivos.get(categoria, [])
        
        if not motivos_list:
            ctk.CTkLabel(
                self.scroll_motivos,
                text="Nenhum motivo disponível",
                text_color="#64748b",
            ).pack(pady=20)
            return

        for motivo in motivos_list:
            rb = ctk.CTkRadioButton(
                self.scroll_motivos,
                text=motivo,
                variable=self.motivo_var,
                value=motivo,
                font=("Segoe UI", 13),
            )
            rb.pack(anchor="w", pady=6, padx=10, fill="x")
            self.radio_buttons.append(rb)

    def _confirmar(self):
        """Confirma a seleção do motivo"""
        motivo = self.motivo_var.get()

        if not motivo:
            messagebox.showwarning("Atenção", "Selecione um motivo.")
            return

        self.on_confirmar(motivo)
        self._fechar()

    def _fechar(self):
        """Fecha o popup de forma segura"""
        # Limpa RadioButtons antes de fechar
        try:
            self.radio_buttons.clear()
            
            # Remove widgets do scroll_motivos de forma segura
            for w in self.scroll_motivos.winfo_children():
                try:
                    w.pack_forget()
                except:
                    pass
        except:
            pass
        
        # Libera o grab
        try:
            self.grab_release()
        except:
            pass
        
        # Destroi a janela
        try:
            self.destroy()
        except:
            pass