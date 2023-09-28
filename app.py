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
    session['ink_history'] = None
    session['ability_message'] = None
    session['player_word_history'] = None
    session['npc_word_history'] = None
    session['llm_response_history'] = None
    session['player_damage_history'] = None
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

    stage = session['stage']
    word_number = session['word_number']
    current_level = session['current_level']
    ink = session['ink']
    redraw = session['redraw']
    summon_letter = session['summon_letter']
    skip_word = session['skip_word']
    increase_hp = session['increase_hp']
    increase_hand_size = session['increase_hand_size']
    lifesteal = session['lifesteal']
    hp = session['hp']
    hand_size = session['hand_size']
    ink_history = session['ink_history']
    ability_message = session['ability_message']
    player_word_history = session['player_word_history']
    npc_word_history = session['npc_word_history']
    llm_response_history = session['llm_response_history']
    player_damage_history = session['player_damage_history']
    lvl1_words = session['lvl1_words']
    lvl2_words = session['lvl2_words']
    lvl3_words = session['lvl3_words']
    lvl4_words = session['lvl4_words']
    lvl5_words = session['lvl5_words']
    lvl6_words = session['lvl6_words']
    lvl7_words = session['lvl7_words']
    lvl8_words = session['lvl8_words']
    lvl9_words = session['lvl9_words']
    lvl10_words = session['lvl10_words']
    hand = session['hand']
    npc_word = session['npc_word']
    list_of_upgrades = session['list_of_upgrades']

    lvl1_base_ink = 2
    lvl1_ink_reward = int(lvl1_base_ink + 0.1 * ink)
    lvl2_base_ink = 3
    lvl2_ink_reward = int(lvl2_base_ink + 0.1 * ink)
    lvl3_base_ink = 4
    lvl3_ink_reward = int(lvl3_base_ink + 0.1 * ink)
    lvl4_base_ink = 5
    lvl4_ink_reward = int(lvl4_base_ink + 0.1 * ink)
    lvl5_base_ink = 6
    lvl5_ink_reward = int(lvl5_base_ink + 0.1 * ink)
    lvl6_base_ink = 7
    lvl6_ink_reward = int(lvl6_base_ink + 0.1 * ink)
    lvl7_base_ink = 8
    lvl7_ink_reward = int(lvl7_base_ink + 0.1 * ink)
    lvl8_base_ink = 9
    lvl8_ink_reward = int(lvl8_base_ink + 0.1 * ink)
    lvl9_base_ink = 10
    lvl9_ink_reward = int(lvl9_base_ink + 0.1 * ink)
    lvl10_base_ink = 11
    lvl10_ink_reward = int(lvl10_base_ink + 0.1 * ink)


    ### ------------------ MAIN GAMEPLAY LOOP - AROUND PLAY WORD BUTTON --------------------------- ###


    if stage == 100:
        return redirect(url_for('you_win'))


    if request.method == "POST":
        if "player_word" in request.form:

            session['player_damage_history'] = None
            player_damage_history = session['player_damage_history']
            session['ability_message'] = None
            ability_message = session['ability_message']

            # capture the details about entered word
            player_word = request.form.get('player_word').lower()
            player_word_list = list(player_word)

            # do checks to make sure the word is allowed to be played
            # checks for special characters
            if any(character in special_characters for character in player_word):
                error_message = "ERROR: Word must not contain any special characters."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )

            # checks for using letters in hand
            error = False
            hand_copy = hand.copy()
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
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )

            # run the llm to see who wins
            llm_response = get_winner(player_word, npc_word)
            print(f"TEST: This is players word: {player_word}")
            print(f"TEST: This is npc word: {npc_word}")
            print(f"TEST: This is llm response (winner): {llm_response}")

            # setting up variables for history
            player_word_history = player_word
            npc_word_history = npc_word
            llm_response_history = llm_response

            # if npc word wins
            if llm_response == npc_word:

                # deal 1 damage to player
                hp -= 1
                player_damage_history = 1

                #increase stage
                stage += 1

                # check if player is dead
                if hp <= 0:
                    return redirect(url_for("game_over"))

            # if player word wins
            elif llm_response == player_word:

                # add correct amount of ink
                if stage < 10:
                    ink_history = f"You gained {lvl1_ink_reward} ink (base: {lvl1_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl1_ink_reward
                elif 10 <= stage < 20:
                    ink_history = f"You gained {lvl2_ink_reward} ink (base: {lvl2_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl2_ink_reward
                elif 20 <= stage < 30:
                    ink_history = f"You gained {lvl3_ink_reward} ink (base: {lvl3_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl3_ink_reward
                elif 30 <= stage < 40:
                    ink_history = f"You gained {lvl4_ink_reward} ink (base: {lvl4_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl4_ink_reward
                elif 40 <= stage < 50:
                    ink_history = f"You gained {lvl5_ink_reward} ink (base: {lvl5_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl5_ink_reward
                elif 50 <= stage < 60:
                    ink_history = f"You gained {lvl6_ink_reward} ink (base: {lvl6_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl6_ink_reward
                elif 60 <= stage < 70:
                    ink_history = f"You gained {lvl7_ink_reward} ink (base: {lvl7_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl7_ink_reward
                elif 70 <= stage < 80:
                    ink_history = f"You gained {lvl8_ink_reward} ink (base: {lvl8_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl8_ink_reward
                elif 80 <= stage < 90:
                    ink_history = f"You gained {lvl9_ink_reward} ink (base: {lvl9_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl9_ink_reward
                elif 90 <= stage < 100:
                    ink_history = f"You gained {lvl10_ink_reward} ink (base: {lvl10_base_ink} + interest: {int(0.1 * ink)})"
                    ink += lvl10_ink_reward

                # add 1 to stage counter
                stage += 1

                if lifesteal == True:
                    heal = lifesteal_check()
                    hp += heal
                    ability_message = f"Lifesteal healed for {heal} hp."

            else:
                error_message = f"ERROR: Please report. LLM returned {llm_response} instead of the winning word. Please proceed with a different word."
                print(f"ERROR: llm_response not player_word or npc_word. llm_response: {llm_response}")
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )

            # if it passes checks
            # remove the letters from hand
            for letter in player_word_list:
                hand.remove(letter)

            word_number += 1


            # if stage is over 9 or something, go to rewards screen
            if stage == 10 or stage == 20 or stage == 30 or stage == 40 or stage == 50 or stage == 60 or stage == 70 or stage == 80 or stage == 90:

                # if no upgrades left available, just render it with only the 50 ink option
                if len(list_of_upgrades) <= 0:
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
            npc_word_history = npc_word

            if stage < 10:
                current_level = 1
                npc_word = pick_npc_word(lvl1_words)
                lvl1_words.remove(npc_word)
            elif 10 <= stage < 20:
                current_level = 2
                npc_word = pick_npc_word(lvl2_words)
                lvl2_words.remove(npc_word)
            elif 20 <= stage < 30:
                current_level = 3
                npc_word = pick_npc_word(lvl3_words)
                lvl3_words.remove(npc_word)
            elif 30 <= stage < 40:
                current_level = 4
                npc_word = pick_npc_word(lvl4_words)
                lvl4_words.remove(npc_word)
            elif 40 <= stage < 50:
                current_level = 5
                npc_word = pick_npc_word(lvl5_words)
                lvl5_words.remove(npc_word)
            elif 50 <= stage < 60:
                current_level = 6
                npc_word = pick_npc_word(lvl6_words)
                lvl6_words.remove(npc_word)
            elif 60 <= stage < 70:
                current_level = 7
                npc_word = pick_npc_word(lvl7_words)
                lvl7_words.remove(npc_word)
            elif 70 <= stage < 80:
                current_level = 8
                npc_word = pick_npc_word(lvl8_words)
                lvl8_words.remove(npc_word)
            elif 80 <= stage < 90:
                current_level = 9
                npc_word = pick_npc_word(lvl9_words)
                lvl9_words.remove(npc_word)
            elif 90 <= stage < 100:
                current_level = 10
                npc_word = pick_npc_word(lvl10_words)
                lvl10_words.remove(npc_word)



            # replace letters for player hand
            len_hand = len(hand)
            print(f"This is len_hand after player word: {len_hand}")
            draw_amount = hand_size - len_hand
            letter_drawn_list = draw_letters(draw_amount)
            for letter in letter_drawn_list:
                hand.append(letter)
            hand = sort_hand(hand)

            print(f"This is len_hand after drawing: {len_hand}")

            print(f"TEST: This is hand right before rendering template at end: {hand}")


    ### ----------------------- REWARDS SECTION - INITIALIZE THE LEVEL(STAGE) AND ADDING REWARD BUFFS -------------- ###

    if request.method == "POST":
        if "reward_choice" in request.form:

            chosen_rewards = session['chosen_rewards']

            # add reward chosen
            chosen_reward_form = request.form.get('reward')

            if chosen_reward_form == "3":  # if reward chosen was gain 50 ink
                ink += 50
            else:
                chosen_reward_number = int(chosen_reward_form)
                chosen_reward = chosen_rewards[chosen_reward_number]

                if chosen_reward['upgrade'] == 'redraw':
                    redraw = True

                if chosen_reward['upgrade'] == 'summon_letter':
                    summon_letter = True

                if chosen_reward['upgrade'] == 'skip_word':
                    skip_word = True

                if chosen_reward['upgrade'] == 'increase_hp':
                    increase_hp = True

                if chosen_reward['upgrade'] == 'increase_hand_size':
                    increase_hand_size = True

                if chosen_reward['upgrade'] == 'lifesteal':
                    lifesteal = True

                # remove the chosen reward so it doesn't show up again
                list_of_upgrades.remove(chosen_reward)

            # initialize the next stage

            # redraw hand
            hand = []
            hand = draw_letters(hand_size)
            hand = sort_hand(hand)

            if stage == 10:
                current_level = 2
                word_number = 1
                npc_word = pick_npc_word(lvl2_words)
                lvl2_words.remove(npc_word)
            elif stage == 20:
                current_level = 3
                word_number = 1
                npc_word = pick_npc_word(lvl3_words)
                lvl3_words.remove(npc_word)
            elif stage == 30:
                current_level = 4
                word_number = 1
                npc_word = pick_npc_word(lvl4_words)
                lvl4_words.remove(npc_word)
            elif stage == 40:
                current_level = 5
                word_number = 1
                npc_word = pick_npc_word(lvl5_words)
                lvl5_words.remove(npc_word)
            elif stage == 50:
                current_level = 6
                word_number = 1
                npc_word = pick_npc_word(lvl6_words)
                lvl6_words.remove(npc_word)
            elif stage == 60:
                current_level = 7
                word_number = 1
                npc_word = pick_npc_word(lvl7_words)
                lvl7_words.remove(npc_word)
            elif stage == 70:
                current_level = 8
                word_number = 1
                npc_word = pick_npc_word(lvl8_words)
                lvl8_words.remove(npc_word)
            elif stage == 80:
                current_level = 9
                word_number = 1
                npc_word = pick_npc_word(lvl9_words)
                lvl9_words.remove(npc_word)
            elif stage == 90:
                current_level = 10
                word_number = 1
                npc_word = pick_npc_word(lvl10_words)
                lvl10_words.remove(npc_word)


    ### ----------------------- BUTTON ABILITIES SECTION - CODE FOR MAKING BUTTON ABILITIES WORK -------------- ###

    if request.method == "POST":
        if "redraw" in request.form:

            if ink < 10:
                error_message = "Error: Not enough ink to cast redraw."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )
            else:
                ink -= 10
                hand = []
                hand = draw_letters(hand_size)
                hand = sort_hand(hand)
                ability_message = "Spent 10 ink to redraw hand."

            return render_template('game.html',
                                   npc_word=npc_word,
                                   hand=hand,
                                   hp=hp,
                                   player_word_history=player_word_history,
                                   npc_word_history=npc_word_history,
                                   llm_response_history=llm_response_history,
                                   player_damage_history=player_damage_history,
                                   current_level=current_level,
                                   redraw=redraw,
                                   summon_letter=summon_letter,
                                   skip_word=skip_word,
                                   increase_hp=increase_hp,
                                   increase_hand_size=increase_hand_size,
                                   lifesteal=lifesteal,
                                   ability_message=ability_message,
                                   ink=ink,
                                   ink_history=ink_history,
                                   word_number=word_number,
                                   )

    if request.method == "POST":
        if "summon_letter" in request.form:

            if ink < 15:
                error_message = "Error: Not enough ink to cast summon letter."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )
            else:
                letter_requested = request.form.get('letter_to_summon').lower()
                if letter_requested not in alphabet:
                    error_message = "Error: Must select letter of English alphabet."
                    return render_template('game.html',
                                           error_message=error_message,
                                           npc_word=npc_word,
                                           hand=hand,
                                           hp=hp,
                                           player_word_history=player_word_history,
                                           npc_word_history=npc_word_history,
                                           llm_response_history=llm_response_history,
                                           player_damage_history=player_damage_history,
                                           current_level=current_level,
                                           redraw=redraw,
                                           summon_letter=summon_letter,
                                           skip_word=skip_word,
                                           increase_hp=increase_hp,
                                           increase_hand_size=increase_hand_size,
                                           lifesteal=lifesteal,
                                           ability_message=ability_message,
                                           ink=ink,
                                           ink_history=ink_history,
                                           word_number=word_number,
                                           )
                else:
                    ink -= 15
                    hand.append(letter_requested)
                    ability_message = f"Spent 15 ink to summon the letter {letter_requested} to hand."

            return render_template('game.html',
                                   npc_word=npc_word,
                                   hand=hand,
                                   hp=hp,
                                   player_word_history=player_word_history,
                                   npc_word_history=npc_word_history,
                                   llm_response_history=llm_response_history,
                                   player_damage_history=player_damage_history,
                                   current_level=current_level,
                                   redraw=redraw,
                                   summon_letter=summon_letter,
                                   skip_word=skip_word,
                                   increase_hp=increase_hp,
                                   increase_hand_size=increase_hand_size,
                                   lifesteal=lifesteal,
                                   ability_message=ability_message,
                                   ink=ink,
                                   ink_history=ink_history,
                                   word_number=word_number,
                                   )

    if request.method == "POST":
        if "skip_word" in request.form:

            if ink < 20:
                error_message = "Error: Not enough ink to cast skip word."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )
            else:
                ink -= 20

                stage += 1
                if stage < 10:
                    current_level = 1
                    npc_word = pick_npc_word(lvl1_words)
                    lvl1_words.remove(npc_word)
                elif 10 <= stage < 20:
                    current_level = 2
                    npc_word = pick_npc_word(lvl2_words)
                    lvl2_words.remove(npc_word)
                elif 20 <= stage < 30:
                    current_level = 3
                    npc_word = pick_npc_word(lvl3_words)
                    lvl3_words.remove(npc_word)
                elif 30 <= stage < 40:
                    current_level = 4
                    npc_word = pick_npc_word(lvl4_words)
                    lvl4_words.remove(npc_word)
                elif 40 <= stage < 50:
                    current_level = 5
                    npc_word = pick_npc_word(lvl5_words)
                    lvl5_words.remove(npc_word)
                elif 50 <= stage < 60:
                    current_level = 6
                    npc_word = pick_npc_word(lvl6_words)
                    lvl6_words.remove(npc_word)
                elif 60 <= stage < 70:
                    current_level = 7
                    npc_word = pick_npc_word(lvl7_words)
                    lvl7_words.remove(npc_word)
                elif 70 <= stage < 80:
                    current_level = 8
                    npc_word = pick_npc_word(lvl8_words)
                    lvl8_words.remove(npc_word)
                elif 80 <= stage < 90:
                    current_level = 9
                    npc_word = pick_npc_word(lvl9_words)
                    lvl9_words.remove(npc_word)
                elif 90 <= stage < 100:
                    current_level = 10
                    npc_word = pick_npc_word(lvl10_words)
                    lvl10_words.remove(npc_word)

                ability_message = "Spent 20 ink to skip word."

            return render_template('game.html',
                                   npc_word=npc_word,
                                   hand=hand,
                                   hp=hp,
                                   player_word_history=player_word_history,
                                   npc_word_history=npc_word_history,
                                   llm_response_history=llm_response_history,
                                   player_damage_history=player_damage_history,
                                   current_level=current_level,
                                   redraw=redraw,
                                   summon_letter=summon_letter,
                                   skip_word=skip_word,
                                   increase_hp=increase_hp,
                                   increase_hand_size=increase_hand_size,
                                   lifesteal=lifesteal,
                                   ability_message=ability_message,
                                   ink=ink,
                                   ink_history=ink_history,
                                   word_number=word_number,
                                   )


    if request.method == "POST":
        if "increase_hp" in request.form:

            if ink < 30:
                error_message = "Error: Not enough ink to cast increase hp."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )
            else:
                ink -= 30
                hp += 1
                ability_message = "Spent 30 ink to increase hp by 1."

            return render_template('game.html',
                                   npc_word=npc_word,
                                   hand=hand,
                                   hp=hp,
                                   player_word_history=player_word_history,
                                   npc_word_history=npc_word_history,
                                   llm_response_history=llm_response_history,
                                   player_damage_history=player_damage_history,
                                   current_level=current_level,
                                   redraw=redraw,
                                   summon_letter=summon_letter,
                                   skip_word=skip_word,
                                   increase_hp=increase_hp,
                                   increase_hand_size=increase_hand_size,
                                   lifesteal=lifesteal,
                                   ability_message=ability_message,
                                   ink=ink,
                                   ink_history=ink_history,
                                   word_number=word_number,
                                   )

    if request.method == "POST":
        if "increase_hand_size" in request.form:

            if ink < 50:
                error_message = "Error: Not enough ink to cast increase hand size."
                return render_template('game.html',
                                       error_message=error_message,
                                       npc_word=npc_word,
                                       hand=hand,
                                       hp=hp,
                                       player_word_history=player_word_history,
                                       npc_word_history=npc_word_history,
                                       llm_response_history=llm_response_history,
                                       player_damage_history=player_damage_history,
                                       current_level=current_level,
                                       redraw=redraw,
                                       summon_letter=summon_letter,
                                       skip_word=skip_word,
                                       increase_hp=increase_hp,
                                       increase_hand_size=increase_hand_size,
                                       lifesteal=lifesteal,
                                       ability_message=ability_message,
                                       ink=ink,
                                       ink_history=ink_history,
                                       word_number=word_number,
                                       )
            else:
                ink -= 50
                hand_size += 1
                ability_message = "Spent 50 ink to increase hand size by 1."

            return render_template('game.html',
                                   npc_word=npc_word,
                                   hand=hand,
                                   hp=hp,
                                   player_word_history=player_word_history,
                                   npc_word_history=npc_word_history,
                                   llm_response_history=llm_response_history,
                                   player_damage_history=player_damage_history,
                                   current_level=current_level,
                                   redraw=redraw,
                                   summon_letter=summon_letter,
                                   skip_word=skip_word,
                                   increase_hp=increase_hp,
                                   increase_hand_size=increase_hand_size,
                                   lifesteal=lifesteal,
                                   ability_message=ability_message,
                                   ink=ink,
                                   ink_history=ink_history,
                                   word_number=word_number,
                                   )

        #lifesteal by player win code


    # a way to check if a variable is still undefined.
    if 'ability_message' not in locals() and 'ability_message' not in globals():
        ability_message = ""

    if 'player_word_history' not in locals() and 'player_word_history' not in globals():
        player_word_history = ""

    if 'npc_word_history' not in locals() and 'npc_word_history' not in globals():
        npc_word_history = ""

    if 'llm_response_history' not in locals() and 'llm_response_history' not in globals():
        llm_response_history = ""

    if 'player_damage_history' not in locals() and 'player_damage_history' not in globals():
        player_damage_history = None

    if 'ink_history' not in locals() and 'ink_history' not in globals():
        ink_history = ""


    return render_template('game.html',
                           npc_word=npc_word,
                           hand=hand,
                           hp=hp,
                           player_word_history=player_word_history,
                           npc_word_history=npc_word_history,
                           llm_response_history=llm_response_history,
                           player_damage_history=player_damage_history,
                           current_level=current_level,
                           redraw=redraw,
                           summon_letter=summon_letter,
                           skip_word=skip_word,
                           increase_hp=increase_hp,
                           increase_hand_size=increase_hand_size,
                           lifesteal=lifesteal,
                           ability_message=ability_message,
                           ink=ink,
                           ink_history=ink_history,
                           word_number=word_number,
                           )



@app.route("/html-test", methods=["POST"])
def html_test():
    return render_template('html_test.html')


@app.route("/tips-and-tricks", methods=["POST"])
def tips_and_tricks():
    return render_template('html_test.html')


@app.route("/game-over", methods=["POST"])
def game_over():
    return render_template('game_over.html')

@app.route("/you-win", methods=["POST"])
def you_win():
    return render_template('you_win.html')


if __name__ == "__main__":
    app.run()