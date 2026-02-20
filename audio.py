import pyaudio
import wave
import threading
from pathlib import Path


class Audio:
    """
    Uses wave, threading, and pyaudio to record audio and save it to a .wav file. The 
    default parameters are set ideal for speech to text:
    
    :filepath: will be either input or output and must be a string
    :sample_rate: Samples per second (1600 = speech recognition standard)
    :channels: 1 = Mono, 2 = Stero (left + right)
    :format: Each sample uses 16 bits / 2 bytes (WAV files)
    :frames_per_buffer: How frames are read ( 4096 / 1600 = 0.256 seconds audio per buffer)
    """
    def __init__(self,
        filepath=str(Path.joinpath(Path(__file__).resolve().parent, 'recording.wav')), 
        sample_rate=16000,
        channels=1, 
        format=pyaudio.paInt16,
        frames_per_buffer=4096,
    ):
        """
        Initializes three additional variables:

        :recording: boolean to manage the recording thread and user input
        :frames: a list to hold the chunks of data recorded.
        :pyaudio_obj: the pyaudio_obj for the stream
        :audio_stream: will hold the pyaudio stream created in _open_audio_stream
        :microphones: list of dictionaries of available microphones
        :speakers: list of dictionaries of available speakers
        """
        self.filepath = str(filepath)
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = format
        self.frames_per_buffer = frames_per_buffer
        self.recording = True
        self.recorded_frames = []
        self.pyaudio_object = None
        self.audio_stream = None
        self.microphones = []
        self.speakers = []
            

    def _open_audio_stream(self, 
            record=True, 
            file_bytes=None, 
            input_device_index=None, 
            output_device_index=None,
        ):
        """
        Creates a pyaudio stream

        :record: if set to True will record
        :file_bytes: only necessary when reading from file to play audio
        :input_device: index of device from pyaudio_object.get_device_count()
        :output_device: index of device from pyaudio_object.get_device_count()
        """
        # Create the pyaudio object
        self.pyaudio_obj = pyaudio.PyAudio()

        # Get the default devices if they weren't passed as parameters
        if input_device_index is None:
            input_device_index = self.pyaudio_obj.get_default_input_device_info()['index']
        if output_device_index is None:
            output_device_index = self.pyaudio_obj.get_default_output_device_info()['index']

        # Handle whether it is recording or playback
        if record:
            output = False
            audio_format = self.format
            channels = self.channels
            sample_rate = self.sample_rate
        else:
            output = True
            audio_format = self.pyaudio_obj.get_format_from_width(file_bytes.getsampwidth())
            channels = file_bytes.getnchannels()
            sample_rate = file_bytes.getframerate()

        # Have the microphone start listening with the audio stream (but not recording yet)
        self.audio_stream = self.pyaudio_obj.open(
            format=audio_format,  
            channels=channels,
            rate=sample_rate,
            input=record,
            output=output,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=input_device_index,
            output_device_index=output_device_index,
        )


    def _close_audio_stream(self):
        """
        Closes and cleans up the stream.
        """
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.pyaudio_obj.terminate()

    
    def _write_to_file(self):
        """
        Joins the data into a single variable and then writes to a .wav
        file. 
        """
        full_audio = b''.join(self.recorded_frames)
        with wave.open(self.filepath, 'wb') as file:
            file.setnchannels(self.channels)
            file.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
            file.setframerate(self.sample_rate)
            file.writeframes(full_audio)


    def _record_thread(self):
        """
        A thread to constantly record audio until the user stops the recording
        and recording attribute is set to False.
        """
        while self.recording:
            data = self.audio_stream.read(self.frames_per_buffer, exception_on_overflow=False)
            self.recorded_frames.append(data)


    def record(self, use_default=True):
        """
        A thread to wait for user input to trigger the start and stop of the
        recording threat. 
        """
        # Prompot user to select device if not using defualt
        if use_default:
            device_index = None
        else:
            device_index = self._select_device()

        # Start the microphone stream
        self._open_audio_stream()

        # Start the recording
        input('Press <ENTER> to start recording...')
        thread = threading.Thread(target=self._record_thread)
        thread.start()

        # Stop the recording
        input('Press <ENTER> to stop the recording')
        self.recording = False
        thread.join()  # Wait for recording thread to stop
        self._close_audio_stream()

        # Write the data to file
        self._write_to_file()


    def play(self, use_default=True):
        """
        Plays audio from the given file. Uses the default speaker.
        """
        # Prompot user to select device if not using defualt
        if use_default:
            device_index = None
        else:
            device_index = self._select_device(record=False)

        # Open the file and get the audio format details
        with wave.open(self.filepath, 'rb') as file:
            self._open_audio_stream(record=False, file_bytes=file, output_device_index=device_index)

            # Read data in chunks and play
            data = file.readframes(self.frames_per_buffer)
            while data:
                self.audio_stream.write(data)
                data = file.readframes(self.frames_per_buffer)

            # Close and clean up the stream
            self._close_audio_stream()


    def _get_available_devices(self):
        """
        Gets the available devices for recording and playback and adds them to the 
        micrphones and speakers class attribute lists.
        """
        pyaudio_obj = pyaudio.PyAudio()
        for i in range(pyaudio_obj.get_device_count()):
            info = pyaudio_obj.get_device_info_by_index(i)
            device_dict = {
                'id': i,
                'name': info['name']
            }
            # Differeniate between speakers and microphones 
            if info['maxInputChannels'] > 0:
                self.microphones.append(device_dict)
            if info['maxOutputChannels'] > 0:
                self.speakers.append(device_dict)
        pyaudio_obj.terminate()


    def _select_device(self, record=True):
        """
        Prompts the user to select the device to use. 

        :record: True for microphones and False for speakers.
        """
        self._get_available_devices()
        devices = self.microphones if record else self.speakers
        prompt = self._format_device_prompt(devices)
        while True:
            user_input = input(prompt).strip()
            try:
                index = int(user_input)
                if index not in [device['id'] for device in devices]:
                    print('\nERROR: You must select a number from the list.\n')
                else:
                    return index
            except ValueError:
                print('\nERROR: Input must be whole number\n')


    def _format_device_prompt(self, devices):
        """
        Returns the device prompt for the user to select a device.

        :devices: List of devices baed on wether a microphone or speaker is 
        needed.
        """
        string = '\n*****************************\nSelect a device to use:\n\n'
        for device in devices:
            string += f"\t{device['id']}. {device['name']}\n"
        string += '\n*****************************\n'
        return string


if __name__ == "__main__":
    audio_obj = Audio()
    audio_obj.record(use_default=True)
    audio_obj.play(use_default=True)
    from converter import Converter
    converter = Converter()
    converter.audio_to_text()

