import customtkinter as ctk
from tkinter import messagebox
from desktop_client.api import TaskAPIClient

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

API = TaskAPIClient()

COLORS = {
    "bg_dark": "#0D1117",
    "bg_card": "#161B22",
    "bg_input": "#21262D",
    "border": "#30363D",
    "text": "#E6EDF3",
    "text_dim": "#8B949E",
    "accent": "#3FB950",
    "accent_hover": "#2EA043",
    "danger": "#DA3633",
    "danger_hover": "#C62828",
    "warning": "#D29922",
    "info": "#58A6FF",
    "pending": "#D29922",
    "in_progress": "#58A6FF",
    "completed": "#3FB950",
}

FONT_TITLE = ("Inter", 26, "bold")
FONT_HEADING = ("Inter", 18, "bold")
FONT_BODY = ("Inter", 14)
FONT_SMALL = ("Inter", 12)
FONT_TINY = ("Inter", 11)

STATUS_ICONS = {"pending": "\u25CB", "in_progress": "\u25D0", "completed": "\u25CF"}
STATUS_LABELS = {"pending": "Pendente", "in_progress": "Em andamento", "completed": "Concluida"}


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TaskFlow")
        self.geometry("460x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])

        self.grid_columnconfigure(0, weight=1)

        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(50, 25), padx=40, sticky="ew")
        ctk.CTkLabel(logo_frame, text="TaskFlow", font=FONT_TITLE, text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(logo_frame, text="Organize sua vida, uma tarefa por vez", font=FONT_SMALL, text_color=COLORS["text_dim"]).pack(pady=(4, 0))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="ew", padx=40)

        fields = [
            ("Email", "seu@email.com", False),
            ("Usuario", "seu usuario", False),
            ("Senha", "minimo 3 caracteres", True),
        ]

        self.entries = {}
        for placeholder, show in [(f[0], f[2]) for f in fields]:
            container = ctk.CTkFrame(content, fg_color=COLORS["bg_input"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            container.pack(fill="x", pady=(0, 12))

            inner = ctk.CTkFrame(container, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            display = placeholder  # unused but kept for clarity
            ctk.CTkLabel(inner, text=placeholder, font=FONT_TINY, text_color=COLORS["text_dim"]).pack(anchor="w")

            entry = ctk.CTkEntry(inner, font=FONT_BODY, fg_color="transparent", border_width=0, placeholder_text="",
                                 height=28, show="*" if show else "")
            entry.pack(fill="x", pady=(2, 0))

            self.entries[placeholder] = entry

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(btn_frame, text="Entrar", font=FONT_BODY, height=44, corner_radius=10,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      command=self._login).pack(fill="x")

        divider = ctk.CTkFrame(content, fg_color="transparent")
        divider.pack(fill="x", pady=(16, 16))
        ctk.CTkLabel(divider, text="ou", font=FONT_SMALL, text_color=COLORS["text_dim"]).pack()

        ctk.CTkButton(btn_frame, text="Criar conta", font=FONT_BODY, height=44, corner_radius=10,
                      fg_color="transparent", border_width=1, border_color=COLORS["border"],
                      hover_color=COLORS["bg_card"], command=self._do_register).pack(fill="x")

        self.status_label = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=COLORS["text_dim"])
        self.status_label.grid(row=2, column=0, pady=(16, 0))
        self.bind("<Return>", lambda _: self._login())

    def _get_values(self):
        return {
            "email": self.entries["Email"].get().strip(),
            "username": self.entries["Usuario"].get().strip(),
            "password": self.entries["Senha"].get().strip(),
        }

    def _login(self):
        vals = self._get_values()
        if not vals["email"] or not vals["password"]:
            self._status("Preencha email e senha.", COLORS["warning"])
            return
        try:
            API.login(vals["email"], vals["password"])
            self._status("Conectado com sucesso!", COLORS["accent"])
            self.after(400, self._open_main)
        except RuntimeError as e:
            self._status(str(e), COLORS["danger"])

    def _do_register(self):
        vals = self._get_values()
        if not all(vals.values()):
            self._status("Preencha todos os campos.", COLORS["warning"])
            return
        if len(vals["password"]) < 3 or len(vals["username"]) < 3:
            self._status("Senha e usuario precisam de pelo menos 3 caracteres.", COLORS["warning"])
            return
        try:
            API.register(**vals)
            API.login(vals["email"], vals["password"])
            messagebox.showinfo("Conta criada!", f"Bem-vindo, {vals['username']}!\nSua conta foi criada com sucesso.")
            self.after(200, self._open_main)
        except RuntimeError as e:
            self._status(str(e), COLORS["danger"])

    def _open_main(self):
        self.destroy()
        MainWindow().mainloop()

    def _status(self, text: str, color: str):
        self.status_label.configure(text=text, text_color=color)
        if color == COLORS["danger"]:
            self.after(5000, lambda: self.status_label.configure(text=""))


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, task: dict | None = None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.task = task
        is_edit = task is not None

        self.title("Editar Tarefa" if is_edit else "Nova Tarefa")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()
        self.after(10, self._center)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 12))
        ctk.CTkLabel(header, text=self.title(), font=FONT_HEADING, text_color=COLORS["text"]).pack(side="left")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24)

        ctk.CTkLabel(body, text="Titulo", font=FONT_SMALL, text_color=COLORS["text_dim"]).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(body, font=FONT_BODY, fg_color=COLORS["bg_input"], border_width=1,
                                        border_color=COLORS["border"], corner_radius=8, height=40)
        self.title_entry.pack(fill="x", pady=(4, 12))
        if is_edit:
            self.title_entry.insert(0, task["title"])

        ctk.CTkLabel(body, text="Descricao", font=FONT_SMALL, text_color=COLORS["text_dim"]).pack(anchor="w")
        self.desc_entry = ctk.CTkEntry(body, font=FONT_BODY, fg_color=COLORS["bg_input"], border_width=1,
                                       border_color=COLORS["border"], corner_radius=8, height=40)
        self.desc_entry.pack(fill="x", pady=(4, 12))
        if is_edit and task.get("description"):
            self.desc_entry.insert(0, task["description"])

        ctk.CTkLabel(body, text="Status", font=FONT_SMALL, text_color=COLORS["text_dim"]).pack(anchor="w")
        status_frame = ctk.CTkFrame(body, fg_color="transparent")
        status_frame.pack(fill="x", pady=(4, 8))

        statuses = list(STATUS_LABELS.items())
        self.status_var = ctk.StringVar(value=task["status"] if is_edit else "pending")
        for i, (key, label) in enumerate(statuses):
            color = COLORS.get(key, COLORS["accent"])
            btn = ctk.CTkButton(status_frame, text=label, font=FONT_SMALL, width=135, height=34,
                                corner_radius=8, fg_color=color if self.status_var.get() == key else COLORS["bg_input"],
                                hover_color=color, border_width=1,
                                border_color=color if self.status_var.get() != key else "transparent",
                                command=lambda k=key: self._select_status(k))
            btn.pack(side="left", padx=(0 if i == 2 else 6, 0))

        self._status_btns = {key: btn for (key, _), btn in zip(statuses, [c for c in status_frame.winfo_children()])}

        ctk.CTkButton(self, text="Salvar alteracoes" if is_edit else "Criar tarefa",
                      font=FONT_BODY, height=44, corner_radius=10, fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      command=self._save).pack(fill="x", padx=24, pady=(8, 24))

        self.title_entry.focus_set()
        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _center(self):
        self.update_idletasks()
        pw, ph = self.master.winfo_width(), self.master.winfo_height()
        mx, my = self.master.winfo_x(), self.master.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = mx + (pw - w) // 2
        y = my + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _select_status(self, key: str):
        self.status_var.set(key)
        for k, btn in self._status_btns.items():
            if k == key:
                btn.configure(fg_color=COLORS[k], border_width=0)
            else:
                btn.configure(fg_color=COLORS["bg_input"], border_width=1)

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Campo obrigatorio", "O titulo da tarefa e obrigatorio.")
            return
        try:
            if self.task:
                API.update_task(self.task["id"], title=title, description=self.desc_entry.get(),
                                status=self.status_var.get())
            else:
                API.create_task(title, self.desc_entry.get(), self.status_var.get())
            if self.callback:
                self.callback()
            self.destroy()
        except RuntimeError as e:
            messagebox.showerror("Erro", str(e))


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TaskFlow")
        self.geometry("820x620")
        self.minsize(680, 450)
        self.configure(fg_color=COLORS["bg_dark"])
        self._center()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._build_header()
        self._build_task_list()
        self._build_footer()

        self.tasks = []
        self._load()
        self.bind("<Control-n>", lambda _: self._add_task())
        self.bind("<Control-r>", lambda _: self._load())

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)

        ctk.CTkLabel(inner, text="TaskFlow", font=FONT_HEADING, text_color=COLORS["accent"]).pack(side="left")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")

        statuses = [("Todas", None)] + [(STATUS_LABELS[k], k) for k in ["pending", "in_progress", "completed"]]
        self.filter_var = ctk.StringVar(value="Todas")
        for i, (label, key) in enumerate(statuses):
            btn = ctk.CTkButton(right, text=label, font=FONT_SMALL, width=100, height=32, corner_radius=8,
                                fg_color=COLORS["accent"] if key is None else COLORS["bg_input"],
                                hover_color=COLORS["accent_hover"], border_width=0,
                                command=lambda k=key: self._set_filter(k))
            btn.pack(side="left", padx=(0 if i == 3 else 4, 0))

        self._filter_btns = {key: btn for (_, key), btn in zip(statuses, right.winfo_children())}

        if API.is_admin:
            ctk.CTkButton(inner, text="Admin", font=FONT_SMALL, width=80, height=32, corner_radius=8,
                          fg_color=COLORS["warning"], hover_color="#C69020",
                          command=self._open_admin).pack(side="right", padx=(0, 8))

        ctk.CTkButton(inner, text="+ Nova Tarefa", font=FONT_SMALL, width=130, height=32, corner_radius=8,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      command=self._add_task).pack(side="right", padx=(16, 0))

    def _set_filter(self, key: str | None):
        self.filter_var.set(key or "Todas")
        for k, btn in self._filter_btns.items():
            btn.configure(fg_color=COLORS["accent"] if k == key else COLORS["bg_input"])
        self._render()

    def _build_task_list(self):
        self.task_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_fg_color=COLORS["bg_card"],
                                                 scrollbar_button_color=COLORS["bg_input"],
                                                 scrollbar_button_hover_color=COLORS["border"])
        self.task_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(12, 8))

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        ctk.CTkLabel(footer, text="Ctrl+N Nova  |  Ctrl+R Atualizar  |  Esc Fechar", font=FONT_TINY,
                     text_color=COLORS["text_dim"]).pack(side="left")
        self.count_label = ctk.CTkLabel(footer, text="", font=FONT_TINY, text_color=COLORS["text_dim"])
        self.count_label.pack(side="right")

    def _load(self):
        try:
            self.tasks = API.list_tasks()
        except RuntimeError as e:
            messagebox.showerror("Erro de conexao",
                                 f"Nao foi possivel conectar ao servidor.\n\n{e}\n\nVerifique se 'make run' esta rodando em outro terminal.",
                                 parent=self)
            return
        self._render()

    def _render(self):
        for w in self.task_frame.winfo_children():
            w.destroy()

        status_filter = self.filter_var.get()
        if status_filter != "Todas":
            filtered = [t for t in self.tasks if t["status"] == status_filter]
        else:
            filtered = self.tasks

        self.count_label.configure(text=f"{len(filtered)} tarefa(s)")

        if not filtered:
            empty_frame = ctk.CTkFrame(self.task_frame, fg_color="transparent")
            empty_frame.pack(expand=True)
            ctk.CTkLabel(empty_frame, text="\U0001F4CB", font=("Inter", 48)).pack()
            ctk.CTkLabel(empty_frame, text="Nenhuma tarefa encontrada", font=FONT_BODY, text_color=COLORS["text_dim"]).pack(pady=(8, 2))
            ctk.CTkLabel(empty_frame, text='Clique em "+ Nova Tarefa" para comecar', font=FONT_SMALL, text_color=COLORS["border"]).pack()
            return

        for task in filtered:
            self._render_card(task)

    def _render_card(self, task: dict):
        status = task["status"]
        color = COLORS.get(status, COLORS["accent"])
        icon = STATUS_ICONS.get(status, "\u25CF")

        card = ctk.CTkFrame(self.task_frame, fg_color=COLORS["bg_card"], corner_radius=12,
                            border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=3)

        color_strip = ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=0)
        color_strip.pack(side="left", fill="y", padx=(0, 0))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=task["title"], font=FONT_BODY, text_color=COLORS["text"]).pack(side="left")
        badge = ctk.CTkLabel(top, text=f"  {icon} {STATUS_LABELS.get(status, status)}  ", font=FONT_TINY,
                             text_color=color, fg_color=COLORS["bg_input"], corner_radius=6)
        badge.pack(side="right")

        if task.get("description"):
            ctk.CTkLabel(content, text=task["description"], font=FONT_SMALL, text_color=COLORS["text_dim"],
                         anchor="w", wraplength=600).pack(anchor="w", pady=(4, 6))
        else:
            spacer = ctk.CTkFrame(content, fg_color="transparent", height=4)
            spacer.pack()

        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(bottom, text=f"Criado em {task['created_at'][:10]}", font=FONT_TINY,
                     text_color=COLORS["border"]).pack(side="left")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=(0, 10), pady=10)

        ctk.CTkButton(actions, text="Editar", font=FONT_TINY, width=56, height=28, corner_radius=6,
                      fg_color=COLORS["info"], hover_color="#4090D0",
                      command=lambda t=task: self._edit(t)).pack(pady=(0, 4))
        ctk.CTkButton(actions, text="Excluir", font=FONT_TINY, width=56, height=28, corner_radius=6,
                      fg_color="transparent", border_width=1, border_color=COLORS["danger"],
                      hover_color=COLORS["danger"],
                      command=lambda t=task: self._delete(t)).pack()

    def _add_task(self):
        TaskDialog(self, callback=self._load)

    def _edit(self, task):
        TaskDialog(self, task=task, callback=self._load)

    def _delete(self, task):
        if messagebox.askyesno("Confirmar exclusao", f'Tem certeza que deseja excluir "{task["title"]}"?', parent=self):
            try:
                API.delete_task(task["id"])
                self._load()
            except RuntimeError as e:
                messagebox.showerror("Erro", str(e), parent=self)


    def _open_admin(self):
        AdminPanel(self)


