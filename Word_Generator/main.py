import tkinter as tk
from tkinter import messagebox
from functions import Interpolation
from data import start_letters, positions
import enchant

class InterpolationGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Word Generator')

        self.interpolation = Interpolation(start_letters, positions)

        self.length_var = tk.StringVar()
        self.dictionary = enchant.Dict("en_US")

        length_label = tk.Label(self, text="Enter length of the word:")
        length_label.pack()

        length_entry = tk.Entry(self, textvariable=self.length_var)
        length_entry.pack()

        generate_button = tk.Button(self, text="Generate Words", command=self.generate_words)
        generate_button.pack()

        #create a label for the valid words, give it a font size of 15
        valid_word_label = tk.Label(self, text="Words:", font=('Helvetica', '15'))
        valid_word_label.pack()

        self.word_text = tk.Text(self)
        self.word_text.pack()

        #create a label for the real words, give it a font size of 15, It should display to the right of the valid words
        real_word_label = tk.Label(self, text="Real Words:", font=('Helvetica', '15'))
        real_word_label.pack()

        self.real_words_text = tk.Text(self)
        self.real_words_text.pack()

        self.word_count_label = tk.Label(self, text="Words generated: 0")
        self.word_count_label.pack()

        self.circular_var = tk.BooleanVar()
        circular_checkbox = tk.Checkbutton(self, text="Circular words", variable=self.circular_var)
        circular_checkbox.pack()

    def generate_words(self):
        try:
            length = int(self.length_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid number")
            return

        # Generate all valid words of the given length
        valid_words = self.generate_all_valid_words(length)
        # Sort the words
        valid_words.sort()

        # Clear the text boxes
        self.word_text.delete('1.0', tk.END)
        self.real_words_text.delete('1.0', tk.END)

        real_words = [word for word in valid_words if self.dictionary.check(word)]

        # Add the words to the text boxes
        for word in valid_words:
            self.word_text.insert(tk.END, word + "\n")
        for word in real_words:
            self.real_words_text.insert(tk.END, word + "\n")

        # Update the word count
        self.word_count_label.config(text=f"Words generated: {len(valid_words)}")

    def generate_all_valid_words(self, length):
        all_words = []
        circular = self.circular_var.get()  # Get the state of the checkbox
        for _ in range(100000):
            word = self.interpolation.generate_word(length, circular)
            if word not in all_words:
                all_words.append(word)
        return all_words

if __name__ == "__main__":
    app = InterpolationGUI()
    app.mainloop()
