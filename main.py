from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'Hello from TLOP Media bot!'

if __name__ == '__main__':
    app.run(debug=True)