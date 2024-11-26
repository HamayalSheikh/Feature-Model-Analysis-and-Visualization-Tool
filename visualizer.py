# Handles feature model visualization and interactions

import tkinter as tk

def start_visualization(xml_data, mwp):
    root = tk.Tk()
    root.title("Feature Model Visualization")
    
    # Create checkboxes for features
    for feature in xml_data.findall(".//feature"):
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=feature.get("name"), variable=var)
        chk.pack()
    
    root.mainloop()
