from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/arcade')
def arcade():
    return render_template('arcade.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

if __name__ == '__main__':
    app.run(debug=True)
