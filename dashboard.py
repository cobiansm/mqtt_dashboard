import customtkinter as ctk
import tkinter as tk


ctk.set_appearance_mode("System")  # or "Light" / "Dark"
ctk.set_default_color_theme("blue")


class ThreeColumnDashboard(ctk.CTk):
    """Dashboard skeleton with three equal resizable columns.

    Column arrangement:
        | col 0 | col 1 | col 2 |
    All columns share the same weight and a uniform group so they always
    remain equal width when the window is resized.
    Each column gets a frame container you can populate further.
    """

    def __init__(self):
        super().__init__()

        # Window basics
        self.title("Three Column Dashboard")
        self.geometry("1200x640")

        # Root grid: 3 equal columns using a uniform group
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="cols")
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        self.grid_columnconfigure(2, weight=1, uniform="cols")

        # High-level column frames
        self.col_frames: list[ctk.CTkFrame] = []
        pad_spec = ((16, 6), (6, 6), (6, 16))  # left/mid/right different outer padding
        for i in range(3):
            f = ctk.CTkFrame(self, corner_radius=8)
            f.grid(row=0, column=i, sticky="nsew", padx=pad_spec[i], pady=16)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(1, weight=1)  # internal scroll / content area can stretch
            self.col_frames.append(f)

        # Populate columns
        self._build_column0(self.col_frames[0])
        self._build_column1(self.col_frames[1])
        self._build_column2(self.col_frames[2])

    # --- Column builders -------------------------------------------------
    def _build_column0(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Column 0", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.text_log = ctk.CTkTextbox(parent)
        self.text_log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.text_log.insert("0.0", "Log output...\n")
        button_bar = ctk.CTkFrame(parent, fg_color="transparent")
        button_bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        button_bar.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(button_bar, text="Clear", command=self._clear_log).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(button_bar, text="Add", command=lambda: self._append_log("Sample line")).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(button_bar, text="Info", command=lambda: self._append_log("Info event")).grid(row=0, column=2, padx=4, pady=4, sticky="ew")

    def _build_column1(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Column 1", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.tabview.add("Main")
        self.tabview.add("Config")
        self.tabview.add("Other")
        # Main tab content
        main_tab = self.tabview.tab("Main")
        main_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(main_tab, text="Select Mode:").grid(row=0, column=0, padx=8, pady=(12, 4), sticky="w")
        self.mode_var = tk.StringVar(value="Auto")
        mode_row = ctk.CTkFrame(main_tab, fg_color="transparent")
        mode_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        for m in ("Auto", "Manual", "Test"):
            ctk.CTkRadioButton(mode_row, text=m, value=m, variable=self.mode_var).pack(side="left", padx=4)
        ctk.CTkButton(main_tab, text="Apply", command=self._apply_mode).grid(row=2, column=0, padx=8, pady=(8, 12), sticky="ew")

        # Config tab content
        cfg_tab = self.tabview.tab("Config")
        cfg_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cfg_tab, text="Parameter A").grid(row=0, column=0, padx=8, pady=(12, 4), sticky="w")
        self.param_a = ctk.CTkSlider(cfg_tab, from_=0, to=100, number_of_steps=100)
        self.param_a.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        ctk.CTkLabel(cfg_tab, text="Parameter B").grid(row=2, column=0, padx=8, pady=(12, 4), sticky="w")
        self.param_b = ctk.CTkEntry(cfg_tab, placeholder_text="Value")
        self.param_b.grid(row=3, column=0, padx=8, pady=4, sticky="ew")
        ctk.CTkButton(cfg_tab, text="Save", command=self._save_config).grid(row=4, column=0, padx=8, pady=(12, 12), sticky="ew")

        # Other tab placeholder
        other_tab = self.tabview.tab("Other")
        other_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(other_tab, text="Misc content here").grid(row=0, column=0, padx=8, pady=12)

    def _build_column2(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Column 2", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        # Scrollable frame example
        scroll = ctk.CTkScrollableFrame(parent, label_text="Sensors")
        scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        scroll.grid_columnconfigure(0, weight=1)
        self.sensor_switches: list[ctk.CTkSwitch] = []
        for i in range(1, 21):
            sw = ctk.CTkSwitch(scroll, text=f"Sensor {i}")
            sw.grid(row=i-1, column=0, padx=8, pady=4, sticky="w")
            self.sensor_switches.append(sw)
        # Bottom actions
        bottom = ctk.CTkFrame(parent, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        ctk.CTkButton(bottom, text="Enable All", command=self._enable_all_sensors).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(bottom, text="Disable All", command=self._disable_all_sensors).pack(side="left", padx=4, pady=4)

    # --- Callbacks --------------------------------------------------------
    def _clear_log(self):
        self.text_log.delete("0.0", "end")

    def _append_log(self, line: str):
        self.text_log.insert("end", line + "\n")
        self.text_log.see("end")

    def _apply_mode(self):
        self._append_log(f"Mode set to: {self.mode_var.get()}")

    def _save_config(self):
        a = self.param_a.get()
        b = self.param_b.get()
        self._append_log(f"Saved config A={a:.0f}, B='{b}'")

    def _enable_all_sensors(self):
        for sw in self.sensor_switches:
            sw.select()
        self._append_log("All sensors enabled")

    def _disable_all_sensors(self):
        for sw in self.sensor_switches:
            sw.deselect()
        self._append_log("All sensors disabled")


if __name__ == "__main__":
	app = ThreeColumnDashboard()
	app.mainloop()

