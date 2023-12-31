from flask import Flask, render_template, redirect, url_for, request, session
from main import draw_letters, hand_size, pick_npc_word, special_characters, sort_hand, generate_upgrades, \
    alphabet, lifesteal_check, number_of_upgrades
from llm import get_winner
import os

app = Flask(__name__)

app.secret_key = os.getenv('secret_key')

@app.route("/")
def homepage():
    return render_template('homepage.html')


@app.route("/initialize-game", methods=["POST"])
def initialize_game():
    # reset all the game variables
    session['stage'] = 1
    session['word_number'] = 1
    session['current_level'] = 1
    session['ink'] = 0
    session['redraw'] = False
    session['summon_letter'] = False
    session['skip_word'] = False
    session['increase_hp'] = False
    session['increase_hand_size'] = False
    session['lifesteal'] = False
    session['hp'] = 10
    session['hand_size'] = 10
    session['lvl1_words'] = ['bat', 'book', 'rock', 'claws', 'scissors', 'cat', 'dog', 'wrestler', 'ice', 'melancholy',
                             'psychology', 'keeper']
    session['lvl2_words'] = ['robot', 'unicorn', 'mystery', 'bee', 'knife', 'fire', 'earth', 'light', 'thunder',
                             'science', 'elf', 'mermaid']
    session['lvl3_words'] = ['wizard', 'pirate', 'nina', 'samurai', 'vampire', 'werewolf', 'zombie', 'ghost', 'troll',
                             'witch', 'knight', 'cyclops', 'yeti', 'minotaur']
    session['lvl4_words'] = ['valkyrie', 'happy', 'believe', 'harmony', 'freedom', 'america', 'eagle', 'energy',
                             'imagination', 'dream', 'truth', 'beauty']
    session['lvl5_words'] = ['chaos', 'mystery', 'time', 'hope', 'knowledge', 'fate', 'courage', 'fear', 'justice',
                             'nightmare', 'villian', 'sickness']
    session['lvl6_words'] = ['mafia', 'magic', 'insane', 'maniac', 'murderer', 'faith', 'truth', 'beauty', 'joy',
                             'grace', 'hope', 'harmony']
    session['lvl7_words'] = ['indomitable', 'thunderbolt', 'explosion', 'earthquake', 'avalanche', 'justice', 'freedom',
                             'wisdom', 'eternal', 'transcendent', 'pinnacle', 'valkyrie']
    session['lvl8_words'] = ['goliath', 'hercules', 'colossus', 'juggernaut', 'warlord', 'inferno', 'behemoth',
                             'leviathan', 'tsunami', 'kraken', 'gladiator']
    session['lvl9_words'] = ['invincible', 'love', 'eternity', 'supreme', 'apex', 'wisdom', 'cataclysm', 'supernova',
                             'phoenix', 'miracle', 'destiny', 'dominant']
    session['lvl10_words'] = ['apocalypse', 'dragon', 'titan', 'warlord', 'omnipotence', 'omniscience', 'perfection',
                              'champion', 'infinity', 'unbeatable', 'undefeated', 'death']
    session['list_of_upgrades'] = [{'upgrade': 'redraw', 'description': 'Redraw your hand. Cost: 10 Ink'},
                     {'upgrade': 'summon_letter', 'description': 'Add any 1 letter to your hand. Cost: 15 Ink'},
                     {'upgrade': 'skip_word', 'description': 'Skip the word. Cost: 20 Ink'},
                     {'upgrade': 'increase_hp', 'description': 'Increase your hp by 1. Cost: 30 Ink'},
                     {'upgrade': 'increase_hand_size', 'description': 'Increase your hand size by 1. Cost: 50 Ink'},
                     {'upgrade': 'lifesteal', 'description': '10% chance to heal 1 HP if beat word. Cost: Passive'}
                     ]

    # draw the correct amount of letters for the player, add to list called hand
    session['hand'] = draw_letters(hand_size)
    session['hand'] = sort_hand(session['hand'])

    # pick a random npc word, remove that word from lvl1 deck, add to lvl1 played words list
    session['npc_word'] = pick_npc_word(session['lvl1_words'])
    session['lvl1_words'].remove(session['npc_word'])

    return redirect(url_for("game"))


