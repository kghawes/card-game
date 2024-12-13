import random

# Constants
MAX_NAME_LENGTH = 12
STARTING_HEALTH = 10
STARTING_STAMINA = 3

M_SPLASH = "Welcome to the game!"
M_NAME_PROMPT = "What is your character’s name? "
M_VICTORY = "You beat the game!"
M_DEFEAT = "Game over!"
M_TEXT_DIVIDER = "------------------------------------------------------------"
M_TURN_INFO = "{}\nEnemy {} | Health:{}/{}\n{} Cards in Deck | {} Cards in Discard\n{}\n{} | Health:{}/{} | Stamina:{}/{}\n{} Cards in Deck | {} Cards in Discard\nCards in Hand:"
M_CARD_IN_HAND = "{}. {} (Cost: {})\n     Deal {} Damage."
M_TURN_OPTIONS_PROMPT = "Enter the number of the Card you want to Play or type PASS to end your Turn: "
M_NOT_ENOUGH_STAMINA = "You’re too fatigued to do that!"
M_CARD_PLAYED = "{} attacked with {}! {} has {} health left!"
M_ENEMY_PASSES = "{} passes their turn."
INPUT_PASS_TURN = "PASS"

# Card Class
class Card:
    def __init__(self, name, damage, cost):
        self.name = name
        self.damage = damage
        self.cost = cost

# CardManager Class
class CardManager:
    def __init__(self, starting_deck):
        self.deck = starting_deck[:]
        self.hand = []
        self.discard_pile = []

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        cards_to_draw = 6
        while cards_to_draw > 0:
            if len(self.deck) == 0:
                self.deck = self.discard_pile[:]
                self.discard_pile = []
                self.shuffle()
            if not self.deck:
                break
            self.hand.append(self.deck.pop(0))
            cards_to_draw -= 1

    def discard(self, card):
        self.discard_pile.append(card)
        self.hand.remove(card)

    def discard_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand = []

# Combatant Class
class Combatant:
    def __init__(self, name, max_health, max_stamina, starting_deck):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.card_manager = CardManager(starting_deck)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def spend_stamina(self, amount):
        self.stamina -= amount

    def replenish_stamina(self):
        self.stamina = self.max_stamina

# Player Class
class Player(Combatant):
    def __init__(self, name, starting_deck):
        super().__init__(name, STARTING_HEALTH, STARTING_STAMINA, starting_deck)
        self.gold = 0
    
    def gain_gold(self, amount):
        self.gold += amount

# Enemy Class
class Enemy(Combatant):
    def __init__(self, name, max_health, max_stamina, starting_deck, loot):
        super().__init__(name, max_health, max_stamina, starting_deck)
        self.loot = loot

# Treasure Class
class Treasure:
    def __init__(self, gold):
        self.gold = gold

# Quest and Encounter Classes
class Encounter:
    def __init__(self, enemy):
        self.enemy = enemy

class Quest:
    def __init__(self, description, encounter):
        self.description = description
        self.encounter = encounter

# TextInterface Class
class TextInterface:
    def send_message(self, message):
        print(message)

    def name_prompt(self):
        response = ""
        while not response or len(response) > MAX_NAME_LENGTH:
            response = input(M_NAME_PROMPT)
        return response

    def display_turn_info(self, enemy, player):
        print(M_TURN_INFO.format(
            M_TEXT_DIVIDER,
            enemy.name, enemy.health, enemy.max_health,
            len(enemy.card_manager.deck), len(enemy.card_manager.discard_pile),
            M_TEXT_DIVIDER,
            player.name, player.health, player.max_health,
            player.stamina, player.max_stamina,
            len(player.card_manager.deck), len(player.card_manager.discard_pile)
        ))
        for idx, card in enumerate(player.card_manager.hand):
            print(M_CARD_IN_HAND.format(idx, card.name, card.cost, card.damage))
        print(M_TEXT_DIVIDER)

    def turn_options_prompt(self):
        while True:
            response = input(M_TURN_OPTIONS_PROMPT).strip()
            if response.isdigit():
                return int(response)
            elif response.upper() == INPUT_PASS_TURN:
                return -1

# CombatManager Class
class CombatManager:
    def is_combat_over(self, player, enemy):
        return player.health <= 0 or enemy.health <= 0

    def do_combat(self, player, enemy, text_interface):
        while True:
            self.do_player_turn(player, enemy, text_interface)
            if self.is_combat_over(player, enemy):
                break
            self.do_enemy_turn(player, enemy, text_interface)
            if self.is_combat_over(player, enemy):
                break
        return player.health > 0

    def do_player_turn(self, player, enemy, text_interface):
        self.beginning_of_turn(player)
        text_interface.display_turn_info(enemy, player)
        turn_ended = False
        while not turn_ended:
            turn_ended = self.do_player_action(player, enemy, text_interface)
        player.card_manager.discard_hand()

    def beginning_of_turn(self, combatant):
        combatant.card_manager.shuffle()
        combatant.card_manager.draw()
        combatant.replenish_stamina()

    def do_player_action(self, player, enemy, text_interface):
        selection = text_interface.turn_options_prompt()
        if selection < 0:
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        if card.cost > player.stamina:
            text_interface.send_message(M_NOT_ENOUGH_STAMINA)
            return False
        if self.play_card(player, enemy, card, text_interface):
            return True
        text_interface.display_turn_info(enemy, player)
        return False

    def play_card(self, combatant, opponent, card, text_interface):
        combatant.card_manager.discard(card)
        combatant.spend_stamina(card.cost)
        opponent.take_damage(card.damage)
        text_interface.send_message(M_CARD_PLAYED.format(
            combatant.name, card.name, opponent.name, opponent.health
        ))
        return opponent.health <= 0

    def do_enemy_turn(self, player, enemy, text_interface):
        self.beginning_of_turn(enemy)
        playable_card_exists = True
        while playable_card_exists:
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.stamina:
                    playable_card_exists = True
                    if self.play_card(enemy, player, card, text_interface):
                        return
                    break
        text_interface.send_message(M_ENEMY_PASSES.format(enemy.name))
        enemy.card_manager.discard_hand()

# Game Loop
def game_loop():
    player = Player("", STARTING_DECK)
    enemy = Enemy("Cliff Racer", 9, 4, E_CLIFFRACER_DECK, Treasure(2))
    quest = Quest("Embarking on a test quest.", Encounter(enemy))
    text_interface = TextInterface()
    combat_manager = CombatManager()

    text_interface.send_message(M_SPLASH)
    player.name = text_interface.name_prompt()
    text_interface.send_message(quest.description)
    text_interface.send_message(quest.encounter.enemy.name + " appeared! Entering combat!")

    if combat_manager.do_combat(player, enemy, text_interface):
        text_interface.send_message(M_VICTORY)
        player.gain_gold(quest.encounter.enemy.loot.gold)
    else:
        text_interface.send_message(M_DEFEAT)

game_loop()