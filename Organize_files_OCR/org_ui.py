import os
import shutil
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import queue
from PIL import Image, ImageTk
from classifier import classify_image
from ocr_processor import extract_text_from_image, create_safe_filename_from_text

class ModernPhotoOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Photo Organizer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom colors
        self.primary_color = '#2196F3'
        self.secondary_color = '#FFC107'
        self.success_color = '#4CAF50'
        self.error_color = '#F44336'
        self.background_color = '#f5f5f5'
        
        # Configure custom styles
        self.configure_styles()
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.processing = False
        self.progress_queue = queue.Queue()
        
        # Default values
        self.input_folder.set('input_photos')
        self.output_folder.set('output_photos')
        
        self.create_widgets()
        self.center_window()
        
        # Start queue checker
        self.check_queue()
    
    def configure_styles(self):
        """Configure custom ttk styles"""
        # Configure button styles
        self.style.configure('Primary.TButton',
                           background=self.primary_color,
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(20, 10))
        
        self.style.map('Primary.TButton',
                      background=[('active', '#1976D2')])
        
        self.style.configure('Success.TButton',
                           background=self.success_color,
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        self.style.configure('Secondary.TButton',
                           background=self.secondary_color,
                           foreground='black',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        # Configure frame styles
        self.style.configure('Card.TFrame',
                           background='white',
                           relief='flat',
                           borderwidth=1)
        
        # Configure label styles
        self.style.configure('Title.TLabel',
                           background='white',
                           foreground='#212121',
                           font=('Segoe UI', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background='white',
                           foreground='#757575',
                           font=('Segoe UI', 10))
        
        self.style.configure('Path.TLabel',
                           background='white',
                           foreground='#424242',
                           font=('Segoe UI', 9))
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Configuration section
        self.create_config_section(main_frame)
        
        # Control buttons
        self.create_control_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent, style='Card.TFrame', padding="20")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🖼️ Ultimate Photo Organizer", 
                               style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame,
                                 text="Automatically classify photos and extract text from documents",
                                 style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_config_section(self, parent):
        """Create configuration section"""
        config_frame = ttk.Frame(parent, style='Card.TFrame', padding="20")
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Section title
        config_title = ttk.Label(config_frame, text="📁 Folder Configuration", 
                                style='Title.TLabel')
        config_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Input folder
        input_frame = ttk.Frame(config_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Input Folder:", style='Path.TLabel').pack(anchor=tk.W)
        input_path_frame = ttk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_entry = ttk.Entry(input_path_frame, textvariable=self.input_folder, 
                                    font=('Consolas', 9))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(input_path_frame, text="Browse", 
                  command=self.browse_input_folder,
                  style='Secondary.TButton').pack(side=tk.RIGHT)
        
        # Output folder
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X)
        
        ttk.Label(output_frame, text="Output Folder:", style='Path.TLabel').pack(anchor=tk.W)
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_entry = ttk.Entry(output_path_frame, textvariable=self.output_folder,
                                     font=('Consolas', 9))
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(output_path_frame, text="Browse", 
                  command=self.browse_output_folder,
                  style='Secondary.TButton').pack(side=tk.RIGHT)
    
    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.Frame(parent, style='Card.TFrame', padding="20")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Section title
        control_title = ttk.Label(control_frame, text="🚀 Processing Controls", 
                                 style='Title.TLabel')
        control_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Start processing button
        self.start_button = ttk.Button(buttons_frame, 
                                      text="▶️ Start Processing",
                                      command=self.start_processing,
                                      style='Primary.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop processing button
        self.stop_button = ttk.Button(buttons_frame, 
                                     text="⏹️ Stop",
                                     command=self.stop_processing,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear logs button
        ttk.Button(buttons_frame, 
                  text="🗑️ Clear Logs",
                  command=self.clear_logs,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Open output folder button
        ttk.Button(buttons_frame, 
                  text="📂 Open Output",
                  command=self.open_output_folder,
                  style='Success.TButton').pack(side=tk.RIGHT)
    
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.Frame(parent, style='Card.TFrame', padding="20")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Section title
        progress_title = ttk.Label(progress_frame, text="📊 Progress", 
                                  style='Title.TLabel')
        progress_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to process photos",
                                     style='Subtitle.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # Statistics frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Files processed: 0",
                                    style='Subtitle.TLabel')
        self.stats_label.pack(side=tk.LEFT)
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.Frame(parent, style='Card.TFrame', padding="20")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Section title
        log_title = ttk.Label(log_frame, text="📝 Processing Log", 
                             style='Title.TLabel')
        log_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 height=15,
                                                 font=('Consolas', 9),
                                                 bg='#fafafa',
                                                 fg='#333333',
                                                 wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_configure("success", foreground=self.success_color)
        self.log_text.tag_configure("error", foreground=self.error_color)
        self.log_text.tag_configure("info", foreground=self.primary_color)
        self.log_text.tag_configure("warning", foreground=self.secondary_color)
    
    def create_footer(self, parent):
        """Create footer section"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X)
        
        footer_label = ttk.Label(footer_frame, 
                                text="Photo Organizer v1.0 | AI-Powered Classification & OCR",
                                style='Subtitle.TLabel')
        footer_label.pack(anchor=tk.CENTER)
    
    def browse_input_folder(self):
        """Browse for input folder"""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def log_message(self, message, tag=""):
        """Add message to log with optional color tag"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        output_path = self.output_folder.get()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Windows
            # For cross-platform use: subprocess.run(['explorer', output_path])  # Windows
            # subprocess.run(['open', output_path])  # macOS
            # subprocess.run(['xdg-open', output_path])  # Linux
        else:
            messagebox.showwarning("Warning", f"Output folder '{output_path}' does not exist.")
    
    def start_processing(self):
        """Start photo processing in background thread"""
        if self.processing:
            return
        
        # Validate folders
        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", f"Input folder '{self.input_folder.get()}' not found.")
            return
        
        self.processing = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.progress.start(10)
        
        # Start processing in background thread
        self.processing_thread = Thread(target=self.process_photos_background)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop photo processing"""
        self.processing = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.progress.stop()
        self.status_label.configure(text="Processing stopped")
        self.log_message("Processing stopped by user", "warning")
    
    def process_photos_background(self):
        """Background photo processing function"""
        try:
            self.organize_photos()
        except Exception as e:
            self.progress_queue.put(("error", f"Error during processing: {str(e)}"))
        finally:
            self.progress_queue.put(("complete", ""))
    
    def organize_photos(self):
        """Main photo organization logic (modified for GUI)"""
        ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        
        self.progress_queue.put(("status", "Starting photo organization..."))
        self.progress_queue.put(("log", "=" * 50, "info"))
        self.progress_queue.put(("log", "Starting The Ultimate Photo Organizer...", "info"))
        self.progress_queue.put(("log", "=" * 50, "info"))
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Get files to process
        files_to_process = [f for f in os.listdir(input_folder) 
                           if os.path.isfile(os.path.join(input_folder, f))]
        
        self.progress_queue.put(("log", f"Found {len(files_to_process)} files to process.", "info"))
        
        processed_count = 0
        
        # Step 1: Classification & Moving Files
        for filename in files_to_process:
            if not self.processing:
                break
                
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in ALLOWED_EXTENSIONS:
                source_path = os.path.join(input_folder, filename)
                
                self.progress_queue.put(("status", f"Classifying: {filename}"))
                category = classify_image(source_path)
                
                destination_folder = os.path.join(output_folder, category)
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                
                destination_path = os.path.join(destination_folder, filename)
                shutil.move(source_path, destination_path)
                
                self.progress_queue.put(("log", f"MOVED: '{filename}' >> Category: {category}", "success"))
                processed_count += 1
                self.progress_queue.put(("stats", f"Files processed: {processed_count}"))
            else:
                self.progress_queue.put(("log", f"SKIPPED: '{filename}' (Not a recognized image file)", "warning"))
        
        if not self.processing:
            return
        
        self.progress_queue.put(("log", "\nClassification and Moving Complete!", "success"))
        self.progress_queue.put(("log", "=" * 50, "info"))
        
        # Step 2: OCR Processing for Documents Folder
        documents_folder = os.path.join(output_folder, 'Document')
        if os.path.exists(documents_folder):
            document_files = [f for f in os.listdir(documents_folder) 
                            if f.lower().endswith(tuple(ALLOWED_EXTENSIONS))]
            
            self.progress_queue.put(("log", f"Found {len(document_files)} document images for OCR.", "info"))
            
            for filename in document_files:
                if not self.processing:
                    break
                    
                image_path = os.path.join(documents_folder, filename)
                self.progress_queue.put(("status", f"Processing OCR: {filename}"))
                self.progress_queue.put(("log", f"Processing OCR for: {filename}", "info"))
                
                text_content = extract_text_from_image(image_path)
                if text_content.strip():
                    summary_name = create_safe_filename_from_text(text_content)
                    
                    # Ensure unique filenames
                    file_extension = os.path.splitext(filename)[1].lower()
                    count = 1
                    base_new_name = summary_name
                    new_image_filename = summary_name + file_extension
                    new_image_path = os.path.join(documents_folder, new_image_filename)
                    while os.path.exists(new_image_path):
                        summary_name = f"{base_new_name}_{count}"
                        new_image_filename = summary_name + file_extension
                        new_image_path = os.path.join(documents_folder, new_image_filename)
                        count += 1
                    
                    # Rename the image file
                    os.rename(image_path, new_image_path)
                    self.progress_queue.put(("log", f"  -> RENAMED Image to: {new_image_filename}", "success"))
                    
                    # Save the text file
                    text_file_path = os.path.join(documents_folder, summary_name + '.txt')
                    with open(text_file_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    self.progress_queue.put(("log", f"  -> OCR SUCCESS: Saved text to '{summary_name}.txt'", "success"))
                else:
                    self.progress_queue.put(("log", f"  -> OCR INFO: No text found in '{filename}'.", "warning"))
        
        self.progress_queue.put(("log", "\n" + "=" * 50, "info"))
        self.progress_queue.put(("log", "OCR Process Complete!", "success"))
        self.progress_queue.put(("log", "=" * 50, "info"))
    
    def check_queue(self):
        """Check progress queue and update GUI"""
        try:
            while True:
                item = self.progress_queue.get_nowait()
                if item[0] == "log":
                    if len(item) == 3:
                        self.log_message(item[1], item[2])
                    else:
                        self.log_message(item[1])
                elif item[0] == "status":
                    self.status_label.configure(text=item[1])
                elif item[0] == "stats":
                    self.stats_label.configure(text=item[1])
                elif item[0] == "error":
                    self.log_message(item[1], "error")
                    messagebox.showerror("Error", item[1])
                    self.stop_processing()
                elif item[0] == "complete":
                    self.processing = False
                    self.start_button.configure(state=tk.NORMAL)
                    self.stop_button.configure(state=tk.DISABLED)
                    self.progress.stop()
                    self.status_label.configure(text="Processing completed successfully!")
                    self.log_message("All processing completed!", "success")
                    messagebox.showinfo("Success", "Photo organization completed successfully!")
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queue)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = tk.Tk()
    app = ModernPhotoOrganizerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()