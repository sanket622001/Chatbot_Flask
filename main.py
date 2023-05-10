import os
import speech_recognition as sr
import openai
from gtts import gTTS
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from playsound import playsound
from apikey import api_data

app = Flask(__name__)

# Set up OpenAI API credentials
openai.api_key = api_data


@app.route('/')
def home():
    return render_template('index.html')


def handle_form():
    text_to_display = []
    r = sr.Recognizer()
    stop_phrase = "stop listening"
    stop_listening = False

    while not stop_listening:
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
        try:
            result = r.recognize_google(audio)
            print("Recognizing.....")
            query = r.recognize_google(audio, language='en-in')
            text_to_display.append("You Said: {} \n".format(query))
            if stop_phrase in query.lower():
                stop_listening = True
                response_text = "Stopping voice chat..."
                print(response_text)
            else:
                response = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=result,
                    max_tokens=200,
                    stop=['\stop'],
                )
                if response.choices:
                    response_text = response.choices[0].text
                else:
                    response_text = "I'm sorry, I didn't understand what you said"
                text_to_display.append("AI Response: {}\n".format(response_text))
                tts = gTTS(text=response_text, lang='en')
                filename = 'response.mp3'
                tts.save(filename)
                playsound(filename)
                os.remove(filename)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from our service; {0}".format(e))

    return render_template('index.html', text=text_to_display)


@app.route('/', methods=['GET', 'POST'])
def submit_textarea():
    if request.method == 'POST':
        return handle_form()
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
