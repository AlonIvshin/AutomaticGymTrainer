from flask import Flask, render_template,redirect,request
from est import my_est


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/my-link/',methods = ['GET','POST'])
def mylink():
    temp = request.form['test']
    #temp2 = request.form['test2']
    my_est()
    return temp+' Estimation process has ended'


if __name__ == '__main__':
    app.run(debug=True)
