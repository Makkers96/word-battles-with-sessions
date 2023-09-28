from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)

app.secret_key = "supersecretkeything124"

@app.route("/home", methods=["GET", "POST"])
def home():
    session['stage'] = 1
    return f"This is our homepage"


@app.route("/show-stage", methods=["GET", "POST"])
def show_stage():
    stage = session['stage']
    session['stage'] = 10
    return f"This is our current stage: {stage}"


@app.route("/addition", methods=["GET", "POST"])
def addition():
    session['stage'] += 1
    return redirect(url_for("show_stage"))


@app.route("/subtraction", methods=["GET", "POST"])
def subtraction():
    session['stage'] -= 1
    return redirect(url_for("show_stage"))




if __name__ == "__main__":
    app.run()