import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.model import model_api


# Function to handle adding new PCM Database
def add_new_database():
    def submit_new_db():
        db_path = new_db_entry.get()
        if db_path.endswith('.cdb'):
            messagebox.showinfo("Add PCM Database", f"Database added: {db_path}")
            pcm_db_combobox['values'] = (*pcm_db_combobox['values'], db_path)
            add_db_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid database file. Please enter a valid .cdb file")

    def browse_db():
        file_path = filedialog.askopenfilename(filetypes=[("CDB files", "*.cdb")])
        new_db_entry.delete(0, tk.END)
        new_db_entry.insert(0, file_path)

    add_db_window = tk.Toplevel(root)
    add_db_window.title("Add a PCM Database")
    tk.Label(add_db_window, text="Enter .cdb file path:").pack(padx=10, pady=5)
    new_db_entry = ttk.Entry(add_db_window, width=50)
    new_db_entry.pack(padx=10, pady=5)
    ttk.Button(add_db_window, text="Browse", command=browse_db).pack(padx=10, pady=5)
    ttk.Button(add_db_window, text="Submit", command=submit_new_db).pack(padx=10, pady=10)


# Function to handle adding new Start List
def add_new_start_list():
    def submit_new_list():
        list_url = new_list_entry.get()
        if list_url.startswith('http://') or list_url.startswith('https://'):
            messagebox.showinfo("Add Start List", f"Start list added: {list_url}")
            start_list_combobox['values'] = (*start_list_combobox['values'], list_url)
            add_list_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid URL. Please enter a valid URL")

    add_list_window = tk.Toplevel(root)
    add_list_window.title("Add a Start List")
    tk.Label(add_list_window, text="Enter start list URL:").pack(padx=10, pady=5)
    new_list_entry = ttk.Entry(add_list_window, width=50)
    new_list_entry.pack(padx=10, pady=5)
    ttk.Button(add_list_window, text="Submit", command=submit_new_list).pack(padx=10, pady=10)


# Function to generate start list
def generate_start_list():
    pcm_db = pcm_db_combobox.get()
    start_list = start_list_combobox.get()
    output_dir = output_dir_entry.get()

    if pcm_db and start_list and output_dir:
        # Here you would implement the functionality to generate the start list file
        messagebox.showinfo("Generate Start List", f"Start List generated in {output_dir}")
    else:
        messagebox.showerror("Error", "Please provide all inputs")


def browse_output_dir():
    dir_path = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, dir_path)


# Create the main window
root = tk.Tk()
root.title("PCM Start List Generator")

# Section 1: Select A PCM Database
section1 = ttk.LabelFrame(root, text="Select A PCM Database")
section1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

pcm_db_combobox = ttk.Combobox(section1)
pcm_db_combobox.grid(row=0, column=0, padx=5, pady=5)
pcm_db_combobox['values'] = ('db1.cdb', 'db2.cdb', 'db3.cdb')

add_db_button = ttk.Button(section1, text="Add New Database", command=add_new_database)
add_db_button.grid(row=1, column=0, padx=5, pady=5)

# Section 2: Select a Race Start List Source
section2 = ttk.LabelFrame(root, text="Select a Race Start List Source")
section2.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

start_list_combobox = ttk.Combobox(section2)
start_list_combobox.grid(row=0, column=0, padx=5, pady=5)
start_list_combobox['values'] = ('list1', 'list2', 'list3')

add_list_button = ttk.Button(section2, text="Add a Start List", command=add_new_start_list)
add_list_button.grid(row=1, column=0, padx=5, pady=5)

# Section 3: Generate Start List
section3 = ttk.LabelFrame(root, text="Generate Start List")
section3.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

tk.Label(section3, text="Output directory:").grid(row=0, column=0, padx=5, pady=5)
output_dir_entry = ttk.Entry(section3, width=50)
output_dir_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(section3, text="Browse", command=browse_output_dir).grid(row=0, column=2, padx=5, pady=5)

generate_button = ttk.Button(section3, text="Generate Start List", command=generate_start_list, style="Accent.TButton")
generate_button.grid(row=1, columnspan=3, padx=5, pady=10)

# Add styling for the generate button to make it stand out
style = ttk.Style()
style.configure("Accent.TButton", foreground="blue", font=('Helvetica', 10, 'bold'))

root.mainloop()
