import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageGrab
import requests
import google.generativeai as genai
import threading
import queue
import os

from dotenv import load_dotenv
config = load_dotenv()

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
WHISPER_API_KEY = os.environ['WHISPER_API_KEY']

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class StyledApplication(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("AI Audio/Image Analyzer")
        self.configure_style()
        self.create_widgets()
        self.setup_bindings()
        self.images = []
        self.image_widgets = []
        self.response_queue = queue.Queue()

    def configure_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('TFrame', background='#F0F0F0')
        style.configure('TLabel', background='#F0F0F0', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Error.TLabel', foreground='#CC0000')
        style.configure('Success.TLabel', foreground='#007ACC')
        style.configure('TEntry', padding=5)
        style.map('TButton',
                background=[('active', '#E0E0E0'), ('!disabled', 'white')],
                bordercolor=[('focus', '#007ACC')])

    def create_widgets(self):

        # Main container
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="AI Analyzer", style='Header.TLabel').pack(side=tk.LEFT)
        
        # MP3 Input Section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="Audio Source:").pack(side=tk.LEFT, padx=(0, 5))
        self.mp3_entry = ttk.Entry(input_frame, width=50)
        self.mp3_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Image Panel - Add Upload Button
        img_container = ttk.LabelFrame(main_frame, text="Pasted/Uploaded Images")  # Updated label
        img_container.pack(fill=tk.BOTH, expand=True, pady=5)

        upload_button = ttk.Button(img_container, text="Upload Image", command=self.upload_image)
        upload_button.pack(side=tk.TOP, pady=(5,0))  # Place above the canvas

        self.canvas = tk.Canvas(img_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(img_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        self.process_btn = ttk.Button(control_frame, text="Analyze", command=self.process)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(control_frame, mode='indeterminate')
        
        # Response Area
        response_container = ttk.LabelFrame(main_frame, text="Analysis Results")
        response_container.pack(fill=tk.BOTH, expand=True, pady=5)
        self.response_text = tk.Text(response_container, height=10, wrap=tk.WORD, 
                                   font=('Segoe UI', 9), padx=5, pady=5,
                                   highlightcolor='#007ACC', highlightthickness=1)
        self.response_text.pack(fill=tk.BOTH, expand=True)

    def setup_bindings(self):
        """Set up keyboard and event bindings."""
        self.master.bind('<Control-v>', self.paste_image)
        self.response_text.tag_configure('error', foreground='#CC0000')
        self.response_text.tag_configure('success', foreground='#007ACC')

    def paste_image(self, event=None):
        """Handle image pasting from clipboard."""
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.images.append(img.copy())
                self.show_image(img)
        except Exception as e:
            self.show_error(f"Error pasting image: {str(e)}")

    def show_image(self, img):
        """Display an image in the scrollable frame."""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(side=tk.TOP, pady=2)
        
        # Create a thumbnail for preview
        preview_img = img.copy()
        preview_img.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(preview_img)
        
        # Display the image
        label = ttk.Label(frame, image=photo)
        label.image = photo
        label.pack(side=tk.LEFT)
        
        # Add a remove button
        ttk.Button(frame, text="Remove", 
                 command=lambda f=frame: self.remove_image(f)).pack(side=tk.LEFT, padx=5)
        
        self.image_widgets.append(frame)

    def remove_image(self, frame):
        """Remove an image from the list and UI."""
        try:
            index = self.image_widgets.index(frame)
            del self.images[index]
            del self.image_widgets[index]
            frame.destroy()
        except ValueError:
            self.show_error("Image not found in list")

    def process(self):
        """Start the analysis process."""
        self.clear_response()
        self.toggle_processing(True)
        
        mp3_input = self.mp3_entry.get().strip()
        if not mp3_input:
            self.show_error("Please enter an MP3 URL/path")
            self.toggle_processing(False)
            return

        threading.Thread(target=self.process_task, args=(mp3_input,), daemon=True).start()
        self.check_response_queue()

    def process_task(self, mp3_input):
        """Background task to handle transcription and Gemini query."""
        try:
            transcription = self.transcribe_mp3(mp3_input)
            if not transcription:
                self.response_queue.put(("error", "Failed to get transcription"))
                return

            self.query_gemini(transcription)
        except Exception as e:
            self.response_queue.put(("error", str(e)))
        finally:
            self.response_queue.put(("progress", False))

    def transcribe_mp3(self, mp3_input):
        """Transcribe the MP3 file using Whisper API."""
        url = "https://api.lemonfox.ai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {WHISPER_API_KEY}"}
        data = {"language": "english", "response_format": "json"}

        try:
            if mp3_input.startswith(('http://', 'https://')):
                data['file'] = mp3_input
                response = requests.post(url, headers=headers, data=data)
            else:
                with open(mp3_input, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                raise Exception(f"Transcription failed: {response.text}")

            return response.json().get('text', '')
        except Exception as e:
            self.show_error(f"Transcription error: {str(e)}")
            return None

    def query_gemini(self, transcription):
        """Query Gemini with the transcription and images."""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""Analyze this audio transcription and answer questions from the images. 
            The transcription is from an MP3 recording:
            {transcription}
            
            Please carefully review any questions or prompts shown in the images and provide detailed, 
            thoughtful answers based on both the audio content and visual information."""
            
            response = model.generate_content([prompt] + self.images, stream=True)
            for chunk in response:
                self.response_queue.put(("text", chunk.text))
                
        except Exception as e:
            self.response_queue.put(("error", f"Gemini Error: {str(e)}"))
        finally:
            self.response_queue.put(None)

    def check_response_queue(self):
        """Check the response queue for updates."""
        try:
            while True:
                content = self.response_queue.get_nowait()
                
                if content is None:
                    break
                    
                if content[0] == "error":
                    self.show_error(content[1])
                elif content[0] == "text":
                    self.response_text.insert(tk.END, content[1], 'success')
                elif content[0] == "progress":
                    self.toggle_processing(content[1])
                
                self.response_text.see(tk.END)
                self.master.update_idletasks()
                
        except queue.Empty:
            pass
        
        self.master.after(100, self.check_response_queue)

    def show_error(self, message):
        """Display an error message in the response box."""
        self.response_text.insert(tk.END, f"\nError: {message}\n", 'error')
        self.response_text.see(tk.END)
    
    def upload_image(self):
        """Handle manual image upload."""
        try:
            filepath = filedialog.askopenfilename(
                title="Select Image", filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.gif"), ("All files", "*.*"))
            )
            if filepath:  # Check if a file was selected
                img = Image.open(filepath)
                self.images.append(img.copy())
                self.show_image(img)
        except Exception as e:
            self.show_error(f"Error uploading image: {str(e)}")


    def clear_response(self):
        """Clear the response text box."""
        self.response_text.delete(1.0, tk.END)

    def toggle_processing(self, state):
        """Toggle the processing state (enable/disable UI elements)."""
        if state:
            self.process_btn.config(state=tk.DISABLED)
            self.progress_bar.start(10)
            self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        else:
            self.process_btn.config(state=tk.NORMAL)
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x800")
    app = StyledApplication(master=root)
    root.mainloop()