from singlestore import insert_chat_log
from singlestore import steps
from deepgram_api import main
# from __file__ import __check_if_step_is_complete__

step_counter = 1
for step in steps:
    count = 2
    name = f"Step_{step_counter}"
    # while not __check_if_step_is_complete__:
    text = main()
    insert_chat_log(name, 'Chat', text, count) 
    count += 1
    step_counter += 1
