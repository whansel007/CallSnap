import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import time
import numpy as np
import soundcard as sc
from vosk import KaldiRecognizer, Model


class NameDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CallSnap - Name Detector")
        self.root.geometry("600x700")
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

        # Device Keyword
        ttk.Label(settings_frame, text="Device Keyword:").grid(row=2, column=0, sticky="w", pady=5)
        self.device_keyword = tk.StringVar(value="")
        ttk.Entry(settings_frame, textvariable=self.device_keyword, width=40).grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Label(settings_frame, text="(Leave empty for default)", font=("Arial", 8)).grid(row=2, column=2, sticky="w")

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

        # Button frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Listening", command=self.start_listening)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Listening", command=self.stop_listening, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Status frame
        status_frame = ttk.LabelFrame(root, text="Status", padding=10)
        status_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Partial transcription label
        partial_frame = ttk.Frame(status_frame)
        partial_frame.pack(fill="x", padx=5, pady=(0, 10))
        ttk.Label(partial_frame, text="Current:").pack(side="left", padx=5)
        self.partial_text = tk.Text(partial_frame, height=2, state="disabled", wrap="word", relief="sunken", borderwidth=1)
        self.partial_text.pack(side="left", padx=5, fill="both", expand=True)

        self.output_text = scrolledtext.ScrolledText(status_frame, height=15, width=70, state="disabled")
        self.output_text.pack(fill="both", expand=True)

    def log(self, message):
        """Log a message to the output text area"""
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")
        self.root.update()

    def update_partial(self, text):
        """Update the partial transcription text widget"""
        self.partial_text.config(state="normal")
        self.partial_text.delete("1.0", "end")
        self.partial_text.insert("1.0", text if text else "(listening...)")
        if not text:
            self.partial_text.tag_add("gray", "1.0", "end")
        self.partial_text.config(state="disabled")
        self.root.update()

    def find_loopback_microphone(self, device_keyword):
        """Find loopback microphone"""
        speakers = sc.all_speakers()

        if device_keyword:
            keyword = device_keyword.lower()
            for spk in speakers:
                if keyword in spk.name.lower():
                    return sc.get_microphone(spk.name, include_loopback=True)

            available = ", ".join(s.name for s in speakers)
            raise RuntimeError(
                f"No speaker device matched '{device_keyword}'. Available: {available}"
            )

        default_speaker = sc.default_speaker()
        return sc.get_microphone(default_speaker.name, include_loopback=True)

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
            device_keyword = self.device_keyword.get() or None
            sample_rate = self.sample_rate.get()
            block_size = self.block_size.get()
            cooldown = self.cooldown.get()

            self.log(f"Loading model from: {model_path}")
            model = Model(model_path)
            self.recognizer = KaldiRecognizer(model, sample_rate)

            self.log("Finding microphone...")
            mic = self.find_loopback_microphone(device_keyword)

            self.log(f"Device: {mic.name}")
            self.log(f"Target: {target_name}")
            self.log("Listening... (Click 'Stop Listening' to stop)\n")

            last_hit = 0.0

            with mic.recorder(
                samplerate=sample_rate,
                channels=1,
                blocksize=block_size,
            ) as recorder:
                while self.listening:
                    data = recorder.record(block_size)
                    data16 = (data * 32767).astype(np.int16)

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
                            self.log(f"✓ DETECTED: '{target_name}'")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))
            
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
