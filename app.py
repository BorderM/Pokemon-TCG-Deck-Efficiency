from flask import Flask, render_template, request

from deck_efficiency.analyzer import analyze_deck

app = Flask(__name__)

SAMPLE_DECK = """4 Charmander
2 Charmeleon
3 Charizard ex
4 Buddy-Buddy Poffin
4 Nest Ball
4 Ultra Ball
3 Rare Candy
4 Iono
3 Professor's Research
2 Boss's Orders
2 Switch
2 Super Rod
12 Fire Energy
""".strip()


@app.route('/', methods=['GET', 'POST'])
def index():
    deck_text = request.form.get('decklist', SAMPLE_DECK if request.method == 'GET' else '')
    analysis = analyze_deck(deck_text) if deck_text.strip() else None
    return render_template('index.html', deck_text=deck_text, analysis=analysis)


if __name__ == '__main__':
    app.run(debug=True)
