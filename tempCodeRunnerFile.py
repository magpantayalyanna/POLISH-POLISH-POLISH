from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary feedback storage
feedbacks = []

@app.route('/')
def homepage():
    return render_template('index.html', feedbacks=feedbacks)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    resort = request.form['resort']
    message = request.form['message']
    feedbacks.append({'resort': resort, 'message': message})
    return redirect(url_for('homepage'))

@app.route('/2ndpage')
def explore():
    return render_template('2ndpage.html')

@app.route('/resort-details')
def resort_details():
    resort = request.args.get('resort')
    return render_template('3rdpage.html', resort=resort, feedbacks=feedbacks)

@app.route('/finalbookingform.html')
def finalbookingform():
    return render_template('finalbookingform.html')

@app.route('/emailtemplate.html')
def emailtemplate():
    return render_template('emailtemplate.html')

if __name__ == '__main__':
    app.run(debug=True)