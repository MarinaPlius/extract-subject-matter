from flask import Flask, redirect, render_template, request, abort
import smtplib, ssl
import help_functions

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Email sending settings
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "marpl8179"  # Enter your address
receiver_email = "fukaiumi@yandex.ru"  # Enter receiver address
password = "xo4uposylatemail"

# The main page
@app.route("/", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        try:
            #read text
            text = request.files["file"].read().decode("utf-8")
            url = request.form.get("url")
        except Exception:
            abort(404, "invalid file")
        finally:
            #deal with empty inputs
            if not text and not url:
                return render_template("index.html")
            elif text and url:
                return render_template("index.html")
            elif not text:
                text = help_functions.text_from_url(url)
            #clean text from enronious characters and stop words
            text_clean = help_functions.clean(text)     
            #find the most frequent words   
            key_words = help_functions.freq_words(text_clean)
            key_words_up = [word.upper() for word in key_words]
            #try:
            subject, subject_short = help_functions.subject(text_clean, key_words)
            #except:
            #    return render_template("result.html", key_words=key_words_up, subject="no subject", facts=["no facts"], text=text)
            #extract facts with spacy
            #facts = help_functions.extract_facts(text, subject)
            facts = []
            if facts == []:
                return render_template("result.html", key_words=key_words_up, subject=subject.capitalize(), facts=["no facts"], text=text)
            #return the result of extracting
            return render_template("result.html", key_words=key_words_up, subject=subject.capitalize(), facts=facts, text=text)
    else:
        return render_template("index.html")

# About the project
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

# Contact page resends a left message to my email
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        #get the message and data
        name = request.form.get("name")
        email = request.form.get("email")
        topic = request.form.get("topic")
        message = request.form.get("message")
        #deal with empty inputs
        if not name or not email or not message:
            return render_template("contact.html")
        else:
            #send an email
            message ="{}, {} From {}, {}".format(topic,message,name,email)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
                #return successful result
            return render_template("contacted.html")
    else:
        return render_template("contact.html")

# Privacy policy information
@app.route("/policy", methods=["GET"])
def policy():
    return render_template("policy.html")