class AdminPanel(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Painel Admin - Usuarios")
        self.geometry("600x450")
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()

        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=56)
        header.pack(fill="x")
        header.grid_propagate(False)
        inner_h = ctk.CTkFrame(header, fg_color="transparent")
        inner_h.pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(inner_h, text="Usuarios Cadastrados", font=FONT_HEADING, text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(inner_h, text="Atualizar", font=FONT_SMALL, width=90, height=28, corner_radius=6,
                      fg_color="transparent", border_width=1, border_color=COLORS["border"],
                      command=self._load).pack(side="right")

        self.user_list = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                scrollbar_fg_color=COLORS["bg_card"],
                                                scrollbar_button_color=COLORS["bg_input"],
                                                scrollbar_button_hover_color=COLORS["border"])
        self.user_list.pack(fill="both", expand=True, padx=20, pady=(12, 20))

        self._load()
        self.bind("<Escape>", lambda _: self.destroy())

    def _load(self):
        for w in self.user_list.winfo_children():
            w.destroy()
        try:
            users = API.list_users()
        except RuntimeError as e:
            messagebox.showerror("Erro", str(e), parent=self)
            return

        for user in users:
            card = ctk.CTkFrame(self.user_list, fg_color=COLORS["bg_card"], corner_radius=10,
                                border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=2)

            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=14, pady=10)

            top = ctk.CTkFrame(content, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=user["username"], font=FONT_BODY, text_color=COLORS["text"]).pack(side="left")

            if user.get("is_admin"):
                ctk.CTkLabel(top, text="  ADMIN", font=FONT_TINY, text_color=COLORS["warning"],
                             fg_color=COLORS["bg_input"], corner_radius=6).pack(side="right")

            ctk.CTkLabel(content, text=user["email"], font=FONT_SMALL, text_color=COLORS["text_dim"]).pack(anchor="w", pady=(4, 2))
            ctk.CTkLabel(content, text=f"ID: {user['id']}  |  Criado em: {user['created_at'][:10]}",
                         font=FONT_TINY, text_color=COLORS["border"]).pack(anchor="w")


def main():
    try:
        app = LoginWindow()
        app.mainloop()
    except RuntimeError:
        messagebox.showerror("Erro de conexao",
                             "Nao foi possivel conectar ao servidor.\n\n"
                             "Certifique-se de que o servidor esta rodando:\n"
                             "  make run\n\n"
                             "Execute em outro terminal e tente novamente.")
    except Exception as e:
        messagebox.showerror("Erro inesperado", str(e))


if __name__ == "__main__":
    main()
