# DIGITAL CHEATSHEET

A digital cheatsheet to cheat during tests. Also uses AI if you have internet.

## Has bypassed

+ All websites that full-screen and block certain keys. (Infosys Springboard, etc.)
+ The Hackerearth proctoring browser. Only the keystroke recording method works for this, but I would recommend connecting to a remote computer of yours over VNC. They cannot detect that, apparently.

## However

+ You shouldn't use it if you are full-screen sharing and they can see your screen or periodically take screenshots. You can create a bypass for that by combining the keystroke recording method (3) and the clipboard pasting method (2). That way, the GUI should never pop up. You will have to modify that yourself, I haven't done it.

## AI KEYBINDS

You will need a gemini api key! if you dont have this just disable all related code yourself. Put that API key in the .env file.

+ Right: Asks AI with the content you have copied in clipboard.
+ 0: Sends a screenshot of your screen to AI to analyze for questions.
+ 9: Screenshot, but works well for math-ish questions
+ 8: Screenshot, but works well for programming questions (defaults to python)
+ 7: Screenshot, but works well for MCQ questions

+ 1: Changes Gemini AI model
+ 3: Starts recording your keystrokes until you press `=`. Then attempts to find a question in everything you have typed, and answers that.

## REGULAR KEYBINDS

+ Up: Silences all hotkeys
+ Left: Opens up a search bar to search through all notes
+ Down: Exits the program. Spam press alphabets after pressing this key. Just in case.
+ All other keys: All your notes.
+ 2: Types out the contents of your keyboard.

## CONFIG

+ Change your "secret_messages" dict to whatever you want
+ Change your gemini api key to whatever you want. Disable all related code if you don't want this feature.
+ Change the color of your application to match the background. Make sure it's hard to see. Defaults to white.
+ Alter your prompts! Please don't simply rely on mine.

## INSTALLING REQUIREMENTS

```py
python -m pip install -r requirements.txt
```

## BUILDING

```console
pyinstaller --noconfirm --onefile --windowed --icon "./fileexplorericon.ico" --name "File Explorer"  "./digital_cheatsheet.py"
```

## EXTRA - AUDIO ANALYZER

+ *Why this exists and what it requires*

I made this app in about 30 minutes using AI. It uses 2 APIs, both Gemini and LemonFox.ai. Lemonfox is a paid service. You can modify the code to use whisper locally, it's free. However, processing will take longer if you don't have a GPU. You can simply modify the `transcribe_mp3` function. Make an issue if you don't know where to start, I'll gladly help.

+ *How to use it*

You put in a link to the .mp3 file that you find from web inspection on your listening test or whatever (you can modify the code to accept .wav or other files too). Then you can paste in images of the questions.

+ *What it does*

This then transcribes the audio and answers the questions from the images. It takes about 10 seconds for an audio that's 2 minutes long and has 1 screenshot with 6 questions.

+ *Disclaimer*

Obviously, this isn't exactly for "sneaky" usage because it's a full-fledged desktop app, but it's useful if you need to speed-run a listening test by tonight, like I did today.

## CHEATING

I don't condone cheating but there is no point of studying something that is barely related to your course. I will never support the Indian Education System.
