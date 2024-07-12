from groq import Groq
import os

note_path = 'C:\\Users\\Tim\\Documents\\test notes'
groq_client = Groq(api_key='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')

pre_prompt = ('You are my ai Assitant for Note taking. You will create a Markdown note file.'
               'You will get have to make a got looking, easy to understand note in German with all the necessary'
               'things given to you. stick to the informtion that is given to you. Make the notes so i can learn with them.'
               'Only create a note out of the information i said to you.'
               'You only return the note with no extra Information.'
               )

def create_note(note):
    combined_content = pre_prompt + " " + note
    convo = [{'role': 'user', 'content': combined_content}]
    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-8b-8192')
    text = chat_completion.choices[0].message.content
    safe_note(text,create_title(note))

def create_title(note):
    combined_content = "Erstelle zu folgender Notiz ein passenden Titel mit keinen Sonderzeichen. Beachte dass der Titel so verfasst sein soll dass ich ihn Einfach finde kann, also so dass ein such algorithmus diese als gesuchte Notiz identifizieren kann Du sollst nur den Titel zurück geben" + note
    convo = [{'role': 'user', 'content': combined_content}]
    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-8b-8192')
    return chat_completion.choices[0].message.content

def safe_note(note, file_name):
    # Ensure the vault path exists
    if not os.path.exists(note_path):
        raise FileNotFoundError(f"The specified Obsidian Vault path does not exist: {note_path}")

    file_name = file_name.strip('"') + ".md"
    print(file_name)
    # Define the full file path
    file_path = os.path.join(note_path, file_name)

    # Write the note to the file in Markdown format
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(note)

create_note(input("your note: "))