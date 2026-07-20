from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from dotenv import load_dotenv
from core.sammarize import summarize , generate_title
from core.transcriber import transcribe_all
from core.extractor import extract_action_items ,extract_key_decisions ,extract_question





load_dotenv()

source = 'https://youtu.be/m8o2GrbR3d8?si=Kwx8cZOtVYMbYbQR'

chunks = process_input(source)

transcript =transcribe_all(chunks)

print('\n' + '=' * 40)
print('===== TRANSCRIPT ======')
print('=' * 40)

print(transcript[:500] + '......' if len(transcript) > 500 else transcript)

title = generate_title(transcript)
summary = summarize(transcript)

print('\n' + '=' * 40)
print('===== Title : {title} ======')
print('=' * 40)

print('\n' + '=' * 40)
print('===== SUMMARY ======')
print('=' * 40)

print(summary)


action_items = extract_action_items(transcript)
decision = extract_key_decisions(transcript)
question = extract_question(transcript)

print('\n' + '=' * 40)
print('===== ACTION ITEMS ======')
print('=' * 40)
print(action_items)


print('\n' + '=' * 40)
print('===== KEY DECISION ======')
print('=' * 40)
print(decision)

print('\n' + '=' * 40)
print('===== OPEN QUESTION ======')
print('=' * 40)
print(question)
