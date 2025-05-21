import random

# --- Karty ---
class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def is_playable(self, other_card):
        return (
            self.color == other_card.color or
            self.value == other_card.value or
            self.color is None
        )

    @property
    def image_filename(self):
        color = self.color.lower() if self.color else "wild"
        value = str(self.value).lower().replace("+", "plus")
        return f"{color}_{value}.png"

    def __str__(self):
        return f"{self.color} {self.value}"


class ActionCard(Card):
    def apply_effect(self, game):
        if self.value == 'Reverse':
            game.direction *= -1
        elif self.value == 'Skip':
            game.message += f" {game.players[game.next_player_index()].name} is skipped."
            game.skip_next_turn = True
        elif self.value == '+2':
            next_idx = game.next_player_index()
            game.players[next_idx].draw(game.deck, 2)
            game.message += f" {game.players[next_idx].name} draws 2 cards and is skipped."
            game.skip_next_turn = True
        return game.skip_next_turn


class WildCard(Card):
    def __init__(self, value):
        super().__init__(None, value)

    def apply_effect(self, game, chosen_color=None):
        if chosen_color in ['Red', 'Yellow', 'Green', 'Blue']:
            self.color = chosen_color
        else:
            self.color = random.choice(['Red', 'Yellow', 'Green', 'Blue'])

        game.message += f" Color chosen: {self.color}."

        if self.value == 'Wild+4':
            next_idx = game.next_player_index()
            game.players[next_idx].draw(game.deck, 4)
            game.message += f" {game.players[next_idx].name} draws 4 cards and is skipped."
            game.skip_next_turn = True
        return game.skip_next_turn


# --- Balíček ---
class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        values = list(range(0, 10)) + ['+2', 'Reverse', 'Skip']

        for color in colors:
            for value in values:
                CardClass = ActionCard if isinstance(value, str) else Card
                self.cards.append(CardClass(color, value))
                if value != 0:
                    self.cards.append(CardClass(color, value))

        for _ in range(4):
            self.cards.append(WildCard('Wild'))
            self.cards.append(WildCard('Wild+4'))

        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None


# --- Hráč ---
class Player:
    def __init__(self, name, is_computer=False):
        self.name = name
        self.hand = []
        self.is_computer = is_computer

    def draw(self, deck, num=1):
        for _ in range(num):
            card = deck.draw_card()
            if card:
                self.hand.append(card)

    def play_card(self, card, current_card):
        if card in self.hand and card.is_playable(current_card):
            self.hand.remove(card)
            return card
        return None

    def has_playable_card(self, current_card):
        return any(card.is_playable(current_card) for card in self.hand)


# --- Hra ---
class Game:
    def __init__(self):
        self.deck = Deck()
        self.players = [Player("Player"), Player("Computer", is_computer=True)]
        self.discard_pile = []
        self.current_player_idx = 0
        self.direction = 1
        self.message = ""
        self.skip_next_turn = False

        self.start_game()

    def start_game(self):
        for player in self.players:
            player.draw(self.deck, 7)

        first_card = self.deck.draw_card()
        while isinstance(first_card, WildCard):
            self.deck.cards.insert(0, first_card)
            random.shuffle(self.deck.cards)
            first_card = self.deck.draw_card()

        self.discard_pile.append(first_card)

    def next_player(self):
        self.current_player_idx = self.next_player_index()

    def next_player_index(self):
        return (self.current_player_idx + self.direction) % len(self.players)

    def play_player_card(self, card_index, chosen_color=None):
        player = self.players[0]
        if self.current_player_idx != 0:
            self.message = "It's not your turn!"
            return

        current_card = self.discard_pile[-1]

        if card_index >= len(player.hand):
            self.message = "Invalid card selection."
            return

        selected_card = player.hand[card_index]

        if not selected_card.is_playable(current_card):
            self.message = "This card is not playable."
            return

        played_card = player.play_card(selected_card, current_card)
        self.discard_pile.append(played_card)
        self.message = f"{player.name} plays {played_card}."

        self.skip_next_turn = False
        if isinstance(played_card, WildCard):
            if played_card.value == 'Wild+4' and chosen_color not in ['Red', 'Yellow', 'Green', 'Blue']:
                self.message = "Invalid color chosen."
                player.hand.insert(card_index, played_card)
                return
            played_card.apply_effect(self, chosen_color)
        elif isinstance(played_card, ActionCard):
            played_card.apply_effect(self)

        self.next_player()

        if self.skip_next_turn:
            self.skip_next_turn = False
            self.next_player()

    def play_computer_turn(self):
        while self.players[self.current_player_idx].is_computer and not self.is_game_over():
            player = self.players[self.current_player_idx]
            current_card = self.discard_pile[-1]
            playable_cards = [card for card in player.hand if card.is_playable(current_card)]

            if playable_cards:
                card_to_play = playable_cards[0]
                played_card = player.play_card(card_to_play, current_card)
                self.discard_pile.append(played_card)
                self.message = f"{player.name} plays {played_card}."

                self.skip_next_turn = False
                if isinstance(played_card, WildCard):
                    played_card.apply_effect(self)
                elif isinstance(played_card, ActionCard):
                    played_card.apply_effect(self)

                self.next_player()
                if self.skip_next_turn:
                    self.skip_next_turn = False
                    self.next_player()

            else:
                player.draw(self.deck)
                self.message = f"{player.name} has no playable cards and draws a card."
                self.next_player()

    def is_game_over(self):
        return any(len(player.hand) == 0 for player in self.players)

    def get_winner(self):
        for player in self.players:
            if len(player.hand) == 0:
                return player.name
        return None