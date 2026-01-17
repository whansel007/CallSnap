import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import time
import warnings
import numpy as np
import soundcard as sc
from vosk import KaldiRecognizer, Model

# Suppress soundcard discontinuity warning
warnings.filterwarnings("ignore", message="data discontinuity in recording")


class NameDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CallSnap - Name Detector")
        self.root.geometry("1000x600")
        self.listening = False
        self.recognizer = None
        self.listener_thread = None

        # Settings frame
        settings_frame = ttk.LabelFrame(root, text="Settings", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Target Name
        ttk.Label(settings_frame, text="Target Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_name = tk.StringVar(value="alex")
        ttk.Entry(settings_frame, textvariable=self.target_name, width=40).grid(row=0, column=1, sticky="ew", padx=5)

        # Model Path
        ttk.Label(settings_frame, text="Model Path:").grid(row=1, column=0, sticky="w", pady=5)
        self.model_path = tk.StringVar(value="./models/vosk-model-small-en-us-0.15")
        ttk.Entry(settings_frame, textvariable=self.model_path, width=40).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(settings_frame, text="Browse...", command=self.browse_model).grid(row=1, column=2, sticky="w")

        # Device Selection
        ttk.Label(settings_frame, text="Audio Device (Zoom output):").grid(row=2, column=0, sticky="w", pady=5)
        self.device_name = tk.StringVar(value="")
        self.device_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.device_name,
            width=40,
            state="readonly",
        )
        self.device_combo.grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Button(settings_frame, text="Refresh", command=self.refresh_devices).grid(row=2, column=2, sticky="w")
        ttk.Button(settings_frame, text="Zoom-only Help", command=self.show_zoom_help).grid(row=2, column=3, sticky="w", padx=(5, 0))

        # Sample Rate
        ttk.Label(settings_frame, text="Sample Rate:").grid(row=3, column=0, sticky="w", pady=5)
        self.sample_rate = tk.IntVar(value=16000)
        ttk.Entry(settings_frame, textvariable=self.sample_rate, width=40).grid(row=3, column=1, sticky="ew", padx=5)

        # Block Size
        ttk.Label(settings_frame, text="Block Size:").grid(row=4, column=0, sticky="w", pady=5)
        self.block_size = tk.IntVar(value=4096)
        ttk.Entry(settings_frame, textvariable=self.block_size, width=40).grid(row=4, column=1, sticky="ew", padx=5)

        # Cooldown
        ttk.Label(settings_frame, text="Cooldown (seconds):").grid(row=5, column=0, sticky="w", pady=5)
        self.cooldown = tk.DoubleVar(value=5.0)
        ttk.Entry(settings_frame, textvariable=self.cooldown, width=40).grid(row=5, column=1, sticky="ew", padx=5)

        settings_frame.columnconfigure(1, weight=1)
        self.refresh_devices()

        # Button frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Listening", command=self.start_listening)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Listening", command=self.stop_listening, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Main content frame (left + right)
        content_frame = ttk.Frame(root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT SIDE - Current transcription
        left_frame = ttk.LabelFrame(content_frame, text="Current", padding=10)
        left_frame.pack(side="left", fill="y", expand=False, padx=(0, 5))

        self.partial_text = tk.Text(left_frame, width=30, state="disabled", wrap="word", relief="sunken", borderwidth=1)
        self.partial_text.pack(fill="both", expand=True)

        # RIGHT SIDE - Log
        right_frame = ttk.LabelFrame(content_frame, text="Log", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.output_text = scrolledtext.ScrolledText(right_frame, state="disabled")
        self.output_text.pack(fill="both", expand=True)

    def log(self, message):
        """Log a message to the output text area"""
        self.output_text.config(state="normal") # Enable the textbox

        self.output_text.insert("end", message + "\n") # add to the "end" the (message + "\n")
        self.output_text.see("end") # scroll down to the "end" so we can see the end

        self.output_text.config(state="disabled") # Redisable the textbox 
        self.root.update()

    def browse_model(self):
        """Open folder picker for model selection"""
        folder = filedialog.askdirectory(title="Select Vosk Model Folder")
        if folder:
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

    def name_in_text(self, target: str, text: str) -> bool:
        """Check if target name is in text"""
        target = target.strip().lower()
        text = text.strip().lower()

        if not target or not text:
            return False

        return target in text

    def listen(self):
        """Listening thread"""
        try:
            target_name = self.target_name.get()
            model_path = self.model_path.get()
            device_name = self.device_name.get() or None
            sample_rate = self.sample_rate.get()
            block_size = self.block_size.get()
            cooldown = self.cooldown.get()

            self.update_partial(f"Loading model from: {model_path}")
            model = Model(model_path)
            self.recognizer = KaldiRecognizer(model, sample_rate)

            self.update_partial("Finding microphone...")
            mic = self.find_loopback_microphone(device_name)

            self.update_partial(f"Device: {mic.name} \nTarget: {target_name} \nListening")
            last_hit = 0.0

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
                            self.update_partial("")  # Clear partial
                            self.log(f"{text}")
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        text = partial.get("partial", "")
                        self.update_partial(text)  # Update partial label

                    if self.name_in_text(target_name, text):
                        now = time.time()
                        if now - last_hit >= cooldown:
                            last_hit = now
                            self.log(f"DETECTED: '{target_name}'")

        # When there is an error launching
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))
        
        # Runs no matter what happens
        finally: 
            self.listening = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.log("\nListening stopped.")

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
