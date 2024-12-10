import tkinter as tk
from tkinter import simpledialog
import keyboard
import threading
import google.generativeai as genai
from mss import mss
import os
import tempfile
import PIL.Image
import pyperclip
from pynput.keyboard import Controller
import pynput.keyboard as pykeyboard
import time

class SecretMessageOverlay:

    def __init__(self):

        self.hotkeysEnabled = True
        self.image_directory = tempfile.mkdtemp()

        self.modelNames = ["gemini-1.5-flash", "gemini-1.5-pro"]

        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

        # Create the main window
        self.root = tk.Tk()
        self.root.title("Secret Message")

        self.message = tk.StringVar()
        self.messageDictionary = {}
        
        self.messageDictionary = secret_messages

        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Make window transparent and always on top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        
        # Calculate screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set maximum width (e.g., 30% of screen width)
        max_width = int(screen_width * 0.2)
        
        # Create a frame to control positioning and styling
        self.frame = tk.Frame(self.root, bg='white')
        self.frame.pack(fill=tk.BOTH, expand=False,)  # Left margin of 10% of screen width
        
        # Create a label for the secret message
        self.label = tk.Label(
            self.frame, 
            textvariable=self.message,
            font=("Arial", 10),  # Reduced font size
            bg='white', 
            fg='black',
            wraplength=max_width,  # Limit wrap length
            justify=tk.LEFT,
            anchor='w'  # Left-align the text
        )
        self.label.pack(fill=tk.X)  # Changed to fill only horizontally
        
        # Position the window
        window_height = int(screen_height * 0.4)  # Reduced height
        window_width = max_width + int(screen_width * 0.1)  # Add margin to width
        x = int(screen_width * 0.1)  # 10% from the left of the screen
        y = (screen_height - window_height) // 2  # Vertically centered
        
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Initially hide the window
        self.root.withdraw()
        
        # Flag to track visibility
        self.is_visible = False
        
        # Start keyboard listener in a separate thread
        self.keyboard_thread = threading.Thread(target=self.start_keyboard_listener, daemon=True)
        self.keyboard_thread.start()

    def type_clipboard_contents(self):
        """
        Types out the contents of the clipboard using the keyboard.

        Args:
            delay_between_keys (float): Time delay (in seconds) between each keypress.
        """

        if not self.hotkeysEnabled:
            return

        clipboard_content = pyperclip.paste()  # Get the clipboard contents
        keyboard = Controller()  # Initialize keyboard controller

        if not clipboard_content:
            print("Clipboard is empty!")
            return

        print("Typing clipboard contents...")
        for char in clipboard_content:
            keyboard.type(char)
            time.sleep(0.05)  # Add delay between typing each character
        
        print("Finished typing clipboard contents.")

    def toggle_hotkeys_enabled(self):
        self.hotkeysEnabled = not self.hotkeysEnabled
    
    def search_keyword_in_data(self, keyword):
        """
        Search for a keyword in the JSON data and return matching text.
        Args:
            data (dict): The JSON data as a dictionary.
            keyword (str): The keyword to search for.
        Returns:
            list: A list of matching text entries.
        """

        keyword = keyword.lower()  # Make the search case-insensitive
        results = []
        data = []

        for key, value in self.messageDictionary.items():
            sentences = value.split("\n")
            for sentence in sentences:
                data.append(sentence)
        
        for sentence in data:
            # If the value contains the keyword, add it to results
            if keyword in sentence.lower():
                results.append(sentence)
        
        return results

    def prompt_and_search(self):
        """
        Prompts the user to enter a keyword and displays the search results.
        """
        # Prompt user for input

        if not self.hotkeysEnabled:
            return

        temporary_parent = tk.Tk()
        temporary_parent.withdraw()

        keyword = simpledialog.askstring("Search", "Enter a keyword to search:", parent=temporary_parent)

        temporary_parent.destroy()
        
        if keyword:  # If user enters a keyword
            results = self.search_keyword_in_data(keyword)
            if results:
                # Display the first result (you can modify this to display all results if needed)
                self.toggle_visibility("\n".join(results))
            else:
                self.toggle_visibility(f"No results found for '{keyword}'.")
    
    def toggle_ai_model(self):
        """
        Toggle between the available AI models.
        """
        if not self.hotkeysEnabled:
            return

        if not self.model:
            self.toggle_visibility("AI model not available.")
            return
        
        # Toggle between the available models
        print(f"Switched from {self.model.model_name} to {self.modelNames[0] if self.model.model_name == self.modelNames[1] else self.modelNames[1]} model.")
        
        if self.model.model_name == f"models/{self.modelNames[0]}":
            self.model = genai.GenerativeModel(self.modelNames[1])
        else:
            self.model = genai.GenerativeModel(self.modelNames[0])
        
        self.toggle_visibility(f"Switched to {self.model.model_name} model.")

    def record_keys(self):

        print("Recording keys... Press '=' to stop.")
        recorded_keys = []

        def on_press(key):
            try:
                # Capture printable characters
                recorded_keys.append(key.char)
            except AttributeError:
                # Handle special keys
                special_keys = {
                    pykeyboard.Key.space: " ",
                    pykeyboard.Key.enter: "\n",
                    pykeyboard.Key.tab: "\t",
                    pykeyboard.Key.backspace: "[BACKSPACE]",
                    pykeyboard.Key.esc: "[ESC]",
                    pykeyboard.Key.shift: "",
                }
                recorded_keys.append(special_keys.get(key, f"[{key}]"))  # Use mapping or show as [Key]

            # Stop on '=' key
            if hasattr(key, 'char') and key.char == "=":
                print("Recording stopped.")
                print("Recorded keys:", ''.join(recorded_keys))
                self.ask_ai_with_clipboard(text=''.join(recorded_keys))
                return False  # Stop the listener

        # Start listening for keypresses
        with pykeyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def ask_ai_with_screenshot(self, prompt=""):

        if not self.hotkeysEnabled or not self.model:
            return
        
        try:

            screenshot_path = ""

            with mss() as sct:
                # Define the path for the screenshot
                screenshot_path = os.path.join(self.image_directory, "screenshot.png")
                # Store the screenshot in the temporary directory
                screenshot_path = sct.shot(output=screenshot_path)
                # You can now use the screenshot_path for further processing
                print(f"Screenshot saved at {screenshot_path}")
            
            if not screenshot_path:
                self.toggle_visibility("Failed to take screenshot.")
                return

            screenshot = PIL.Image.open(screenshot_path)

            PROMPT = prompt or "The following image contains a question or a statement that requires an answer. If you believe it does not have an answer, say 'no answer to this'. Answer the image concisely, do not explain unless the question asks you to. If you believe the problem is somewhat mathematical, please solve it step-by-step. If you believe it is incomplete and you can't figure it out yourself, reply with 'incomplete, cannot solve or infer further question'."
            response = self.model.generate_content([PROMPT, screenshot])

            if response:
                print(response)
                self.toggle_visibility(response.text)
                pyperclip.copy(response.text)
            else:
                self.toggle_visibility("AI did not answer.")
        
        except Exception as e:
            print(e)
            self.toggle_visibility("Failed to ask AI.")


    def ask_ai_with_clipboard(self, text="", prompt=""):

        if not self.hotkeysEnabled or not self.model:
            return

        try:

            clipboard_content = text or self.root.clipboard_get()

            if not clipboard_content:
                self.toggle_visibility("Clipboard is empty.")
                return

            PROMPT = prompt or "The following is a likely a question or statement that requires an answer. If you believe it does not have an answer, say 'no answer to this'. Answer concisely, do not explain unless the question asks you to. If this is a programming question, answer in python. If this is an MCQ question, answer with the appropriate and correct answer. Feel free to do calculations to prove yourself. Question: " + clipboard_content

            response = self.model.generate_content(PROMPT)
            print(response)

            if response:
                self.toggle_visibility(response.text)
                pyperclip.copy(response.text)
            else:
                self.toggle_visibility("AI did not answer.")

        except:
            self.toggle_visibility("Failed to ask AI.")
    
    def start_keyboard_listener(self):

        print("Starting keyboard listener")

        if ENABLE_SECRET_MESSAGES:
            for key in self.messageDictionary:  # MUST NOT HAVE Q OR F keys. They are reserved for toggling the program and searching.
                keyboard.add_hotkey(key, self.toggle_visibility, args=(self.messageDictionary[key],))
        
        keyboard.add_hotkey('up', self.toggle_hotkeys_enabled) # Bind 'up' to toggle hotkeys
        keyboard.add_hotkey('left', self.prompt_and_search)  # Bind 'left' to prompt and search
        keyboard.add_hotkey('right', self.ask_ai_with_clipboard) # Bind 'right' to ask AI
        keyboard.add_hotkey('down', self.root.quit) # Bind 'down' to exit the program
        keyboard.add_hotkey('0', self.ask_ai_with_screenshot) # Bind '0' to ask about general questions
        keyboard.add_hotkey('9', self.ask_ai_with_screenshot, 
                            ("The following image contains a question or a statement that requires some sort of answer. If you believe the image does not contain such text, reply with 'no question or statement requiring answer'. If the question requires you to solve a problem, reply with a step-by-step solution to the problem. If you believe it is a statement, reply with a reason for it. If you believe it is incomplete and you can't figure it out yourself, reply with 'incomplete, cannot solve or infer further question'",)
                            ) # Bind '9' to ask AI about specific math-ish question
        keyboard.add_hotkey('8', self.ask_ai_with_screenshot,
                            ("The following image contains a programming related question. The language it expects is python, use only python unless specified otherwise. Do not wrap the code with ```, answer it raw. If you believe it does not contain a programming question, reply with 'no programming question'. If you believe it is incomplete and you can't figure it out yourself, reply with 'incomplete, cannot solve or infer further question'. Answer the question concisely, do not explain unless the question asks you to. Make sure you write clear and correct code for the problem.",),
                            ),
        keyboard.add_hotkey('7', self.ask_ai_with_screenshot,
                            ("The following image contains multiple choice questions. If you believe it does not contain multiple choice questions, say 'no mcq detected'. There may be an option selected, but it is not necessarily correct! Your goal is to find the correct option(s) for the questions in the image. Answer concisely, do not explain unless the question asks you to.",)
                            ) # Bind '7' to ask AI about MCQ questions
        keyboard.add_hotkey('1', self.toggle_ai_model) # Bind '9' to toggle AI model
        keyboard.add_hotkey('2', self.type_clipboard_contents) # Bind '2' to type clipboard contents
        keyboard.add_hotkey('3', self.record_keys) # Bind '3' to record keys temporarily until "=" is pressed and then ask AI.

        keyboard.wait()  # Keep the thread running
    
    def toggle_visibility(self, updateMessage=""):

        if not self.hotkeysEnabled:

            if self.is_visible:

                self.root.withdraw()
                self.is_visible = False

            return

        self.message.set(updateMessage)

        # Toggle window visibility
        if not self.is_visible:
            # Show the window
            self.root.deiconify()
            self.is_visible = True
        else:
            # Hide the window
            self.root.withdraw()
            self.is_visible = False
    
    def run(self):
        # Start the Tkinter event loop
        self.root.mainloop()

