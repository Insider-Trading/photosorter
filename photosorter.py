import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
import shutil

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width=100, height=30, radius=15, btncolor="#1F6AA5", hovercolor="#155A8C", fg="white", text="", command=None):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.radius = radius
        self.btncolor = btncolor
        self.hovercolor = hovercolor
        self.fg = fg
        self.text = text
        self.width = width
        self.height = height
        self['cursor'] = 'hand2'
        self.draw_button(btncolor)

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def draw_button(self, color):
        self.delete("all")
        self.create_rounded_rect(0, 0, self.width, self.height, self.radius, fill=color, outline=color)
        self.create_text(self.width/2, self.height/2, text=self.text, fill=self.fg, font=('Segoe UI', 10))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x1+r, y1,
            x2-r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y1+r,
            x2, y2-r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x2-r, y2,
            x1+r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y2-r,
            x1, y1+r,
            x1, y1+r,
            x1, y1,
        ]
        self.create_polygon(points, **kwargs, smooth=True)

    def _on_press(self, event):
        self.draw_button(self.hovercolor)

    def _on_release(self, event):
        self.draw_button(self.btncolor)
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.draw_button(self.hovercolor)

    def _on_leave(self, event):
        self.draw_button(self.btncolor)

class PhotoSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Sorting Application")
        self.root.geometry("1100x700")
        self.current_image_index = 0
        self.image_paths = []
        self.target_dirs = {}
        self.move_history = []
        self.max_history = 5  # For undo functionality

        # Set the default font to Segoe UI
        default_font = ('Segoe UI', 10)
        self.root.option_add('*Font', default_font)

        # Set up the UI components
        self.setup_ui()

        # Bind arrow keys for navigation
        self.root.bind("<Left>", self.show_previous_image)
        self.root.bind("<Right>", self.show_next_image)

    def setup_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='#2D2D2D')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar frame for directories
        self.sidebar_frame = tk.Frame(self.main_frame, width=200, bg='#2D2D2D')
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Label for the sidebar
        self.sidebar_label = tk.Label(self.sidebar_frame, text="Target Directories", fg='white', bg='#2D2D2D')
        self.sidebar_label.pack(pady=5)

        # Directory listbox
        self.dir_listbox = tk.Listbox(self.sidebar_frame, bg='#3C3F41', fg='white', selectbackground='#6A6A6A', highlightthickness=0, borderwidth=0)
        self.dir_listbox.pack(fill=tk.Y, expand=True, padx=5, pady=5)

        # Button to add directories
        self.add_dir_button = RoundedButton(self.sidebar_frame, text="Add Directory", command=self.add_directory)
        self.add_dir_button.pack(pady=5)

        # Frame for the image display
        self.image_frame = tk.Frame(self.main_frame, bg='#2D2D2D')
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.image_frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Frame for the control buttons
        self.control_frame = tk.Frame(self.root, bg='#2D2D2D')
        self.control_frame.pack(pady=10)

        # Load folder button
        self.load_button = RoundedButton(self.control_frame, text="Load Folder", command=self.load_folder)
        self.load_button.grid(row=0, column=0, padx=5)

        # Undo button
        self.undo_button = RoundedButton(self.control_frame, text="Undo", command=self.undo_move)
        self.undo_button.grid(row=0, column=1, padx=5)

        # Progress label
        self.progress_label = tk.Label(self.root, text="No images loaded.", fg='white', bg='#2D2D2D')
        self.progress_label.pack(pady=5)

    def load_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Folder with Images")
        if folder_selected:
            self.image_paths = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if not self.image_paths:
                messagebox.showwarning("No Images", "No image files found in the selected directory.")
                return

            # Reset variables
            self.current_image_index = 0
            self.move_history.clear()

            # Load the first image
            self.display_image()
        else:
            messagebox.showinfo("No Folder Selected", "Please select a folder to load images from.")

    def display_image(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            img = Image.open(img_path)

            # Resize image to fit canvas while maintaining aspect ratio
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width == 1 or canvas_height == 1:
                # Default size before window is fully rendered
                canvas_width = 800
                canvas_height = 600
            img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            self.canvas.delete("all")  # Clear previous image
            self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.photo)

            # Update progress label
            self.update_progress_label()
        else:
            messagebox.showinfo("Completed", "All images have been sorted.")
            self.canvas.delete("all")
            self.progress_label.config(text="All images have been sorted.")

    def update_progress_label(self):
        current_image_name = os.path.basename(self.image_paths[self.current_image_index])
        self.progress_label.config(text=f"Photo {self.current_image_index + 1} of {len(self.image_paths)} - {current_image_name}")

    def add_directory(self):
        dir_name = simpledialog.askstring("Directory Name", "Enter name for the directory:", parent=self.root)
        if not dir_name:
            return
        dir_path = filedialog.askdirectory(title=f"Select path for '{dir_name}'")
        if dir_path:
            # Ask for custom hotkey
            while True:
                hotkey = simpledialog.askstring("Assign Hotkey", f"Assign a hotkey for '{dir_name}':", parent=self.root)
                if hotkey and len(hotkey) == 1:
                    hotkey = hotkey.lower()
                    if hotkey not in [d['hotkey'] for d in self.target_dirs.values()]:
                        break
                    else:
                        messagebox.showwarning("Hotkey Conflict", f"The hotkey '{hotkey}' is already in use. Please choose another.")
                else:
                    messagebox.showwarning("Invalid Hotkey", "Please enter a single character for the hotkey.")

            self.target_dirs[dir_name] = {'path': dir_path, 'hotkey': hotkey}

            # Update listbox
            self.dir_listbox.insert(END, f"{dir_name} (Hotkey: {hotkey.upper()})")

            # Bind hotkey
            self.root.bind(f"<KeyPress-{hotkey}>", lambda event, d=dir_name: self.move_image(d))
        else:
            messagebox.showwarning("No Directory Selected", f"No directory selected for '{dir_name}'.")

    def move_image(self, dir_name):
        if 0 <= self.current_image_index < len(self.image_paths):
            src_path = self.image_paths[self.current_image_index]
            dst_dir = self.target_dirs[dir_name]['path']
            try:
                shutil.move(src_path, dst_dir)
                self.move_history.append((src_path, dst_dir))
                if len(self.move_history) > self.max_history:
                    self.move_history.pop(0)
                self.image_paths.pop(self.current_image_index)
                if self.current_image_index >= len(self.image_paths):
                    self.current_image_index = len(self.image_paths) - 1
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error Moving File", f"An error occurred while moving the file: {e}")
        else:
            messagebox.showinfo("Completed", "All images have been sorted.")

    def undo_move(self):
        if self.move_history:
            src_path, dst_dir = self.move_history.pop()
            filename = os.path.basename(src_path)
            src_path_new = os.path.join(dst_dir, filename)
            try:
                shutil.move(src_path_new, os.path.dirname(src_path))
                self.image_paths.insert(self.current_image_index, src_path)
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error Undoing Move", f"An error occurred while undoing the move: {e}")
        else:
            messagebox.showinfo("Undo", "No actions to undo.")

    def show_next_image(self, event=None):
        if self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.display_image()
        else:
            messagebox.showinfo("End of Images", "You have reached the last image.")

    def show_previous_image(self, event=None):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_image()
        else:
            messagebox.showinfo("Start of Images", "You are at the first image.")

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#2D2D2D')  # Set the background color
    app = PhotoSorterApp(root)
    root.mainloop()
