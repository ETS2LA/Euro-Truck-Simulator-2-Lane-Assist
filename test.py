import tkinter as tk

def demo(master):
    listbox = tk.Listbox(master)
    listbox.pack(expand=1, fill="both")

    # inserting some items
    for names in [0,1,-2,3,4,-5,6]:
        listbox.insert("end", names)
        listbox.itemconfig("end", bg = "red" if names < 0 else "green")

        #instead of one-liner if-else, you can use common one of course
        #if item < 0:
        #     listbox.itemconfig("end", bg = "red")
        #else:
        #     listbox.itemconfig("end", bg = "green")

if __name__ == "__main__":
    root = tk.Tk()
    demo(root)
    root.mainloop()