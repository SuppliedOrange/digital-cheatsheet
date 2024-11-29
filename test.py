import tkinter as tk
from tkinter import simpledialog
import keyboard
import threading
import google.generativeai as genai

class SecretMessageOverlay:

    def __init__(self):

        self.hotkeysEnabled = True

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
    
    def ask_ai(self):

        try:

            clipboard_content = self.root.clipboard_get()

            if not clipboard_content:
                self.toggle_visibility("Clipboard is empty.")
                return

            PROMPT = "The following is a likely a question or statement that requires an answer. If you believe it does not have an answer, say 'no answer to this'. Answer concisely, do not explain anything. Question: " + clipboard_content

            response = model.generate_content(PROMPT)
            print(response)

            if response:
                self.toggle_visibility(response.text)
            else:
                self.toggle_visibility("AI did not answer.")
        except:
            self.toggle_visibility("Failed to ask AI.")
    
    def start_keyboard_listener(self):

        print("Starting keyboard listener")

        for key in self.messageDictionary:  # MUST NOT HAVE Q OR F keys. They are reserved for toggling the program and searching.
            keyboard.add_hotkey(key, self.toggle_visibility, args=(self.messageDictionary[key],))
        
        keyboard.add_hotkey('up', self.toggle_hotkeys_enabled) # Bind 'up' to toggle hotkeys
        keyboard.add_hotkey('left', self.prompt_and_search)  # Bind 'left' to prompt and search
        keyboard.add_hotkey('right', self.ask_ai) # Bind 'right' to ask AI
        keyboard.add_hotkey('down', self.root.quit) # Bind 'down' to exit the program

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

    GEMINI_API_KEY = ""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    main()

# pyinstaller --noconfirm --onefile --windowed --icon "C:\Users\Dhruv\Downloads\icons8-file-explorer-48.ico" --name "File Explorer"  "C:\Users\Dhruv\Desktop\digital cheatsheet\test.py"