def main():
    
    # Create and run the overlay
    overlay = SecretMessageOverlay()
    overlay.run()

if __name__ == "__main__":

    secret_messages = {
        "q": "Which of the following is a key strategy to improve psychological health? [Ans]: Developing positive thinking\nWhich of the following is an example of a healthy coping strategy for stress? [Ans]: Talking to a friend or family member\nHow can regular physical exercise contribute to better psychological health? [Ans]: It helps release endorphins, improving mood\nWhat role does sleep play in maintaining psychological health? [Ans]: Lack of sleep can lead to cognitive impairment and emotional instability\nWhich of the following is an important component of emotional intelligence? [Ans]: Focusing on the present moment without judgment",
        "w": "What is mindfulness? [Ans]: Reduced stress levels\nWhich of the following is NOT a benefit of social support in maintaining good psychological health? [Ans]: Increased feelings of loneliness\nWhich of the following best describes self-compassion? [Ans]: Treating yourself with kindness and understanding during difficult times\nWhich of the following practices is recommended for improving mental well-being? [Ans]: Engaging in regular physical exercise\nWhen dealing with negative thoughts, which approach is most likely to improve psychological health? [Ans]: Replacing the negative thought with a more realistic and balanced perspective",
        "e": "Which of the following is a healthy way to cope with difficult emotions? [Ans]: Talking about feelings with a trusted friend or therapist\nWhich of the following is most helpful in improving your mood during a stressful situation? [Ans]: Practicing mindfulness or meditation\nWhat is the primary benefit of engaging in hobbies and leisure activities? [Ans]: They help develop new skills and provide relaxation\nWhich practice can help improve self-awareness? [Ans]: Reflecting on your thoughts and feelings regularly\nWhich of the following can improve emotional resilience? [Ans]: Practicing mindfulness and positive thinking",
        "r": "_____ states that family members influence health behaviours through direct and indirect mechanisms. [Ans]: Umberson\n_____ may also directly regulate one’s health behaviour by physical means and supportive behaviours. [Ans]: Family members\nEvery family member can influence another family member’s health attitudes and behaviours through _____ [Ans]: Communication\nResearch reveals that _____ from family members predicts the chance of relapse in depression, eating disorders and schizophrenia. [Ans]: Critical comments\nPersonality is measured using _____framework made up of extroversion, openness, neuroticism, agreeableness and conscientiousness. [Ans]: Big Five Framework",
        "t": "The _____ personality was significantly predictive of worse physical functioning, role limitations, fatigue and pain. [Ans]: Disordered\nIn the workplace, your _____ affects how you react with your colleagues. [Ans]: Personality\nYour _____ may have an impact on your earnings potential, your career trajectory and job satisfaction. [Ans]: Personality\nIn India, the vulnerable groups that face discrimination include Women, SC/ST, Children, Aged, _____ and poor migrants. [Ans]: Lower class\n_____ factors can affect health directly. [Ans]: Psychological",
        "y": "Health Psychology is the study of psychological, cultural and _____ processes in health, illness and healthcare. [Ans]: Behavioural\nThe goal of health Psychology is to apply health education, information, prevention and control in ways that will alleviate patients’ _____ symptoms and improve their lives. [Ans]: Physical\n_____ is influenced by thoughts, behaviours and environments. [Ans]: Personality\nWhich lifestyle change can significantly improve family health? [Ans]: Family exercise activities\nWhich of the following is a genetic risk factor for health issues? [Ans]: Family history of heart disease",
        "u": "What is the leading cause of preventable disease in families? [Ans]: All of the above\nHow can one improve communication skills? [Ans]: Listening with willingness, responding appropriately, and providing feedback\nWhat are the steps to increase vocal clarity? [Ans]: Both a and b\nObjectives of communication skills are: [Ans]: Both a and b\nWhich factors are not required for communication growth? [Ans]: Negative atmosphere",
        "i": "Which of the following can be used to overcome the communication barrier? [Ans]: Using a translator\nBody language plays an important role in: [Ans]: Both a and b\nGoals of communication are: [Ans]: To inform, to persuade\nUsing abbreviations in communication helps overcome the communication barrier: [Ans]: Language/Linguistic\nAccording to Bacon, without friends the world is: [Ans]: Wasteland",
        "o": "What, according to Bacon, is the principal fruit of Friendship? [Ans]: Close emotional bond\nWhat happens when a person communicates and discourses with friends? [Ans]: Person becomes wiser than himself\nBacon compares the third fruit of friendship to: [Ans]: A Pomegranate\nA friendship must have _____ as its main strand. [Ans]: Time and faith\nA friendless, cut-off person is _____ to live in the society. [Ans]: Unfit",
        "p": "According to Bacon, the second fruit of friendship is: [Ans]: Benefit of the clarity of understanding\nRest, sleep, physical exercise, and cleanliness are a part of: [Ans]: Personal hygiene\nWhich of the following is necessary for a healthy person? [Ans]: All of the above\nA balanced diet should normally provide: [Ans]: 3,500 calories per day\nWhich of the following nourishes nerve cells? [Ans]: Vitamin B1"
    }

    GEMINI_API_KEY = ""
    ENABLE_SECRET_MESSAGES = True
    genai.configure(api_key=GEMINI_API_KEY)

    main()

