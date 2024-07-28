from flask import Flask, request, render_template, redirect, url_for, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = '/home/ec2-user/uploads/'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_timestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d_%H-%M-%S")

def get_output_file_path(prefix='output'):
    timestamp = get_timestamp()
    output_dir = os.path.expanduser('~/Documents/')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, f'{prefix}-{timestamp}.txt')

def process_file(input_file, output_file, columns_to_keep):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            parts = line.strip().split('\t')
            if len(parts) >= max(columns_to_keep):
                selected_parts = [parts[i] for i in columns_to_keep if i <= len(parts)]
                output_line = '\t'.join(selected_parts)
                f_out.write(output_line + '\n')
    return output_file

def remove_duplicates(input_file, output_file):
    unique_lines = set()
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            unique_lines.add(line.strip())
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for line in unique_lines:
            f_out.write(line + '\n')
    return output_file

def delete_lines_from_file(data_file, input_file, output_file):
    with open(data_file, 'r', encoding='utf-8') as data:
        strings_to_retain = {line.strip() for line in data.readlines()}
    with open(input_file, 'r', encoding='utf-8') as input_f:
        lines = input_f.readlines()
    with open(output_file, 'w', encoding='utf-8') as output_f:
        for line in lines:
            words = line.split()
            if any(word in strings_to_retain for word in words):
                output_f.write(line)
    return output_file

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Process the file
        columns_to_keep = [1, 2, 3]
        processed_file = get_output_file_path('processed_columns')
        process_file(input_path, processed_file, columns_to_keep)
        
        # Remove duplicates
        unique_file = get_output_file_path('unique_lines')
        remove_duplicates(processed_file, unique_file)
        
        # Filter lines based on data file
        data_file = 'data_file.txt'  # Adjust path as necessary
        filtered_file = get_output_file_path('filtered_lines')
        delete_lines_from_file(data_file, unique_file, filtered_file)
        
        flash('File successfully processed')
        return redirect(url_for('upload_file'))
    else:
        flash('Allowed file types are txt')
        return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)
