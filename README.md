# DIGITAL CHEATSHEET

A digital cheatsheet tool to access reference materials during tests. Integrates with Gemini AI for enhanced assistance when connected to the internet.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Has bypassed

+ All websites that implement full-screen enforcement and keyboard restrictions (e.g., Infosys Springboard and similar platforms)
+ The Hackerearth proctoring browser. Only the keystroke recording method works for this, but I would recommend connecting to a remote computer of yours over VNC. They cannot detect that, apparently.

## However

+ You shouldn't use it if you are full-screen sharing and they can see your screen or periodically take screenshots. You can create a bypass for that by combining the keystroke recording method (3) and the clipboard pasting method (2). That way, the GUI should never pop up. You will have to modify that yourself, I haven't done it.


## AI Features & Keyboard Shortcuts

> ⚠️ **API Key Required**: To use AI features, you must have a Gemini API key. Add it to a `.env` file in the project root.

> It doesn't matter if you haven't studied the test, but study these keybinds- or the ones that matter to you!

### AI-Powered Shortcuts

| Key | Function | Description |
|-----|----------|-------------|
| `Right Arrow` | AI Clipboard Analysis | Analyzes text from your clipboard using Gemini AI |
| `0` | Screen Analysis | Takes a screenshot and sends it to AI for general question analysis |
| `9` | Math Question Analysis | Optimized screenshot analysis for mathematical questions |
| `8` | Programming Question Analysis | Optimized screenshot analysis for code questions (defaults to Python) |
| `7` | Multiple Choice Analysis | Optimized screenshot analysis for multiple-choice questions |
| `1` | Toggle AI Model | Switches between available Gemini models |
| `3` | Keystroke Recording | Records keystrokes until `=` is pressed, then analyzes the captured text |

### Standard Shortcuts

| Key | Function | Description |
|-----|----------|-------------|
| `Up Arrow` | Toggle Hotkeys | Enables/disables all keyboard shortcuts |
| `Left Arrow` | Search Notes | Opens a search bar to find content in your reference materials |
| `Down Arrow` | Exit Program | Closes the application (press additional keys after to ensure exit) |
| `2` | Type Clipboard | Types out the current clipboard contents via keyboard simulation |
| `A-Z` and others | Access Notes | Various keys mapped to specific reference materials in `secret_messages` |
| `-` | Toggle window visibility |  Hides / Shows the hidden window |

## Configuration Options

### Customizing Content and Appearance

| Setting | Description | Location |
|---------|-------------|----------|
| Reference Materials | Modify the `secret_messages` dictionary | Edit in `digital_cheatsheet.py` |
| AI Integration | Add your Gemini API key | Create `.env` file with `GEMINI_API_KEY=your_key_here` |
| Voice To Text | Add your WhisperAPI key | Create `.env` file with `WHISPER_API_KEY=yourkeyhere` |
| UI Customization | Change application background color | Modify `self.frame = tk.Frame(self.root, bg='white')` |
| AI Prompts | Customize AI interaction prompts | Edit the `PROMPT` variables in various AI methods |

### Stealth Recommendations

+ Set application background to match your test paper colour (defaults to white). Replace all instances of 'white' in the code to 'black' or whatever you want.
+ Adjust transparency with `self.root.attributes('-alpha', 0.8)` (lower values = more transparent)
+ By default, it's disguised as `File Explorer`, you can change that by changing the icon and the file name.

## Installation & Setup

### Prerequisites

+ Python 3.7 or higher
+ Pip package manager

If you don't know how, just type "python" into your command bar and it will take you to the microsoft store page to install it.

### Installing Dependencies

Type this into a console window that's in the same directory as this project or the VSCode terminal.

```bash
python -m pip install -r requirements.txt
```

### Environment Setup

1. Create a `.env` file in the root directory
2. Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
3. If using Audio Analyzer, add: `WHISPER_API_KEY=your_key_here`

## Building the Application

### Creating a Standalone Executable

```bash
# Windows
pyinstaller --noconfirm --onefile --windowed --icon "./fileexplorericon.ico" --name "File Explorer" "./digital_cheatsheet.py"

# macOS/Linux (adjust icon format if needed)
pyinstaller --noconfirm --onefile --windowed --icon "./fileexplorericon.ico" --name "File Explorer" "./digital_cheatsheet.py"
```

## Audio Analyzer Component

The project includes a separate audio analysis utility (`audio_analyzer.py`) application to cheat on listening tests.

### Overview

I made this app in about 30 minutes using AI. It uses 2 APIs, both Gemini and LemonFox.ai. Lemonfox is a paid service. You can modify the code to use whisper locally, it's free. However, processing will take longer if you don't have a GPU. You can simply modify the `transcribe_mp3` function. Make an issue if you don't know where to start, I'll gladly help.

### Technical Details

| Feature | Description |
|---------|-------------|
| Audio Input | Supports direct MP3 URLs or local MP3 files |
| Image Analysis | Supports clipboard pasting or file upload for question images |
| Transcription | Uses LemonFox.ai API (paid service) for high-quality audio transcription |
| Alternative Setup | Can be modified to use local Whisper model for free transcription |
| Response Quality | Optimized for educational content and listening comprehension tests |

### Usage Instructions

1. Launch the audio analyzer: `python audio_analyzer.py`
2. Enter the MP3 URL or file path in the "Audio Source" field
3. Paste (Ctrl+V) or upload question images using the "Upload Image" button
4. Click "Analyze" to process the audio and generate answers
5. Review the AI-generated responses in the "Analysis Results" section

### Note

This component functions as a standalone desktop application rather than a discreet overlay. It's designed for situations where you need to quickly analyze listening test materials rather than for use during supervised tests.

## Cheating

I don't condone cheating but there is no point of studying something that is barely related to your course. I will never support the Indian Education System.