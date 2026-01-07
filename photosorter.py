import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import os
import shutil
import json

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width=120, height=38, radius=19, btncolor="#4A90E2", hovercolor="#357ABD", presscolor="#2A5A8D", fg="white", text="", command=None, font_size=10, font_weight='normal'):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.radius = radius
        self.btncolor = btncolor
        self.hovercolor = hovercolor
        self.presscolor = presscolor
        self.fg = fg
        self.text = text
        self.width = width
        self.height = height
        self.font_size = font_size
        self.font_weight = font_weight
        self['cursor'] = 'hand2'
        self.is_pressed = False
        self.draw_button(btncolor, shadow=True)

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def draw_button(self, color, shadow=False):
        self.delete("all")

        # Draw shadow for depth
        if shadow and not self.is_pressed:
            shadow_offset = 2
            shadow_color = '#00000040'  # Semi-transparent black
            self.create_rounded_rect(shadow_offset, shadow_offset,
                                    self.width + shadow_offset, self.height + shadow_offset,
                                    self.radius, fill='#1A1A1A', outline='')

        # Draw button background
        y_offset = 2 if self.is_pressed else 0
        self.create_rounded_rect(0, y_offset, self.width, self.height + y_offset,
                                self.radius, fill=color, outline='')

        # Draw subtle inner highlight for 3D effect (top half lighter)
        if not self.is_pressed:
            # Calculate lighter color for gradient effect
            lighter = self._lighten_color(color, 0.15)
            self.create_rounded_rect(2, y_offset + 2, self.width - 2, self.height//3 + y_offset,
                                    self.radius - 2, fill=lighter, outline='')

        # Draw text
        self.create_text(self.width/2, self.height/2 + y_offset, text=self.text,
                        fill=self.fg, font=('Segoe UI', self.font_size, self.font_weight))

    def _lighten_color(self, hex_color, factor):
        """Lighten a hex color by a factor (0.0 to 1.0)"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

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
        self.is_pressed = True
        self.draw_button(self.presscolor, shadow=False)

    def _on_release(self, event):
        self.is_pressed = False
        self.draw_button(self.hovercolor, shadow=True)
        if self.command:
            self.command()

    def _on_enter(self, event):
        if not self.is_pressed:
            self.draw_button(self.hovercolor, shadow=True)

    def _on_leave(self, event):
        self.is_pressed = False
        self.draw_button(self.btncolor, shadow=True)

class PhotoSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Sorter - LoRA Training Assistant")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.current_image_index = 0
        self.image_paths = []
        self.target_dirs = {}
        self.move_history = []
        self.max_history = 100
        self.config_file = "photosorter_config.json"
        self.last_folder = None
        self.show_metadata = True  # Enable metadata by default
        self.flagged_images = []
        self.show_help = False

        # Color scheme - Modern dark theme with accent colors
        self.colors = {
            'bg_dark': '#1E1E1E',
            'bg_medium': '#252526',
            'bg_light': '#2D2D30',
            'bg_lighter': '#3E3E42',
            'accent_blue': '#4A90E2',
            'accent_blue_hover': '#357ABD',
            'accent_green': '#5CB85C',
            'accent_green_hover': '#449D44',
            'accent_orange': '#FF9500',
            'accent_red': '#E74C3C',
            'text_primary': '#FFFFFF',
            'text_secondary': '#CCCCCC',
            'text_muted': '#858585',
            'border': '#3E3E42',
            'shadow': '#000000'
        }

        # Set default font
        default_font = ('Segoe UI', 10)
        self.root.option_add('*Font', default_font)

        # Set up the UI components
        self.setup_ui()

        # Load saved configuration
        self.load_config()

        # Bind keyboard shortcuts
        self.root.bind("<Left>", self.show_previous_image)
        self.root.bind("<Right>", self.show_next_image)
        self.root.bind("<Control-z>", lambda e: self.undo_move())
        self.root.bind("<Delete>", lambda e: self.move_to_trash())
        self.root.bind("i", lambda e: self.toggle_metadata())
        self.root.bind("<space>", lambda e: self.show_next_image())
        self.root.bind("f", lambda e: self.toggle_flag())
        self.root.bind("F", lambda e: self.view_flagged())
        self.root.bind("h", lambda e: self.toggle_help())
        self.root.bind("<question>", lambda e: self.toggle_help())

        # Bind number keys 1-9 for quick directory access
        for i in range(1, 10):
            self.root.bind(str(i), lambda e, idx=i-1: self.move_to_index(idx))

        # Save config on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Main container with padding
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # TOP BAR - Title and controls
        self.top_bar = tk.Frame(self.main_frame, bg=self.colors['bg_light'], height=60)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)
        self.top_bar.pack_propagate(False)

        # App title
        title_label = tk.Label(self.top_bar, text="Photo Sorter",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_light'])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Subtitle
        subtitle_label = tk.Label(self.top_bar, text="LoRA Training Dataset Assistant",
                                 font=('Segoe UI', 9),
                                 fg=self.colors['text_muted'],
                                 bg=self.colors['bg_light'])
        subtitle_label.pack(side=tk.LEFT, pady=15)

        # Help button in top bar
        help_btn = tk.Label(self.top_bar, text="? Help (H)",
                           font=('Segoe UI', 9),
                           fg=self.colors['accent_blue'],
                           bg=self.colors['bg_light'],
                           cursor='hand2')
        help_btn.pack(side=tk.RIGHT, padx=20)
        help_btn.bind("<Button-1>", lambda e: self.toggle_help())

        # Content area
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # SIDEBAR - Enhanced with cards
        self.sidebar_frame = tk.Frame(content_frame, width=280, bg=self.colors['bg_medium'])
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        self.sidebar_frame.pack_propagate(False)

        # Sidebar header
        sidebar_header = tk.Label(self.sidebar_frame, text="TARGET DIRECTORIES",
                                 font=('Segoe UI', 9, 'bold'),
                                 fg=self.colors['text_muted'],
                                 bg=self.colors['bg_medium'])
        sidebar_header.pack(pady=(15, 10), padx=15, anchor='w')

        # Scrollable directory list container
        list_container = tk.Frame(self.sidebar_frame, bg=self.colors['bg_medium'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Directory listbox with modern styling - enable multi-select
        self.dir_listbox = tk.Listbox(list_container,
                                      bg=self.colors['bg_light'],
                                      fg=self.colors['text_primary'],
                                      selectbackground=self.colors['accent_blue'],
                                      selectforeground=self.colors['text_primary'],
                                      highlightthickness=0,
                                      borderwidth=0,
                                      font=('Segoe UI', 9),
                                      activestyle='none',
                                      selectmode=tk.EXTENDED)  # Enable multi-select with Ctrl+Click
        self.dir_listbox.pack(fill=tk.BOTH, expand=True)

        # Right-click context menu for directory list
        self.dir_context_menu = tk.Menu(self.dir_listbox, tearoff=0,
                                        bg=self.colors['bg_light'],
                                        fg=self.colors['text_primary'],
                                        activebackground=self.colors['accent_blue'],
                                        activeforeground=self.colors['text_primary'])
        self.dir_context_menu.add_command(label="Delete Directory", command=self.delete_selected_directory)

        # Bind right-click to show context menu
        self.dir_listbox.bind("<Button-3>", self.show_directory_context_menu)

        # Button container
        button_frame = tk.Frame(self.sidebar_frame, bg=self.colors['bg_medium'])
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)

        # Add Directory button
        self.add_dir_button = RoundedButton(button_frame, width=250, height=38,
                                           text="+ Add Directory",
                                           command=self.add_directory,
                                           btncolor=self.colors['accent_blue'],
                                           hovercolor=self.colors['accent_blue_hover'])
        self.add_dir_button.pack(pady=(0, 8))

        # Remove Directory button
        self.remove_dir_button = RoundedButton(button_frame, width=250, height=38,
                                              text="- Remove Selected",
                                              command=self.delete_selected_directory,
                                              btncolor=self.colors['accent_red'],
                                              hovercolor='#C0392B')
        self.remove_dir_button.pack(pady=(0, 8))

        # Quick Setup button
        self.quick_setup_button = RoundedButton(button_frame, width=250, height=38,
                                               text="Quick Setup",
                                               command=self.quick_setup,
                                               btncolor=self.colors['accent_green'],
                                               hovercolor=self.colors['accent_green_hover'])
        self.quick_setup_button.pack()

        # MAIN IMAGE AREA
        self.image_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Canvas for image with subtle border
        canvas_container = tk.Frame(self.image_frame, bg=self.colors['border'],
                                   highlightthickness=0)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg='#000000', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Enhanced preview with better styling
        self.preview_canvas = tk.Canvas(self.image_frame, width=160, height=160,
                                       bg=self.colors['bg_light'],
                                       highlightthickness=2,
                                       highlightbackground=self.colors['border'])
        self.preview_canvas.place(relx=0.98, rely=0.98, anchor='se')

        # BOTTOM BAR - Controls and progress
        self.bottom_bar = tk.Frame(self.main_frame, bg=self.colors['bg_light'], height=70)
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_bar.pack_propagate(False)

        # Control buttons container
        controls_left = tk.Frame(self.bottom_bar, bg=self.colors['bg_light'])
        controls_left.pack(side=tk.LEFT, padx=20, pady=15)

        # Load Folder button
        self.load_button = RoundedButton(controls_left, width=140, height=38,
                                        text="Load Folder",
                                        command=self.load_folder,
                                        btncolor=self.colors['accent_blue'],
                                        hovercolor=self.colors['accent_blue_hover'],
                                        font_size=10,
                                        font_weight='bold')
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Undo button
        self.undo_button = RoundedButton(controls_left, width=100, height=38,
                                        text="Undo",
                                        command=self.undo_move,
                                        btncolor=self.colors['bg_lighter'],
                                        hovercolor=self.colors['accent_blue_hover'])
        self.undo_button.pack(side=tk.LEFT, padx=5)

        # Progress info in center
        progress_container = tk.Frame(self.bottom_bar, bg=self.colors['bg_light'])
        progress_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=15)

        self.progress_label = tk.Label(progress_container,
                                      text="No images loaded",
                                      font=('Segoe UI', 10),
                                      fg=self.colors['text_secondary'],
                                      bg=self.colors['bg_light'])
        self.progress_label.pack()

        # Progress bar
        self.progress_bar_canvas = tk.Canvas(progress_container, height=4,
                                            bg=self.colors['bg_medium'],
                                            highlightthickness=0)
        self.progress_bar_canvas.pack(fill=tk.X, padx=100, pady=(5, 0))

        # Stats in right corner
        stats_frame = tk.Frame(self.bottom_bar, bg=self.colors['bg_light'])
        stats_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        self.stats_label = tk.Label(stats_frame,
                                    text="0 sorted | 0 remaining",
                                    font=('Segoe UI', 9),
                                    fg=self.colors['text_muted'],
                                    bg=self.colors['bg_light'])
        self.stats_label.pack()

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
            self.last_folder = folder_selected
            self.save_config()

            # Load the first image
            self.display_image()
        else:
            messagebox.showinfo("No Folder Selected", "Please select a folder to load images from.")

    def display_image(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            img = Image.open(img_path)
            original_width, original_height = img.size

            # Resize image to fit canvas while maintaining aspect ratio
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width == 1 or canvas_height == 1:
                canvas_width = 800
                canvas_height = 600

            # Add padding for better framing
            padding = 40
            img.thumbnail((canvas_width - padding, canvas_height - padding), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            self.canvas.delete("all")
            self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.photo)

            # Display compact metadata overlay
            if self.show_metadata:
                filename = os.path.basename(img_path)
                file_size = os.path.getsize(img_path) / 1024
                aspect_ratio = original_width / original_height

                # Compact metadata card
                card_x = 12
                card_y = 12
                card_padding = 10

                # Truncate filename if too long
                display_name = filename if len(filename) <= 30 else filename[:27] + "..."

                # Measure text to make card fit content - more reasonable width
                card_width = min(260, max(200, len(display_name) * 6 + 20))
                card_height = 68

                # Shadow
                self.canvas.create_rectangle(card_x + 2, card_y + 2,
                                            card_x + card_width + 2, card_y + card_height + 2,
                                            fill='#000000', outline='')

                # Card background with slight transparency effect
                self.canvas.create_rectangle(card_x, card_y, card_x + card_width, card_y + card_height,
                                            fill=self.colors['bg_light'], outline=self.colors['border'], width=1)

                # Filename on first line
                self.canvas.create_text(card_x + card_padding, card_y + card_padding,
                                       text=display_name,
                                       fill=self.colors['text_primary'],
                                       font=('Segoe UI', 9, 'bold'), anchor='nw')

                # Compact metadata on second line
                metadata_line = f"{original_width}×{original_height} • {file_size:.1f}KB • {aspect_ratio:.2f}:1"
                self.canvas.create_text(card_x + card_padding, card_y + card_padding + 22,
                                       text=metadata_line,
                                       fill=self.colors['text_secondary'],
                                       font=('Segoe UI', 8), anchor='nw')

                # Index in smaller text on third line
                index_text = f"#{self.current_image_index + 1} of {len(self.image_paths)}"
                self.canvas.create_text(card_x + card_padding, card_y + card_padding + 44,
                                       text=index_text,
                                       fill=self.colors['text_muted'],
                                       font=('Segoe UI', 8), anchor='nw')

            # Enhanced flag indicator
            if img_path in self.flagged_images:
                flag_width = 120
                flag_height = 44
                flag_x = canvas_width - flag_width - 15
                flag_y = 15

                # Shadow
                self.canvas.create_rectangle(flag_x + 2, flag_y + 2,
                                            flag_x + flag_width + 2, flag_y + flag_height + 2,
                                            fill='#000000', outline='', stipple='gray50')

                # Flag badge
                self.canvas.create_rectangle(flag_x, flag_y, flag_x + flag_width, flag_y + flag_height,
                                            fill=self.colors['accent_orange'],
                                            outline='#FF5722', width=2)
                self.canvas.create_text(flag_x + flag_width//2, flag_y + flag_height//2,
                                       text="FLAGGED",
                                       fill='white', font=('Segoe UI', 11, 'bold'))

            # Update all UI elements
            self.update_progress_label()
            self.update_progress_bar()
            self.update_directory_list()
            self.update_stats()
            self.show_preview()
        else:
            messagebox.showinfo("Completed", "All images have been sorted.")
            self.canvas.delete("all")
            self.preview_canvas.delete("all")
            self.progress_label.config(text="All images sorted")

    def update_progress_label(self):
        if self.image_paths and 0 <= self.current_image_index < len(self.image_paths):
            current_image_name = os.path.basename(self.image_paths[self.current_image_index])
            # Truncate long filenames
            if len(current_image_name) > 40:
                current_image_name = current_image_name[:37] + "..."
            self.progress_label.config(text=f"{current_image_name}")

    def update_progress_bar(self):
        """Update the visual progress bar"""
        if not self.image_paths:
            return

        total = len(self.image_paths) + len(self.move_history)
        if total == 0:
            return

        sorted_count = len(self.move_history)
        progress_percent = sorted_count / total

        # Clear and redraw progress bar
        self.progress_bar_canvas.delete("all")
        bar_width = self.progress_bar_canvas.winfo_width()
        if bar_width <= 1:
            bar_width = 400

        # Background
        self.progress_bar_canvas.create_rectangle(0, 0, bar_width, 4,
                                                 fill=self.colors['bg_medium'],
                                                 outline='')

        # Progress fill
        fill_width = bar_width * progress_percent
        if fill_width > 0:
            self.progress_bar_canvas.create_rectangle(0, 0, fill_width, 4,
                                                     fill=self.colors['accent_blue'],
                                                     outline='')

    def update_stats(self):
        """Update the stats label with sorted/remaining counts"""
        sorted_count = len(self.move_history)
        remaining_count = len(self.image_paths)
        self.stats_label.config(text=f"{sorted_count} sorted | {remaining_count} remaining")

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
            self.update_directory_list()

            # Bind hotkey
            self.root.bind(f"<KeyPress-{hotkey}>", lambda event, d=dir_name: self.move_image(d))
        else:
            messagebox.showwarning("No Directory Selected", f"No directory selected for '{dir_name}'.")

    def move_image(self, dir_name):
        if 0 <= self.current_image_index < len(self.image_paths):
            src_path = self.image_paths[self.current_image_index]
            dst_dir = self.target_dirs[dir_name]['path']
            try:
                # Create destination directory if it doesn't exist
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)

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

    def show_preview(self):
        """Display enhanced thumbnail preview of next image"""
        self.preview_canvas.delete("all")
        next_index = self.current_image_index + 1

        if next_index < len(self.image_paths):
            try:
                next_img_path = self.image_paths[next_index]
                next_img = Image.open(next_img_path)
                next_img.thumbnail((150, 150), Image.LANCZOS)
                self.preview_photo = ImageTk.PhotoImage(next_img)

                # Draw preview
                self.preview_canvas.create_image(80, 80, image=self.preview_photo)

                # "NEXT" label with background
                self.preview_canvas.create_rectangle(0, 0, 160, 22,
                                                    fill=self.colors['accent_blue'],
                                                    outline='')
                self.preview_canvas.create_text(80, 11, text="NEXT",
                                               fill='white',
                                               font=('Segoe UI', 8, 'bold'))
            except Exception:
                pass
        else:
            # No next image
            self.preview_canvas.create_text(80, 80, text="Last Image",
                                           fill=self.colors['text_muted'],
                                           font=('Segoe UI', 9))

    def toggle_help(self):
        """Toggle help overlay"""
        self.show_help = not self.show_help
        if self.show_help:
            self.show_help_overlay()
        else:
            self.hide_help_overlay()

    def show_help_overlay(self):
        """Display keyboard shortcuts help overlay"""
        # Create semi-transparent overlay
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600

        # Dark overlay background
        self.help_overlay_bg = self.canvas.create_rectangle(
            0, 0, canvas_width, canvas_height,
            fill='#000000', stipple='gray50', tags='help_overlay'
        )

        # Help panel
        panel_width = 500
        panel_height = 450
        panel_x = (canvas_width - panel_width) / 2
        panel_y = (canvas_height - panel_height) / 2

        # Panel shadow
        self.canvas.create_rectangle(
            panel_x + 5, panel_y + 5,
            panel_x + panel_width + 5, panel_y + panel_height + 5,
            fill='#000000', outline='', tags='help_overlay'
        )

        # Panel background
        self.canvas.create_rectangle(
            panel_x, panel_y, panel_x + panel_width, panel_y + panel_height,
            fill=self.colors['bg_light'], outline=self.colors['accent_blue'], width=2,
            tags='help_overlay'
        )

        # Title
        self.canvas.create_text(
            panel_x + panel_width / 2, panel_y + 30,
            text="Keyboard Shortcuts",
            fill=self.colors['text_primary'],
            font=('Segoe UI', 14, 'bold'),
            tags='help_overlay'
        )

        # Shortcuts list
        shortcuts = [
            ("Navigation", ""),
            ("←  →", "Previous / Next image"),
            ("Space", "Skip to next image"),
            ("", ""),
            ("Sorting", ""),
            ("1-9", "Move to directory (by position)"),
            ("Q/W/E/R/A/S", "Quick setup hotkeys"),
            ("Delete", "Move to trash"),
            ("", ""),
            ("Organization", ""),
            ("F", "Toggle flag on current image"),
            ("Shift+F", "View only flagged images"),
            ("Ctrl+Z", "Undo last move"),
            ("", ""),
            ("Display", ""),
            ("I", "Toggle metadata overlay"),
            ("H or ?", "Toggle this help screen"),
        ]

        y_offset = panel_y + 70
        for key, desc in shortcuts:
            if not key:  # Spacer
                y_offset += 10
                continue
            if not desc:  # Section header
                self.canvas.create_text(
                    panel_x + 30, y_offset,
                    text=key,
                    fill=self.colors['accent_blue'],
                    font=('Segoe UI', 10, 'bold'),
                    anchor='w',
                    tags='help_overlay'
                )
                y_offset += 25
            else:
                # Shortcut key
                self.canvas.create_text(
                    panel_x + 40, y_offset,
                    text=key,
                    fill=self.colors['accent_orange'],
                    font=('Consolas', 9, 'bold'),
                    anchor='w',
                    tags='help_overlay'
                )
                # Description
                self.canvas.create_text(
                    panel_x + 160, y_offset,
                    text=desc,
                    fill=self.colors['text_secondary'],
                    font=('Segoe UI', 9),
                    anchor='w',
                    tags='help_overlay'
                )
                y_offset += 22

        # Close instruction
        self.canvas.create_text(
            panel_x + panel_width / 2, panel_y + panel_height - 20,
            text="Press H or ? to close",
            fill=self.colors['text_muted'],
            font=('Segoe UI', 9, 'italic'),
            tags='help_overlay'
        )

    def hide_help_overlay(self):
        """Remove help overlay"""
        self.canvas.delete('help_overlay')

    def update_directory_list(self):
        """Update the directory listbox with current counts"""
        self.dir_listbox.delete(0, tk.END)
        for idx, (dir_name, info) in enumerate(self.target_dirs.items(), 1):
            count = self.count_images_in_dir(info['path'])
            hotkey_display = info['hotkey'].upper()
            # Show number key if within first 9
            if idx <= 9:
                self.dir_listbox.insert(tk.END, f"[{idx}] {dir_name} ({hotkey_display}) - {count} images")
            else:
                self.dir_listbox.insert(tk.END, f"{dir_name} ({hotkey_display}) - {count} images")

    def count_images_in_dir(self, dir_path):
        """Count image files in a directory"""
        try:
            if not os.path.exists(dir_path):
                return 0
            files = os.listdir(dir_path)
            return len([f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
        except:
            return 0

    def load_config(self):
        """Load saved configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.target_dirs = config.get('target_dirs', {})
                    self.last_folder = config.get('last_folder', None)

                    # Rebind hotkeys
                    for dir_name, info in self.target_dirs.items():
                        hotkey = info['hotkey']
                        self.root.bind(f"<KeyPress-{hotkey}>", lambda event, d=dir_name: self.move_image(d))

                    # Update UI
                    self.update_directory_list()

                    # Auto-load last folder if it exists
                    if self.last_folder and os.path.exists(self.last_folder):
                        self.auto_load_folder(self.last_folder)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration to JSON file"""
        config = {
            'target_dirs': self.target_dirs,
            'last_folder': self.last_folder
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def auto_load_folder(self, folder_path):
        """Automatically load a folder without dialog"""
        self.image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if self.image_paths:
            self.current_image_index = 0
            self.move_history.clear()
            self.display_image()

    def on_closing(self):
        """Handle window close event"""
        self.save_config()
        self.root.destroy()

    def toggle_metadata(self):
        """Toggle metadata overlay on/off"""
        self.show_metadata = not self.show_metadata
        self.display_image()

    def move_to_index(self, index):
        """Move current image to directory at given index"""
        dirs_list = list(self.target_dirs.keys())
        if 0 <= index < len(dirs_list):
            self.move_image(dirs_list[index])

    def move_to_trash(self):
        """Move current image to a 'trash' directory"""
        # Create or use a trash directory
        if 'trash' not in self.target_dirs:
            # Create a trash folder in the current image directory
            if self.image_paths:
                current_dir = os.path.dirname(self.image_paths[self.current_image_index])
                trash_dir = os.path.join(current_dir, "_trash")
                if not os.path.exists(trash_dir):
                    os.makedirs(trash_dir)
                self.target_dirs['trash'] = {'path': trash_dir, 'hotkey': 'delete'}
                self.update_directory_list()

        if 'trash' in self.target_dirs:
            self.move_image('trash')

    def toggle_flag(self):
        """Toggle flag status for current image"""
        if self.image_paths and 0 <= self.current_image_index < len(self.image_paths):
            img_path = self.image_paths[self.current_image_index]
            if img_path in self.flagged_images:
                self.flagged_images.remove(img_path)
            else:
                self.flagged_images.append(img_path)
            self.display_image()

    def view_flagged(self):
        """Show only flagged images"""
        if self.flagged_images:
            # Filter to only show flagged images that still exist in current list
            self.image_paths = [p for p in self.image_paths if p in self.flagged_images]
            self.current_image_index = 0
            self.display_image()
            messagebox.showinfo("Flagged Images", f"Showing {len(self.image_paths)} flagged images.\nPress 'f' to unflag.")
        else:
            messagebox.showinfo("No Flagged Images", "No images have been flagged yet.")

    def quick_setup(self):
        """Quick setup with common LoRA training categories"""
        # Ask user to select base directory
        base_dir = filedialog.askdirectory(title="Select Base Directory for Categories")
        if not base_dir:
            return

        # Common LoRA training categories
        templates = [
            ("Face", "q"),
            ("Full Body", "w"),
            ("Upper Body", "e"),
            ("Landscape", "r"),
            ("Keep", "a"),
            ("Discard", "s")
        ]

        # Create directories and add them
        for dir_name, hotkey in templates:
            dir_path = os.path.join(base_dir, dir_name.lower().replace(" ", "_"))

            # Create directory if it doesn't exist
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # Add to target directories
            self.target_dirs[dir_name] = {'path': dir_path, 'hotkey': hotkey}

            # Bind hotkey
            self.root.bind(f"<KeyPress-{hotkey}>", lambda event, d=dir_name: self.move_image(d))

        # Update UI
        self.update_directory_list()
        self.save_config()

        messagebox.showinfo("Quick Setup Complete",
                           f"Created {len(templates)} categories in:\n{base_dir}\n\n" +
                           "Hotkeys:\nQ - Face\nW - Full Body\nE - Upper Body\nR - Landscape\nA - Keep\nS - Discard")

    def show_directory_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under cursor
        index = self.dir_listbox.nearest(event.y)
        if index >= 0:
            self.dir_listbox.selection_clear(0, tk.END)
            self.dir_listbox.selection_set(index)
            self.dir_listbox.activate(index)
            # Show the context menu
            try:
                self.dir_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.dir_context_menu.grab_release()

    def delete_selected_directory(self):
        """Delete the currently selected directory/directories from the list"""
        selection = self.dir_listbox.curselection()
        if not selection:
            return  # Silently do nothing if nothing selected

        dir_names = list(self.target_dirs.keys())

        # Get all selected directories
        selected_dirs = []
        for index in selection:
            if index < len(dir_names):
                selected_dirs.append(dir_names[index])

        if not selected_dirs:
            return

        # Build confirmation message
        if len(selected_dirs) == 1:
            dir_name = selected_dirs[0]
            dir_path = self.target_dirs[dir_name]['path']
            hotkey = self.target_dirs[dir_name]['hotkey']

            confirm_msg = (f"Remove '{dir_name}' from target directories?\n\n" +
                          f"Path: {dir_path}\n" +
                          f"Hotkey: {hotkey.upper()}\n\n" +
                          "Note: Files in this directory will NOT be deleted.")
        else:
            dir_list = "\n".join([f"  • {d} ({self.target_dirs[d]['hotkey'].upper()})"
                                 for d in selected_dirs])
            confirm_msg = (f"Remove {len(selected_dirs)} directories from target list?\n\n" +
                          f"{dir_list}\n\n" +
                          "Note: Files in these directories will NOT be deleted.")

        confirm = messagebox.askyesno("Remove Target Directory" if len(selected_dirs) == 1
                                     else "Remove Target Directories", confirm_msg)

        if confirm:
            # Remove all selected directories
            for dir_name in selected_dirs:
                # Unbind the hotkey
                hotkey = self.target_dirs[dir_name]['hotkey']
                try:
                    self.root.unbind(f"<KeyPress-{hotkey}>")
                except:
                    pass

                # Remove from target directories
                del self.target_dirs[dir_name]

            # Update UI and save
            self.update_directory_list()
            self.save_config()

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#1E1E1E')
    app = PhotoSorterApp(root)
    root.mainloop()
