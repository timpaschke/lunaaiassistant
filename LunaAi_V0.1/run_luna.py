from modules import speech_converter
def main():
    global listening_for_trigger_word
    while should_run:
        command = listen_for_command()
        if listening_for_trigger_word:
            listening_for_trigger_word = False
        else:
            perform_command(command)
        time.sleep(1)
    respond("Goodbye.")

if __name__ == "__main__":
    main()