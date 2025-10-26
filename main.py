import tkinter as tk
from tkinter import messagebox
import json
import random

class CrimeInfoDialog(tk.Toplevel):
    """
    クリックされたカードの情報を表示するためのカスタムポップアップウィンドウ。
    """
    def __init__(self, parent, crime_name, crime_years):
        super().__init__(parent)
        self.title("判決") # ポップアップのタイトル
        self.geometry("200x100")
        self.resizable(False, False)

        # 親ウィンドウの中央に表示するための計算
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        self.geometry(f"+{parent_x + (parent_width // 2) - 175}+{parent_y + (parent_height // 2) - 90}")

        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # 犯罪名を表示するラベル
        tk.Label(main_frame, text=crime_name, font=("Helvetica", 16, "bold"), wraplength=300).pack(pady=(0, 10))

        # 懲役年数を赤文字で表示するラベル
        years_text = f"懲役: {crime_years}年"
        tk.Label(main_frame, text=years_text, font=("Helvetica", 14), fg="red").pack()

        # OKボタン
        # ok_button = tk.Button(main_frame, text="OK", command=self.destroy, width=10, font=("Helvetica", 10))
        # ok_button.pack(pady=(15, 0))
        # ok_button.focus_set() # 最初からOKボタンにフォーカスを当てる

        # このウィンドウが閉じられるまで、他のウィンドウを操作不能にする
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

class GameGUI:
    """懲役ブラックジャックのGUIとゲームロジックを管理するクラス"""
    TARGET_SCORE = 21

    def __init__(self, master):
        self.master = master
        self.master.title("⚖️ 懲役ブラックジャック ⚖️")
        self.master.geometry("1400x800")
        self.master.resizable(False, False)

        main_frame = tk.Frame(master, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=10)

        self.p1_score_var = tk.StringVar()
        self.p2_score_var = tk.StringVar()
        self.turn_var = tk.StringVar()
        
        tk.Label(info_frame, text=f"目標懲役: {self.TARGET_SCORE}年", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Label(info_frame, textvariable=self.p1_score_var, font=("Helvetica", 12)).grid(row=1, column=0, padx=20)
        tk.Label(info_frame, textvariable=self.p2_score_var, font=("Helvetica", 12)).grid(row=1, column=1, padx=20)
        tk.Label(info_frame, textvariable=self.turn_var, font=("Helvetica", 14, "bold"), fg="blue").grid(row=2, column=0, columnspan=2, pady=10)

        self.cards_frame = tk.Frame(main_frame, padx=10, pady=10)
        self.cards_frame.pack()

        self.control_frame = tk.Frame(main_frame, pady=10)
        self.control_frame.pack()
        
        self.change_player_button = tk.Button(self.control_frame, text="プレイヤーチェンジ", font=("Helvetica", 12), command=self.change_player_action)
        self.change_player_button.grid(row=0, column=0, padx=10)
        
        self.reset_button = tk.Button(self.control_frame, text="リセット", font=("Helvetica", 12), command=self.start_game)
        self.reset_button.grid(row=0, column=1, padx=10)

        self.start_game()

    def load_cards(self):
        try:
            with open("crimes.json", 'r', encoding='utf-8') as f:
                return json.load(f)['crimes']
        except FileNotFoundError:
            messagebox.showerror("エラー", "crimes.json が見つかりません。")
            return None

    def start_game(self):
        self.card_data = self.load_cards()
        if self.card_data is None:
            self.master.quit()
            return
        
        random.shuffle(self.card_data)
        
        self.players_scores = [0, 0]
        self.player_status = ["playing", "playing"]
        self.current_player_index = 0
        self.game_over = False

        self.create_card_widgets()
        self.update_ui()

    def create_card_widgets(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        self.card_buttons = []
        # 50枚のカードを横長のウィンドウに合わせるため、列数を10に変更
        cols = 10
        for i, crime_data in enumerate(self.card_data):
            button = tk.Button(
                self.cards_frame, 
                text=crime_data['name'], 
                width=15, height=3, 
                font=("Helvetica", 10),
                command=lambda idx=i: self.on_card_click(idx)
            )
            row = i // cols
            col = i % cols
            button.grid(row=row, column=col, padx=5, pady=5)
            self.card_buttons.append(button)

    def on_card_click(self, index):
        if self.game_over or self.player_status[self.current_player_index] != "playing":
            return

        crime_data = self.card_data[index]
        years = crime_data['years']
        
        # ★変更点: ポップアップウィンドウを表示する
        CrimeInfoDialog(self.master, crime_data['name'], years)

        self.players_scores[self.current_player_index] += years
        
        # ボタンを無効化し、背景を灰色にする（テキストは変更しない）
        button = self.card_buttons[index]
        button.config(state=tk.DISABLED, bg="lightgrey")
        
        self.update_ui()

        if self.players_scores[self.current_player_index] > self.TARGET_SCORE:
            self.player_status[self.current_player_index] = "bust"
            messagebox.showwarning("ドボン！", f"プレイヤー{self.current_player_index + 1}は {self.TARGET_SCORE}年 を超えました！")
            self.determine_winner()

    def change_player_action(self):
        if self.game_over or self.player_status[self.current_player_index] != "playing":
            return
        
        self.switch_player()
        self.update_ui()
        

        if self.player_status[0] != "playing" and self.player_status[1] != "playing":
            self.determine_winner()

    def switch_player(self):
        self.current_player_index = 1 - self.current_player_index

    def update_ui(self):
        p1_score = self.players_scores[0]
        p2_score = self.players_scores[1]
        
        p1_status_text = f" ({self.player_status[0].upper()})" if self.player_status[0] != "playing" else ""
        p2_status_text = f" ({self.player_status[1].upper()})" if self.player_status[1] != "playing" else ""

        self.p1_score_var.set(f"プレイヤー1: {p1_score}年{p1_status_text}")
        self.p2_score_var.set(f"プレイヤー2: {p2_score}年{p2_status_text}")
        
        if not self.game_over:
            self.turn_var.set(f"ターン: プレイヤー{self.current_player_index + 1}")
            self.change_player_button.config(state=tk.NORMAL)
        else:
            self.change_player_button.config(state=tk.DISABLED)

    def determine_winner(self):
        if self.game_over: return
        self.game_over = True
        
        self.turn_var.set("ゲーム終了")
        self.change_player_button.config(state=tk.DISABLED)

        p1_score, p2_score = self.players_scores
        p1_status, p2_status = self.player_status

        if p1_status == "bust":
            winner_msg = "プレイヤー2の勝利です！"
        elif p2_status == "bust":
            winner_msg = "プレイヤー1の勝利です！"
        elif p1_score > p2_score:
            winner_msg = "プレイヤー1の勝利です！"
        elif p2_score > p1_score:
            winner_msg = "プレイヤー2の勝利です！"
        else:
            winner_msg = "引き分けです！"

        messagebox.showinfo("ゲーム終了", f"結果\nプレイヤー1: {p1_score}年\nプレイヤー2: {p2_score}年\n\n{winner_msg}")
        
        for btn in self.card_buttons:
            if btn['state'] == tk.NORMAL:
                 btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()