import os
import psycopg2
from werkzeug.utils import secure_filename
import zipfile
import tempfile
from flask import Flask, request, render_template
from psycopg2.extensions import Binary

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="flask_db",
    user="postgres",
    password="4356"
)
print("Connected to database successfully.")

# Get a cursor object to execute SQL statements
cur = conn.cursor()

app = Flask(__name__, static_url_path='/static')



@app.route('/', methods=['GET', 'POST'])
def extract_and_store():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        # Check if the request contains a file
        if 'file' not in request.files:
            return 'No file provided.', 400

        file = request.files['file']

        # Check if the file has a valid extension
        if not file.filename.endswith('.zip'):
            return 'Invalid file type. Only .zip files are allowed.', 400

        # Extract the images from the zip archive
        zip_filename = secure_filename(file.filename)
        file.save(zip_filename)
        extracted_contents_path = tempfile.mkdtemp()
        print("extracted_contents_path")
        d = extracted_contents_path(".jpg")

        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(extracted_contents_path)
            print("Image names extracted")

        # Loop through the files in the directory and print the path of the first image file
        for root, dirs, files in os.walk(extracted_contents_path):
            for imagename in files:
                if imagename.endswith(".jpg"):  # or any other image file extension you are looking for
                    image_file = os.path.join(root, imagename)
                    print(image_file)
                    query = "INSERT INTO images (name) VALUES (%s)"
                    values = (os.path.basename(image_file),)
                    cur.execute(query, values)
                    print('cur.execute(query, values)')
                    conn.commit()  # Commit changes to the database
                    break
            else:
                continue
            break

            # if image_file_names.endswith(('.jpg', '.jpeg', '.png')):

        conn.commit()
        cur.close()

        return 'Images extracted and stored successfully.', 200


if __name__ == '__main__':
    app.run(debug=True)
