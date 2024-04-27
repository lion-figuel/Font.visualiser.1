import tkinter as tk
from tkinter import ttk, PhotoImage
import tkinter.simpledialog
from tkinter import font
import json
import sys
import os

def resource_path(relative_path):
    """ Obtient le chemin absolu vers une ressource, nécessaire pour PyInstaller """
    try:
        # Si l'application est empaquetée, le chemin d'accès à la base est celui du répertoire temporaire de l'exécutable
        base_path = sys._MEIPASS
    except Exception:
        # Sinon, c'est le chemin d'accès normal du répertoire de travail
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FontViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Manager")
        self.root.configure(bg="#F2F2F2")
        self.fonts = font.families()
        self.favorite_fonts = []
        self.custom_folders = {}

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Black.TButton', foreground='#2f2f2f', background='#d7d7d7')
        self.style.map('Black.TButton', foreground=[('active', 'black')])

        font_list_frame = tk.Frame(self.root, bg="#F2F2F2")
        font_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.font_listbox = tk.Listbox(font_list_frame, selectmode=tk.SINGLE, bg='#d0d0d0', fg='#2f2f2f', font=('Arial', 10))
        self.font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(font_list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.config(command=self.font_listbox.yview)
        self.font_listbox.config(yscrollcommand=self.scrollbar.set)

        self.font_listbox.bind('<<ListboxSelect>>', self.show_font)
        self.font_listbox.bind("<Button-3>", self.show_context_menu)
        self.font_listbox.bind("<Button-1>", self.show_fonts_in_folder)

        for f in sorted(self.fonts):
            self.font_listbox.insert(tk.END, f)

        self.default_text = "Portez ce vieux whisky au juge blond qui fume"
        self.text_label = tk.Label(self.root, text=self.default_text, font=("Arial", 30), bg="#F2F2F2", fg="#2f2f2f")
        self.text_label.pack(pady='250')

        text_button_frame = tk.Frame(self.root, bg="#F2F2F2", name='text_button_frame')
        text_button_frame.pack(side=tk.TOP, pady=10)

        self.font_size_scale = tk.Scale(text_button_frame, from_=10, to=40, orient=tk.HORIZONTAL, length=200, label='    ', command=self.update_font_size, troughcolor="#F2F2F2", bg="#F2F2F2", highlightthickness=0)
        self.font_size_scale.set(30)
        self.font_size_scale.pack(side=tk.TOP, padx=10)

        self.text_entry = tk.Entry(text_button_frame, bg='#d0d0d0', fg='#2f2f2f', font=('Arial', 12))
        self.text_entry.insert(0, self.default_text)
        self.text_entry.pack(pady=5, padx=10, ipadx=100)
        self.text_entry.bind("<Key>", self.limit_characters)
        self.text_entry.bind("<KeyRelease>", self.update_text_in_real_time)

        self.add_folder_button = ttk.Button(text_button_frame, text="Ajouter un dossier", command=self.add_custom_folder, style='Black.TButton')
        self.add_folder_button.pack(side=tk.TOP, padx=15)

        self.preview_frame = tk.Frame(self.root, bg="#F2F2F2")
        self.preview_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        app_width = self.root.winfo_screenwidth() // 3
        self.preview_frame.config(width=app_width)

        self.search_font_entry = tk.Entry(self.font_listbox, bg='#F2F2F2', fg='#2f2f2f', font=('Arial', 10))
        self.search_font_entry.pack(side=tk.BOTTOM, pady=5, padx=10, ipadx=100)
        self.search_font_entry.bind("<KeyRelease>", self.search_fonts)

        self.load_data()

        self.black_square = tk.Canvas(self.root, width=30, height=30, bg="black", highlightthickness=0)
        self.black_square.place(relx=1, rely=0, anchor="ne")
        self.black_square.bind("<Button-1>", self.change_theme)

        # Charger les icônes pour les thèmes
        self.icon_night = PhotoImage(file=resource_path("Night.png"))
        self.icon_day = PhotoImage(file=resource_path("Day.png"))

        # Initialiser l'icône par défaut
        self.theme_icon = tk.Label(self.root, image=self.icon_night, bg="#F2F2F2")
        self.theme_icon.place(relx=1, rely=0, anchor="ne")
        self.theme_icon.bind("<Button-1>", self.change_theme)  # Lier le clic à la méthode change_theme

    def change_theme(self, event):
        current_bg_color = self.root.cget("bg")
        if current_bg_color == "#F2F2F2":  # Thème clair à thème sombre
            new_bg_color = "#0A0A0A"
            new_fg_color = "#d5d5d5"
            new_trough_color = "#333333"
            button_bg_color = "#000000"
            button_fg_color = "#FFFFFF"
            self.theme_icon.config(image=self.icon_day)  # Utiliser l'icône Day
        else:  # Thème sombre à thème clair
            new_bg_color = "#F2F2F2"
            new_fg_color = "#2f2f2f"
            new_trough_color = "#d0d0d0"
            button_bg_color = "#d7d7d7"
            button_fg_color = "#2f2f2f"
            self.theme_icon.config(image=self.icon_night)  # Revenir à l'icône Night

        # Appliquer les nouvelles couleurs à tous les widgets pertinents
        self.apply_theme_to_widgets(self.root, new_bg_color, new_fg_color, new_trough_color)
        self.style.configure('Black.TButton', background=button_bg_color, foreground=button_fg_color)

    def apply_theme_to_widgets(self, widget, bg_color, fg_color, trough_color):
        try:
            widget.config(bg=bg_color)
            if hasattr(widget, 'config'):
                widget.config(bg=bg_color, fg=fg_color)
                if 'troughcolor' in widget.keys():
                    widget.config(troughcolor=trough_color)
        except tk.TclError:
            pass  # Ignorer les widgets qui ne supportent pas ces propriétés

        for child in widget.winfo_children():
            self.apply_theme_to_widgets(child, bg_color, fg_color, trough_color)

    def limit_characters(self, event):
        if len(self.text_entry.get()) > 50:
            self.text_entry.delete(50, tk.END)

    def update_text_in_real_time(self, event):
        text = self.text_entry.get()
        selected_font = self.font_listbox.get(self.font_listbox.curselection()[0]) if self.font_listbox.curselection() else 'Arial'
        self.text_label.config(text=text, font=(selected_font, self.font_size_scale.get()))

    def search_fonts(self, event=None):
        query = self.search_font_entry.get().lower()
        self.font_listbox.delete(0, tk.END)
        for font_name in sorted(self.fonts):
            if query in font_name.lower():
                self.font_listbox.insert(tk.END, font_name)

    def show_font(self, event=None):
        if self.font_listbox.curselection():
            selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
            text = self.text_entry.get() if self.text_entry.get() else self.default_text
            self.text_label.config(text=text, font=(selected_font, self.font_size_scale.get()), wraplength=self.root.winfo_screenwidth() * 2 / 3)

    def add_to_favorites(self):
        selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
        if selected_font not in self.favorite_fonts:
            self.favorite_fonts.insert(0, selected_font)
            self.update_font_listbox()
            self.font_listbox.insert(tk.END, selected_font)

    def add_custom_folder(self):
        folder_name = tk.simpledialog.askstring("Nouveau dossier", "Entrez le nom du nouveau dossier :")
        if folder_name:
            self.custom_folders[folder_name] = []
            self.update_font_listbox()

    def add_font_to_folder(self, folder_name, font_name):
        if folder_name in self.custom_folders:
            if font_name not in self.custom_folders[folder_name]:  # Vérifier si la police n'est pas déjà dans le dossier
                self.custom_folders[folder_name].append(font_name)
                self.update_font_listbox()
            else:
                tk.messagebox.showinfo("Information", "Cette police est déjà dans le dossier.")

    def remove_font_from_folder(self, folder_name, font_name):
        if folder_name in self.custom_folders and font_name in self.custom_folders[folder_name]:
            self.custom_folders[folder_name].remove(font_name)
            self.update_font_listbox()

    def update_font_listbox(self):
        self.font_listbox.delete(0, tk.END)

        # Tri des favoris
        sorted_favorite_fonts = sorted(self.favorite_fonts)
        if sorted_favorite_fonts:
            self.font_listbox.insert(tk.END, "Favoris")
            for f in sorted_favorite_fonts:
                self.font_listbox.insert(tk.END, f)
            self.font_listbox.insert(tk.END, "")

        # Ajouter le reste des polices
        for folder_name, folder_fonts in self.custom_folders.items():
            self.font_listbox.insert(tk.END, folder_name)
            # Tri des polices dans le dossier personnalisé
            sorted_folder_fonts = sorted(folder_fonts)
            for f in sorted_folder_fonts:
                self.font_listbox.insert(tk.END, f)
            self.font_listbox.insert(tk.END, "")

        # Ajouter le reste des polices
        for f in sorted(set(self.fonts) - set(self.favorite_fonts)):
            self.font_listbox.insert(tk.END, f)

    def update_font_size(self, size):
        if self.font_listbox.curselection():
            selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
            text = self.text_entry.get() if self.text_entry.get() else self.default_text
            self.text_label.config(text=text, font=(selected_font, int(size)))

    def show_context_menu(self, event):
        selected_font_or_folder = self.font_listbox.get(self.font_listbox.nearest(event.y))
        if selected_font_or_folder in self.custom_folders:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Supprimer le dossier", command=self.remove_folder)
            menu.add_command(label="Renommer le dossier", command=self.rename_folder)
            menu.add_command(label="Prévisualiser le dossier",
                             command=lambda: self.preview_folder_contents(selected_font_or_folder, self.custom_folders[
                                 selected_font_or_folder]))  # Passer le nom du dossier et ses polices
            menu.post(event.x_root, event.y_root)
        elif selected_font_or_folder in self.favorite_fonts:
            if selected_font_or_folder != "Favoris":
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Supprimer du favori", command=self.remove_from_favorites)
                menu.post(event.x_root, event.y_root)
        else:
            if selected_font_or_folder == "Favoris":
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Prévisualiser le dossier", command=self.preview_favorite_fonts)
                menu.post(event.x_root, event.y_root)
            else:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Ajouter aux favoris", command=self.add_to_favorites)
                for folder_name in self.custom_folders.keys():
                    menu.add_command(label="Ajouter à '{}'".format(folder_name),
                                     command=lambda name=folder_name: self.add_to_folder_from_menu(name))
                if any(selected_font_or_folder in fonts for fonts in self.custom_folders.values()):
                    menu.add_command(label="Supprimer la police du dossier", command=self.remove_from_folder_from_menu)
                menu.post(event.x_root, event.y_root)

    def get_text_color(self):
        current_bg_color = self.root.cget("bg")
        if current_bg_color == "#F2F2F2":  # Thème clair
            return "#2f2f2f"  # Couleur de texte sombre
        else:  # Thème sombre
            return "#FFFFFF"  # Couleur de texte claire

    def preview_favorite_fonts(self):
        selected_folder = "Favoris"
        fonts_in_folder = self.favorite_fonts
        self.preview_folder_contents(selected_folder, fonts_in_folder)

    def preview_folder_contents(self, selected_folder, fonts_in_folder):
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Prévisualisation de {}".format(selected_folder))
        preview_window.configure(bg=self.root.cget('bg'))

        preview_canvas = tk.Canvas(preview_window, bg=self.root.cget('bg'), highlightthickness=0)
        preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(preview_window, orient=tk.VERTICAL, command=preview_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_canvas.configure(yscrollcommand=scrollbar.set)

        preview_frame_inner = tk.Frame(preview_canvas, bg=self.root.cget('bg'))
        preview_canvas.create_window((0, 0), window=preview_frame_inner, anchor=tk.NW)

        # Créer une étiquette pour chaque police dans le dossier
        for font_name in fonts_in_folder:
            text_color = self.get_text_color()  # Obtenir la couleur de texte appropriée en fonction du thème
            label = tk.Label(preview_frame_inner, text=font_name, font=(font_name, 20), bg=self.root.cget('bg'),
                             fg=text_color)
            label.pack(anchor="w")

        # Mettre à jour la zone de défilement
        preview_frame_inner.update_idletasks()
        preview_canvas.config(scrollregion=preview_canvas.bbox("all"))

        # Ajouter la gestion de la molette de la souris pour faire défiler la liste
        def on_mouse_wheel(event):
            preview_canvas.yview_scroll(-1 * (event.delta // 120), "units")

        preview_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    def get_font_styles(self, font_name):
        styles = []
        for style in ['bold', 'italic', 'underline', 'overstrike']:
            if font.Font(font=(font_name, 10), weight=style).actual()['weight'] == style:
                styles.append(style)
        return styles

    def add_to_folder_from_menu(self, folder_name):
        selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
        self.add_font_to_folder(folder_name, selected_font)

    def remove_from_folder_from_menu(self):
        selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
        selected_index = self.font_listbox.curselection()[0]
        selected_font_or_folder = self.font_listbox.get(selected_index)
        if any(selected_font_or_folder in fonts for fonts in self.custom_folders.values()):
            sub_menu = tk.Menu(self.root, tearoff=0)
            for folder_name, folder_fonts in self.custom_folders.items():
                if selected_font_or_folder in folder_fonts:
                    sub_menu.add_command(label=folder_name, command=lambda folder=folder_name: self.remove_font_from_folder(folder, selected_font))
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_cascade(label="De quel dossier?", menu=sub_menu)
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def remove_folder(self):
        selected_folder = self.font_listbox.get(self.font_listbox.curselection()[0])
        del self.custom_folders[selected_folder]
        self.update_font_listbox()

    def rename_folder(self):
        selected_folder = self.font_listbox.get(self.font_listbox.curselection()[0])
        new_name = tk.simpledialog.askstring("Renommer le dossier", "Entrez un nouveau nom pour le dossier '{}':".format(selected_folder))
        if new_name:
            self.custom_folders[new_name] = self.custom_folders.pop(selected_folder)
            self.update_font_listbox()

    def remove_from_favorites(self):
        selected_font = self.font_listbox.get(self.font_listbox.curselection()[0])
        self.favorite_fonts.remove(selected_font)
        self.update_font_listbox()

    def show_fonts_in_folder(self, event):
        selected_font_or_folder = self.font_listbox.get(self.font_listbox.nearest(event.y))
        if selected_font_or_folder in self.custom_folders or selected_font_or_folder == "Favoris":
            fonts_in_folder = self.custom_folders[
                selected_font_or_folder] if selected_font_or_folder in self.custom_folders else self.favorite_fonts
        else:
            self.destroy_preview_frame()  # Détruire le frame de prévisualisation
            return  # Si aucun dossier n'est sélectionné, ne rien faire

        # Tri des polices par ordre alphabétique
        fonts_in_folder_sorted = sorted(fonts_in_folder)

        self.preview_frame.destroy()
        self.preview_frame = tk.Frame(self.root, bg="#F2F2F2")
        self.preview_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        preview_canvas = tk.Canvas(self.preview_frame, bg="#F2F2F2", highlightthickness=0)
        preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, command=preview_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_canvas.configure(yscrollcommand=scrollbar.set)
        preview_frame_inner = tk.Frame(preview_canvas, bg="#F2F2F2")
        preview_canvas.create_window((0, 0), window=preview_frame_inner, anchor=tk.NW)

        for font_name in fonts_in_folder_sorted:
            label = tk.Label(preview_frame_inner, text=font_name, font=(font_name, 20))
            label.pack(anchor="w")
        preview_frame_inner.update_idletasks()
        preview_canvas.config(scrollregion=preview_canvas.bbox("all"))
        preview_canvas.bind("<MouseWheel>",
                            lambda event: preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    def destroy_preview_frame(self):
        if hasattr(self, "preview_frame"):
            self.preview_frame.destroy()

    def load_data(self):
        try:
            with open("font_viewer_data.json", "r") as file:
                data = json.load(file)
                self.favorite_fonts = data.get("favorite_fonts", [])
                self.custom_folders = data.get("custom_folders", {})
                self.update_font_listbox()
        except FileNotFoundError:
            pass  # Fichier non trouvé, aucune donnée à charger

    def save_data(self):
        with open("font_viewer_data.json", "w") as file:
            data = {
                "favorite_fonts": self.favorite_fonts,
                "custom_folders": self.custom_folders
            }
            json.dump(data, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = FontViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_data(), root.destroy()))  # Enregistrer les données lors de la fermeture de l'application
    root.mainloop()
