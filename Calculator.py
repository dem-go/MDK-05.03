import tkinter as tk
from tkinter import messagebox
import math
from pathlib import Path

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, active_bg, fg_color, font, radius=12):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0)
        self.command = command
        self.bg_color = bg_color
        self.active_bg = active_bg
        self.fg_color = fg_color
        self.font = font
        self.text = text
        self.radius = radius
        self.current_bg = bg_color

        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = min(self.radius, w // 2, h // 2)
        
        points = [
            r, 0, w - r, 0, w, 0, w, r,
            w, h - r, w, h, w - r, h, r, h,
            0, h, 0, h - r, 0, r, 0, 0
        ]
        self.create_polygon(points, smooth=True, fill=self.current_bg)
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg_color, font=self.font)

    def _on_enter(self, event):
        self.current_bg = self.active_bg
        self._draw()

    def _on_leave(self, event):
        self.current_bg = self.bg_color
        self._draw()

    def _on_click(self, event):
        self.current_bg = self.bg_color
        self._draw()

    def _on_release(self, event):
        self.current_bg = self.active_bg
        self._draw()
        if self.command:
            self.command()

class CalculatorEngine:
    def __init__(self):
        self._memory = 0.0

    def add(self, a, b): return a + b
    def subtract(self, a, b): return a - b
    def multiply(self, a, b): return a * b
    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Деление на ноль невозможно")
        return a / b

    def power(self, base, exponent): return base ** exponent
    def sqrt(self, value):
        if value < 0:
            raise ValueError("Корень из отрицательного числа не определён")
        return math.sqrt(value)

    def save_memory(self, value): self._memory = value
    def read_memory(self): return self._memory
    def add_to_memory(self, value): self._memory += value
    def subtract_from_memory(self, value): self._memory -= value
    def clear_memory(self): self._memory = 0.0

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("400x530")
        self.root.resizable(False, False)

        self.bg_color = "#202020"
        self.root.configure(bg=self.bg_color)

        icon_path = Path(__file__).parent / "icon.png"
        self.icon = tk.PhotoImage(file=str(icon_path))
        self.root.iconphoto(True, self.icon)

        self.engine = CalculatorEngine()
        self.display_var = tk.StringVar(value="0")

        self.stored_value = None
        self.pending_op = None
        self.reset_display = True

        self._build_ui()

    def _build_ui(self):
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        tk.Label(top_frame, text="≡", font=("Segoe UI", 16), bg=self.bg_color, fg="#ffffff").pack(side="left")
        tk.Label(top_frame, text="Обычный", font=("Segoe UI", 14), bg=self.bg_color, fg="#ffffff").pack(side="left", padx=10)

        display = tk.Entry(
            self.root, textvariable=self.display_var,
            font=("Segoe UI", 30), justify="right",
            state="readonly", readonlybackground=self.bg_color, fg="#ffffff",
            relief="flat", bd=0, highlightthickness=0
        )
        display.pack(fill="x", padx=15, pady=(15, 20))

        mem_frame = tk.Frame(self.root, bg=self.bg_color)
        mem_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        mem_buttons = [
            ("MC", self._memory_clear), ("MR", self._memory_read), 
            ("M+", self._memory_add), ("M-", self._memory_subtract), 
            ("MS", self._memory_save), ("Mv", lambda: None)
        ]
        for text, cmd in mem_buttons:
            b = tk.Button(mem_frame, text=text, font=("Segoe UI", 10), 
                          bg=self.bg_color, fg="#aaaaaa", relief="flat", command=cmd,
                          activebackground=self.bg_color, activeforeground="#ffffff", bd=0)
            b.pack(side="left", expand=True, fill="x")

        grid_frame = tk.Frame(self.root, bg=self.bg_color)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        buttons = [
            ("%", 0, 0, "op"), ("CE", 0, 1, "op"), ("C", 0, 2, "op"), ("⌫", 0, 3, "op"),
            ("1/x", 1, 0, "op"), ("x²", 1, 1, "op"), ("²√x", 1, 2, "op"), ("÷", 1, 3, "op"),
            ("7", 2, 0, "num"), ("8", 2, 1, "num"), ("9", 2, 2, "num"), ("×", 2, 3, "op"),
            ("4", 3, 0, "num"), ("5", 3, 1, "num"), ("6", 3, 2, "num"), ("−", 3, 3, "op"),
            ("1", 4, 0, "num"), ("2", 4, 1, "num"), ("3", 4, 2, "num"), ("+", 4, 3, "op"),
            ("+/−", 5, 0, "num"), ("0", 5, 1, "num"), (",", 5, 2, "num"), ("=", 5, 3, "eq"),
        ]

        for text, row, col, btn_type in buttons:
            if btn_type == "num":
                bg_color = "#3b3b3b"
                active_bg = "#323232"
                fg_color = "#ffffff"
                font_style = ("Segoe UI", 16) 
            elif btn_type == "op":
                bg_color = "#323232"
                active_bg = "#3b3b3b"
                fg_color = "#ffffff"
                font_style = ("Segoe UI", 12)
            else:
                bg_color = "#0067c0"
                active_bg = "#005a9e"
                fg_color = "#ffffff"
                font_style = ("Segoe UI", 15)

            btn = RoundedButton(
                grid_frame, text=text, font=font_style,
                bg_color=bg_color, fg_color=fg_color,
                active_bg=active_bg, radius=12,
                command=lambda t=text: self._on_button_click(t)
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")


        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            grid_frame.grid_rowconfigure(i, weight=1)

    def _on_button_click(self, text):
        try:
            if text.isdigit():
                self._input_digit(text)
            elif text == ",":
                self._input_dot()
            elif text in ["+", "−", "×", "÷"]:
                self._set_operator(text)
            elif text == "=":
                self._calculate()
            elif text == "C":
                self._clear()
            elif text == "CE":
                self.display_var.set("0")
                self.reset_display = True
            elif text == "⌫":
                self._backspace()
            elif text == "%":
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format(val / 100))
                self.reset_display = True
            elif text == "1/x":
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format(self.engine.divide(1, val)))
                self.reset_display = True
            elif text == "x²":
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format(self.engine.power(val, 2)))
                self.reset_display = True
            elif text == "²√x":
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format(self.engine.sqrt(val)))
                self.reset_display = True
            elif text == "+/−":
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format(-val))
            elif text == "MC": self._memory_clear()
            elif text == "MR": self._memory_read()
            elif text == "M+": self._memory_add()
            elif text == "M-": self._memory_subtract()
            elif text == "MS": self._memory_save()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self._clear()

    def _input_digit(self, digit):
        current = self.display_var.get()
        if self.reset_display or current == "0":
            self.display_var.set(digit)
            self.reset_display = False
        else:
            self.display_var.set(current + digit)

    def _input_dot(self):
        current = self.display_var.get()
        if self.reset_display:
            self.display_var.set("0,")
            self.reset_display = False
        elif "," not in current:
            self.display_var.set(current + ",")

    def _backspace(self):
        current = self.display_var.get()
        if self.reset_display:
            return
        if len(current) > 1:
            self.display_var.set(current[:-1])
        else:
            self.display_var.set("0")
            self.reset_display = True

    def _set_operator(self, op):
        current = float(self.display_var.get().replace(",", "."))
        if self.pending_op is not None and not self.reset_display:
            self.stored_value = self._apply(self.stored_value, current, self.pending_op)
            self.display_var.set(self._format(self.stored_value))
        else:
            self.stored_value = current
        self.pending_op = op
        self.reset_display = True

    def _calculate(self):
        if self.pending_op is None:
            return
        current = float(self.display_var.get().replace(",", "."))
        result = self._apply(self.stored_value, current, self.pending_op)
        self.display_var.set(self._format(result))
        self.stored_value = None
        self.pending_op = None
        self.reset_display = True

    def _apply(self, a, b, op):
        if op == "+": return self.engine.add(a, b)
        if op == "−": return self.engine.subtract(a, b)
        if op == "×": return self.engine.multiply(a, b)
        if op == "÷": return self.engine.divide(a, b)

    def _format(self, value):
        if isinstance(value, float) and value.is_integer():
            res = str(int(value))
        else:
            res = str(round(value, 10))
        return res.replace(".", ",")

    def _clear(self):
        self.display_var.set("0")
        self.stored_value = None
        self.pending_op = None
        self.reset_display = True

    def _memory_save(self):
        self.engine.save_memory(float(self.display_var.get().replace(",", ".")))
        self.reset_display = True

    def _memory_read(self):
        self.display_var.set(self._format(self.engine.read_memory()))
        self.reset_display = True

    def _memory_add(self):
        self.engine.add_to_memory(float(self.display_var.get().replace(",", ".")))
        self.reset_display = True

    def _memory_subtract(self):
        self.engine.subtract_from_memory(float(self.display_var.get().replace(",", ".")))
        self.reset_display = True

    def _memory_clear(self):
        self.engine.clear_memory()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()