import customtkinter as ctk
from tkinter import messagebox
import ldap3

class Login(ctk.CTkFrame):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.pack(expand=True, fill="both")
        self.configure(fg_color="#0b1220")

        # ================= CARD ANIMADO =================
        self.card = ctk.CTkFrame(
            self,
            width=450,
            height=380,
            corner_radius=20,
            fg_color="#1f2933"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.bind("<Enter>", lambda e: self.card.configure(fg_color="#273449"))
        self.card.bind("<Leave>", lambda e: self.card.configure(fg_color="#1f2933"))

        # ================= TÍTULO =================
        ctk.CTkLabel(
            self.card,
            text="Carteira do\nProdutor Rural",
            font=("Segoe UI", 26, "bold"),
            text_color="#f9fafb",
            justify="center"
        ).pack(pady=(30, 25))

        # ================= ENTRADAS =================
        self.entry_usuario = ctk.CTkEntry(
            self.card,
            placeholder_text="Usuário",
            width=360,
            height=44,
            font=("Segoe UI", 14),
            corner_radius=12,
            fg_color="#0f172a",
            border_color="#334155",
            border_width=1,
            text_color="#f9fafb"
        )
        self.entry_usuario.pack(pady=(0, 20))
        self.entry_usuario.focus()

        self.entry_senha = ctk.CTkEntry(
            self.card,
            placeholder_text="Senha",
            width=360,
            height=44,
            font=("Segoe UI", 14),
            corner_radius=12,
            fg_color="#0f172a",
            border_color="#334155",
            border_width=1,
            text_color="#f9fafb",
            show="*"
        )
        self.entry_senha.pack(pady=(0, 30))

        # ================= BOTÃO =================
        self.btn_login = ctk.CTkButton(
            self.card,
            text="Entrar no Sistema",
            height=50,
            width=360,
            font=("Segoe UI", 15, "bold"),
            corner_radius=12,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.fazer_login
        )
        self.btn_login.pack(pady=(0, 20))
        self.btn_login.bind("<Enter>", lambda e: self.btn_login.configure(fg_color="#3b82f6"))
        self.btn_login.bind("<Leave>", lambda e: self.btn_login.configure(fg_color="#2563eb"))

        # ================= RODAPÉ =================
        ctk.CTkLabel(
            self.card,
            text="SECTOR AUTOMATION",
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        ).pack(pady=(0, 20))

    # ================= LOGIN =================
    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Informe usuário e senha")
            return

        if self.login_ldap(usuario, senha):
            self.on_success(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    # ================= LOGIN LDAP =================
    def login_ldap(self, usuario, senha):
        """
        Autenticação via LDAP.
        Altere LDAP_SERVER, BASE_DN e DOMAIN conforme seu ambiente.
        """
        LDAP_SERVER = "ldap://seu_servidor_ldap"
        BASE_DN = "dc=empresa,dc=com"
        DOMAIN = "EMPRESA"

        try:
            conn = ldap3.Connection(
                LDAP_SERVER,
                user=f"{DOMAIN}\\{usuario}",
                password=senha,
                authentication=ldap3.NTLM,
                auto_bind=True
            )
            if conn.bound:
                conn.unbind()
                return True
        except ldap3.LDAPException as e:
            print("Erro LDAP:", e)
            return False

        return False
