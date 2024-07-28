import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

def select_file():
    file_path = filedialog.askopenfilename()
    return file_path

def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H-%M-%S")
    return timestamp

def get_output_file_path(prefix='output'):
    timestamp = get_timestamp()
    output_dir = os.path.expanduser('~/Documents/')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, f'{prefix}-{timestamp}.txt')
    return output_file

def process_file(input_file, output_file, columns_to_keep):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            parts = line.strip().split('\t')
            if len(parts) >= max(columns_to_keep):
                selected_parts = [parts[i] for i in columns_to_keep if i <= len(parts)]
                output_line = '\t'.join(selected_parts)
                f_out.write(output_line + '\n')
    messagebox.showinfo("Info", f"Processing complete. Output saved to: {output_file}")

def remove_duplicates(input_file, output_file):
    unique_lines = set()
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            unique_lines.add(line.strip())
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for line in unique_lines:
            f_out.write(line + '\n')
    messagebox.showinfo("Info", f"Unique lines extracted and saved to: {output_file}")

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
    messagebox.showinfo("Info", f"Lines retained based on data file and written to: {output_file}")

def main():
    root = tk.Tk()
    root.title("File Processor")
    
    tk.Label(root, text="Step 1: Select input file and process").pack()
    tk.Button(root, text="Select and Process File", command=lambda: process_file(
        select_file(), get_output_file_path('processed_columns'), [1, 2, 3]
    )).pack()
    
    tk.Label(root, text="Step 2: Remove duplicates").pack()
    tk.Button(root, text="Remove Duplicates", command=lambda: remove_duplicates(
        select_file(), get_output_file_path('unique_lines')
    )).pack()
    
    tk.Label(root, text="Step 3: Filter lines based on data file").pack()
    tk.Button(root, text="Filter Lines", command=lambda: delete_lines_from_file(
        select_file(), select_file(), get_output_file_path('filtered_lines')
    )).pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()
