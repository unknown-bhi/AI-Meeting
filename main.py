from dotenv import load_dotenv
from utils.audio_processor import process_input ,get_audio_only
from core.transcriber import transcribe_all
from core.sammarize import summarize, generate_title
from core.extractor import extract_action_items,extract_key_decisions,extract_question
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

def run_pipeline(source : str ) -> dict:
    print('starting AI Assistant')

    

    chunks  =process_input(source)

    transcript =transcribe_all(chunks)
    print(f'raw transcription (first 300 characters) {transcript[:300]}')

    title =generate_title(transcript)
    print('title generate succesfully')

    summary = summarize(transcript)
    print('summary generate succesfully')


    action_items = extract_action_items(transcript)
    key_decisions =extract_key_decisions(transcript)
    question = extract_question(transcript)

    print('rag start suceesfully succesfully')

    rag_chain = build_rag_chain(transcript)
    print('rag end succesfully')

    return {
        'transcript' : transcript,
        'title' : title,
        'summary' : summary,
        'action items' : action_items,
        'key decisions' : key_decisions,
        'question' : question,
        'rag' : rag_chain

    }


# ============ MAIN ============
if __name__ == "__main__":
    # CLI input
    
    source = input("Enter YouTube URL or local file path: ").strip()
    print("type  'audio' for geting audion and type 'summary' for get summery")
    option = input('select option : ')
    if option == 'audio':
        only_audio = get_audio_only(source)
        print('audio file download successfully!')
    else:
    # Pipeline run karo
        result = run_pipeline(source)
    
        # Results print karo
        print("\n" + "=" * 60)
        print(f"📌 Title: {result['title']}")
        print(f"\n📄 Summary:\n{result['summary']}")
        print(f"\n✅ Action Items:\n{result['action items']}")
        print(f"\n🔑 Key Decisions:\n{result['key decisions']}")
        print(f"\n❓ Questions:\n{result['question']}")
        print("\n" + "=" * 60)
        
    
    
        while True:
            question = input("Your question : ").strip()
            if question == 'exit':
                print("😊 Goodbye!")
                break

            if not question:
                continue
            answer = ask_question(result['rag'], question)
            print(f"\n💡 Answer: {answer}")

