# Bilingual Assistant

A bilingual language assistant application that supports Hindi and Kannada languages. This application utilizes speech recognition, translation services, and text-to-speech capabilities to facilitate seamless communication between the two languages.

## Features

- **Speech Recognition**: Converts spoken language into text.
- **Language Translation**: Translates text between Hindi and Kannada.
- **Text-to-Speech**: Converts translated text back into speech.
- **User-Friendly Interface**: Built with Tkinter for easy interaction.

## Requirements

To run this project, you will need the following Python packages:

- `tkinter`
- `speech_recognition`
- `sounddevice`
- `numpy`
- `threading`
- `pygame`
- `google-cloud-texttospeech`
- `google-generativeai`
- `google-cloud-translate`
- `Pillow`

## Installation

1. Clone this repository:
```
git clone https://github.com/chethanareddy-2801/bilingual-assistant.git
cd bilingual-assistant
```
2. Install the required packages:
```
pip install -r requirements.txt
```

3. Set up Google Cloud credentials:
- Create a service account in Google Cloud and download the JSON key file.
- Replace the path in the code with the path to your JSON key file.

4. Run the application:
```
python main.py
```

## Usage

1. Select the language (Hindi or Kannada) using the radio buttons.
2. Click "Start Recording" to begin speaking.
3. After recording, the application will process the audio, translate it, and generate speech.
4. Click "Play Translation" to hear the translated audio.

## Acknowledgments

- Google Cloud for providing powerful APIs for translation and text-to-speech.
- The open-source community for their invaluable contributions.
