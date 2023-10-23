
import mysql.connector as sql
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import randfacts
import pyjokes
import requests
import json
from AppOpener import open, close
import tkinter as tk
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import tkinter.scrolledtext as st
from threading import Thread

'''
INSTRUCTIONS:
1.Check Chrome_path
2.Check MySQL password
3.Check your API key for pyowm
'''

class voice_assist():


    def __init__(self):

        #Initialisation function

        #Initialising file paths and voice recognition
        self.chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'

        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)

        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / \
            Path(r"Assets")

        #Initialising TK interface
        self.window = Tk()
        self.window.geometry("600x400")
        self.window.configure(bg="#404040")

        #Window Title
        self.window.title("Friday Assistant")

        #Window Icon
        self.img = PhotoImage(file='Assets\icon.png')
        self.window.iconphoto(False, self.img)

        #Creating TK canvas
        self.canvas = Canvas(
            self.window,
            bg = "#404040",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        #Adding Background Image
        self.canvas.place(x = 0, y = 0)
        self.image_image_1 = PhotoImage(
            file=self.relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(
            300.0,
            200.0,
            image = self.image_image_1
        )

        #Adding Output TextBox
        self.text_image = PhotoImage(
            file = self.relative_to_assets("entry_1.png"))
        self.entry_bg_1 = self.canvas.create_image(
            299.5,
            332.5,
            image=self.text_image
        )
        self.text_area = st.ScrolledText(
            bd = 0,
            bg = "#292929",
            fg = "#ffffff",
            highlightthickness = 0,
            wrap = tk.WORD,
            font = ("Roboto", 11)
        )
        self.text_area.place(
            x = 12.0,
            y = 272.0,
            width = 575.0,
            height = 119.0
        )
        self.text_area.configure(state='disabled')

        # Adding speak button
        self.speak_image = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        self.speak_button = Button(
            image = self.speak_image,
            borderwidth = 0,
            highlightthickness = 0,
            command = lambda: Thread(target=self.startListening).start(),
            relief = "flat"
        )
        self.speak_button.place(
            x = 247.0,
            y = 95.0,
            width = 105.0,
            height = 105.0
        )
        self.window.resizable(False, False)


        # connecting mySQL
        try:
            self.con = sql.connect(
                host = 'localhost', user='root', password='Abhi0812')
            self.cons('Connected with mySQL')
        except Exception as e:
            self.cons('Database not connected.... Exiting')
            self.cons('Error:'+str(e))
            exit()

        self.cur = self.con.cursor()

        #Creating/Accessing database
        try:
            self.cur.execute('USE SR_SEARCH_HISTORY;')
        except:
            self.cur.execute('CREATE DATABASE SR_SEARCH_HISTORY;')

        #Creating/Accessing Tables in database
        try:
            self.cur.execute('SHOW TABLES;')
            self.data = self.cur.fetchall()
            # cons(data)
            if ('command_centre',) not in self.data:
                # cons("created")
                self.cur.execute(
                    "CREATE TABLE COMMAND_CENTRE(EXE_TIME BIGINT PRIMARY KEY, COMMAND_NAME VARCHAR(30), SUBCOMMAND VARCHAR(30));")
        except Exception as e:
            self.cons("Error" + str(e))

        # Run the GUI main loop
        #self.wishMe()
        self.window.mainloop()

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def cons(self, message):
        
        #Function to display output message in TextBox
        self.text_area.configure(state = 'normal')
        self.text_area.insert(tk.INSERT , message + '\n')
        self.text_area.see("end")
        self.text_area.configure(state = 'disabled')

    def speak(self, audio):

        #Function to speak audio
        self.engine.say(audio)
        self.engine.runAndWait()

    def wishMe(self):

        #Starter function to greet the user
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            self.speak("Good Morning!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("I am Friday, your assistant")
        self.speak("How may I help you?")

    def listenForCommand(self, modl):

        #Function listens for voice command prompt from user and 
        #accesses other functions in the program

        self.r = sr.Recognizer()
        with sr.Microphone() as source:

            #Creating microphone object
            self.cons("Listening...")
            self.r.pause_threshold = 1
            audio = self.r.listen(source)

        try:

            self.cons("Recognizing...")
            self.query = self.r.recognize_google(audio, language='en-in')
            self.query = audio
            self.cons(f"User said: {self.query}")
            if modl == "ref":
                return self.query
            elif modl == "report":
                self.processReport(self.query.lower())
            else:
                self.processCommand(self.query.lower())

        except Exception as e:

            #Exception handling in case audio is not recognized or unkown command is given
            self.cons("Say that again please...")
            self.speak("Say that again please...")
            self.cons("Error: " + e)
            self.listenForCommand('loop')

    def openGoogle(self):

        #Opens Google
        self.speak("What would you like to search")
        search = self.listenForCommand("ref")
        search = search.replace(' ', '+')
        webbrowser.get(self.chrome_path).open(
            "https://www.google.co.in/search?q=" + search)
        self.insrt_table("google: " + search)

    def openspGoogle(self, search):

        #Searches a specific thing in Google
        search = search.replace(' ', '+')
        webbrowser.get(self.chrome_path).open(
            "https://www.google.co.in/search?q=" + search)
        self.insrt_table("google: " + search.replace('+',' '))

    def openApp(self):

        #Opens specified app
        self.speak("Which app would you like to open")
        search = self.listenForCommand("ref")
        search = search.lower()
        open(search, match_closest=True)
        self.cons("Opening " + search)
        self.speak("Opening " + search)
        self.insrt_table("open " + search)

    def closeApp(self):

        #Closes specified app
        self.speak("Which app would you like to close")
        search = self.listenForCommand("ref")
        search = search.lower()
        close(search, match_closest=True)
        self.cons("Closing " + search)
        self.speak("Closing " + search)
        self.insrt_table("close " + search)

    def searchWikipedia(self, command):

        #Function to search something on wikipedia.org
        try:

            self.speak('What would you like to search on Wikipedia?')
            query = self.listenForCommand("ref")
            self.speak('Searching Wikipedia...')
            results = wikipedia.summary(query, sentences = 2, auto_suggest=False)
            self.speak("According to Wikipedia")
            self.cons(results)
            self.speak(results)
            update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"%s","%s");' % (
                datetime.datetime.now().timestamp(), command, query.lower())
            self.cur.execute(update_command)
            self.cur.execute('commit')

        except wikipedia.exceptions.DisambiguationError as e:

            #Exception handling in case multiple wikipedia pages are found with 
            #ambiguous titles
            #First result will be displayed
            self.speak('Ambiguous results found')
            self.speak('Here is the top result')
            query = e.options[0]
            results = wikipedia.summary(query, sentences=2, auto_suggest=False)
            self.speak("According to Wikipedia")
            self.cons(results)
            self.speak(results)
            update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"%s","%s");' % (
                datetime.datetime.now().timestamp(), command, query.lower())
            self.cur.execute(update_command)
            self.cur.execute('commit')
         
    def insrt_table(self, cmd):

        #Function enters command history into MySQL database
        update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"%s",NULL);' % (
            datetime.datetime.now().timestamp(), cmd)
        self.cur.execute(update_command)
        self.cur.execute('commit')

    def openYouTube(self):

        #Function to open YouTube
        self.speak("Opening YouTube...")
        webbrowser.get(self.chrome_path).open("https://www.youtube.com")
        self.insrt_table("youtube")

    def tellJoke(self):

        #Tells a random joke to the user
        joke = pyjokes.get_joke()
        self.cons(joke)
        self.speak(joke)
        self.insrt_table("joke")

    def weather(self):

        # Returns weather

        city = "Bangalore"
        # Your api_key here
        api_key = "27e05acd3725979496d15cb14e79bfa7"

        response = requests.get('https://api.openweathermap.org/data/2.5/weather?'+'q='+city+'&appid='+api_key)
        data = response.json()

        # Accessing Data From OpenWeatherMap
        main = data['main']
        temperature = round(main['temp'] - 273)
        humidity = main['humidity']
        report = data['weather']

        self.cons(f"{city:-^30}")
        self.cons(f"Temperature: {temperature} °C")
        self.cons(f"Humidity: {humidity} %")
        self.cons(f"Weather Report: {report[0]['description']}")
        self.speak(f"{city}")
        self.speak(f"Temperature: {temperature} degrees celsius")
        self.speak(f"Humidity: {humidity} percent")
        self.speak(f"Weather Report: {report[0]['description']}")

        self.insrt_table('Weather')

    def tellFact(self):

        #Tells a random fact
        fact1 = randfacts.get_fact()
        self.cons(fact1)
        self.speak(fact1)
        self.insrt_table("fact")

    def playMusic(self):

        #Opens spotify
        self.speak("Playing music...")
        webbrowser.get(self.chrome_path).open("https://open.spotify.com")
        self.insrt_table("music")

    def getTime(self):

        #Returns only time
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        self.cons(f"The time is {strTime}")
        self.speak(f"The time is {strTime}")
        self.insrt_table("time")

    def getDate(self):

        #Returns only date
        today = datetime.date.today()
        self.cons(f"Today's date is {today}")
        self.speak(f"Today's date is {today}")
        self.insrt_table("date")

    def thankExit(self):

        #Exits
        self.cons("Welcome. Have a nice day. Bye")
        self.speak("Welcome. Have a nice day. Bye")
        self.cur.close()
        self.con.close()
        exit()

    def showReport(self):

        #Displays menu for the report function
        self.cons('Choose report you would like to see from the following options')
        self.speak('Choose report you would like to see from the following options:')   
        self.cons('1. FULL DATA (TELL "FULL DATA")')
        self.cons('2. FREQUENCY OF COMMANDS USED (TELL "COMMAND")')
        self.cons('3. FREQUENCY OF TOPICS USED(TELL "TOPIC")')
        self.speak('full data, command frequency, topic frequency')
        self.listenForCommand("report")

    def processReport(self, command):

        #Returns the MySQL table containing the log book of all commands entered
        if any(ext in command for ext in ['full data', 'command', 'topic']):
            update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"report","%s");' % (
                datetime.datetime.now().timestamp(), command)
            self.cur.execute(update_command)
            self.cur.execute('commit')

        if 'full data' in command:

            #Returns all data in table
            self.cur.execute('SELECT * FROM COMMAND_CENTRE;')
            cur_details = self.cur.fetchall()
            self.cons("Time".center(30)+"Command".center(
                30)+"Subcommand".center(40))
            for i in cur_details:
                if i[2] == 'NULL' or i[2] is None:
                    self.cons(datetime.datetime.fromtimestamp(i[0]).strftime(
                        '%d/%m/%Y %H:%M:%S').ljust(30)+i[1].ljust(30))
                else:
                    self.cons(datetime.datetime.fromtimestamp(i[0]).strftime(
                        '%d/%m/%Y %H:%M:%S').ljust(30)+i[1].ljust(30)+i[2].ljust(30))
                    
        elif 'command' in command:

            #Returns only frequency of commands used 
            self.cur.execute(
                'SELECT COMMAND_NAME, COUNT(*) FROM COMMAND_CENTRE GROUP BY COMMAND_NAME;')
            cur_details = self.cur.fetchall()
            self.cons("Command".center(30)+"Frequency".center(10))
            for i in cur_details:
                self.cons(str(i[0].ljust(30)) + '\t\t\t' + str(i[1]))

        elif 'topic' in command:

            #Returns only topics searched on wikipedia
            self.cur.execute(
                'SELECT SUBCOMMAND, COUNT(*) FROM COMMAND_CENTRE WHERE COMMAND_NAME="WIKIPEDIA" GROUP BY SUBCOMMAND;')
            cur_details = self.cur.fetchall()
            self.cons("Subcommand".center(30)+"Frequency".center(10))
            for i in cur_details:
                self.cons(str(i[0].ljust(30)) + '\t\t\t' + str(i[1]))

        else:

            #Exception handling
            self.cons("Sorry, I didn't understand that.")
            self.speak("Sorry, I didn't understand that.")

    def processCommand(self, command):

        #Receives command from listenForCommand(command) function
        #and goes through the prompt to give appropriate response

        #List of commands
        commands = {
            "wikipedia": "self.searchWikipedia(command)",
            "open youtube": "self.openYouTube()",
            "open google": "self.openGoogle()",
            "what is": 'self.openspGoogle(command)',
            'play music': 'self.playMusic()',
            'play song': 'self.playMusic()',
            'open app': 'self.openApp()',
            'close app': 'self.closeApp()',
            'weather': 'self.weather()',
            'time': 'self.getTime()',
            'date': 'self.getDate()',
            'report': 'self.showReport()',
            'joke': 'self.tellJoke()',
            'fact': 'self.tellFact()',
            'exit': 'exit()',
            'thank you': 'self.thankExit()'
        }

        flag = False

        #Checks for keyword in user prompt
        for key in commands:
            if (key in command):
                eval(commands[key])
                flag = True

        if flag == False:
            self.speak("Sorry, I didn't understand that.")

    def startListening(self):

        #Starts listening to user
        while True:
            self.listenForCommand("loop")


#Runs mainloop
if __name__ == '__main__':
    ai_project = voice_assist()
