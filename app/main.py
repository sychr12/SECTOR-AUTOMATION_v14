import os
import sys
import ctypes
import customtkinter as ctk

# eu odeio essa parte sempre da dublicidade
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)


try:
    _orig_ctk_scroll_init = ctk.CTkScrollableFrame.__init__

    def _ctk_scrollable_init_hide_scroll(self, *args, **kwargs):
        _orig_ctk_scroll_init(self, *args, **kwargs)
        for child in self.winfo_children():
            if "scrollbar" in str(type(child)).lower():
                try:
                    child.pack_forget()
                except:
                    try:
                        child.grid_forget()
                    except:
                        pass

    ctk.CTkScrollableFrame.__init__ = _ctk_scrollable_init_hide_scroll
except Exception:
    pass


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.login import Login
from core.menu import AppPrincipal
from core.menu_administrador import MenuAdministrador


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sector Automation")
        self.geometry("1600x900")
        self.minsize(1200, 700)

        self.login_frame = Login(self, self.login_sucesso)

    def login_sucesso(self, usuario):
        self.login_frame.destroy()

        perfil = usuario.get("perfil", "usuario")

        
        self.withdraw()

        if perfil in ("administrador", "chefe"):
            win = MenuAdministrador(usuario, master=self)
        else:
            win = AppPrincipal(usuario, master=self)

        
        win.deiconify()
        win.lift()
        win.focus_force()

        self.wait_window(win)

        
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()