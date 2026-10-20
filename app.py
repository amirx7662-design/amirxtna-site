from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/arcade')
def arcade():
    return render_template('arcade.html')

if __name__ == '__main__':
    app.run(debug=True)
