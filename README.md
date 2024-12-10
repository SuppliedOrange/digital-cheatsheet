# DIGITAL CHEATSHEET

A digital cheatsheet to cheat during tests. Also uses AI if you have internet.

## Has bypassed

+ All websites that full-screen and block certain keys.
+ The Hackerearth proctoring browser. Only the keystroke recording method works for this, but I would recommend connecting to a remote computer of yours over VNC. They cannot detect that, apparently.

## However

+ You shouldn't use it if you are full-screen sharing and they can see your screen or periodically take screenshots. You can create a bypass for that by combining the keystroke recording method (3) and the clipboard pasting method (2). That way, the GUI should never pop up. You will have to modify that yourself, I haven't done it.

## AI KEYBINDS

You will need a gemini api key! if you dont have this just disable all related code yourself.

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
+ Alter your prompts! Please don't simply rely on mine.

## INSTALLING REQUIREMENTS

```py
python -m pip install -r requirements.txt
```

## BUILDING

```console
pyinstaller --noconfirm --onefile --windowed --icon "./fileexplorericon.ico" --name "File Explorer"  "./test.py"
```

## CHEATING

I don't condone cheating but there is no point of studying something that is barely related to your course. I will never support the Indian Education System.
