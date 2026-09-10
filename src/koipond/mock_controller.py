import tkinter as tk


def launch_controller(on_button1, on_button2, on_button3, on_button4):
  root = tk.Tk()
  root.title("Koi Pond Controller")
  root.geometry("220x275")

  tk.Label(root, text="Mock Controller", font=("Arial", 12, "bold")).pack(pady=10)

  tk.Button(root, text="Power", width=20, height=2, command=on_button1).pack(pady=5)
  tk.Button(root, text="Drop Food", width=20, height=2, command=on_button2).pack(pady=5)
  tk.Button(root, text="Add Koi", width=20, height=2, command=on_button3).pack(pady=5)
  tk.Button(root, text="Remove Koi", width=20, height=2, command=on_button4).pack(pady=5)

  root.mainloop()