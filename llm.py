# pip install langchain huggingfacehub
# or
# pip install google-generativeai

import os

####### ------------------------ HUGGINGFACE/HUB ----------------------------------- ###########

# from langchain import PromptTemplate, HuggingFaceHub, LLMChain
# token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
#
# google_key = None
#
# template = """Two words are going to fight. Which of the following words wins?
#
# {player_word} VS {npc_word}
#
# Answer: The word that would win is: """
#
# prompt = PromptTemplate(template=template, input_variables=["player_word", "npc_word"])
#
# llm_chain = LLMChain(prompt=prompt,
#                      llm=HuggingFaceHub(repo_id="google/flan-t5-large",
#                                         model_kwargs={"temperature":0,
#                                                       "max_length":64}))
#
#
# def get_winner(player_word, npc_word):
#     llm_answer = llm_chain.predict(player_word=player_word, npc_word=npc_word)
#     return llm_answer



###### --------------------------------- GOOGLE --------------------------------------------- #######
import google.generativeai as palm

key = os.getenv('google_key')

palm.configure(api_key=key)

models = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
]

for m in models:
    print(f"Model Name: {m.name}")

model = models[0].name


def get_winner(player_word, npc_word):
    prompt = f"""Two words are going to fight. Which of the following words wins? If you are unsure about which word would win, or think neither would win, use your best reasoning to pick one of them. Always, no matter what, respond with one of the words.

    {player_word} VS {npc_word}

    Answer: The word that would win is: """

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=32,
    )

    result = completion.result
    return result