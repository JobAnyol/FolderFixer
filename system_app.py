import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ctypes # Windowsのシステム設定を触るためのライブラリ

class FileOrganizerApp:
    CATEGORY_MAP = {
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"],
        "Documents": ["pdf", "docx", "xlsx", "pptx", "txt", "csv", "md"],
        "Videos": ["mp4", "mov", "avi", "mkv", "webm"],
        "Audio": ["mp3", "wav", "flac", "m4a"],
        "Archives": ["zip", "rar", "7z", "tar", "gz"],
        "Installers": ["exe", "msi", "dmg", "iso"],
        "Programs": ["py", "js", "html", "css", "cpp", "java"]
    }
    CATEGORY_KEYS = list(CATEGORY_MAP.keys())
    OTHER_CATEGORY = "Others"

    def __init__(self):
        # 高画質化コード（さっき入れたやつ）
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

        self.root = tk.Tk()
        self.root.title("Tidy-Bot (Desktop Cleaner)")
        self.root.geometry("600x480") 
        self.root.configure(bg="#f0f2f5")

        # ===========【ここを追加】===========
        # 起動時にウィンドウを最前面に持ってくる魔法
        self.root.lift()
        self.root.focus_force()
        # 一瞬だけ「常に手前」にして、すぐに解除する（確実に見えるようにするため）
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        # ===================================

        # Folder selection
        self.selected_folder = tk.StringVar(value="")
        self._set_up_gui()

        self.root.mainloop()

    def _set_up_gui(self):
        # フォント設定
        base_font = ("Meiryo UI", 10)
        bold_font = ("Meiryo UI", 11, "bold")
        title_font = ("Meiryo UI", 18, "bold")

        # タイトルエリア
        header_frame = tk.Frame(self.root, bg="white", pady=15)
        header_frame.pack(fill="x")
        
        title = tk.Label(header_frame, text="Desktop Cleaner", font=title_font, bg="white", fg="#1a73e8")
        title.pack()
        subtitle = tk.Label(header_frame, text="散らかったフォルダを一瞬で整理整頓", font=("Meiryo UI", 9), bg="white", fg="#5f6368")
        subtitle.pack()

        # メインエリア
        main_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # フォルダ選択エリア
        select_frame = tk.Frame(main_frame, bg="#f0f2f5")
        select_frame.pack(fill="x", pady=(0, 20))

        # 【修正】ボタンを先に配置（pack）する！これで絶対に隠れない
        sel_btn = tk.Button(select_frame, text="📂 フォルダ選択", font=bold_font,
                            bg="#fff", fg="#1a73e8", command=self._choose_folder, 
                            activebackground="#e8f0fe", relief="raised", bd=1)
        sel_btn.pack(side="right") # 右側に固定

        # 【修正】ラベルは残りのスペースを埋めるように配置（width指定を削除）
        self.folder_label = tk.Label(select_frame, text="フォルダが選択されていません", bg="white", fg="#555", 
                                   font=base_font, relief="flat", padx=10, pady=8, anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 実行ボタン
        run_btn = tk.Button(main_frame, text="✨ 整理を開始 (RUN)", font=("Meiryo UI", 12, "bold"),
                            bg="#1a73e8", fg="white", cursor="hand2",
                            command=self._start_organizing, activebackground="#1557b0", 
                            relief="flat", pady=10)
        run_btn.pack(fill="x", pady=(0, 20))

        # ログエリア
        log_frame = tk.Frame(main_frame, bg="#f0f2f5")
        log_frame.pack(fill="both", expand=True)
        
        log_label = tk.Label(log_frame, text="実行ログ:", font=("Meiryo UI", 9, "bold"), bg="#f0f2f5", fg="#5f6368")
        log_label.pack(anchor="w", pady=(0, 5))

        self.log_area = scrolledtext.ScrolledText(log_frame, font=("Consolas", 9), height=8, wrap=tk.WORD, state="disabled", bg="white", relief="flat")
        self.log_area.pack(fill="both", expand=True)

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="整理するフォルダを選択")
        if folder:
            self.selected_folder.set(folder)
            self.folder_label.config(text=folder, fg="#333")
            self._log(f"ターゲット: {folder}")

    def _start_organizing(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showwarning("フォルダ未選択", "先に整理するフォルダを選択してください。")
            return
        self._log("処理を開始します...")
        self.root.after(100, lambda: self._organize_files(folder))

    def _organize_files(self, folder):
        moved_count = 0
        try:
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            total = len(files)
            
            if total == 0:
                self._log("整理するファイルが見つかりませんでした。")
                return

            self._log(f"検出されたファイル数: {total}")
            
            for fname in files:
                # 自分自身のスクリプトやexeは移動しないようにする安全策
                if fname.endswith(".py") or fname.endswith(".exe") or fname.endswith(".ico"):
                    continue

                src_path = os.path.join(folder, fname)
                ext = os.path.splitext(fname)[1][1:].lower()
                category = self._get_category_by_ext(ext)

                dest_dir = os.path.join(folder, category)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)

                dest_path = os.path.join(dest_dir, fname)
                dest_path = self._get_safe_filename(dest_path)

                shutil.move(src_path, dest_path)
                moved_count += 1
                self._log(f"✔ [{category}] {fname}")
            
            self._log("-" * 30)
            self._log(f"完了！ 合計 {moved_count} 個のファイルを整理しました。")
            messagebox.showinfo("成功", f"整理完了！\n{moved_count}個のファイルを移動しました。")
            
        except Exception as e:
            self._log(f"❌ エラー: {str(e)}")

    def _get_category_by_ext(self, ext):
        for cat, exts in self.CATEGORY_MAP.items():
            if ext in exts:
                return cat
        return self.OTHER_CATEGORY

    def _get_safe_filename(self, dest_path):
        if not os.path.exists(dest_path):
            return dest_path
        base, ext = os.path.splitext(dest_path)
        count = 1
        while True:
            new_path = f"{base}_copy{count}{ext}"
            if not os.path.exists(new_path):
                return new_path
            count += 1

    def _log(self, msg):
        self.log_area.configure(state="normal")
        self.log_area.insert("end", msg + "\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

if __name__ == "__main__":
    FileOrganizerApp()