# pyinstaller --noconfirm --onefile --windowed --icon "./fileexplorericon.ico" --name "File Explorer"  "./test.py"

"""
SFH
    secret_messages = {
        "q": "Which of the following is a key strategy to improve psychological health? [Ans]: Developing positive thinking\nWhich of the following is an example of a healthy coping strategy for stress? [Ans]: Talking to a friend or family member\nHow can regular physical exercise contribute to better psychological health? [Ans]: It helps release endorphins, improving mood\nWhat role does sleep play in maintaining psychological health? [Ans]: Lack of sleep can lead to cognitive impairment and emotional instability\nWhich of the following is an important component of emotional intelligence? [Ans]: Focusing on the present moment without judgment",
        "w": "What is mindfulness? [Ans]: Reduced stress levels\nWhich of the following is NOT a benefit of social support in maintaining good psychological health? [Ans]: Increased feelings of loneliness\nWhich of the following best describes self-compassion? [Ans]: Treating yourself with kindness and understanding during difficult times\nWhich of the following practices is recommended for improving mental well-being? [Ans]: Engaging in regular physical exercise\nWhen dealing with negative thoughts, which approach is most likely to improve psychological health? [Ans]: Replacing the negative thought with a more realistic and balanced perspective",
        "e": "Which of the following is a healthy way to cope with difficult emotions? [Ans]: Talking about feelings with a trusted friend or therapist\nWhich of the following is most helpful in improving your mood during a stressful situation? [Ans]: Practicing mindfulness or meditation\nWhat is the primary benefit of engaging in hobbies and leisure activities? [Ans]: They help develop new skills and provide relaxation\nWhich practice can help improve self-awareness? [Ans]: Reflecting on your thoughts and feelings regularly\nWhich of the following can improve emotional resilience? [Ans]: Practicing mindfulness and positive thinking",
        "r": "_____ states that family members influence health behaviours through direct and indirect mechanisms. [Ans]: Umberson\n_____ may also directly regulate one’s health behaviour by physical means and supportive behaviours. [Ans]: Family members\nEvery family member can influence another family member’s health attitudes and behaviours through _____ [Ans]: Communication\nResearch reveals that _____ from family members predicts the chance of relapse in depression, eating disorders and schizophrenia. [Ans]: Critical comments\nPersonality is measured using _____framework made up of extroversion, openness, neuroticism, agreeableness and conscientiousness. [Ans]: Big Five Framework",
        "t": "The _____ personality was significantly predictive of worse physical functioning, role limitations, fatigue and pain. [Ans]: Disordered\nIn the workplace, your _____ affects how you react with your colleagues. [Ans]: Personality\nYour _____ may have an impact on your earnings potential, your career trajectory and job satisfaction. [Ans]: Personality\nIn India, the vulnerable groups that face discrimination include Women, SC/ST, Children, Aged, _____ and poor migrants. [Ans]: Lower class\n_____ factors can affect health directly. [Ans]: Psychological",
        "y": "Health Psychology is the study of psychological, cultural and _____ processes in health, illness and healthcare. [Ans]: Behavioural\nThe goal of health Psychology is to apply health education, information, prevention and control in ways that will alleviate patients’ _____ symptoms and improve their lives. [Ans]: Physical\n_____ is influenced by thoughts, behaviours and environments. [Ans]: Personality\nWhich lifestyle change can significantly improve family health? [Ans]: Family exercise activities\nWhich of the following is a genetic risk factor for health issues? [Ans]: Family history of heart disease",
        "u": "What is the leading cause of preventable disease in families? [Ans]: All of the above\nHow can one improve communication skills? [Ans]: Listening with willingness, responding appropriately, and providing feedback\nWhat are the steps to increase vocal clarity? [Ans]: Both a and b\nObjectives of communication skills are: [Ans]: Both a and b\nWhich factors are not required for communication growth? [Ans]: Negative atmosphere",
        "i": "Which of the following can be used to overcome the communication barrier? [Ans]: Using a translator\nBody language plays an important role in: [Ans]: Both a and b\nGoals of communication are: [Ans]: To inform, to persuade\nUsing abbreviations in communication helps overcome the communication barrier: [Ans]: Language/Linguistic\nAccording to Bacon, without friends the world is: [Ans]: Wasteland",
        "o": "What, according to Bacon, is the principal fruit of Friendship? [Ans]: Close emotional bond\nWhat happens when a person communicates and discourses with friends? [Ans]: Person becomes wiser than himself\nBacon compares the third fruit of friendship to: [Ans]: A Pomegranate\nA friendship must have _____ as its main strand. [Ans]: Time and faith\nA friendless, cut-off person is _____ to live in the society. [Ans]: Unfit",
        "p": "According to Bacon, the second fruit of friendship is: [Ans]: Benefit of the clarity of understanding\nRest, sleep, physical exercise, and cleanliness are a part of: [Ans]: Personal hygiene\nWhich of the following is necessary for a healthy person? [Ans]: All of the above\nA balanced diet should normally provide: [Ans]: 3,500 calories per day\nWhich of the following nourishes nerve cells? [Ans]: Vitamin B1"
    }

"""

