from flask import Flask, render_template, request, redirect, url_for
from game_logic import Game

app = Flask(__name__)
game = Game()

@app.route("/")
def index():
    if game.is_game_over():
        winner = game.get_winner()
        return render_template("game.html", game_over=True, winner=winner)

    player = game.players[0]
    bot = game.players[1]
    return render_template("game.html",
                           player_hand=player.hand,
                           top_card=game.discard_pile[-1],
                           bot_card_count=len(bot.hand),
                           message=game.message,
                           game_over=False)

@app.route("/play/<int:card_index>", methods=["POST"])
def play(card_index):
    # Zabrání hráči hrát mimo svůj tahbnbnbn
    if game.current_player_idx != 0:
        game.message = "It's not your turn!"
        return redirect(url_for("index"))

    color = request.form.get("color")
    game.play_player_card(card_index, chosen_color=color)

    # Po hráčově tahu přechází hra automaticky na bota (pokud nebyl přeskočen)
    if game.current_player_idx == 1 and not game.is_game_over():
        game.play_computer_turn()

    return redirect(url_for("index"))

@app.route("/draw", methods=["POST"])
def draw():
    # Zabrání hráči táhnout mimo svůj tah
    if game.current_player_idx != 0:
        game.message = "It's not your turn!"
        return redirect(url_for("index"))

    player = game.players[0]
    player.draw(game.deck)
    game.message = "You drew a card."
    game.next_player()

    # Po tahu hráče (tahání) hraje bot
    if not game.is_game_over():
        game.play_computer_turn()

    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    global game
    game = Game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5002, debug=True)