import os
import subprocess
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def compress(input_file_path, output_file_path, power=0):
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }

    gs = get_ghostscript_path()
    subprocess.call(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={quality[power]}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_file_path}",
            input_file_path,
        ]
    )

def get_ghostscript_path():
    # Specify the path to the GhostScript executable
    gs_path = r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe"
    
    if os.path.isfile(gs_path):
        return gs_path
    else:
        raise FileNotFoundError("GhostScript executable not found. Please provide the correct path.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')
    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if not allowed_file(file.filename):
        return render_template('index.html', error='Invalid file type')

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    compression_level = int(request.form['compression_level'])
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed_' + filename)

    compress(file_path, output_filename, power=compression_level)
    
    original_size = os.path.getsize(file_path) / (1024 * 1024)  
    compressed_size = os.path.getsize(output_filename) / (1024 * 1024) 
    compression_ratio = compressed_size / original_size

    return render_template(
        'index.html',
        compressed_file='compressed_' + filename,
        original_size=original_size,
        compressed_size=compressed_size,
        compression_ratio=compression_ratio
    )

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
