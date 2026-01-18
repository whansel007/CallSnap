import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from whitelist import minmaxPrograms
import threading
import queue
import json
import time
import warnings
import os
import numpy as np
import soundcard as sc
from vosk import KaldiRecognizer, Model

# Suppress soundcard discontinuity warning
warnings.filterwarnings("ignore", message="data discontinuity in recording")

BG = "#f3f1ed"
TEXT_PRIMARY = "#2d2a26"
TEXT_SECONDARY = "#5f5a54"
PRIMARY_BG = "#f7d070"
PRIMARY_HOVER = "#e7c15f"
SECONDARY_BG = "#9cc5a1"
SECONDARY_HOVER = "#86b28c"
UTILITY_BG = "#e6e2dc"
UTILITY_HOVER = "#d7d1ca"


class NameDetectorGUI:
    def __init__(self, root, configure_window=True, show_settings=True):
        self.root = root
        self.toplevel = root.winfo_toplevel()

        if configure_window:
            self.toplevel.title("zoomSnap - Name Detector")
            self.toplevel.geometry("1000x600")
            self.toplevel.configure(bg=BG)
        else:
            try:
                self.root.configure(bg=BG)
            except tk.TclError:
                pass
        style = ttk.Style(self.toplevel)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Style ===
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT_PRIMARY, font=("Georgia", 11))
        style.configure("TEntry", fieldbackground="white", foreground=TEXT_PRIMARY)
        style.configure("TCombobox", fieldbackground="white", foreground=TEXT_PRIMARY)
        style.configure("Section.TLabelframe", background=BG)
        style.configure(
            "Section.TLabelframe.Label",
            background=BG,
            foreground=TEXT_PRIMARY,
            font=("Georgia", 12, "bold"),
        )
        style.configure(
            "Primary.TButton",
            background=PRIMARY_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            padding=2,
        )
        style.map("Primary.TButton", background=[("active", PRIMARY_HOVER)])
        style.configure(
            "Secondary.TButton",
            background=SECONDARY_BG,
            foreground="#1f2a22",
            font=("Segoe UI", 10, "bold"),
            padding=2,
        )
        style.map("Secondary.TButton", background=[("active", SECONDARY_HOVER)])
        style.configure(
            "Utility.TButton",
            background=UTILITY_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            padding=1,
        )
        style.map("Utility.TButton", background=[("active", UTILITY_HOVER)])
        
        # Variables ===
        self.minmaxPrograms = minmaxPrograms
        self.listening = False
        self.recognizer = None
        self.listener_thread = None
        self.ui_queue = queue.Queue()
        self.settings_window = None
        self.device_combo = None

        self.target_name = tk.StringVar(value="william,harvin")
        self.model_path = tk.StringVar(value="./models/vosk-model-small-en-us-0.15")
        self.device_name = tk.StringVar(value="")
        self.sample_rate = tk.IntVar(value=16000)
        self.block_size = tk.IntVar(value=4096)
        self.cooldown = tk.DoubleVar(value=10.0)

        if show_settings:
            self.build_settings_frame(root)

        # Button frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill="x", padx=24, pady=(4, 10))

        self.start_button = ttk.Button(
            button_frame,
            text="Start Listening",
            command=self.start_listening,
            style="Primary.TButton",
        )
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Listening",
            command=self.stop_listening,
            state="disabled",
            style="Secondary.TButton",
        )
        self.stop_button.pack(side="left")

        # Main content frame (left + right)
        content_frame = ttk.Frame(root)
        content_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # LEFT SIDE - Current transcription
        left_frame = ttk.LabelFrame(content_frame, text="Current", padding=12, style="Section.TLabelframe")
        left_frame.pack(side="left", fill="y", expand=False, padx=(0, 5))

        self.partial_text = tk.Text(
            left_frame,
            width=30,
            state="disabled",
            wrap="word",
            relief="sunken",
            borderwidth=1,
            bg="white",
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        )
        self.partial_text.pack(fill="both", expand=True)

        # RIGHT SIDE - Log
        right_frame = ttk.LabelFrame(content_frame, text="Log", padding=12, style="Section.TLabelframe")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            state="disabled",
            bg="white",
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        )
        self.output_text.pack(fill="both", expand=True)

        self.root.after(100, self.process_ui_queue)

    def process_ui_queue(self):
        """Apply UI updates from the worker thread."""
        try:
            while True:
                func, args, kwargs = self.ui_queue.get_nowait()
                func(*args, **kwargs)
        except queue.Empty:
            pass
        self.root.after(100, self.process_ui_queue)

    def ui_call(self, func, *args, **kwargs):
        """Schedule a UI update safely from any thread."""
        self.ui_queue.put((func, args, kwargs))

    def build_settings_frame(self, parent, include_save_button=False):
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding=12, style="Section.TLabelframe")
        settings_frame.pack(fill="x", padx=24, pady=(20, 10))

        # Target Name
        target_name_label = ttk.Label(settings_frame, text="Target Name:")
        target_name_label.grid(row=0, column=0, sticky="w", pady=5)
        target_name_entry = ttk.Entry(settings_frame, textvariable=self.target_name, width=40)
        target_name_entry.grid(row=0, column=1, sticky="ew", padx=8)

        # Model Path
        model_path_label = ttk.Label(settings_frame, text="Model Path:")
        model_path_label.grid(row=1, column=0, sticky="w", pady=5)
        model_path_entry = ttk.Entry(settings_frame, textvariable=self.model_path, width=40)
        model_path_entry.grid(row=1, column=1, sticky="ew", padx=8)
        browse_model_btn = ttk.Button(
            settings_frame,
            text="Browse...",
            command=self.browse_model,
            style="Utility.TButton",
        )
        browse_model_btn.grid(row=1, column=2, sticky="w")

        # Device Selection
        device_label = ttk.Label(settings_frame, text="Speaker Device (Zoom Output):")
        device_label.grid(row=2, column=0, sticky="w", pady=5)
        self.device_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.device_name,
            width=40,
            state="readonly",
        )
        self.device_combo.grid(row=2, column=1, sticky="ew", padx=8)
        refresh_devices_btn = ttk.Button(
            settings_frame,
            text="Refresh",
            command=self.refresh_devices,
            style="Utility.TButton",
        )
        refresh_devices_btn.grid(row=2, column=2, sticky="w")
        zoom_help_btn = ttk.Button(
            settings_frame,
            text="Zoom-only Help",
            command=self.show_zoom_help,
            style="Utility.TButton",
        )
        zoom_help_btn.grid(row=2, column=3, sticky="w", padx=(6, 0))

        # Sample Rate
        sample_rate_label = ttk.Label(settings_frame, text="Sample Rate:")
        sample_rate_label.grid(row=3, column=0, sticky="w", pady=5)
        sample_rate_entry = ttk.Entry(settings_frame, textvariable=self.sample_rate, width=40)
        sample_rate_entry.grid(row=3, column=1, sticky="ew", padx=8)

        # Block Size
        block_size_label = ttk.Label(settings_frame, text="Block Size:")
        block_size_label.grid(row=4, column=0, sticky="w", pady=5)
        block_size_entry = ttk.Entry(settings_frame, textvariable=self.block_size, width=40)
        block_size_entry.grid(row=4, column=1, sticky="ew", padx=8)

        # Cooldown
        cooldown_label = ttk.Label(settings_frame, text="Cooldown (seconds):")
        cooldown_label.grid(row=5, column=0, sticky="w", pady=5)
        cooldown_entry = ttk.Entry(settings_frame, textvariable=self.cooldown, width=40)
        cooldown_entry.grid(row=5, column=1, sticky="ew", padx=8)

        settings_frame.columnconfigure(1, weight=1)
        self.refresh_devices()

        if include_save_button:
            save_frame = ttk.Frame(parent)
            save_frame.pack(fill="x", padx=24, pady=(0, 12))
            save_button = ttk.Button(
                save_frame,
                text="Save",
                command=self.save_settings_and_close,
                style="Primary.TButton",
            )
            save_button.pack(side="right")

        return settings_frame

    def open_settings_window(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return

        self.settings_window = tk.Toplevel(self.toplevel)
        self.settings_window.title("zoomSnap - Detector Settings")
        self.settings_window.configure(bg=BG)
        self.settings_window.geometry("640x360")
        self.build_settings_frame(self.settings_window, include_save_button=True)
        self.settings_window.transient(self.toplevel)
        self.settings_window.grab_set()

    def save_settings_and_close(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.destroy()
            self.settings_window = None

    def log(self, message):
        """Log a message to the output text area"""
        self.output_text.config(state="normal") # Enable the textbox

        self.output_text.insert("end", message + "\n") # add to the "end" the (message + "\n")
        self.output_text.see("end") # scroll down to the "end" so we can see the end

        self.output_text.config(state="disabled") # Redisable the textbox 
        self.root.update()

    def get_last_log_snippet(self, max_chars=500):
        """Return the last N characters from the log"""
        try:
            return self.output_text.get(f"end-1c - {max_chars} chars", "end-1c")
        except tk.TclError:
            return self.output_text.get("1.0", "end-1c")

    def show_detection_popup(self, target_name):
        """Show a popup with a log snippet when a name is detected"""
        message = self.get_last_log_snippet(500).strip() or "(no log entries yet)"
        messagebox.showinfo(f"Detected: {target_name}", message)

    def browse_model(self):
        """Open folder picker for model selection"""
        had_grab = False
        if self.settings_window and self.settings_window.winfo_exists():
            try:
                if self.settings_window.grab_current() is not None:
                    self.settings_window.grab_release()
                    had_grab = True
            except tk.TclError:
                pass
        filename = filedialog.askopenfilename(
            title="Select any file inside the Vosk model folder",
            parent=self.settings_window or self.toplevel,
        )
        if had_grab and self.settings_window and self.settings_window.winfo_exists():
            try:
                self.settings_window.grab_set()
            except tk.TclError:
                pass
        if filename:
            folder = os.path.dirname(filename)
            self.model_path.set(folder)

    def update_partial(self, text):
        """Update the partial transcription text widget"""

        self.partial_text.config(state="normal") # Enable the text box
        
        self.partial_text.delete("1.0", "end") # Clear out from the beggining to the end
        self.partial_text.insert("1.0", text if text else "(listening...)") # Insert from the beggining the text else just listening
            
        self.partial_text.config(state="disabled") # Redisable the textbox
        self.root.update()

    def refresh_devices(self):
        """Refresh the list of audio devices"""
        if not self.device_combo:
            return
        speakers = sc.all_speakers()
        names = [s.name for s in speakers]
        default_name = sc.default_speaker().name if speakers else ""
        display_names = ["(Default system output)"] + names
        self.device_combo["values"] = display_names
        if not self.device_name.get():
            self.device_name.set("(Default system output)")
        elif self.device_name.get() not in display_names and default_name:
            self.device_name.set("(Default system output)")

    def find_loopback_microphone(self, device_name):
        """Find loopback microphone"""
        speakers = sc.all_speakers()

        if device_name and device_name != "(Default system output)":
            for spk in speakers:
                if spk.name == device_name:
                    # Turns that speaker into a loopback microphone and returns it
                    return sc.get_microphone(spk.name, include_loopback=True)

            available = ", ".join(s.name for s in speakers)
            raise RuntimeError(
                f"No speaker device matched '{device_name}'. Available: {available}"
            )

        # Use the default speakers if none
        default_speaker = sc.default_speaker()
        return sc.get_microphone(default_speaker.name, include_loopback=True)

    def show_zoom_help(self):
        message = (
            "To isolate Zoom audio, route Zoom to its own output device and select that device here:\n\n"
            "1) In Zoom > Settings > Audio, set Speaker to a dedicated device.\n"
            "2) Or in Windows > System > Sound > App volume and device preferences, set Zoom output.\n"
            "3) Optional: use a virtual audio cable device to keep Zoom separate.\n\n"
            "Then pick that same device from the Audio Device list."
        )
        messagebox.showinfo("Zoom-only Audio", message)

    def name_in_text(self, target: list[str], text: str) -> bool:
        """Check if target name is in text"""
        text = text.strip().lower()

        if not target or not text:
            return False
        
        for name in target:
            if name in text:
                return True

        return False

    def listen(self):
        """Listening thread"""
        try:
            target_name = self.target_name.get().strip().lower().replace(","," ").split()
            print(target_name)
            model_path = self.model_path.get()
            device_name = self.device_name.get() or None
            sample_rate = self.sample_rate.get()
            block_size = self.block_size.get()
            cooldown = self.cooldown.get()

            self.ui_call(self.update_partial, f"Loading model from: {model_path}")
            model = Model(model_path)
            self.recognizer = KaldiRecognizer(model, sample_rate)
            last_hit = 0.0

            while self.listening:
                try:
                    self.ui_call(self.update_partial, "Finding microphone...")
                    mic = self.find_loopback_microphone(device_name)

                    self.ui_call(
                        self.update_partial,
                        f"Device: {mic.name} \nTarget: {target_name} \nListening",
                    )

                    with mic.recorder(
                        samplerate=sample_rate,
                        channels=1,
                        blocksize=block_size,
                    ) as recorder:
                        while self.listening:
                            data = recorder.record(block_size) # Data is audio described in float -1.0 to 1.0
                            data16 = (data * 32767).astype(np.int16) # Amplify the audio because Vosk only accepts 16 bit integers (-32767 to 32767)

                            # Feed the audio into the recognizer
                            # Will return True if speech has ended (Final result) and False if not (Partial)
                            if self.recognizer.AcceptWaveform(data16.tobytes()): 
                                result = json.loads(self.recognizer.Result())
                                text = result.get("text", "")
                                if text:
                                    self.ui_call(self.update_partial, "")  # Clear partial
                                    self.ui_call(self.log, f"{text}")
                            else:
                                partial = json.loads(self.recognizer.PartialResult())
                                text = partial.get("partial", "")
                                self.ui_call(self.update_partial, text)  # Update partial label

                            if self.name_in_text(target_name, text):
                                now = time.time()
                                if now - last_hit >= cooldown:
                                    last_hit = now
                                    self.ui_call(self.log, f"DETECTED: '{target_name}'")
                                    self.ui_call(self.minmaxPrograms)
                                    self.ui_call(self.show_detection_popup, target_name)
                except Exception as e:
                    message = str(e).lower()
                    if "0x8889000a" in message or "audclnt_e_device_invalidated" in message:
                        self.ui_call(
                            self.update_partial,
                            "Audio device changed or was reset.\nRecconecting...\nPlease choose another audio device!",
                        )
                        time.sleep(1.0)
                        continue
                    raise
                            

        # When there is an error launching
        except Exception as e:
            self.ui_call(self.log, f"ERROR: {str(e)}")
            self.ui_call(messagebox.showerror, "Error", str(e))
        
        # Runs no matter what happens
        finally: 
            self.listening = False
            self.ui_call(self.start_button.config, state="normal")
            self.ui_call(self.stop_button.config, state="disabled")
            self.ui_call(self.log, "\nListening stopped.")

    def start_listening(self):
        """Start the listening thread"""
        if self.listening:
            messagebox.showwarning("Warning", "Already listening!")
            return

        self.listening = True

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")

        self.listener_thread = threading.Thread(target=self.listen, daemon=True)
        self.listener_thread.start()

    def stop_listening(self):
        """Stop the listening thread"""
        self.listening = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = NameDetectorGUI(root)
    root.mainloop()
