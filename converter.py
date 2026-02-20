import wave
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from pathlib import Path


class Converter:
    """
    Converts either a text to audio or a audio to text. 
    Default is transcription.
    Can only conver .wav file (WAV, mono, 16-bit PCM).
    """
    def __init__(self,
            input_path=None, 
            output_path=None,
            speech_to_text_model_path=None, 
            text_to_speech_model_path=None,
            sample_rate=1600,
            speech_to_text=True,
        ):
        self.input_path = input_path
        self.output_path = output_path
        self.text_to_speech_model_path=text_to_speech_model_path
        self.speech_to_text_model_path=speech_to_text_model_path
        self.sample_rate=1600
        self.speech_to_text=speech_to_text


    def _process_paths(self):
        """
        Checks for necessary filepaths and uses defaults if none were given.
        """
        # Get the necessay filepaths
        current_directory = Path(__file__).resolve().parent
        default_audio_path = str(Path.joinpath(current_directory, 'recording.wav'))
        default_text_path = str(Path.joinpath(current_directory, 'transcription.txt'))
        default_speech_to_text_model_path = str(Path.joinpath(
                current_directory, 
                'speech_recognition_models',
                'vosk_en_small'
            ))
        default_text_to_speech_model_path = str(Path.joinpath(
            current_directory,
            '',
        ))
        if self.speech_to_text:
            if not self.input_path:
                self.input_path = default_audio_path
            if not self.output_path:
                self.output_path = default_text_path
            if not self.speech_to_text_model_path:
                self.speech_to_text_model_path = default_speech_to_text_model_path
        else:
            if not self.input_path:
                self.input_path = default_text_path
            if not self.output_path:
                self.output_path = default_audio_path
            if not self.text_to_speech_model_path:
                self.text_to_speech_model_path= default_text_to_speech_model_path


    def _check_audio_file(self):
        """
        Opens the audio file and checks that it is in the proper format.
        """
        with wave.open(self.input_path) as file:
            channels = file.getnchannels()
            sample_width = file.getsampwidth()
            comp_type = file.getcomptype()

        if channels != 1 or sample_width != 2 or comp_type != "NONE":
            raise ValueError('Audio input file must be WAV, mono, 16-bit PCM')
        

    def _read_audio_file(self):
        """
        Reads the audio file and converts to text using the model. 
        """
        # Initialize the model
        print(self.speech_to_text_model_path)
        model = Model(self.speech_to_text_model_path)

        with wave.open(self.input_path) as file:
            recognizer = KaldiRecognizer(model, file.getframerate())
            results = []
            while True:
                data = file.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    results.append(result.get('text', ''))
            # Get final bits:
            final_result = json.loads(recognizer.FinalResult())
            results.append(final_result.get('text', ''))

        # Convert results list to string
        self.text = ' '.join(results)


    def _write_text_file(self):
        """
        Writes the transcribed text to a .txt file.
        """
        with open(self.output_path, 'w') as file:
            file.write(self.text)

    
    def audio_to_text(self):
        """
        Parent methods to call all necessary methods to conver the 
        input audio file to an output text file. 
        """
        self._process_paths()
        self._check_audio_file()
        self._read_audio_file()
        self._write_text_file()


    def text_to_audio(self):
        """
        Converts a text file to audio calling the necessary child methods.
        """
        pass


if __name__ == '__main__':
    converter = Converter()
    converter.audio_to_text()
