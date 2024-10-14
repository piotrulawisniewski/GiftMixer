# GiftMixer project
# R32NOR | ZOLCBYTERS
# 2024


import os
import google.generativeai as genai
from google.generativeai.types.generation_types import StopCandidateException

import functions
from logger_config import logger


def gemini_api(group_name: str, price_limit: str):
    """
    Interacts with the Gemini AI API to provide gift ideas based on user input, group name, and price limit.

    This function initializes a chat session with the Gemini AI model, loads a training prompt from a local file,
    and starts a conversation with the user to suggest gift ideas. The conversation continues until the user runs out of
    tokens or chooses to exit. The prompt and price limit are customized based on the group name and price limit provided.

    The user is guided through several prompts where they can interact with the AI for gift suggestions. Tokens are
    consumed during the conversation, and the function tracks the number of tokens used and remaining.

    :param group_name: The name of the group for which the gift ideas are generated.
    :param price_limit: The maximum price limit for gifts to be considered.

    :return:
        - None if an error occurs or the user exits.
        - False if a violation of safety rules occurs (triggering `StopCandidateException`).

    :raises FileNotFoundError: If the training prompt file is not found.
    :raises EOFError: If an error occurs while reading the prompt file.
    :raises OSError: If a system-related error occurs while accessing the file.
    :raises StopCandidateException: If the user's input violates safety rules.
    :raises Exception: For any other unexpected errors.
    """

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])

    # fetching training prompt
    try:
        training_prompt_filepath = os.getcwd() + "\\gemini_API_training_prompt.txt"
        if os.path.isfile(training_prompt_filepath):
            training_prompt = ""

            with open(training_prompt_filepath, 'r') as file:
                for line in file:
                    line = line.strip()

                    # removing new lines at the end of the line
                    if line[len(line) - 1:] == '\n':
                        line = line[:len(line) - 1]
                    training_prompt += line

            training_prompt = training_prompt.format(group_name=group_name, price_limit=price_limit)

    except FileNotFoundError or EOFError or OSError as err:
        print("System error.")
        logger.error(err, exc_info=True)
        return None
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None

    response = chat.send_message(training_prompt, generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=[],
            temperature=1.5,
            ),
        )

    training_tokens = model.count_tokens(chat.history).total_tokens

    # WishAI chat greetings
    print(f"\nWelcome to WishAI - GiftMixer ideas helper! \nIf you have no idea what you could wish - don't worry - I am here to help you. \
    Just give me hint what you are interested in or how do you like to spent your free time.\n")

    try:
        prompt = functions.get_non_empty_input("Your prompt: ")

        while True:

            response = chat.send_message(prompt)
            response.resolve()

            print("\n")
            for chunk in response:
                print(chunk.text)
            print("_" * 100)

            tokens_used = model.count_tokens(chat.history).total_tokens - training_tokens
            tokens_awarded = 2000
            tokens_left = tokens_awarded - tokens_used

            if tokens_left <= 0:
                print(f"You run out of the limit of {tokens_awarded} tokens.")
                break
            else:
                print(f"Tokens used for conversation: {tokens_used}")
                print(f"Tokens left: {tokens_left}")

            prompt = input("\nNext prompt (Press 'ENTER' if you want to exit): ")
            # ending message
            if prompt == "":
                print("\nHave fun with GiftMixer! :)\n")
                break

    except StopCandidateException as stop_err:
        print("Your prompt violates our safety rules. It is forbidden to use any harmful phrase. \nWishAI chat interrupted.\n")
        logger.error(stop_err, exc_info=True)
        return False
    except Exception as e:
        print(f"An unexpected error occurred.")
        logger.error(e, exc_info=True)
        return None
