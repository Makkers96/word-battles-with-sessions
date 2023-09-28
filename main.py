# pip install flask

import random

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
alphabet_weights = [9, 2, 2, 4, 12, 2, 3, 2, 9, 1, 1, 4, 2, 6, 8, 2, 1, 6, 4, 6, 4, 2, 2, 1, 2, 1]
weighted_alphabet = ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'c', 'c', 'd', 'd', 'd', 'd', 'e', 'e', 'e',
                     'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'f', 'f', 'g', 'g', 'g', 'h', 'h', 'i', 'i', 'i', 'i',
                     'i', 'i', 'i', 'i', 'i', 'j', 'k', 'l', 'l', 'l', 'l', 'm', 'm', 'n', 'n', 'n', 'n', 'n', 'n', 'o',
                     'o', 'o', 'o', 'o', 'o', 'o', 'o', 'p', 'p', 'q', 'r', 'r', 'r', 'r', 'r', 'r', 's', 's', 's', 's',
                     't', 't', 't', 't', 't', 't', 'u', 'u', 'u', 'u', 'v', 'v', 'w', 'w', 'x', 'y', 'y', 'z']

vowels = ['a', 'e', 'i', 'o', 'u']
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
special_characters = ".?!@#$%^&*()-=+[]{}|;:'\,<>?/1234567890"

lvl1_words = ['bat', 'book', 'rock', 'claws', 'scissors', 'cat', 'dog', 'wrestler', 'ice', 'melancholy', 'psychology', 'keeper']
lvl2_words = ['robot', 'unicorn', 'mystery', 'bee', 'knife', 'fire', 'earth', 'light', 'thunder', 'science', 'elf', 'mermaid']
lvl3_words = ['wizard', 'pirate', 'nina', 'samurai', 'vampire', 'werewolf', 'zombie', 'ghost', 'troll', 'witch', 'knight', 'cyclops', 'yeti', 'minotaur']
lvl4_words = ['valkyrie', 'happy', 'believe', 'harmony', 'freedom', 'america', 'eagle', 'energy', 'imagination', 'dream', 'truth', 'beauty']
lvl5_words = ['chaos', 'mystery', 'time', 'hope', 'knowledge', 'fate', 'courage', 'fear', 'justice', 'nightmare', 'villian', 'sickness']
lvl6_words = ['mafia', 'magic', 'insane', 'maniac', 'murderer', 'faith', 'truth', 'beauty', 'joy', 'grace', 'hope', 'harmony']
lvl7_words = ['indomitable', 'thunderbolt', 'explosion', 'earthquake', 'avalanche', 'justice', 'freedom', 'wisdom', 'eternal', 'transcendent', 'pinnacle', 'valkyrie']
lvl8_words = ['goliath', 'hercules', 'colossus', 'juggernaut', 'warlord', 'inferno', 'behemoth', 'leviathan', 'tsunami', 'kraken', 'gladiator']
lvl9_words = ['invincible', 'love', 'eternity', 'supreme', 'apex', 'wisdom', 'cataclysm', 'supernova', 'phoenix', 'miracle', 'destiny', 'dominant' ]
lvl10_words = ['apocalypse', 'dragon', 'titan', 'warlord', 'omnipotence', 'omniscience', 'perfection', 'champion', 'infinity', 'unbeatable', 'undefeated', 'death']

# player variables for levels
# base values
hand_size = 10
hp = 10

list_of_upgrades = [{'upgrade': 'redraw', 'description': 'Redraw your hand. Cost: 10 Ink'},
                     {'upgrade': 'summon_letter', 'description': 'Add any 1 letter to your hand. Cost: 15 Ink'},
                     {'upgrade': 'skip_word', 'description': 'Skip the word. Cost: 20 Ink'},
                     {'upgrade': 'increase_hp', 'description': 'Increase your hp by 1. Cost: 30 Ink'},
                     {'upgrade': 'increase_hand_size', 'description': 'Increase your hand size by 1. Cost: 50 Ink'},
                     {'upgrade': 'lifesteal', 'description': '10% chance to heal 1 HP if beat word. Cost: Passive'}
                     ]

def pick_npc_word(word_list):
    npc_word = random.choice(word_list)
    return npc_word


def draw_letters(number):
    list_of_letters = random.sample(weighted_alphabet, k=number)
    for letter in list_of_letters:
        weighted_alphabet.remove(letter)
    return list_of_letters


def sort_hand(hand):
    organized_hand = []
    for letter in vowels:
        if letter in hand:
            number_of_times_letter_in_hand = hand.count(letter)
            for i in range(number_of_times_letter_in_hand):
                organized_hand.append(letter)
    for letter in consonants:
        if letter in hand:
            number_of_times_letter_in_hand = hand.count(letter)
            for i in range(number_of_times_letter_in_hand):
                organized_hand.append(letter)

    return organized_hand


def generate_upgrades(number):
    return random.sample(list_of_upgrades, k=number)


def number_of_upgrades():
    number_of_upgrades_offered = 0
    if len(list_of_upgrades) < 3:
        for upgrade in list_of_upgrades:
            number_of_upgrades_offered += 1
    else:
        number_of_upgrades_offered = 3
    return number_of_upgrades_offered


def lifesteal_check():
    chance_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    heal = 0
    chance_hit = random.choice(chance_list)
    if chance_hit == 1:
        heal += 1
    else:
        pass
    return heal
