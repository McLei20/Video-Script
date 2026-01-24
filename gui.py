import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from ffmpeg_utils import batch_create_variations

class VideoVariationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Variation System")
        self.root.geometry("550x500")
        self.root.resizable(False, False)
        
        # Main frame with padding
        main_frame = tk.Frame(root, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        tk.Label(main_frame, text="Video Variation System", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Input folder
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill="x", pady=5)
        tk.Label(input_frame, text="Input Folder:", width=12, anchor="w").pack(side="left")
        self.input_path = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.input_path, width=35).pack(side="left", padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_input, width=8).pack(side="left")
        
        # Output folder
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill="x", pady=5)
        tk.Label(output_frame, text="Output Folder:", width=12, anchor="w").pack(side="left")
        self.output_path = tk.StringVar()
        tk.Entry(output_frame, textvariable=self.output_path, width=35).pack(side="left", padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output, width=8).pack(side="left")
        
        # Variations count
        var_frame = tk.Frame(main_frame)
        var_frame.pack(fill="x", pady=5)
        tk.Label(var_frame, text="Variations:", width=12, anchor="w").pack(side="left")
        self.variations = tk.IntVar(value=3)
        tk.Spinbox(var_frame, from_=1, to=100, textvariable=self.variations, width=10).pack(side="left", padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=15)
        
        # Options label
        tk.Label(main_frame, text="Options:", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        
        # Options frame
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill="x", pady=10, padx=20)
        
        self.reencode = tk.BooleanVar()
        self.use_filter = tk.BooleanVar()
        self.use_audio = tk.BooleanVar()
        
        tk.Checkbutton(options_frame, text="Re-encode (slower, deeper uniqueness)", variable=self.reencode, anchor="w").pack(fill="x", pady=2)
        tk.Checkbutton(options_frame, text="Visual filters (brightness, contrast, saturation, gamma)", variable=self.use_filter, anchor="w").pack(fill="x", pady=2)
        tk.Checkbutton(options_frame, text="Audio filters (volume, tempo)", variable=self.use_audio, anchor="w").pack(fill="x", pady=2)
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=15)
        
        # Progress
        self.progress_label = tk.Label(main_frame, text="Ready", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate", length=300)
        self.progress_bar.pack(pady=5)
        
        # Start button
        self.start_btn = tk.Button(
            main_frame, 
            text="START PROCESSING", 
            command=self.start_processing, 
            bg="#28a745", 
            fg="white", 
            font=("Arial", 11, "bold"),
            width=20, 
            height=2,
            cursor="hand2"
        )
        self.start_btn.pack(pady=15)
    
    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)
    
    def start_processing(self):
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select input and output folders")
            return
        
        # Enable reencode if filters are selected
        reencode = self.reencode.get()
        if (self.use_filter.get() or self.use_audio.get()) and not reencode:
            reencode = True
        
        # Update UI
        self.progress_label.config(text="Processing...")
        self.progress_bar.start(10)
        self.start_btn.config(state="disabled", bg="gray")
        
        # Run in thread to prevent GUI freeze
        thread = threading.Thread(target=self.run_batch, args=(reencode,))
        thread.start()
    
    def run_batch(self, reencode):
        try:
            results = batch_create_variations(
                input_folder=self.input_path.get(),
                output_folder=self.output_path.get(),
                variations_per_video=self.variations.get(),
                reencode=reencode,
                use_filter=self.use_filter.get(),
                use_audio=self.use_audio.get()
            )
            self.root.after(0, lambda: self.on_complete(len(results)))
        except Exception as e:
            self.root.after(0, lambda: self.on_error(str(e)))
    
    def on_complete(self, count):
        self.progress_bar.stop()
        self.progress_label.config(text=f"Done! Created {count} videos")
        self.start_btn.config(state="normal", bg="#28a745")
        messagebox.showinfo("Complete", f"Successfully created {count} unique videos!")
    
    def on_error(self, error):
        self.progress_bar.stop()
        self.progress_label.config(text="Error occurred")
        self.start_btn.config(state="normal", bg="#28a745")
        messagebox.showerror("Error", error)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoVariationGUI(root)
    root.mainloop()