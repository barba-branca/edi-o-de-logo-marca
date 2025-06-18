import os
import sys
import threading
from pathlib import Path
from tkinter import (
    Tk, Label, Button, Entry, Scale, StringVar, IntVar, DoubleVar, Frame,
    filedialog, messagebox, ttk, HORIZONTAL, W, E, N, S, Checkbutton
)
from PIL import Image, ImageTk, ImageEnhance

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Overlay Tool")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Tema: white/black
        self.theme = StringVar(value="white")
        self.setup_theme()
        
        # Variáveis
        self.images_folder = StringVar()
        self.logo_path = StringVar()
        self.pos_preset = StringVar(value="bottom_right")
        self.pos_x = IntVar(value=0)
        self.pos_y = IntVar(value=0)
        self.scale_percent = IntVar(value=20)
        self.opacity = IntVar(value=70)
        self.colorize = IntVar(value=0)  # 0 off, 1 on
        
        self.setup_ui()
        
    def setup_theme(self):
        # Define cores base para o tema
        if self.theme.get() == "white":
            self.bg_color = "#FFFFFF"
            self.fg_color = "#222222"
            self.entry_bg = "#FFFFFF"
            self.btn_bg = "#E0E0E0"
            self.log_bg = "#F9F9F9"
        else:
            self.bg_color = "#222222"
            self.fg_color = "#EEEEEE"
            self.entry_bg = "#333333"
            self.btn_bg = "#555555"
            self.log_bg = "#333333"
        self.root.configure(bg=self.bg_color)
        
    def setup_ui(self):
        # Limpa tudo e recria widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        pad = 10
        lbl_font = ("Segoe UI", 10)
        btn_font = ("Segoe UI", 10, "bold")
        
        # Pasta imagens
        Label(self.root, text="Pasta das imagens:", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=0, column=0, sticky=W, padx=pad, pady=5)
        Entry(self.root, textvariable=self.images_folder, bg=self.entry_bg, fg=self.fg_color, width=40).grid(row=0, column=1, sticky=W, padx=pad, pady=5)
        Button(self.root, text="Selecionar", bg=self.btn_bg, command=self.select_images_folder).grid(row=0, column=2, padx=pad, pady=5)
        
        # Logo
        Label(self.root, text="Arquivo da logo:", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=1, column=0, sticky=W, padx=pad, pady=5)
        Entry(self.root, textvariable=self.logo_path, bg=self.entry_bg, fg=self.fg_color, width=40).grid(row=1, column=1, sticky=W, padx=pad, pady=5)
        Button(self.root, text="Selecionar", bg=self.btn_bg, command=self.select_logo_file).grid(row=1, column=2, padx=pad, pady=5)
        
        # Posição (preset + manual)
        Label(self.root, text="Posição da logo:", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=2, column=0, sticky=W, padx=pad, pady=5)
        
        presets = [
            ("Canto Superior Esquerdo", "top_left"),
            ("Centro Superior", "top_center"),
            ("Canto Superior Direito", "top_right"),
            ("Centro Esquerdo", "center_left"),
            ("Centro", "center"),
            ("Centro Direito", "center_right"),
            ("Canto Inferior Esquerdo", "bottom_left"),
            ("Centro Inferior", "bottom_center"),
            ("Canto Inferior Direito", "bottom_right"),
        ]
        preset_frame = Frame(self.root, bg=self.bg_color)
        preset_frame.grid(row=2, column=1, columnspan=2, sticky=W, padx=pad)
        for i, (text, val) in enumerate(presets):
            b = ttk.Radiobutton(preset_frame, text=text, variable=self.pos_preset, value=val)
            b.grid(row=i//3, column=i%3, sticky=W, padx=3, pady=1)
        
        # Ajuste manual (X,Y)
        Label(self.root, text="Posição manual X:", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=5, column=0, sticky=W, padx=pad, pady=5)
        Entry(self.root, textvariable=self.pos_x, bg=self.entry_bg, fg=self.fg_color, width=10).grid(row=5, column=1, sticky=W, padx=pad, pady=5)
        Label(self.root, text="Posição manual Y:", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=5, column=2, sticky=W, padx=pad, pady=5)
        Entry(self.root, textvariable=self.pos_y, bg=self.entry_bg, fg=self.fg_color, width=10).grid(row=5, column=3, sticky=W, padx=pad, pady=5)
        
        # Tamanho (escala %)
        Label(self.root, text="Tamanho da logo (% da largura da imagem):", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=6, column=0, columnspan=2, sticky=W, padx=pad, pady=5)
        Scale(self.root, from_=1, to=100, orient=HORIZONTAL, variable=self.scale_percent, length=150).grid(row=6, column=2, columnspan=2, sticky=W, padx=pad, pady=5)
        
        # Opacidade
        Label(self.root, text="Opacidade da logo (%):", bg=self.bg_color, fg=self.fg_color, font=lbl_font).grid(row=7, column=0, sticky=W, padx=pad, pady=5)
        Scale(self.root, from_=0, to=100, orient=HORIZONTAL, variable=self.opacity, length=150).grid(row=7, column=1, columnspan=3, sticky=W, padx=pad, pady=5)
        
        # Botão modo tema
        self.btn_theme = Button(self.root, text=f"Mudar para modo {'Preto' if self.theme.get() == 'white' else 'Branco'}", command=self.toggle_theme, bg=self.btn_bg)
        self.btn_theme.grid(row=8, column=0, padx=pad, pady=15)
        
        # Botão processar
        Button(self.root, text="Processar imagens", command=self.start_process, bg="#007ACC", fg="#fff", font=btn_font).grid(row=8, column=1, columnspan=3, padx=pad, pady=15, sticky=E+W)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(self.root, orient=HORIZONTAL, length=580, mode='determinate')
        self.progress.grid(row=9, column=0, columnspan=4, padx=pad, pady=5)
        
        # Log simples
        self.log = ttk.Treeview(self.root, columns=("msg",), show="headings", height=6)
        self.log.heading("msg", text="Status")
        self.log.grid(row=10, column=0, columnspan=4, padx=pad, pady=5, sticky=E+W)
        
        # Configura grid weights para resize horizontal do log
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(10, weight=1)
        
        # Atalhos de teclado
        self.root.bind('<Control-o>', lambda e: self.select_images_folder())
        self.root.bind('<Control-l>', lambda e: self.select_logo_file())
        self.root.bind('<Control-p>', lambda e: self.start_process())
        
    def toggle_theme(self):
        self.theme.set("black" if self.theme.get() == "white" else "white")
        self.setup_theme()
        self.setup_ui()
        
    def select_images_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_folder.set(folder)
            
    def select_logo_file(self):
        filetypes = [("Arquivos de imagem", "*.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*")]
        file = filedialog.askopenfilename(filetypes=filetypes)
        if file:
            self.logo_path.set(file)
            
    def log_message(self, msg):
        self.log.insert("", "end", values=(msg,))
        self.log.yview_moveto(1)
        
    def start_process(self):
        folder = self.images_folder.get()
        logo_file = self.logo_path.get()
        
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Erro", "Selecione uma pasta válida para as imagens.")
            return
        if not logo_file or not os.path.isfile(logo_file):
            messagebox.showerror("Erro", "Selecione um arquivo válido para a logo.")
            return
        
        self.progress['value'] = 0
        self.log.delete(*self.log.get_children())
        
        thread = threading.Thread(target=self.process_images, args=(folder, logo_file))
        thread.start()
        
    def process_images(self, folder, logo_file):
        try:
            img_extensions = {".png", ".jpg", ".jpeg", ".bmp"}
            images_paths = [p for p in Path(folder).iterdir() if p.suffix.lower() in img_extensions and p.is_file()]
            if not images_paths:
                self.log_message("Nenhuma imagem encontrada na pasta.")
                return
            
            output_folder = Path(folder) / "output"
            output_folder.mkdir(exist_ok=True)
            
            # Carrega logo base
            logo_base = Image.open(logo_file).convert("RGBA")
            
            total = len(images_paths)
            for idx, img_path in enumerate(images_paths, start=1):
                try:
                    base_img = Image.open(img_path).convert("RGBA")
                    w_base, h_base = base_img.size
                    
                    # Redimensiona logo mantendo proporção, baseado na largura da imagem
                    scale_factor = self.scale_percent.get() / 100
                    new_width = int(w_base * scale_factor)
                    w_logo, h_logo = logo_base.size
                    new_height = int((new_width / w_logo) * h_logo)
                    logo_resized = logo_base.resize((new_width, new_height), Image.ANTIALIAS)
                    
                    # Aplica opacidade
                    opacity_val = self.opacity.get()
                    if opacity_val < 100:
                        alpha = logo_resized.split()[3]
                        alpha = alpha.point(lambda p: p * (opacity_val / 100))
                        logo_resized.putalpha(alpha)
                    
                    # Determina posição
                    pos = self.calculate_position(base_img.size, logo_resized.size)
                    
                    # Sobrepõe logo
                    base_img.paste(logo_resized, pos, logo_resized)
                    
                    # Salva arquivo
                    output_path = output_folder / img_path.name
                    base_img = base_img.convert("RGB")  # para salvar jpeg sem alpha
                    base_img.save(output_path)
                    
                    self.log_message(f"Processado: {img_path.name}")
                except Exception as e:
                    self.log_message(f"Erro em {img_path.name}: {e}")
                
                self.progress['value'] = (idx / total) * 100
            self.log_message("Processamento concluído!")
            messagebox.showinfo("Concluído", "Todas as imagens foram processadas.")
        except Exception as e:
            self.log_message(f"Erro geral: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    
    def calculate_position(self, base_size, logo_size):
        w_base, h_base = base_size
        w_logo, h_logo = logo_size
        preset = self.pos_preset.get()
        pos_x_manual = self.pos_x.get()
        pos_y_manual = self.pos_y.get()
        
        # Usar manual se não for (0,0)
        if pos_x_manual != 0 or pos_y_manual != 0:
            # Confere limites para não sair da imagem
            x = max(0, min(pos_x_manual, w_base - w_logo))
            y = max(0, min(pos_y_manual, h_base - h_logo))
            return (x, y)
        
        # Preset
        positions = {
            "top_left": (0, 0),
            "top_center": ((w_base - w_logo)//2, 0),
            "top_right": (w_base - w_logo, 0),
            "center_left": (0, (h_base - h_logo)//2),
            "center": ((w_base - w_logo)//2, (h_base - h_logo)//2),
            "center_right": (w_base - w_logo, (h_base - h_logo)//2),
            "bottom_left": (0, h_base - h_logo),
            "bottom_center": ((w_base - w_logo)//2, h_base - h_logo),
            "bottom_right": (w_base - w_logo, h_base - h_logo),
        }
        return positions.get(preset, (w_base - w_logo, h_base - h_logo))
    
if __name__ == "__main__":
    # Verifica se Pillow está instalado
    try:
        import PIL
    except ImportError:
        print("Pillow não está instalado. Rode: pip install pillow")
        sys.exit(1)
    
    root = Tk()
    app = WatermarkApp(root)
    root.mainloop()
