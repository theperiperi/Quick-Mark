import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import cv2
import numpy as np

# Color palette
COLOR_PRIMARY = "#413299"  # Deep Purple
COLOR_ACCENT = "#7EDAD5"   # Seafoam
COLOR_BG = "#E9EBED"       # Light Gray
COLOR_TEXT = "#000000"     # Black text

class RoundedFrame(tk.Frame):
    """Custom rounded frame class."""
    def __init__(self, parent, width, height, radius, bg_color, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, **kwargs)
        self.width = width
        self.height = height
        self.radius = radius
        self.bg_color = bg_color
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg_color, bd=0, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.canvas.create_arc(0, 0, radius * 2, radius * 2, start=90, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(width - radius * 2, 0, width, radius * 2, start=0, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(0, height - radius * 2, radius * 2, height, start=180, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_arc(width - radius * 2, height - radius * 2, width, height, start=270, extent=90, fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(radius, 0, width - radius, height, fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(0, radius, width, height - radius, fill=bg_color, outline=bg_color)

class QuickMarkUI:
    def __init__(self, root, on_close_callback):
        self.root = root
        self.root.title("QuickMark")
        self.root.configure(bg=COLOR_BG)  # Light Gray background
        self.on_close_callback = on_close_callback

        # Define fonts
        self.courier_font = font.Font(family="Courier New", size=12, weight="bold")  # For "Center your face..." text
        self.segoe_ui_large = font.Font(family="Segoe UI", size=16)  # For instructions (top message)
        self.segoe_ui_small = font.Font(family="Segoe UI", size=12)  # For name and actions (bottom text)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        # Video frame label
        self.video_label = tk.Label(self.main_frame, bg=COLOR_BG)
        self.video_label.pack(pady=(0, 20))

        # "Center your face and wait for instructions" text (overlaid on video)
        self.instruction_text = "Center your face and wait for instructions"
        self.instruction_label = tk.Label(self.main_frame, text=self.instruction_text,
                                         font=self.courier_font, fg="white")  # Transparent background
        self.instruction_label.place(in_=self.video_label, relx=0.5, rely=0.1, anchor="center")

        # --- Top Rounded Frame for Instructions ---
        self.top_frame = RoundedFrame(self.main_frame, width=680, height=60, radius=20, bg_color=COLOR_PRIMARY)
        self.top_frame.pack(pady=(20, 10))

        self.liveness_instruction = tk.Label(self.top_frame, text="Performing liveness check...",
                                             font=self.segoe_ui_large, fg="white", bg=COLOR_PRIMARY)
        self.liveness_instruction.place(relx=0.5, rely=0.5, anchor="center")

        # --- Bottom Rounded Frame for Name + Actions ---
        self.bottom_frame = RoundedFrame(self.main_frame, width=680, height=110, radius=20, bg_color=COLOR_ACCENT)
        self.bottom_frame.pack(pady=(5, 0))

        self.name_label = tk.Label(self.bottom_frame, text="Name: Unknown",
                                   font=self.segoe_ui_small, fg=COLOR_TEXT, bg=COLOR_ACCENT)
        self.name_label.place(relx=0.5, rely=0.35, anchor="center")

        self.actions_label = tk.Label(self.bottom_frame, text="Completed Actions: 0/3",
                                      font=self.segoe_ui_small, fg=COLOR_TEXT, bg=COLOR_ACCENT)
        self.actions_label.place(relx=0.5, rely=0.7, anchor="center")

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_frame(self, frame):
        """Update the webcam feed in the UI."""
        # Resize frame to fit UI (e.g., 640x480 as per preprocessing)
        frame = cv2.resize(frame, (640, 480))
        # Convert frame to RGB for Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        # Update video label
        self.video_label.configure(image=photo)
        self.video_label.image = photo  # Keep a reference to avoid garbage collection

    def update_instructions(self, instruction):
        """Update the liveness instruction text."""
        self.liveness_instruction.configure(text=instruction)

    def update_name(self, name):
        """Update the detected name."""
        self.name_label.configure(text=f"Name: {name}")

    def update_actions(self, completed, total=3):
        """Update the completed actions counter."""
        self.actions_label.configure(text=f"Completed Actions: {completed}/{total}")

    def on_closing(self):
        """Handle window closing."""
        self.on_close_callback()
        self.root.destroy()

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()