"""
ICO NOTES
    secret_messages = {
        "w": "President impeachment for violating Constitution: Both houses of Parliament\nVice-President election: Members of both houses of Parliament\nPresident and VP duties in absence: Chief Justice of India\nPresidential emergency declaration: Threat of war, state machinery breakdown, financial instability\nGovernor legislative powers: Summon/prorogue, appoint members, dissolve assembly\nLegislative Assembly members: Directly elected by people\nGovernor appointment: Appointed by President\nReprieve: Temporary suspension of death sentence\nCEC removal: President on Parliament's recommendation\nParliament quorum: One-tenth members",
        "e": "Governor ordinance power: When legislature is not in session\nRajya Sabha election: Members of Legislative Assemblies\nVP ex-officio role: Chairman of Rajya Sabha\nLok Sabha Speaker election: Elected by Lok Sabha members\nRajya Sabha permanency: One-third retires every two years\nGovernor eligibility: Must be 35 years old\nHigh Court Chief Justice appointment: By President\nLegislative Assembly membership range: 60 to 500\nLegislative Council non-constituency: Reserved constituency\nLegislative Council tenure: 6 years",
        "r": "Legislative Council minimum members: 40\nSC & HC shared jurisdiction: Fundamental Rights protection\nCouncil of Ministers head: Prime Minister; appointed by President\nRajya Sabha alias: Council of States\nLok Sabha life post-emergency: 6 months max\nQuorum definition: Minimum attendance to start session\nProrogation: Ends session; pending bills don't lapse\nGovernor term: 5 years, serves at President's pleasure\nAdvocate General advisory: State Government\nState Council of Ministers cap: 15% of Assembly strength",
        "t": "SC power: None can abolish High Courts\nRS nominations by President: 12 members\nHC judges retirement: At 62 years\nMoney Bill initiation: Lok Sabha only\nJoint-session presiding officer: Speaker of Lok Sabha\nPardon death sentence: President\nArticle 360: Financial Emergency\nState Emergency functions: Assumed by President\nNon-impeachable roles: Prime Minister\nLongest amendment: 42nd Amendment",
        "y": "SC judges minimum age: No set age\nNon-Fundamental Rights: Property, Strike, Die\nDirective Principles enforcement: Not enforceable\nProhibited titles: Article 18\nEqual pay for equal work: Directive Principles\nFreedom of silence protection: Speech & Expression\nSelf-incrimination protection: Testimonial compulsion\nInternational Law recognition: Article 51\nHabeas Corpus: Produce person before court\nAnti-Fundamental Rights laws: Declared void",
        "u": "Non-Union formers: Police\nMinority consideration: Religious or linguistic\nExploitation prohibition: Trafficking\nLower court decisions quashing: Certiorari\nRight to Assembly: Processions/meetings\nUniform Civil Code directive: Article 44\nNon-Fundamental Duty: School attendance for wards\nState special law protection: Women & Children\nSilence Freedom case: National Anthem Case\nDirective Principles aim: Welfare State",
        "i": "SC Chief Justice appointment: President\nMLA anti-defection disqualification: Speaker of Assembly\nRS term: 6 years\nSC location: Delhi\nUnforeseen expenses fund: Contingency Fund\nAttorney General appointment: President\nPM appointment: President\nRS maximum strength: 250\nVP election: Members of Parliament\nState CM appointment: Governor",
        "o": "Fundamental Rights protection: Supreme Court\nArticle 14 test: Intelligible Differentia\nIndependence Act enactor: British Parliament\nPreamble words added (42nd Amendment): Socialist\nWritten Constitution length: Bulky document\nIndia Constitution effective date: 26th Jan 1950\nPreamble amendment method: 42nd Amendment\nFraming duration: 2 years 11 months 18 days\nConstituent Assembly chairman: Dr. Rajendra Prasad; Drafting: Dr. B.R. Ambedkar\nCore influence on Constitution: Government of India Act, 1935",
        "p": "Federal government definition: Centre-state power division\nFundamental Rights source: USA Constitution\nGuardians of public finances: CAG\nLok Sabha council cap: 15%\nNon-suspendable Right: Article 21 (National Emergency)\nGovernor oath: Chief Justice of respective HC\nState Emergency takeover: President",
        "a": "**Constitution Basics**:\n- **Definition**: Fundamental principles governing state and citizens.\n- **World’s Longest Constitution**: 465 articles, 25 parts, 12 schedules, 118 amendments (as of 2023), ~117,369 words.\n- **Drafting**: Idea proposed by M.N. Roy in 1934. Constituent Assembly formed (Dec 1946) under Cabinet Mission Plan; first meeting on 9 Dec 1946.\n- **Adoption & Enactment**: Adopted on 26 Nov 1949; effective from 26 Jan 1950.\n- **Drafting Duration**: 2 years, 11 months, 18 days; Cost: ₹64 lakh.\n- **Contributors**: Dr. B.R. Ambedkar (Chairman of Drafting Committee), 6 members including Alladi Krishnaswamy Ayyar, K.M. Munshi.",
        "s": "**Salient Features**:\n- **Blend of Rigidity & Flexibility**: Amendable via simple or special majority (Art. 368).\n- **Federal System with Unitary Bias**: Central dominance during emergencies (Art. 352, 356, 360).\n- **Sovereign, Socialist, Secular, Democratic, Republic**: Defined in Preamble (42nd Amendment, 1976).\n- **Parliamentary System**: President as constitutional head; PM holds executive powers.\n- **Single Citizenship**: Unlike dual citizenship systems (e.g., USA).\n- **Emergency Provisions**:\n  - National Emergency (352): War, external aggression, armed rebellion.\n  - State Emergency (356): Constitutional machinery failure in states.\n  - Financial Emergency (360): Threat to fiscal stability.",
        "d": "**Preamble**:\n- Based on Nehru's \"Objective Resolution\" (13 Dec 1946); Amended by 42nd Amendment (1976): Added \"Socialist,\" \"Secular,\" \"Integrity.\"\n- Key ideals: Justice (social, economic, political), Liberty, Equality, Fraternity.\n\n**Fundamental Rights (Part III, Articles 12–35)**:\n1. **Right to Equality (14–18)**:\n   - Equal law protection (14).\n   - No discrimination on caste, creed, gender, etc. (15).\n   - Equal opportunity in public employment (16).\n   - Abolishes untouchability (17) and hereditary titles (18).",
        "g": "2. **Right to Freedom (19–22)**:\n   - Speech, assembly, movement, residence, profession (19).\n   - Safeguards against arbitrary conviction (20) and detention (22).\n3. **Right Against Exploitation (23–24)**:\n   - Prohibits human trafficking and child labor (below 14 years in hazardous jobs).\n4. **Right to Freedom of Religion (25–28)**:\n   - Practice, propagate religion; no state-sponsored religion or taxes for religious purposes.\n5. **Cultural/Educational Rights (29–30)**:\n   - Minorities can preserve language, culture, and run institutions.\n6. **Right to Constitutional Remedies (32)**:\n   - Writs like Habeas Corpus, Mandamus, Prohibition, Certiorari, Quo Warranto enforce rights.",
        "h": "**Directive Principles of State Policy (Part IV, Articles 36–51)**:\n- **Socialist Principles**:\n  - Equal pay (39), legal aid (39A), improved public health (47).\n- **Gandhian Principles**:\n  - Panchayati Raj (40), prohibition (47), SC/ST welfare (46).\n- **Liberal Principles**:\n  - Uniform Civil Code (44), environmental protection (48A), international peace (51).\n- **Amendments**:\n  - 42nd (1976): Legal aid (39A), workers' participation (43A).\n  - 44th (1978): Reduced inequalities (38).\n  - 86th (2002): Early childhood education.",
        "j": "**Fundamental Duties (Part IVA, Article 51A)**:\n- Added by 42nd Amendment (1976); expanded by 86th (2002).\n- Includes: Abide by Constitution, preserve heritage, promote harmony, educate children (6–14 years).\n- Non-justiciable but enforceable through legislation.",
        "k": "**Historical Development**:\n- Regulating Act (1773), Government of India Act (1935) laid the foundation.\n- Constituent Assembly: Initially 389 members; reduced to 299 post-partition.",
        "l": "Additional Information:\n- Preamble ideals: Justice, Liberty, Equality, Fraternity reflect a democratic framework.\n- Directive Principles aim for a welfare state.\n- Fundamental Duties promote civic responsibility.",
        "z": "Constitution in action:\n- Balance of rights and duties ensures a harmonious society.\n- Federal principles adapt to unique socio-political contexts.\n- Amendments like the 42nd and 86th highlight its evolution."
    }
"""