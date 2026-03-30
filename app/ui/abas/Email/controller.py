# -*- coding: utf-8 -*-
"""
Controller para download de emails com anexos PDF
"""

import os
import re
import json
import base64
from datetime import datetime
from googleapiclient.errors import HttpError


class EmailDownloadController:
    """Controller para operações de download de email"""

    def __init__(self, base_dir, save_directory, usuario=None):
        self.base_dir         = base_dir
        self.save_directory   = save_directory  # mantido por compatibilidade
        self.usuario          = usuario
        self.labels_cache     = {}
        self.municipios_cache = {}
        self._carregar_configuracoes()

    def _carregar_configuracoes(self):
        """Carrega mapeamento de emails para municípios"""
        path = os.path.join(self.base_dir, "jsons files", "Emails_recebimento.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    self.municipios_cache = data.get("municipios", {})
            except Exception as e:
                print(f"[Controller] Aviso ao carregar configuracoes: {e}")

    def obter_municipio_por_email(self, sender_email: str) -> str:
        """Identifica município pelo email do remetente"""
        for email, municipio in self.municipios_cache.items():
            if email in sender_email:
                return municipio
        return "Desconhecido"

    def formatar_data(self, timestamp) -> str:
        """
        Converte timestamp do Gmail (ms) para string de data.
        Formato: DD-MM-YYYY
        """
        try:
            return datetime.utcfromtimestamp(int(timestamp) / 1000).strftime("%d-%m-%Y")
        except Exception:
            return "Data_Desconhecida"

    def extrair_parts_pdf(self, parts):
        """Percorre partes do email e yielda apenas as que são PDF"""
        for part in parts:
            filename = part.get("filename", "")
            if filename.lower().endswith(".pdf"):
                yield part
            if part.get("parts"):
                yield from self.extrair_parts_pdf(part["parts"])

    def obter_bytes_anexo_pdf(self, service, msg_id: str, part: dict) -> tuple:
        """
        Baixa o anexo PDF e retorna os bytes em memória.
        NÃO salva nada no disco — os bytes vão direto para o banco.

        Retorna: (nome_arquivo: str, dados: bytes, erro: str | None)
        """
        try:
            att = service.users().messages().attachments().get(
                userId="me",
                messageId=msg_id,
                id=part["body"]["attachmentId"],
            ).execute()

            dados = base64.urlsafe_b64decode(att["data"])
            # Sanitiza nome para exibição
            nome = re.sub(r'[\\/:*?"<>|]+', "_", part.get("filename", "anexo.pdf"))
            return nome, dados, None

        except HttpError as e:
            return None, None, f"HttpError {e.resp.status}: {e._get_reason()}"
        except Exception as e:
            return None, None, str(e)

    def buscar_label_id(self, service, label_name: str):
        """Busca e cacheia o ID de uma label do Gmail"""
        if label_name in self.labels_cache:
            return self.labels_cache[label_name]
        try:
            labels = service.users().labels().list(userId="me").execute().get("labels", [])
            for label in labels:
                if label["name"] == label_name:
                    self.labels_cache[label_name] = label["id"]
                    return label["id"]
        except Exception as e:
            print(f"[Controller] Erro ao buscar label '{label_name}': {e}")
        return None

    def marcar_email_como_processado(self, service, msg_id: str, label_name: str) -> bool:
        """Adiciona label ao email para marcá-lo como processado"""
        try:
            label_id = self.buscar_label_id(service, label_name)
            if label_id:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"addLabelIds": [label_id]},
                ).execute()
                return True
        except Exception as e:
            print(f"[Controller] Erro ao marcar email {msg_id}: {e}")
        return False