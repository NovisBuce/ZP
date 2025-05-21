from flask import Flask, render_template, request, jsonify
import os
import random

app = Flask(__name__)

CARDS_PATH = "static/cardsBJ"  # cesta pro načítání obrázků

class Hrac:
    def __init__(self):
        self.karty = []
        self.penize = 1000
        self.sazka = 0

    def pridej_kartu(self, karta):
        self.karty.append(karta)

    def vypocitej_hodnotu(self):
        hodnota = 0
        esa = 0
        for karta in self.karty:
            rank = karta.split("_")[0]
            if rank in ["jack", "queen", "king"]:
                hodnota += 10
            elif rank == "ace":
                hodnota += 11
                esa += 1
            else:
                hodnota += int(rank)
        while hodnota > 21 and esa:
            hodnota -= 10
            esa -= 1
        return hodnota

    def reset(self):
        self.karty = []
        self.sazka = 0


class Hra:
    def __init__(self):
        self.hrac = Hrac()
        self.dealer = Hrac()
        self.konec = False
        self.tah_hrace = True

    def rozdej_kartu(self, komu):
        karta = random.choice(os.listdir(CARDS_PATH))
        komu.pridej_kartu(karta)

    def nova_hra(self, sazka):
        self.hrac.reset()
        self.dealer.reset()
        self.hrac.sazka = sazka
        self.hrac.penize -= sazka
        self.konec = False
        self.tah_hrace = True
        self.rozdej_kartu(self.hrac)
        self.rozdej_kartu(self.hrac)
        self.rozdej_kartu(self.dealer)
        self.rozdej_kartu(self.dealer)

    def hit(self):
        if self.tah_hrace and self.hrac.vypocitej_hodnotu() <= 21:
            self.rozdej_kartu(self.hrac)
            if self.hrac.vypocitej_hodnotu() > 21:
                self.konec = True
                self.tah_hrace = False

    def stand(self):
        self.tah_hrace = False
        while self.dealer.vypocitej_hodnotu() < 17:
            self.rozdej_kartu(self.dealer)
        self.konec = True
        self.vyhodnot()

    def vyhodnot(self):
        skore_hrace = self.hrac.vypocitej_hodnotu()
        skore_dealera = self.dealer.vypocitej_hodnotu()
        if skore_hrace > 21:
            return "Prohrál jsi!"
        elif skore_dealera > 21:
            self.hrac.penize += self.hrac.sazka 
            return "Vyhrál jsi!"
        elif skore_hrace > skore_dealera:
            self.hrac.penize += self.hrac.sazka 
            return "Vyhrál jsi!"
        elif skore_hrace < skore_dealera:
            return "Prohrál jsi!"
        else:
            self.hrac.penize += self.hrac.sazka
            return "Remíza!"


hra = Hra()

@app.route('/')
def index():
    return render_template("index.html", player_money=hra.hrac.penize, player_bet=hra.hrac.sazka)

@app.route('/start_game', methods=['POST'])
def start_game():
    sazka = int(request.form.get("bet", 10))
    hra.nova_hra(sazka)
    return jsonify({
        "player_money": hra.hrac.penize,
        "player_bet": hra.hrac.sazka,
        "player_cards": hra.hrac.karty,
        "dealer_cards": hra.dealer.karty[:1]
    })

@app.route('/hit', methods=['POST'])
def hit():
    hra.hit()
    return jsonify({
        "player_cards": hra.hrac.karty,
        "game_over": hra.konec
    })

@app.route('/stand', methods=['POST'])
def stand():
    hra.stand()
    return jsonify({
        "player_cards": hra.hrac.karty,
        "dealer_cards": hra.dealer.karty,
        "game_result": hra.vyhodnot(),
        "player_money": hra.hrac.penize
    })

@app.route('/reset_game', methods=['POST'])
def reset_game():
    hra.hrac.reset()
    hra.dealer.reset()
    return jsonify({
        "player_money": hra.hrac.penize,
        "player_bet": hra.hrac.sazka
    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)
