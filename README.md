# political_audio_analyzer
analyzes audio files and creates useful output based on them

need to use python3.9 or high for library dependencies
run 

pip install -r requirements.txt

will need api keys from https://huggingface.co/settings/tokens
there were alot of things on the website I had to enable that I dont remember all of the settings but outputs were very helpful

save the api keys in .env before running


OPENAI_API_KEY=TOKEN

HUGGING_FACE_HUB_TOKEN=TOKEN..

open source diarization (labeling whos talking in the audio) takes a long time, could possibly speed it up with multi threading but didnt look into too much
