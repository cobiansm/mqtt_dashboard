import customtkinter as ctk
import tkinter as tk
from mqtt_service import MqttService

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class MobileRobotDashboard(ctk.CTk):
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


    # --- Devices --------------------------------------------------------------
    def _log_window(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Log", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self.text_log = ctk.CTkTextbox(parent)
        self.text_log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        clear_btn = ctk.CTkFrame(parent, fg_color="transparent")
        clear_btn.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        clear_btn.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(clear_btn, text="Clear", command=self._clear_log).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

    def _fleet_manager(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Fleet Manager", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        # row/column configuration
        parent.grid_rowconfigure(1, weight=0)       # connection frame
        parent.grid_rowconfigure(2, weight=0)       # job panel 
        parent.grid_rowconfigure(3, weight=0)       # bumper frame
        parent.grid_columnconfigure(0, weight=1)
    
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        self.tabview.add("Config")
        cfg_tab = self.tabview.tab("Config")
        cfg_tab.grid_columnconfigure(0, weight=1)
        
        # connection switch frame 
        switch_panel = ctk.CTkFrame(cfg_tab)
        switch_panel.grid(row=1, column=0, sticky="ew", padx=8, pady=(12, 12))
        switch_panel.grid_columnconfigure(0, weight=1)
        switch_panel.grid_columnconfigure(1, weight=0)
        ctk.CTkLabel(switch_panel, text="Connection", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=4, pady=(8,4), sticky="w")
        self.connection_switch = ctk.CTkSwitch(switch_panel, text="Robot Connected", command=self._on_connection_switch_toggled)
        self.connection_switch.grid(row=1, column=0, padx=4, pady=(0,6), sticky="w")
        self.connection_led = ctk.CTkLabel(switch_panel, text="●", font=ctk.CTkFont(size=30, weight="bold"), text_color="#ff4444")
        self.connection_led.grid(row=1, column=1, padx=(0,8), pady=(0,6), sticky="e")

        # job panel
        job_panel = ctk.CTkFrame(cfg_tab)
        job_panel.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 12))
        job_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(job_panel, text="Job", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=4, pady=(8,4), sticky="w")
        self.job_var = tk.StringVar(value="Idle")
        self.job_menu = ctk.CTkOptionMenu(job_panel, variable=self.job_var, values=["Idle", "Moving", "Delivery", "Task failed"], command=self._on_job_selected)
        self.job_menu.grid(row=1, column=0, padx=4, pady=(0,6), sticky="ew")
        
        # LCD for job subscriber
        self.robot_status_display = ctk.CTkLabel(
            job_panel,
            text="--",
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color="#cccccc",
            fg_color="#303030",
            corner_radius=8,
            padx=8,
            pady=6
        )
        self.robot_status_display.grid(row=2, column=0, padx=4, pady=(0,4), sticky="ew")

        # LCD display for battery subscriber
        battery_panel = ctk.CTkFrame(cfg_tab)
        battery_panel.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 12))
        battery_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(battery_panel, text="Battery", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=4, pady=(8,4), sticky="w")
        self.battery_display = ctk.CTkLabel(
            battery_panel,
            text="--",
            font=ctk.CTkFont(size=50, weight="bold"),
            fg_color="#202020",
            corner_radius=8,
            height=110,
            anchor="center",
            padx=12,
            pady=6
        )
        self.battery_display.grid(row=1, column=0, padx=4, pady=(0, 12), sticky="ew")

    def _robot_core(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(parent, text="Core", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        # row/column configuration
        parent.grid_rowconfigure(1, weight=0)       # laser frame
        parent.grid_rowconfigure(2, weight=0)       # mode panel 
        parent.grid_rowconfigure(3, weight=0)       # bumper frame
        parent.grid_rowconfigure(4, weight=1)       # spacer
        parent.grid_columnconfigure(0, weight=1)

        # mode panel 
        mode_panel = ctk.CTkFrame(parent)
        mode_panel.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,12))
        mode_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(mode_panel, text="Driving Mode", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=8, pady=(12,4), sticky="w")
        self.selected_mode = tk.StringVar(value="Auto")
        mode_row = ctk.CTkFrame(mode_panel, fg_color="transparent")
        mode_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        for m in ("Auto", "Manual"):
            ctk.CTkRadioButton(mode_row, text=m, value=m, variable=self.selected_mode).pack(side="left", padx=4)
        ctk.CTkButton(mode_panel, text="Apply", command=self._on_mode_apply).grid(row=2, column=0, padx=8, pady=(4,8), sticky="ew")

        # laser panel 
        laser_panel = ctk.CTkFrame(parent)
        laser_panel.grid(row=2, column=0, sticky="ew", padx=12, pady=(0,12))
        laser_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(laser_panel, text="Laser (cm)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=(12,4), sticky="w")
        self.laser_progressbar = ctk.CTkProgressBar(laser_panel)
        self.laser_progressbar.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        self.laser_slider = ctk.CTkSlider(laser_panel, from_=0, to=100, number_of_steps=100)
        self.laser_slider.grid(row=2, column=0, padx=12, pady=(4,12), sticky="ew")
        self.laser_slider.set(50)
        self.laser_slider.bind("<ButtonRelease-1>", lambda e: self._on_laser_released())

        # bumper panel 
        bumper_panel = ctk.CTkFrame(parent)
        bumper_panel.grid(row=3, column=0, sticky="ew", padx=12, pady=(0,12))
        bumper_panel.grid_columnconfigure(0, weight=1)
        bumper_panel.grid_rowconfigure(2, minsize=132)
        btn_font = ctk.CTkFont(size=16, weight="bold")
        self._bumper_font_large = ctk.CTkFont(family="Consolas", size=80, weight="bold")
        self._bumper_font_medium = ctk.CTkFont(family="Consolas", size=50, weight="bold")
        self.bumper_true_button = ctk.CTkButton(
            bumper_panel,
            text="Bumper",
            height=44,
            font=btn_font,
            command=self._on_bumper_true
        )
        self.bumper_true_button.grid(row=0, column=0, padx=12, pady=(12,4), sticky="ew")
        self.bumper_false_button = ctk.CTkButton(
            bumper_panel,
            text="Release",
            height=36,
            font=btn_font,
            fg_color="#444444",
            command=self._on_bumper_false
        )
        self.bumper_false_button.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        
        # LCD for bumper subscriber
        self.bumper_display = ctk.CTkLabel(
            bumper_panel,
            text="--",
            font=self._bumper_font_large,
            text_color="#cccccc",
            fg_color="#202020",
            corner_radius=8,
            anchor="center",
            height=120,
            padx=12,
            pady=6
        )
        self.bumper_display.grid(row=2, column=0, padx=12, pady=(6,12), sticky="ew")

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

        # text box for speed subscriber
        self.speed_value_box = ctk.CTkTextbox(speed, height=28, width=120)
        self.speed_value_box.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.speed_value_box.insert("0.0", " -- ")
        self.speed_value_box.configure(state="disabled")  
        
        # battery panel 
        battery_panel = ctk.CTkFrame(parent)
        battery_panel.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        battery_panel.grid_columnconfigure(0, weight=1)
        # battery percentage gauge 
        gauge_wrapper = ctk.CTkFrame(battery_panel, fg_color="transparent")
        gauge_wrapper.grid(row=0, column=0, padx=4, pady=(8, 4))
        gauge_wrapper.grid_columnconfigure(0, weight=1)
        CANVAS_W = 300  
        CANVAS_H = 120  
        self.battery_canvas = tk.Canvas(gauge_wrapper, width=CANVAS_W, height=CANVAS_H, bg="#111111", highlightthickness=0)
        self.battery_canvas.grid(row=0, column=0, sticky="n")  
        # geometry for body and terminal
        body_left = 6
        body_top = 6
        body_right = CANVAS_W - 48  
        body_bottom = CANVAS_H - 6
        term_left = body_right
        term_right = CANVAS_W - 12
        term_top = CANVAS_H/2 - 24
        term_bottom = CANVAS_H/2 + 24
        outline_color = "#bbbbbb"
        self._battery_body_rect = self.battery_canvas.create_rectangle(body_left, body_top, body_right, body_bottom, outline=outline_color, width=3)
        self._battery_tip_rect = self.battery_canvas.create_rectangle(term_left, term_top, term_right, term_bottom, outline=outline_color, width=3)
        # fill area 
        self._battery_fill_left = body_left + 4
        self._battery_fill_top = body_top + 4
        self._battery_fill_right_max = body_right - 4
        self._battery_fill_bottom = body_bottom - 4
        # initial empty fill 
        self._battery_fill_rect = self.battery_canvas.create_rectangle(
            self._battery_fill_left,
            self._battery_fill_top,
            self._battery_fill_left,
            self._battery_fill_bottom,
            outline="",
            fill="#ffffff"
        )
        self._battery_percent_value = None

        # input to publish battery 
        input_row = ctk.CTkFrame(battery_panel, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        input_row.grid_columnconfigure(0, weight=1)
        self.battery_entry = ctk.CTkEntry(input_row, placeholder_text="Battery %")
        self.battery_entry.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        self.battery_send_btn = ctk.CTkButton(input_row, text="Send", width=70, command=self._send_battery)
        self.battery_send_btn.grid(row=0, column=1, padx=0, pady=4)

        # LCD display for motion subscriber
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


    # --- Callbacks Log --------------------------------------------------------
    def _clear_log(self):
        self.text_log.delete("0.0", "end")

    def _append_log(self, line: str):
        self.text_log.insert("end", line + "\n")
        self.text_log.see("end")

        
    # --- Callbacks Fleet Manager  ---------------------------------------------
    # connection switch subscriber
    def _handle_connection_state_update(self, payload: str):
        val = (payload or '').strip().lower()
        is_on = val in ("true", "1", "on", "yes")
        if is_on:
            self.connection_switch.select()
            self.connection_led.configure(text_color="#00cc55")
        else:
            self.connection_switch.deselect()
            self.connection_led.configure(text_color="#ff4444")
        self._append_log(f"(SUB) Connection state '{payload}' in {getattr(self, '_connection_state_sub', '?')}")

    # job publisher
    def _on_job_selected(self, choice: str):
        if hasattr(self, 'mqtt') and hasattr(self, '_job_pub'):
            self.mqtt.publish(self._job_pub, choice)
            self._append_log(f"(PUB) Job '{choice}' in {self._job_pub}")

    # job subscriber
    def _handle_robot_status_update(self, payload: str):
        raw = (payload or '').strip()
        if not raw:
            text = "--"; color = "#cccccc"
        else:
            text = raw
            lw = raw.lower()
            if any(k in lw for k in ("ok", "ready", "idle")):
                color = "#9aff9a"
            elif any(k in lw for k in ("error", "fail", "stuck")):
                color = "#ff5555"
            elif "warn" in lw:
                color = "#ffd27f"
            else:
                color = "#cccccc"
        self.robot_status_display.configure(text=text, text_color=color)
        self._append_log(f"(SUB) Robot status '{payload}' in {getattr(self, '_robot_status_sub', '?')}")

     # battery subscriber 
    def _handle_battery_update(self, payload: str):
        raw = (payload or "").strip()
        val = None
        try:
            num = raw.rstrip('%').strip()
            if num:
                val = int(float(num))
                val = max(0, min(100, val))
        except Exception:
            val = None

        if val is not None:
            if val == 0:
                display_text = "EMPTY"; color = "#ff5555"
            elif val < 30:
                display_text = "CHARGING"; color = "#ffd27f"
            elif val >= 100:
                display_text = "FULL"; color = "#9aff9a"
            else:
                display_text = "STANDBY"; color = "#cccccc"
        self.battery_display.configure(text=display_text, text_color=color)
        self._append_log(f"(SUB) Battery state '{payload}' in {getattr(self, '_battery_sub', '?')}")


    # --- Callbacks Core ------------------------------------------------------
    # laser publisher
    def _on_laser_released(self):
        cm = int(self.laser_slider.get())
        if hasattr(self, '_laser_pub'):
            self.mqtt.publish(self._laser_pub, cm)
            self._append_log(f"(PUB) Laser {cm} cm in {self._laser_pub}")
        self.laser_progressbar.set(cm / 100.0)

    # mode publisher
    def _on_mode_apply(self):
        mode = self.selected_mode.get()
        if hasattr(self, 'mqtt') and hasattr(self, '_mode_pub'):
            self.mqtt.publish(self._mode_pub, mode)
            self._append_log(f"(PUB) Mode {mode} in {self._mode_pub}")

    # bumper publisher true
    def _on_bumper_true(self):
        if hasattr(self, 'mqtt') and hasattr(self, '_bumper_pub'):
            self.mqtt.publish(self._bumper_pub, "true")
            self._append_log(f"(PUB) Bumper true in {self._bumper_pub}")

    # bumper publisher false
    def _on_bumper_false(self):
        if hasattr(self, 'mqtt') and hasattr(self, '_bumper_pub'):
            self.mqtt.publish(self._bumper_pub, "false")
            self._append_log(f"(PUB) Bumper false in {self._bumper_pub}")

    # bumper subscriber
    def _handle_bumper_sensor_update(self, payload: str):
        raw = (payload or "").strip()
        obstacle = None
        if "true" in raw.lower():
            obstacle = True
            display_text = "OBSTACLE"
            color = "#ffd27f"
        elif "false" in raw.lower():
            obstacle = False
            display_text = "FREE"
            color = "#9aff9a"
        else:
            display_text = "--"
            color = "#cccccc"
        font_to_use = self._bumper_font_medium if display_text == "OBSTACLE" else self._bumper_font_large
        self.bumper_display.configure(text=display_text, text_color=color, font=font_to_use)
        log_val = "true" if obstacle is True else ("false" if obstacle is False else "--")
        self._append_log(f"(SUB) Bumper sensor '{log_val}' in {getattr(self, '_bumper_sensor_sub', '?')}")

    # --- Callbacks Low-level-microcontroller ----------------------------------
    # speed publisher
    def _on_speed_released(self):
        percent = int(self.speed_slider.get())  
        self.mqtt.publish(self._speed_pub, percent)
        self._append_log(f"(PUB) Speed {percent}% in {self._speed_pub}")

    # speed subscriber
    def _handle_speed_update(self, val: int):
        self.speed_progressbar.set(val / 100.0)
        if hasattr(self, "speed_value_box"):
            self.speed_value_box.configure(state="normal")
            self.speed_value_box.delete("0.0", "end")
            self.speed_value_box.insert("0.0", f"{val}%")
            self.speed_value_box.configure(state="disabled")
        self._append_log(f"(SUB) Speed {val}% in {self._speed_sub}")

    # battery publisher
    def _send_battery(self):
        try:
            val = int(float(self.battery_entry.get()))
            val = max(0, min(100, val))
            self.battery_entry.delete(0, "end")
            if hasattr(self, "_battery_pub"):
                self.mqtt.publish(self._battery_pub, val)
                self._append_log(f"(PUB) Battery {val}% in {self._battery_pub}")
            else:
                self._append_log("(WARN) Battery topic no inicializado")
        except Exception as e:
            self._append_log(f"Payload inválido '{self.battery_entry.get()}': {e}")

    # motion subscriber 
    def _handle_motion_update(self, payload: str):
        raw = (payload or "").strip()
        try:
            val_cm = int(float(raw))
            if val_cm < 0:
                val_cm = 0
        except Exception:
            val_cm = getattr(self, "_last_laser_cm", None)

        if val_cm is None:
            text = "--"; color = "#cccccc"
        elif val_cm < 15:
            text = "STOP"; color = "#ff5555"
        else:
            text = "GO"; color = "#9aff9a"
        self.motion_display.configure(text=text, text_color=color)
        self._append_log(f"(SUB) Motion '{payload}' in {getattr(self, '_motion_sub', '?')}")


    # --- MQTT -----------------------------------------------------------------
    def _init_mqtt(self):
        # topics
        self._speed_pub = "/speed_slider/data/value"
        self._speed_sub = "/low_level_controller/speed/data/value"
        self._battery_pub = "/battery_entry/data/value"          
        self._battery_sub = "/fleet/battery_status/status"  
        self._laser_pub = "/laser_slider/data/value"
        self._motion_sub = "/low_level_controller/motion/command"
        self._bumper_pub = "/bumper_button/pressed/value"
        self._bumper_sensor_sub = "/core/sensor_bumper/data"
        self._mode_pub = "/mode_selector/drive_mode/value"
        self._connection_switch_pub = "/switch_connection/state"  
        self._connection_state_sub = "/fleet/connection_status/state"
        self._job_pub = "/option_list/job"
        self._robot_status_sub = "/fleet/robot_status/state"
        self._battery_percentage_sub = "/low_level_controller/battery/percentage"
        
        self.mqtt = MqttService(log_fn=self._append_log)
        self.mqtt.start()

        self.mqtt.subscribe(self._speed_sub, self._on_speed_message)
        self.mqtt.subscribe(self._battery_sub, self._on_battery_message)
        self.mqtt.subscribe(self._motion_sub, self._on_motion_message)
        self.mqtt.subscribe(self._bumper_sensor_sub, self._on_bumper_sensor_message)
        self.mqtt.subscribe(self._connection_state_sub, self._on_connection_state_message)
        self.mqtt.subscribe(self._robot_status_sub, self._on_robot_status_message)
        self.mqtt.subscribe(self._battery_percentage_sub, self._on_battery_percentage_message)

    def _on_speed_message(self, topic: str, payload: str):
        try:
            val = int(float(payload))
            val = max(0, min(100, val))
            self.after(0, lambda v=val: self._handle_speed_update(v))
        except Exception as e:
            self._append_log(f"Payload inválido '{payload}': {e}")

    def _on_battery_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_battery_update(p))
        raw = payload.strip()
        try:
            num = raw.rstrip('%').strip()
            val = int(float(num))
            val = max(0, min(100, val))
            self.after(0, lambda v=val: self._handle_battery_percentage_update(str(v)))
        except Exception:
            pass

    def _on_motion_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_motion_update(p))
    
    def _on_bumper_sensor_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_bumper_sensor_update(p))

    def _on_connection_state_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_connection_state_update(p))

    def _on_robot_status_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_robot_status_update(p))

    def _on_battery_percentage_message(self, topic: str, payload: str):
        self.after(0, lambda p=payload: self._handle_battery_percentage_update(p))

    def _on_connection_switch_toggled(self):
        if hasattr(self, 'mqtt') and hasattr(self, '_connection_switch_pub'):
            payload = "true" if self.connection_switch.get() else "false"
            self.mqtt.publish(self._connection_switch_pub, payload)
            self._append_log(f"(PUB) Connection request {payload} in {self._connection_switch_pub}")

    def _handle_battery_percentage_update(self, payload: str):
        raw = (payload or "").strip()
        try:
            if raw == "":
                percent = None
            else:
                percent = int(float(raw))
                percent = max(0, min(100, percent))
        except Exception:
            percent = None

        left_x = getattr(self, "_battery_fill_left", 4)
        right_x_max = getattr(self, "_battery_fill_right_max", 184)
        if percent is None:
            top = getattr(self, "_battery_fill_top", 4)
            bottom = getattr(self, "_battery_fill_bottom", 52)
            self.battery_canvas.coords(self._battery_fill_rect, left_x, top, left_x, bottom)
            self.battery_canvas.itemconfig(self._battery_fill_rect, fill="#ffffff")
            self._append_log(f"(SUB) Battery % '--' in {getattr(self, '_battery_percentage_sub', '?')}")
            return

        fill_width = (percent / 100.0) * (right_x_max - left_x)
        new_right = left_x + fill_width
        top = getattr(self, "_battery_fill_top", 4)
        bottom = getattr(self, "_battery_fill_bottom", 52)
        self.battery_canvas.coords(self._battery_fill_rect, left_x, top, new_right, bottom)
        self.battery_canvas.itemconfig(self._battery_fill_rect, fill="#ffffff")
        self._battery_percent_value = percent
        self._append_log(f"(SUB) Battery % '{percent}' in {getattr(self, '_battery_percentage_sub', '?')}")

    def _on_close(self):
        try:
            if hasattr(self, "mqtt"):
                self.mqtt.stop()
        finally:
            self.destroy()


if __name__ == "__main__":
	app = MobileRobotDashboard()
	app.mainloop()

