from flask import Flask, render_template,redirect,request,Response
from est import my_est


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


'''@app.route('/my-link/',methods = ['GET','POST'])
def mylink():
    temp = request.form['test']
    temp2 = request.form['test2']
    my_est(temp2)
    return temp+' Estimation process has ended' '''

@app.route('/video')
def video():
    return Response(my_est(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
