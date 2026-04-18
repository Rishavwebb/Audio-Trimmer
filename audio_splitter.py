import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

def extract_and_name_words(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading audio file... (This may take a moment)")
    sound = AudioSegment.from_file(file_path)

    print("Detecting silences and splitting audio...")
    chunks = split_on_silence(
        sound,
        min_silence_len=500,          
        silence_thresh=sound.dBFS-14, 
        keep_silence=200              
    )

    print(f"Detected {len(chunks)} audio segments. Processing transcription...")

    recognizer = sr.Recognizer()

    for i, chunk in enumerate(chunks):
        # SpeechRecognition requires .wav to read the audio, so we make a temporary file
        temp_filename = os.path.join(output_dir, f"temp_chunk_{i}.wav")
        chunk.export(temp_filename, format="wav")

        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)

            try:
                spoken_text = recognizer.recognize_google(audio_data)
                
                safe_name = "".join(
                    [c for c in spoken_text if c.isalnum() or c == ' ']
                ).strip().replace(' ', '_').lower()

                if safe_name:
                    final_filepath = os.path.join(output_dir, f"{safe_name}.mp3")

                    counter = 1
                    while os.path.exists(final_filepath):
                        final_filepath = os.path.join(output_dir, f"{safe_name}_{counter}.mp3")
                        counter += 1

                    # Export the final cut as .mp3 directly
                    chunk.export(final_filepath, format="mp3")
                    
                    # Delete the temporary .wav file
                    os.remove(temp_filename)
                    
                    print(f"Successfully processed and saved: {final_filepath}")
                else:
                    print(f"Segment {i}: Recognized text invalid for filename. Kept as {temp_filename}")

            except sr.UnknownValueError:
                print(f"Segment {i}: Could not understand the audio. Kept as {temp_filename}")
            except sr.RequestError as e:
                print(f"Segment {i}: API request error ({e}). Kept as {temp_filename}")

if __name__ == "__main__":
    INPUT_FILE = "ALL.mp3" 
    OUTPUT_FOLDER = "extracted_words"
    
    extract_and_name_words(INPUT_FILE, OUTPUT_FOLDER)