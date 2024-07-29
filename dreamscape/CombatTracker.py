import tkinter as tk
from tkinter import scrolledtext

class CombatTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Combat Tracker")

        # Frame for enemies and statuses
        self.enemies_frame = tk.Frame(root)
        self.enemies_frame.pack(side=tk.TOP, fill=tk.X)
        self.enemies_labels = []
        for i in range(4):  # Assuming a maximum of 4 enemies
            enemy_name = tk.Label(self.enemies_frame, text=f"Enemy {i + 1}")
            enemy_status = tk.Label(self.enemies_frame, text="Status: Healthy")
            enemy_name.grid(row=0, column=i)
            enemy_status.grid(row=1, column=i)
            self.enemies_labels.append((enemy_name, enemy_status))

        # Frame for initiative
        self.initiative_frame = tk.Frame(root)
        self.initiative_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(self.initiative_frame, text="Initiative").pack()
        self.initiative_list = tk.Listbox(self.initiative_frame)
        self.initiative_list.pack(fill=tk.BOTH, expand=True)

        # Frame for main storytelling paragraphs
        self.story_frame = tk.Frame(root)
        self.story_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.story_text = scrolledtext.ScrolledText(self.story_frame, wrap=tk.WORD, width=40, height=10)
        self.story_text.pack(fill=tk.BOTH, expand=True)

        # Frame for HP and spell slots
        self.hp_spell_frame = tk.Frame(root)
        self.hp_spell_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(self.hp_spell_frame, text="HP").pack()
        self.hp_label = tk.Label(self.hp_spell_frame, text="Current HP / Max HP")
        self.hp_label.pack()
        tk.Label(self.hp_spell_frame, text="Spell Slots").pack()
        self.spell_slots_label = tk.Label(self.hp_spell_frame, text="Spell Slots Info")
        self.spell_slots_label.pack()

        # Frame for roll log
        self.roll_log_frame = tk.Frame(root)
        self.roll_log_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.roll_log_frame, text="Roll Log").pack()
        self.roll_log_text = scrolledtext.ScrolledText(self.roll_log_frame, wrap=tk.WORD, width=20, height=10)
        self.roll_log_text.pack(fill=tk.BOTH, expand=True)
        self.toggle_button = tk.Button(self.roll_log_frame, text="Toggle Roll Log", command=self.toggle_roll_log)
        self.toggle_button.pack()

    def toggle_roll_log(self):
        if self.roll_log_text.winfo_ismapped():
            self.roll_log_text.pack_forget()
        else:
            self.roll_log_text.pack(fill=tk.BOTH, expand=True)

    def update_enemy_status(self, enemy_index, status):
        self.enemies_labels[enemy_index][1].config(text=f"Status: {status}")

    def update_initiative(self, initiative_list):
        self.initiative_list.delete(0, tk.END)
        for item in initiative_list:
            self.initiative_list.insert(tk.END, item)

    def update_story(self, story_text):
        self.story_text.insert(tk.END, story_text + '\n')

    def update_hp(self, current_hp, max_hp):
        self.hp_label.config(text=f"{current_hp} / {max_hp}")

    def update_spell_slots(self, spell_slots_info):
        self.spell_slots_label.config(text=spell_slots_info)

    def update_roll_log(self, roll_log_text):
        self.roll_log_text.insert(tk.END, roll_log_text + '\n')

if __name__ == "__main__":
    root = tk.Tk()
    tracker = CombatTracker(root)
    root.mainloop()
