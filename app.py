from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = "change_this_secret_key"  # needed for flash messages

# ------ You can replace this with YOUR resize code ------
def resize_image(file_storage, new_width, new_height):
    # file_storage is the uploaded file from the form
    img = Image.open(file_storage.stream)
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    buf = BytesIO()
    # keep same format or default to PNG
    img_format = img.format if img.format is not None else "PNG"
    resized.save(buf, format=img_format)
    buf.seek(0)
    return buf, img_format
# --------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        width = request.form.get("width")
        height = request.form.get("height")

        if not file or file.filename == "":
            flash("Please choose an image file.")
            return redirect(url_for("index"))

        if not width or not height:
            flash("Please enter both width and height.")
            return redirect(url_for("index"))

        try:
            new_width = int(width)
            new_height = int(height)
            if new_width <= 0 or new_height <= 0:
                raise ValueError
        except ValueError:
            flash("Width and height must be positive integers.")
            return redirect(url_for("index"))

        # Call your resize function
        resized_bytes, img_format = resize_image(file, new_width, new_height)

        # Create a nice download name
        original_name = secure_filename(file.filename)
        name, ext = os.path.splitext(original_name)
        download_name = f"{name}_resized_{new_width}x{new_height}{ext or '.png'}"

        return send_file(
            resized_bytes,
            mimetype=file.mimetype or "image/png",
            as_attachment=True,
            download_name=download_name,
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
