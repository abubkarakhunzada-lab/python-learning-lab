import os
import speech_recognition as sr
import pyttsx3
import PyPDF2
import tkinter as tk
from tkinter import filedialog, scrolledtext
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Text-to-speech engine
engine = pyttsx3.init()

# Global knowledge text
knowledge_text = ""

# Load PDF or TXT knowledge
def load_knowledge_base(path):
    global knowledge_text
    try:
        if path.endswith(".pdf"):
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                knowledge_text = " ".join(
                    [page.extract_text() for page in reader.pages if page.extract_text()]
                )
        elif path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                knowledge_text = f.read()
        chatbox.insert(tk.END, f"[Loaded file: {os.path.basename(path)}]\n\n")
    except Exception as e:
        chatbox.insert(tk.END, f"[File Load Error: {e}]\n\n")

# Ask OpenAI GPT
def get_ai_response(prompt):
    try:
        full_prompt = knowledge_text + "\n\nUser: " + prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Change to gpt-4 if available
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error: {e}]"

# Speak the response
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        chatbox.insert(tk.END, f"[TTS Error: {e}]\n")

# Voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except Exception as e:
            return f"[Voice Error: {e}]"

# Send typed message
def send():
    user_input = entry.get()
    entry.delete(0, tk.END)
    if not user_input.strip():
        return
    chatbox.insert(tk.END, f"You: {user_input}\n")
    reply = get_ai_response(user_input)
    chatbox.insert(tk.END, f"AI: {reply}\n\n")
    speak(reply)

# Send voice message
def voice_input():
    user_input = listen()
    chatbox.insert(tk.END, f"You (voice): {user_input}\n")
    reply = get_ai_response(user_input)
    chatbox.insert(tk.END, f"AI: {reply}\n\n")
    speak(reply)

# Load knowledge file
def load_file():
    path = filedialog.askopenfilename(filetypes=[("Text/PDF files", "*.txt *.pdf")])
    if path:
        load_knowledge_base(path)

# GUI Setup
window = tk.Tk()
window.title("AI Chatbot with GPT + Voice + Knowledge")
window.geometry("720x600")

chatbox = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
chatbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(window, font=("Arial", 12))
entry.pack(padx=10, pady=5, fill=tk.X)

btn_frame = tk.Frame(window)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Send", width=10, command=send).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="🎤 Voice", width=10, command=voice_input).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="📂 Load File", width=12, command=load_file).grid(row=0, column=2, padx=5)

window.mainloop()
