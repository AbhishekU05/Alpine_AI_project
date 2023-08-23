import mysql.connector as sql
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import randfacts
import pyjokes
import tkinter as tk
from threading import Thread

chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Friday, your assistant")
    speak("How may I help you?")

def listenForCommand(modl):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        if modl=="wiki":
            return query
        elif modl=="report":
            processReport(query.lower())
        else:
            processCommand(query.lower())
    except Exception as e:
        print("Say that again please...")
        speak("Say that again please...")
        listenForCommand("loop")

def processCommand(command):
    if 'wikipedia' in command:
        searchWikipedia(command)
    elif 'open youtube' in command:
        openYouTube()
    elif 'open google' in command:
        openGoogle()
    elif 'play music' in command or 'play song' in command:
        playMusic()
    elif 'the time' in command:
        getTime()
    elif 'date' in command:
        getDate()
    elif 'report' in command:
        showReport()
    elif 'joke' in command:
        tellJoke()
    elif 'fact' in command:
        tellFact()
    elif 'exit' in command:
        cur.close()
        con.close()
        exit()
    elif 'thank you' in command:
        speak("Welcome. Have a nice day. Bye")
        print("Welcome. Have a nice day. Bye")
        cur.close()
        con.close()
        exit()
    else:
        speak("Sorry, I didn't understand that.")

def insrt_table(cmd):
    update_command='INSERT INTO COMMAND_CENTRE VALUES(%d,"%s",NULL);'%(datetime.datetime.now().timestamp(),cmd)
    print(update_command)
    cur.execute(update_command)
    cur.execute('commit')

def searchWikipedia(command):
    speak('What would you like to search on Wikipedia?')
    query = listenForCommand("wiki")
    speak('Searching Wikipedia...')
    results = wikipedia.summary(query, sentences=2)
    speak("According to Wikipedia")
    print(results)
    speak(results)
    update_command='INSERT INTO COMMAND_CENTRE VALUES(%d,"%s","%s");'%(datetime.datetime.now().timestamp(),command,query.lower())
    print(update_command)
    cur.execute(update_command)
    cur.execute('commit')

def openYouTube():
    speak("Opening YouTube...")
    webbrowser.get(chrome_path).open("https://www.youtube.com")
    insrt_table("youtube")

def openGoogle():
    speak("Opening Google...")
    webbrowser.get(chrome_path).open("https://www.google.com")
    insrt_table("google")

def tellJoke():
    joke = pyjokes.get_joke()
    speak(joke)
    print(joke)
    insrt_table("joke")

def tellFact():
    fact1 = randfacts.get_fact()
    speak(fact1)
    print(fact1)
    insrt_table("fact")

def playMusic():
    speak("Playing music...")
    webbrowser.get(chrome_path).open("https://open.spotify.com")
    insrt_table("music")

def getTime():
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"The time is {strTime}")
    print(f"The time is {strTime}")
    insrt_table("time")

def getDate():
    today = datetime.date.today()
    speak(f"Today's date is {today}")
    print(f"Today's date is {today}")
    insrt_table("date")

def startListening():
    while True:
        listenForCommand("loop")

def showReport():
    speak('Choose report you would like to see from the following options')
    print('Choose report you would like to see from the following options:')
    speak('full data, command frequency, topic frequency')
    print('1. FULL DATA (TELL "FULL DATA")')
    print('2. FREQUENCY OF COMMANDS USED (TELL "COMMAND")')
    print('3. FREQUENCY OF TOPICS USED (TELL "TOPIC")')
    listenForCommand("report")

def processReport(command):
    if any(ext in command for ext in ['full data','command','topic']):
        update_command='INSERT INTO COMMAND_CENTRE VALUES(%d,"report","%s");'%(datetime.datetime.now().timestamp(),command)
        print(update_command)
        cur.execute(update_command)
        cur.execute('commit')

    if 'full data' in command:
        cur.execute('SELECT * FROM COMMAND_CENTRE;')
        cur_details=cur.fetchall()
        print("Time".center(30),"Command".center(30),"Subcommand".center(40))
        for i in cur_details:
            if i[2]=='NULL' or i[2] is None:
                print(datetime.datetime.fromtimestamp(i[0]).strftime('%d/%m/%Y %H:%M:%S').ljust(30),i[1].ljust(30))
            else:
                print(datetime.datetime.fromtimestamp(i[0]).strftime('%d/%m/%Y %H:%M:%S').ljust(30),i[1].ljust(30),i[2].ljust(30))
    elif 'command' in command:
        cur.execute('SELECT COMMAND_NAME, COUNT(*) FROM COMMAND_CENTRE GROUP BY COMMAND_NAME;')
        cur_details=cur.fetchall()
        print("Command".center(30),"Frequency".center(10))
        for i in cur_details:
            print(i[0].ljust(30),i[1])
    elif 'topic' in command:
        cur.execute('SELECT SUBCOMMAND, COUNT(*) FROM COMMAND_CENTRE WHERE COMMAND_NAME="WIKIPEDIA" GROUP BY SUBCOMMAND;')
        cur_details=cur.fetchall()
        print("Subcommand".center(30),"Frequency".center(10))
        for i in cur_details:
            print(i[0].ljust(30),i[1])
    else:
        speak("Sorry, I didn't understand that.")
        print("Sorry, I didn't understand that.")


try:
    #con=sql.connect(host='localhost',user='root',password='1234',database='SR_SEARCH_HISTORY')
    con=sql.connect(host='localhost',user='root',password='nov@30112005')
    print('Connected with mySQL database')
except Exception as e:
    print('Database not connected.... Exiting')
    exit()

cur=con.cursor()
#cur.execute('CREATE DATABASE SR_SEARCH_HISTORY;')
cur.execute('USE SR_SEARCH_HISTORY;')
#cur.execute("CREATE TABLE COMMAND_CENTRE(EXE_TIME BIGINT PRIMARY KEY, COMMAND_NAME VARCHAR(30), SUBCOMMAND VARCHAR(30));")

# Create the main window
window = tk.Tk()
window.title("Friday Assistant")

# Create and position the GUI components
label = tk.Label(window, text="Press the 'Speak' button and give a command:")
label.pack()

speak_button = tk.Button(window, text="Speak", command=lambda: Thread(target=startListening).start())
speak_button.pack()

showreport_button=tk.Button(window,text="Show report",command=showReport)
showreport_button.pack()

# Run the GUI main loop
wishMe()
window.mainloop()
