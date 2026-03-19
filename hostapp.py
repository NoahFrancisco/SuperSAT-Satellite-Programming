# Import Libraries
from flask import Flask, render_template
import os

# Flask
app = Flask(__name__)

@app.route('/')
def index():
    global Image
    ImageDirectory = os.listdir('static') # Get the latest image (In static)

    if len(ImageDirectory) > 0:
        ValidImage = [f for f in ImageDirectory if not f.startswith('.')] # Ensures theres a valid image, but it won't break if there is not
        ImageHTML = ValidImage[0] if ValidImage else None
    else:
        ImageHTML = None

    return render_template('index.html', ImageHTML = ImageHTML)

app.run(host="0.0.0.0", port = 8080) # Locally host it using port 8080