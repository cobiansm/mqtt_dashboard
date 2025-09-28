import customtkinter as ctk
import tkinter as tk
from mqtt_service import MqttService

ctk.set_appearance_mode("System")  # or "Light" / "Dark"
ctk.set_default_color_theme("blue")

class ThreeColumnDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mobile Robot Dashboard")
        self.geometry("1320x550")

        self.grid_rowconfigure(0, weight=1)
        for c in range(4):
            self.grid_columnconfigure(c, weight=1, uniform="cols")

        # column padding
        self.col_frames: list[ctk.CTkFrame] = []
        pad_spec = ((16, 6), (6, 6), (6, 6), (6, 16))
      
        for i in range(4):
            f = ctk.CTkFrame(self, corner_radius=8)
            f.grid(row=0, column=i, sticky="nsew", padx=pad_spec[i], pady=16)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(1, weight=1)
            self.col_frames.append(f)

        # columns
        self._log_window(self.col_frames[0])
        self._fleet_manager(self.col_frames[1])
        self._robot_core(self.col_frames[2])
        self._low_level_microcontroller(self.col_frames[3])

        # MQTT service init
        self._init_mqtt()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------- Devices -------------------
    def _log_window(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Log", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.text_log = ctk.CTkTextbox(parent)
        self.text_log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        button_bar = ctk.CTkFrame(parent, fg_color="transparent")
        button_bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        button_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(button_bar, text="Clear", command=self._clear_log).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

    def _fleet_manager(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Fleet Manager", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.tabview.add("Config")
        cfg_tab = self.tabview.tab("Config")
        cfg_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cfg_tab, text="Parameter A").grid(row=0, column=0, padx=8, pady=(12, 4), sticky="w")
        self.param_a = ctk.CTkSlider(cfg_tab, from_=0, to=100, number_of_steps=100)
        self.param_a.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        ctk.CTkLabel(cfg_tab, text="Parameter B").grid(row=2, column=0, padx=8, pady=(12, 4), sticky="w")
        self.param_b = ctk.CTkEntry(cfg_tab, placeholder_text="Value")
        self.param_b.grid(row=3, column=0, padx=8, pady=4, sticky="ew")
        ctk.CTkButton(cfg_tab, text="Save").grid(row=4, column=0, padx=8, pady=(12, 12), sticky="ew")

    def _robot_core(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Core", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text="Select Driving Mode:").grid(row=0, column=0, padx=8, pady=(12,4), sticky="w")
        self.mode2_var = tk.StringVar(value="Auto")
        mode_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        mode_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        for m in ("Auto", "Manual"):
            ctk.CTkRadioButton(mode_row, text=m, value=m, variable=self.mode2_var).pack(side="left", padx=4)
        ctk.CTkButton(wrapper, text="Apply", command=lambda: self._append_log(f"Mode2 -> {self.mode2_var.get()}")) \
            .grid(row=2, column=0, padx=8, pady=(8,12), sticky="ew")

    def _low_level_microcontroller(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Low Level Microcontroller", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        # row/column configuration
        parent.grid_rowconfigure(1, weight=0)       # speed frame
        parent.grid_rowconfigure(2, weight=0)       # battery panel 
        parent.grid_rowconfigure(3, weight=0)       # motion panel
        parent.grid_columnconfigure(0, weight=1)

        # speed frame 
        speed = ctk.CTkFrame(parent)
        speed.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        speed.grid_columnconfigure(0, weight=1)

        # slider to publish speed 
        ctk.CTkLabel(speed, text="Speed", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")
        self.speed_progressbar = ctk.CTkProgressBar(speed)
        self.speed_progressbar.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        self.speed_slider = ctk.CTkSlider(speed, from_=0, to=100, number_of_steps=100)
        self.speed_slider.grid(row=2, column=0, padx=12, pady=(4, 12), sticky="ew")
        self.speed_slider.set(50)
        self.speed_slider.bind("<ButtonRelease-1>", lambda e: self._on_speed_released())

        # text box for subscriber
        self.speed_value_box = ctk.CTkTextbox(speed, height=28, width=120)
        self.speed_value_box.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.speed_value_box.insert("0.0", " -- ")
        self.speed_value_box.configure(state="disabled")  
        
        # battery panel 
        battery_panel = ctk.CTkFrame(parent)
        battery_panel.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        battery_panel.grid_columnconfigure(0, weight=1)

        # LCD display for battery
        self.battery_display = ctk.CTkLabel(
            battery_panel,
            text="--",
            font=ctk.CTkFont(size=80, weight="bold"),
            text_color="#9aff9a",
            fg_color="#142214",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.battery_display.grid(row=0, column=0, padx=4, pady=(8, 12), sticky="ew")

        # input to publish battery 
        input_row = ctk.CTkFrame(battery_panel, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        input_row.grid_columnconfigure(0, weight=1)
        self.battery_entry = ctk.CTkEntry(input_row, placeholder_text="Battery %")
        self.battery_entry.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        self.battery_send_btn = ctk.CTkButton(input_row, text="Send", width=70)
        self.battery_send_btn.grid(row=0, column=1, padx=0, pady=4)

        # LCD display for motion
        motion_panel = ctk.CTkFrame(parent)
        motion_panel.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))
        motion_panel.grid_columnconfigure((0, 1), weight=1)
        self.motion_display = ctk.CTkLabel(
            motion_panel,
            text="--",
            font=ctk.CTkFont(size=80, weight="bold"),
            text_color="#ffd27f",   
            fg_color="#202020",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.motion_display.grid(row=0, column=0, columnspan=2, padx=4, pady=(8, 8), sticky="ew")

    # --- Callbacks --------------------------------------------------------
    def _clear_log(self):
        self.text_log.delete("0.0", "end")

    def _append_log(self, line: str):
        self.text_log.insert("end", line + "\n")
        self.text_log.see("end")

    # speed publisher
    def _on_speed_released(self):
        percent = int(self.speed_slider.get())  
        self._publish_speed(percent)
        self._append_log(f"(PUB) Speed {percent}% in {self._speed_pub}")

    def _handle_speed_update(self, val: int):
        self.speed_progressbar.set(val / 100.0)
        if hasattr(self, "speed_value_box"):
            self.speed_value_box.configure(state="normal")
            self.speed_value_box.delete("0.0", "end")
            self.speed_value_box.insert("0.0", f"{val}% (RX)")
            self.speed_value_box.configure(state="disabled")
        self._append_log(f"(SUB) Speed {val}% in {self._speed_sub}")

    # --- MQTT ------------------------------------------
    def _init_mqtt(self):
        # topics
        self._speed_pub = "/speed_slider/data/value"
        self._speed_sub = "/low_level_controller/speed/data/value"

        self.mqtt = MqttService(log_fn=self._append_log)
        self.mqtt.start()

        self.mqtt.subscribe(self._speed_sub, self._on_speed_message)

    def _on_speed_message(self, topic: str, payload: str):
        try:
            val = int(float(payload))
            val = max(0, min(100, val))
            self.after(0, lambda v=val: self._handle_speed_update(v))
        except Exception as e:
            self._append_log(f"Payload inválido '{payload}': {e}")

    def _publish_speed(self, value: int):
        self.mqtt.publish(self._speed_pub, value)

    def _on_close(self):
        try:
            if hasattr(self, "mqtt"):
                self.mqtt.stop()
        finally:
            self.destroy()


if __name__ == "__main__":
	app = ThreeColumnDashboard()
	app.mainloop()