@app.route("/game", methods=["GET", "POST"])
def game():
    print(f"/game something was sent in request.form: {request.form}")

    # stage = session['stage']
    # word_number = session['word_number']
    # current_level = session['current_level']
    # ink = session['ink']
    # redraw = session['redraw']
    # summon_letter = session['summon_letter']
    # skip_word = session['skip_word']
    # increase_hp = session['increase_hp']
    # increase_hand_size = session['increase_hand_size']
    # lifesteal = session['lifesteal']
    # hp = session['hp']
    # hand_size = session['hand_size']
    # ink_history = session['ink_history']
    # ability_message = session['ability_message']
    # player_word_history = session['player_word_history']
    # npc_word_history = session['npc_word_history']
    # llm_response_history = session['llm_response_history']
    # player_damage_history = session['player_damage_history']
    # lvl1_words = session['lvl1_words']
    # lvl2_words = session['lvl2_words']
    # lvl3_words = session['lvl3_words']
    # lvl4_words = session['lvl4_words']
    # lvl5_words = session['lvl5_words']
    # lvl6_words = session['lvl6_words']
    # lvl7_words = session['lvl7_words']
    # lvl8_words = session['lvl8_words']
    # lvl9_words = session['lvl9_words']
    # lvl10_words = session['lvl10_words']
    # hand = session['hand']
    # npc_word = session['npc_word']
    # list_of_upgrades = session['list_of_upgrades']

    lvl1_base_ink = 2
    lvl1_ink_reward = int(lvl1_base_ink + 0.1 * session['ink'])
    lvl2_base_ink = 3
    lvl2_ink_reward = int(lvl2_base_ink + 0.1 * session['ink'])
    lvl3_base_ink = 4
    lvl3_ink_reward = int(lvl3_base_ink + 0.1 * session['ink'])
    lvl4_base_ink = 5
    lvl4_ink_reward = int(lvl4_base_ink + 0.1 * session['ink'])
    lvl5_base_ink = 6
    lvl5_ink_reward = int(lvl5_base_ink + 0.1 * session['ink'])
    lvl6_base_ink = 7
    lvl6_ink_reward = int(lvl6_base_ink + 0.1 * session['ink'])
    lvl7_base_ink = 8
    lvl7_ink_reward = int(lvl7_base_ink + 0.1 * session['ink'])
    lvl8_base_ink = 9
    lvl8_ink_reward = int(lvl8_base_ink + 0.1 * session['ink'])
    lvl9_base_ink = 10
    lvl9_ink_reward = int(lvl9_base_ink + 0.1 * session['ink'])
    lvl10_base_ink = 11
    lvl10_ink_reward = int(lvl10_base_ink + 0.1 * session['ink'])


    ### ------------------ MAIN GAMEPLAY LOOP - AROUND PLAY WORD BUTTON --------------------------- ###


    if session['stage'] == 100:
        return redirect(url_for('you_win'))


    if request.method == "POST":
        if "player_word" in request.form:

            session['ink_history'] = None
            session['ability_message'] = None
            session['player_word_history'] = None
            session['npc_word_history'] = None
            session['llm_response_history'] = None
            session['player_damage_history'] = None

            # capture the details about entered word
            player_word = request.form.get('player_word').lower()
            player_word_list = list(player_word)

            # do checks to make sure the word is allowed to be played
            # checks for special characters
            if any(character in special_characters for character in player_word):
                error_message = "ERROR: Word must not contain any special characters."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )

            # checks for using letters in hand
            error = False
            hand_copy = session['hand'].copy()
            for letter in player_word_list:
                if letter not in hand_copy:
                    error = True
                    break
                else:
                    hand_copy.remove(letter)
            if error:
                error_message = "ERROR: Word contained letters not in 'hand'."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )

            # run the llm to see who wins
            llm_response = get_winner(player_word, session['npc_word'])

            # setting up variables for history
            session['player_word_history'] = player_word
            session['npc_word_history'] = session['npc_word']
            session['llm_response_history'] = llm_response

            # if npc word wins
            if llm_response == session['npc_word']:

                # deal 1 damage to player
                session['hp'] -= 1
                session['player_damage_history'] = 1

                #increase stage
                session['stage'] += 1

                # check if player is dead
                if session['hp'] <= 0:
                    return redirect(url_for("game_over"))

            # if player word wins
            elif llm_response == player_word:

                # add correct amount of ink
                if session['stage'] < 10:
                    session['ink_history'] = f"You gained {lvl1_ink_reward} ink (base: {lvl1_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl1_ink_reward
                elif 10 <= session['stage'] < 20:
                    session['ink_history'] = f"You gained {lvl2_ink_reward} ink (base: {lvl2_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl2_ink_reward
                elif 20 <= session['stage'] < 30:
                    session['ink_history'] = f"You gained {lvl3_ink_reward} ink (base: {lvl3_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl3_ink_reward
                elif 30 <= session['stage'] < 40:
                    session['ink_history'] = f"You gained {lvl4_ink_reward} ink (base: {lvl4_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl4_ink_reward
                elif 40 <= session['stage'] < 50:
                    session['ink_history'] = f"You gained {lvl5_ink_reward} ink (base: {lvl5_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl5_ink_reward
                elif 50 <= session['stage'] < 60:
                    session['ink_history'] = f"You gained {lvl6_ink_reward} ink (base: {lvl6_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl6_ink_reward
                elif 60 <= session['stage'] < 70:
                    session['ink_history'] = f"You gained {lvl7_ink_reward} ink (base: {lvl7_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl7_ink_reward
                elif 70 <= session['stage'] < 80:
                    session['ink_history'] = f"You gained {lvl8_ink_reward} ink (base: {lvl8_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl8_ink_reward
                elif 80 <= session['stage'] < 90:
                    session['ink_history'] = f"You gained {lvl9_ink_reward} ink (base: {lvl9_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl9_ink_reward
                elif 90 <= session['stage'] < 100:
                    session['ink_history'] = f"You gained {lvl10_ink_reward} ink (base: {lvl10_base_ink} + interest: {int(0.1 * session['ink'])})"
                    session['ink'] += lvl10_ink_reward

                # add 1 to stage counter
                session['stage'] += 1

                if session['lifesteal'] == True:
                    heal = lifesteal_check()
                    session['hp'] += heal
                    session['ability_message'] = f"Lifesteal healed for {heal} hp."

            else:
                error_message = f"ERROR: Please report. LLM returned {llm_response} instead of the winning word. Please proceed with a different word."
                print(f"ERROR: llm_response not player_word or npc_word. llm_response: {llm_response}")
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )

            # if it passes checks
            # remove the letters from hand
            for letter in player_word_list:
                session['hand'].remove(letter)

            session['word_number'] += 1
            print(f"TEST TEST: After word played, passed all checks, word_number: {session['word_number']}")
            print(f"TEST TEST: After word played, passed all checks, session['word_number']: {session['word_number']}")


            # if stage is over 9 or something, go to rewards screen
            if session['stage'] == 10 or session['stage'] == 20 or session['stage'] == 30 or session['stage'] == 40 or session['stage'] == 50 or session['stage'] == 60 or session['stage'] == 70 or session['stage'] == 80 or session['stage'] == 90:

                # if no upgrades left available, just render it with only the 50 ink option
                if len(session['list_of_upgrades']) <= 0:
                    return render_template('rewards.html')

                # will get us 3 upgrades unless there aren't that many left to grab
                number_of_upgrades_shown = number_of_upgrades()

                # an empty list to store the descriptions of the upgrades we pull
                rewards_descriptions = []

                # pulling X amount of random upgrades from the list of upgrades
                session['chosen_rewards'] = generate_upgrades(number_of_upgrades_shown)
                chosen_rewards = session['chosen_rewards']

                # adding the descriptions of the chosen_rewards to the rewards_descriptions list
                for i, reward_description in enumerate(range(number_of_upgrades_shown)):
                    reward_choice_number = (i + 1) - 1
                    the_reward = chosen_rewards[reward_choice_number]
                    reward_description = the_reward['description']
                    rewards_descriptions.append(reward_description)

                # assigning each reward description to it's' own variable. (add 2 None's first incase less than 3 avaialable)
                reward1_text, reward2_text, reward3_text = (rewards_descriptions + [None, None])[:3]

                return render_template('rewards.html',
                                       reward1=reward1_text,
                                       reward2=reward2_text,
                                       reward3=reward3_text
                                       )

            # generate a new word for npc
            session['npc_word_history'] = session['npc_word']

            if session['stage'] < 10:
                current_level = 1
                session['npc_word'] = pick_npc_word(session['lvl1_words'])
                session['lvl1_words'].remove(session['npc_word'])
            elif 10 <= session['stage'] < 20:
                current_level = 2
                session['npc_word'] = pick_npc_word(session['lvl2_words'])
                session['lvl2_words'].remove(session['npc_word'])
            elif 20 <= session['stage'] < 30:
                current_level = 3
                session['npc_word'] = pick_npc_word(session['lvl3_words'])
                session['lvl3_words'].remove(session['npc_word'])
            elif 30 <= session['stage'] < 40:
                current_level = 4
                session['npc_word'] = pick_npc_word(session['lvl4_words'])
                session['lvl4_words'].remove(session['npc_word'])
            elif 40 <= session['stage'] < 50:
                current_level = 5
                session['npc_word'] = pick_npc_word(session['lvl5_words'])
                session['lvl5_words'].remove(session['npc_word'])
            elif 50 <= session['stage'] < 60:
                current_level = 6
                session['npc_word'] = pick_npc_word(session['lvl6_words'])
                session['lvl6_words'].remove(session['npc_word'])
            elif 60 <= session['stage'] < 70:
                current_level = 7
                session['npc_word'] = pick_npc_word(session['lvl7_words'])
                session['lvl7_words'].remove(session['npc_word'])
            elif 70 <= session['stage'] < 80:
                current_level = 8
                session['npc_word'] = pick_npc_word(session['lvl8_words'])
                session['lvl8_words'].remove(session['npc_word'])
            elif 80 <= session['stage'] < 90:
                current_level = 9
                session['npc_word'] = pick_npc_word(session['lvl9_words'])
                session['lvl9_words'].remove(session['npc_word'])
            elif 90 <= session['stage'] < 100:
                current_level = 10
                session['npc_word'] = pick_npc_word(session['lvl10_words'])
                session['lvl10_words'].remove(session['npc_word'])



            # replace letters for player hand
            len_hand = len(session['hand'])
            print(f"This is len_hand after player word: {len_hand}")
            draw_amount = session['hand_size'] - len_hand
            letter_drawn_list = draw_letters(draw_amount)
            for letter in letter_drawn_list:
                session['hand'].append(letter)
            session['hand'] = sort_hand(session['hand'])

            print(f"This is len_hand after drawing: {len_hand}")

            print(f"TEST: This is hand right before rendering template at end: {session['hand']}")


    ### ----------------------- REWARDS SECTION - INITIALIZE THE LEVEL(STAGE) AND ADDING REWARD BUFFS -------------- ###

    if request.method == "POST":
        if "reward_choice" in request.form:

            chosen_rewards = session['chosen_rewards']

            # add reward chosen
            chosen_reward_form = request.form.get('reward')

            if chosen_reward_form == "3":  # if reward chosen was gain 50 ink
                session['ink'] += 50
            else:
                chosen_reward_number = int(chosen_reward_form)
                chosen_reward = chosen_rewards[chosen_reward_number]

                if chosen_reward['upgrade'] == 'redraw':
                    session['redraw'] = True

                if chosen_reward['upgrade'] == 'summon_letter':
                    session['summon_letter'] = True

                if chosen_reward['upgrade'] == 'skip_word':
                    session['skip_word'] = True

                if chosen_reward['upgrade'] == 'increase_hp':
                    session['increase_hp'] = True

                if chosen_reward['upgrade'] == 'increase_hand_size':
                    session['increase_hand_size'] = True

                if chosen_reward['upgrade'] == 'lifesteal':
                    session['lifesteal'] = True

                # remove the chosen reward so it doesn't show up again
                session['list_of_upgrades'].remove(chosen_reward)

            # initialize the next stage

            # redraw hand
            session['hand'] = []
            session['hand'] = draw_letters(session['hand_size'])
            session['hand'] = sort_hand(session['hand'])

            if session['stage'] == 10:
                current_level = 2
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl2_words'])
                session['lvl2_words'].remove(session['npc_word'])
            elif session['stage'] == 20:
                current_level = 3
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl3_words'])
                session['lvl3_words'].remove(session['npc_word'])
            elif session['stage'] == 30:
                current_level = 4
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl4_words'])
                session['lvl4_words'].remove(session['npc_word'])
            elif session['stage'] == 40:
                current_level = 5
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl5_words'])
                session['lvl5_words'].remove(session['npc_word'])
            elif session['stage'] == 50:
                current_level = 6
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl6_words'])
                session['lvl6_words'].remove(session['npc_word'])
            elif session['stage'] == 60:
                current_level = 7
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl7_words'])
                session['lvl7_words'].remove(session['npc_word'])
            elif session['stage'] == 70:
                current_level = 8
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl8_words'])
                session['lvl8_words'].remove(session['npc_word'])
            elif session['stage'] == 80:
                current_level = 9
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl9_words'])
                session['lvl9_words'].remove(session['npc_word'])
            elif session['stage'] == 90:
                current_level = 10
                session['word_number'] = 1
                session['npc_word'] = pick_npc_word(session['lvl10_words'])
                session['lvl10_words'].remove(session['npc_word'])


    ### ----------------------- BUTTON ABILITIES SECTION - CODE FOR MAKING BUTTON ABILITIES WORK -------------- ###

    if request.method == "POST":
        if "redraw" in request.form:

            if session['ink'] < 10:
                error_message = "Error: Not enough ink to cast redraw."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )
            else:
                session['ink'] -= 10
                session['hand'] = []
                session['hand'] = draw_letters(session['hand_size'])
                session['hand'] = sort_hand(session['hand'])
                session['ability_message'] = "Spent 10 ink to redraw hand."

            return render_template('game.html',
                                   npc_word=session['npc_word'],
                                   hand=session['hand'],
                                   hp=session['hp'],
                                   player_word_history=session['player_word_history'],
                                   npc_word_history=session['npc_word_history'],
                                   llm_response_history=session['llm_response_history'],
                                   player_damage_history=session['player_damage_history'],
                                   current_level=session['current_level'],
                                   redraw=session['redraw'],
                                   summon_letter=session['summon_letter'],
                                   skip_word=session['skip_word'],
                                   increase_hp=session['increase_hp'],
                                   increase_hand_size=session['increase_hand_size'],
                                   lifesteal=session['lifesteal'],
                                   ability_message=session['ability_message'],
                                   ink=session['ink'],
                                   ink_history=session['ink_history'],
                                   word_number=session['word_number'],
                                   )

    if request.method == "POST":
        if "summon_letter" in request.form:

            if session['ink'] < 15:
                error_message = "Error: Not enough ink to cast summon letter."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )
            else:
                letter_requested = request.form.get('letter_to_summon').lower()
                if letter_requested not in alphabet:
                    error_message = "Error: Must select letter of English alphabet."
                    return render_template('game.html',
                                           error_message=error_message,
                                           npc_word=session['npc_word'],
                                           hand=session['hand'],
                                           hp=session['hp'],
                                           player_word_history=session['player_word_history'],
                                           npc_word_history=session['npc_word_history'],
                                           llm_response_history=session['llm_response_history'],
                                           player_damage_history=session['player_damage_history'],
                                           current_level=session['current_level'],
                                           redraw=session['redraw'],
                                           summon_letter=session['summon_letter'],
                                           skip_word=session['skip_word'],
                                           increase_hp=session['increase_hp'],
                                           increase_hand_size=session['increase_hand_size'],
                                           lifesteal=session['lifesteal'],
                                           ability_message=session['ability_message'],
                                           ink=session['ink'],
                                           ink_history=session['ink_history'],
                                           word_number=session['word_number'],
                                           )
                else:
                    session['ink'] -= 15
                    session['hand'].append(letter_requested)
                    session['ability_message'] = f"Spent 15 ink to summon the letter {letter_requested} to hand."

            return render_template('game.html',
                                   npc_word=session['npc_word'],
                                   hand=session['hand'],
                                   hp=session['hp'],
                                   player_word_history=session['player_word_history'],
                                   npc_word_history=session['npc_word_history'],
                                   llm_response_history=session['llm_response_history'],
                                   player_damage_history=session['player_damage_history'],
                                   current_level=session['current_level'],
                                   redraw=session['redraw'],
                                   summon_letter=session['summon_letter'],
                                   skip_word=session['skip_word'],
                                   increase_hp=session['increase_hp'],
                                   increase_hand_size=session['increase_hand_size'],
                                   lifesteal=session['lifesteal'],
                                   ability_message=session['ability_message'],
                                   ink=session['ink'],
                                   ink_history=session['ink_history'],
                                   word_number=session['word_number'],
                                   )

    if request.method == "POST":
        if "skip_word" in request.form:

            if session['ink'] < 20:
                error_message = "Error: Not enough ink to cast skip word."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )
            else:
                session['ink'] -= 20

                session['stage'] += 1
                if session['stage'] < 10:
                    current_level = 1
                    session['npc_word'] = pick_npc_word(session['lvl1_words'])
                    session['lvl1_words'].remove(session['npc_word'])
                elif 10 <= session['stage'] < 20:
                    current_level = 2
                    session['npc_word'] = pick_npc_word(session['lvl2_words'])
                    session['lvl2_words'].remove(session['npc_word'])
                elif 20 <= session['stage'] < 30:
                    current_level = 3
                    session['npc_word'] = pick_npc_word(session['lvl3_words'])
                    session['lvl3_words'].remove(session['npc_word'])
                elif 30 <= session['stage'] < 40:
                    current_level = 4
                    session['npc_word'] = pick_npc_word(session['lvl4_words'])
                    session['lvl4_words'].remove(session['npc_word'])
                elif 40 <= session['stage'] < 50:
                    current_level = 5
                    session['npc_word'] = pick_npc_word(session['lvl5_words'])
                    session['lvl5_words'].remove(session['npc_word'])
                elif 50 <= session['stage'] < 60:
                    current_level = 6
                    session['npc_word'] = pick_npc_word(session['lvl6_words'])
                    session['lvl6_words'].remove(session['npc_word'])
                elif 60 <= session['stage'] < 70:
                    current_level = 7
                    session['npc_word'] = pick_npc_word(session['lvl7_words'])
                    session['lvl7_words'].remove(session['npc_word'])
                elif 70 <= session['stage'] < 80:
                    current_level = 8
                    session['npc_word'] = pick_npc_word(session['lvl8_words'])
                    session['lvl8_words'].remove(session['npc_word'])
                elif 80 <= session['stage'] < 90:
                    current_level = 9
                    session['npc_word'] = pick_npc_word(session['lvl9_words'])
                    session['lvl9_words'].remove(session['npc_word'])
                elif 90 <= session['stage'] < 100:
                    current_level = 10
                    session['npc_word'] = pick_npc_word(session['lvl10_words'])
                    session['lvl10_words'].remove(session['npc_word'])

                session['ability_message'] = "Spent 20 ink to skip word."

            return render_template('game.html',
                                   npc_word=session['npc_word'],
                                   hand=session['hand'],
                                   hp=session['hp'],
                                   player_word_history=session['player_word_history'],
                                   npc_word_history=session['npc_word_history'],
                                   llm_response_history=session['llm_response_history'],
                                   player_damage_history=session['player_damage_history'],
                                   current_level=session['current_level'],
                                   redraw=session['redraw'],
                                   summon_letter=session['summon_letter'],
                                   skip_word=session['skip_word'],
                                   increase_hp=session['increase_hp'],
                                   increase_hand_size=session['increase_hand_size'],
                                   lifesteal=session['lifesteal'],
                                   ability_message=session['ability_message'],
                                   ink=session['ink'],
                                   ink_history=session['ink_history'],
                                   word_number=session['word_number'],
                                   )


    if request.method == "POST":
        if "increase_hp" in request.form:

            if session['ink'] < 30:
                error_message = "Error: Not enough ink to cast increase hp."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )
            else:
                session['ink'] -= 30
                session['hp'] += 1
                session['ability_message'] = "Spent 30 ink to increase hp by 1."

            return render_template('game.html',
                                   npc_word=session['npc_word'],
                                   hand=session['hand'],
                                   hp=session['hp'],
                                   player_word_history=session['player_word_history'],
                                   npc_word_history=session['npc_word_history'],
                                   llm_response_history=session['llm_response_history'],
                                   player_damage_history=session['player_damage_history'],
                                   current_level=session['current_level'],
                                   redraw=session['redraw'],
                                   summon_letter=session['summon_letter'],
                                   skip_word=session['skip_word'],
                                   increase_hp=session['increase_hp'],
                                   increase_hand_size=session['increase_hand_size'],
                                   lifesteal=session['lifesteal'],
                                   ability_message=session['ability_message'],
                                   ink=session['ink'],
                                   ink_history=session['ink_history'],
                                   word_number=session['word_number'],
                                   )

    if request.method == "POST":
        if "increase_hand_size" in request.form:

            if session['ink'] < 50:
                error_message = "Error: Not enough ink to cast increase hand size."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=session['npc_word'],
                                       hand=session['hand'],
                                       hp=session['hp'],
                                       player_word_history=session['player_word_history'],
                                       npc_word_history=session['npc_word_history'],
                                       llm_response_history=session['llm_response_history'],
                                       player_damage_history=session['player_damage_history'],
                                       current_level=session['current_level'],
                                       redraw=session['redraw'],
                                       summon_letter=session['summon_letter'],
                                       skip_word=session['skip_word'],
                                       increase_hp=session['increase_hp'],
                                       increase_hand_size=session['increase_hand_size'],
                                       lifesteal=session['lifesteal'],
                                       ability_message=session['ability_message'],
                                       ink=session['ink'],
                                       ink_history=session['ink_history'],
                                       word_number=session['word_number'],
                                       )
            else:
                session['ink'] -= 50
                session['hand_size'] += 1
                session['ability_message'] = "Spent 50 ink to increase hand size by 1."

            return render_template('game.html',
                                   npc_word=session['npc_word'],
                                   hand=session['hand'],
                                   hp=session['hp'],
                                   player_word_history=session['player_word_history'],
                                   npc_word_history=session['npc_word_history'],
                                   llm_response_history=session['llm_response_history'],
                                   player_damage_history=session['player_damage_history'],
                                   current_level=session['current_level'],
                                   redraw=session['redraw'],
                                   summon_letter=session['summon_letter'],
                                   skip_word=session['skip_word'],
                                   increase_hp=session['increase_hp'],
                                   increase_hand_size=session['increase_hand_size'],
                                   lifesteal=session['lifesteal'],
                                   ability_message=session['ability_message'],
                                   ink=session['ink'],
                                   ink_history=session['ink_history'],
                                   word_number=session['word_number'],
                                   )

        #lifesteal by player win code


    # # a way to check if a variable is still undefined.
    # if 'ability_message' not in locals() and 'ability_message' not in globals():
    #     ability_message = ""
    #
    # if 'player_word_history' not in locals() and 'player_word_history' not in globals():
    #     player_word_history = ""
    #
    # if 'npc_word_history' not in locals() and 'npc_word_history' not in globals():
    #     npc_word_history = ""
    #
    # if 'llm_response_history' not in locals() and 'llm_response_history' not in globals():
    #     llm_response_history = ""
    #
    # if 'player_damage_history' not in locals() and 'player_damage_history' not in globals():
    #     player_damage_history = None
    #
    # if 'ink_history' not in locals() and 'ink_history' not in globals():
    #     session['ink_history'] = ""


    return render_template('game.html',
                           npc_word=session['npc_word'],
                           hand=session['hand'],
                           hp=session['hp'],
                           player_word_history=session['player_word_history'],
                           npc_word_history=session['npc_word_history'],
                           llm_response_history=session['llm_response_history'],
                           player_damage_history=session['player_damage_history'],
                           current_level=session['current_level'],
                           redraw=session['redraw'],
                           summon_letter=session['summon_letter'],
                           skip_word=session['skip_word'],
                           increase_hp=session['increase_hp'],
                           increase_hand_size=session['increase_hand_size'],
                           lifesteal=session['lifesteal'],
                           ability_message=session['ability_message'],
                           ink=session['ink'],
                           ink_history=session['ink_history'],
                           word_number=session['word_number'],
                           )



@app.route("/html-test", methods=["POST"])
def html_test():
    return render_template('html_test.html')


@app.route("/tips-and-tricks", methods=["POST"])
def tips_and_tricks():
    return render_template('html_test.html')


@app.route("/game-over", methods=["GET", "POST"])
def game_over():
    return render_template('game_over.html')

@app.route("/you-win", methods=["POST"])
def you_win():
    return render_template('you_win.html')


if __name__ == "__main__":
    app.run()