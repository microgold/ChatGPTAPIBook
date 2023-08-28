import tkinter as tk
from tkinter import ttk

def submit():
    animal1 = combo1.get()
    animal2 = combo2.get()
    scenario = entry_box.get()

    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)  # Clear any previous results
    result_text.insert(tk.END, f"Animal 1: {animal1}\n")
    result_text.insert(tk.END, f"Animal 2: {animal2}\n")
    result_text.insert(tk.END, f"Discussion scenario: {scenario}\n")
    result_text.config(state="disabled")

app = tk.Tk()
app.title("Animal Discussion Scenario")

# Label and ComboBox for the first animal
label1 = ttk.Label(app, text="Select Animal 1:")
label1.grid(column=0, row=0, padx=10, pady=5)
combo1 = ttk.Combobox(app, values=["Lion", "Elephant", "Giraffe", "Kangaroo", "Panda"])
combo1.grid(column=1, row=0, padx=10, pady=5)
combo1.set("Lion")

# Label and ComboBox for the second animal
label2 = ttk.Label(app, text="Select Animal 2:")
label2.grid(column=0, row=1, padx=10, pady=5)
combo2 = ttk.Combobox(app, values=["Lion", "Elephant", "Giraffe", "Kangaroo", "Panda"])
combo2.grid(column=1, row=1, padx=10, pady=5)
combo2.set("Elephant")

# Label and Entry for entering the discussion scenario
label3 = ttk.Label(app, text="Enter Discussion Scenario:")
label3.grid(column=0, row=2, padx=10, pady=5)
entry_box = ttk.Entry(app, width=30)
entry_box.grid(column=1, row=2, padx=10, pady=5)

# Button to submit the details
submit_btn = ttk.Button(app, text="Submit", command=submit)
submit_btn.grid(column=1, row=3, padx=10, pady=20)

# Text widget to display results
result_text = tk.Text(app, width=40, height=10)
result_text.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
result_text.config(state="disabled")

app.mainloop()
