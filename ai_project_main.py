import mysql.connector as sql
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import randfacts
import pyjokes
import pyowm
from AppOpener import open, close
import tkinter as tk
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import tkinter.scrolledtext as st
from threading import Thread


class voice_assist():
    def __init__(self):
        
        self.chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        
        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[0].id)

        
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / Path(r"D:\Abhi Data\Data\Programming\AI\Assets")
        

        #TK!
        self.window = Tk()
        
        self.window.geometry("600x400")
        self.window.configure(bg="#404040")
        self.window.title("Friday Assistant")
        
        self.canvas = Canvas(
            self.window,
            bg = "#404040",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        
        self.canvas.place(x=0, y=0)
        self.image_image_1 = PhotoImage(
            file=self.relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(
            300.0,
            200.0,
            image=self.image_image_1
        )
        
        self.text_image = PhotoImage(
            file=self.relative_to_assets("entry_1.png"))
        self.entry_bg_1 = self.canvas.create_image(
            299.5,
            332.5,
            image=self.text_image
        )
        self.text_area = st.ScrolledText(
            bd=0,
            bg="#292929",
            fg="#ffffff",
            highlightthickness=0,
            font=("Times New Roman", 10)
        )
        self.text_area.place(
            x=12.0,
            y=272.0,
            width=575.0,
            height=119.0
        )
        self.text_area.configure(state = 'disabled')
        
        self.report_image = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        self.report_button = Button(
            image=self.report_image,
            borderwidth=0,
            highlightthickness=0,
            command=self.showReport,
            relief="flat"
        )
        self.report_button.place(
            x=563.0,
            y=9.0,
            width=25.0,
            height=25.0
        )
        
        self.speak_image = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        self.speak_button = Button(
            image=self.speak_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: Thread(target=self.startListening).start(),
            relief="flat"
        )
        self.speak_button.place(
            x=247.0,
            y=95.0,
            width=105.0,
            height=105.0
        )
        self.window.resizable(False, False)
        
        
        #connecting mySQL
        try:
            self.con = sql.connect(
                host='localhost', user='root', password='Abhi0812')
            self.cons('Connected with mySQL')
        except Exception as e:
            self.cons('Database not connected.... Exiting')
            self.cons('Error:', e)
            self.exit()
        
        self.cur = self.con.cursor()
        
        try:
            self.cur.execute('USE SR_SEARCH_HISTORY;')
        except:
            self.cur.execute('CREATE DATABASE SR_SEARCH_HISTORY;')
        
        try:
            self.cur.execute('SHOW TABLES;')
            self.data = self.cur.fetchall()
            # cons(data)
            if ('command_centre',) not in self.data:
                # cons("created")
                self.cur.execute(
                    "CREATE TABLE COMMAND_CENTRE(EXE_TIME BIGINT PRIMARY KEY, COMMAND_NAME VARCHAR(30), SUBCOMMAND VARCHAR(30));")
        except Exception as e:
            self.cons("Error", e)
        
        
        # Run the GUI main loop
        #self.wishMe()
        self.window.mainloop()


    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

       
    def cons(self, message):
        self.text_area.configure(state = 'normal')
        self.text_area.insert(tk.INSERT, message+'\n')
        self.text_area.see("end")
        self.text_area.configure(state='disabled')

    
    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()
    
    
    def wishMe(self):
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
        self.r = sr.Recognizer()
        with sr.Microphone() as source:
            self.cons("Listening...")
            self.r.pause_threshold = 1
            audio = self.r.listen(source)
        try:
            self.cons("Recognizing...")
            self.query = self.r.recognize_google(audio, language='en-in')
            self.cons(f"User said: {self.query}")
            if modl == "ref":
                return self.query
            elif modl == "report":
                self.processReport(self.query.lower())
            else:
                self.processCommand(self.query.lower())
        except Exception as e:
            self.cons("Say that again please...")
            self.speak("Say that again please...")
            self.listenForCommand("loop")
    
    
    def openGoogle(self):
        self.speak("What would you like to search")
        search = self.listenForCommand("ref")
        search = search.replace(' ','+')
        webbrowser.get(self.chrome_path).open(
            "https://www.google.co.in/search?q="+search)
        self.insrt_table("google:", search)
    

    def openspGoogle(self, search):
        search = search.replace(' ', '+')
        webbrowser.get(self.chrome_path).open(
            "https://www.google.co.in/search?q="+search)
        self.insrt_table("google:", search)

    
    def openApp(self):
        self.speak("Which app would you like to open")
        search = self.listenForCommand("ref")
        search = search.lower()
        open(search, match_closest=True)
        self.speak("Opening"+search)
        self.cons("Opening", search)
        self.insrt_table("open", search)
    
    
    def closeApp(self):
        self.speak("Which app would you like to close")
        search = self.listenForCommand("ref")
        search = search.lower()
        close(search, match_closest=True)
        self.speak("Closing"+search)
        self.cons("Closing", search)
        self.insrt_table("close", search)
    
    
    def searchWikipedia(self, command):
        self.speak('What would you like to search on Wikipedia?')
        query = self.listenForCommand("ref")
        self.speak('Searching Wikipedia...')
        results = wikipedia.summary(query, sentences=2)
        self.speak("According to Wikipedia")
        self.cons(results)
        self.speak(results)
        update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"%s","%s");' % (
            datetime.datetime.now().timestamp(), command, query.lower())
        #con(update_command)
        self.cur.execute(update_command)
        self.cur.execute('commit')
    
    
    def insrt_table(self, cmd):
        update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"%s",NULL);' % (
            datetime.datetime.now().timestamp(), cmd)
        #con(update_command)
        self.cur.execute(update_command)
        self.cur.execute('commit')
    
    
    def openYouTube(self):
        self.speak("Opening YouTube...")
        webbrowser.get(self.chrome_path).open("https://www.youtube.com")
        self.insrt_table("youtube")
    
    
    def tellJoke(self):
        joke = pyjokes.get_joke()
        self.speak(joke)
        self.cons(joke)
        self.insrt_table("joke")
    
    
    def weather(self):
        owm = self.pyowm.OWM('6cf345bdb3238dcc59d4d0878b3ad803')  # Replace 'your_api_key' with your actual API key
    
        while True:
            # Ask the user for the city
            self.speak("Which city's weather do you want to know?")
            city = self.listenForCommand("re")
    
            try:
                observation = owm.weather_at_place(city)
                weather_data = observation.get_weather()
                temperature = weather_data.get_temperature(unit='celsius')['temp']
                status = weather_data.get_status()
    
                # Print and speak the weather information
                self.speak(
                    f"Temperature in {city} is {temperature} degrees Celsius.")
                self.speak(f"The weather in {city} is {status}.")
                print(f"Temperature in {city} is {temperature} degrees Celsius.")
                print(f"The weather in {city} is {status}.")
                self.insrt_table("Weather")
                break  # Exit the loop since weather information was found
    
            except self.pyowm.exceptions.not_found_error.NotFoundError:
                # Retry or exit
                self.speak(
                    "Weather information not found for that city. Would you like to try another city?")
                retry = self.listenForCommand("re")
                if "no" in retry.lower():
                    self.speak("Alright, no weather information retrieved.")
                    break  # Exit the loop if the user doesn't want to try again
    
        self.insrt_table('Weather')
    
    
    def tellFact(self):
        fact1 = randfacts.get_fact()
        self.speak(fact1)
        self.cons(fact1)
        self.insrt_table("fact")
    
    
    def playMusic(self):
        self.speak("Playing music...")
        webbrowser.get(self.chrome_path).open("https://open.spotify.com")
        self.insrt_table("music")
    
    
    def getTime(self):
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        self.speak(f"The time is {strTime}")
        self.cons(f"The time is {strTime}")
        self.insrt_table("time")
    
    
    def getDate(self):
        today = datetime.date.today()
        self.speak(f"Today's date is {today}")
        self.cons(f"Today's date is {today}")
        self.insrt_table("date")
    
    
    def thankExit(self):
        self.speak("Welcome. Have a nice day. Bye")
        self.cons("Welcome. Have a nice day. Bye")
        self.cur.close()
        self.con.close()
        exit()
    
    
    def showReport(self):
        self.speak('Choose report you would like to see from the following options')
        self.cons('Choose report you would like to see from the following options:')
        self.speak('full data, command frequency, topic frequency')
        self.cons('1. FULL DATA (TELL "FULL DATA")')
        self.cons('2. FREQUENCY OF COMMANDS USED (TELL "COMMAND")')
        self.listenForCommand("report")
    
    
    def processReport(self, command):
        if any(ext in command for ext in ['full data', 'command', 'topic']):
            update_command = 'INSERT INTO COMMAND_CENTRE VALUES(%d,"report","%s");' % (
                datetime.datetime.now().timestamp(), command)
            #cons(update_command)
            self.cur.execute(update_command)
            self.cur.execute('commit')
    
        if 'full data' in command:
            self.cur.execute('SELECT * FROM COMMAND_CENTRE;')
            cur_details = self.cur.fetchall()
            self.cons("Time".center(30), "Command".center(
                30), "Subcommand".center(40))
            for i in cur_details:
                if i[2] == 'NULL' or i[2] is None:
                    self.cons(datetime.datetime.fromtimestamp(i[0]).strftime(
                        '%d/%m/%Y %H:%M:%S').ljust(30), i[1].ljust(30))
                else:
                    self.cons(datetime.datetime.fromtimestamp(i[0]).strftime(
                        '%d/%m/%Y %H:%M:%S').ljust(30), i[1].ljust(30), i[2].ljust(30))
        elif 'command' in command:
            self.cur.execute(
                'SELECT COMMAND_NAME, COUNT(*) FROM COMMAND_CENTRE GROUP BY COMMAND_NAME;')
            cur_details = self.cur.fetchall()
            self.cons("Command".center(30), "Frequency".center(10))
            for i in cur_details:
                self.cons(i[0].ljust(30), i[1])
        elif 'topic' in command:
            self.cur.execute(
                'SELECT SUBCOMMAND, COUNT(*) FROM COMMAND_CENTRE WHERE COMMAND_NAME="WIKIPEDIA" GROUP BY SUBCOMMAND;')
            cur_details = self.cur.fetchall()
            self.cons("Subcommand".center(30), "Frequency".center(10))
            for i in cur_details:
                self.cons(i[0].ljust(30), i[1])
        else:
            self.speak("Sorry, I didn't understand that.")
            self.cons("Sorry, I didn't understand that.")
    
    
    def processCommand(self, command):
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
            'the time': 'self.getTime()',
            'date': 'self.getDate()',
            'report': 'self.showReport()',
            'joke': 'self.tellJoke()',
            'fact': 'self.tellFact()',
            'exit': 'exit()',
            'thank you': 'self.thankExit()'
        }
    
        flag = False
    
        for key in commands:
            if (key in command):
                eval(commands[key])
                flag = True
    
        if flag == False:
            self.speak("Sorry, I didn't understand that.")
    
    
    def startListening(self):
        while True:
            self.listenForCommand("loop")
    
    

if __name__ == '__main__':
    ai_project = voice_assist()
