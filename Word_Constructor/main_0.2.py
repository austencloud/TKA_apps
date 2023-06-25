import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.geometry('1000x800')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=0)  # this is the row with "Saved:" label
root.grid_rowconfigure(7, weight=1)  # this is the row with the Text widget for saved words
root.grid_rowconfigure(8, weight=1)


positions = {
    "A": ("alpha", "alpha"),
    "B": ("alpha", "alpha"),
    "C": ("alpha", "alpha"),
    "D": ("beta", "alpha"),
    "E": ("beta", "alpha"),
    "F": ("beta", "alpha"),
    "G": ("beta", "beta"),
    "H": ("beta", "beta"),
    "I": ("beta", "beta"),
    "J": ("alpha", "beta"),
    "K": ("alpha", "beta"),
    "L": ("alpha", "beta"),
    "M": ("gamma", "gamma"),
    "N": ("gamma", "gamma"),
    "O": ("gamma", "gamma"),
    "P": ("gamma", "gamma"),
    "Q": ("gamma", "gamma"),
    "R": ("gamma", "gamma"),
    "S": ("gamma", "gamma"),
    "T": ("gamma", "gamma"),
    "U": ("gamma", "gamma"),
    "V": ("gamma", "gamma"),
    "W": ("gamma", "alpha"),
    "X": ("gamma", "alpha"),
    "Y": ("gamma", "beta"),
    "Z": ("gamma", "beta"),
    "Σ": ("alpha", "gamma"),
    "Δ": ("alpha", "gamma"),
    "θ": ("beta", "gamma"),
    "Ω": ("beta", "gamma"),
    "Φ": ("beta", "alpha"),
    "Ψ": ("alpha", "beta"),
    "Λ": ("gamma", "gamma"),
    "W-": ("gamma", "alpha"),
    "X-": ("gamma", "alpha"),
    "Y-": ("gamma", "beta"),
    "Z-": ("gamma", "beta"),
    "Σ-": ("beta", "gamma"),
    "Δ-": ("beta", "gamma"),
    "θ-": ("alpha", "gamma"),
    "Ω-": ("alpha", "gamma"),
    "Φ-": ("alpha", "alpha"),
    "Ψ-": ("beta", "beta"),
    "Λ-": ("gamma", "gamma"),
    "α": ("alpha", "alpha"),
    "β": ("beta", "beta"),
    "Γ": ("gamma", "gamma"),

}


letter_rows = [
    ['A', 'B', 'C'],
    ['D', 'E', 'F'],
    ['G', 'H', 'I'],
    ['J', 'K', 'L'],
    ['M', 'N', 'O'],
    ['P', 'Q', 'R'],
    ['S', 'T', 'U', 'V'],
    ['W', 'X', 'Y', 'Z'],
    ['Σ', 'Δ', 'θ', 'Ω'],
    ['Φ', 'Ψ', 'Λ'],
    ['W-', 'X-', 'Y-', 'Z-'],
    ['Σ-', 'Δ-', 'θ-', 'Ω-'],
    ['Φ-', 'Ψ-', 'Λ-'],
    ['α', 'β', 'Γ']
]

saved_words = []
state = {
    'sequence': [],
}

state_label = tk.Label(root, text='', font=('Helvetica', '20'))
state_label.grid(row=3, column=3, sticky='nw', padx=50)

sequence_label = tk.Label(root, text='', font=('Helvetica', '32'))
sequence_label.grid(row=2, column=3, sticky='nw', padx=50)

start_position_label = tk.Label(root, text='', font=('Helvetica', '20'))
start_position_label.grid(row=0, column=3, sticky='nw', padx=50)

end_positions_label = tk.Label(root, text='', font=('Helvetica', '20'))
end_positions_label.grid(row=1, column=3, sticky='nw', padx=50)  # change row to 3

saved_label = tk.Label(root, text='Saved:', font=('Helvetica', '20'))
saved_label.grid(row=4, column=3, sticky='nw',padx=50)  # change row to 4

saved_text = tk.Text(root, font=('Helvetica', '20'), height=5, width=30)
saved_text.grid(row=5, column=3, sticky='nw', padx=50)  # change row to 5


buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=0, sticky='nw', padx=50)

clear_button = tk.Button(root, text="Clear", command=lambda: clear_sequence(), height=2, width=4, font=('Helvetica', '20'))
clear_button.grid(row=5, column=2, sticky='nw', padx=50)

save_button = tk.Button(root, text="Save", command=lambda: save_sequence(), height=2, width=4, font=('Helvetica', '20'))
save_button.grid(row=6, column=2, sticky='nw', padx=50)

# put text at the beginning of the saved label that says "saved:" and then a new line


def can_follow(letter):
    if not state['sequence']:
        return positions[letter][0] in ['alpha', 'beta', 'gamma']
    last_letter = state['sequence'][-1]
    return positions[last_letter][1] == positions[letter][0]


def update_state(letter):
    state['sequence'].append(letter)
    sequence_label.config(text=''.join(state['sequence']))
    update_end_positions_label()
    if len(state['sequence']) == 1:  # if it's the first character
        start_position_str = positions[letter][0].replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
        start_position_label.config(text=f'Start: {start_position_str}')
    update_buttons()

def clear_sequence():
    state['sequence'].clear()
    sequence_label.config(text='')
    start_position_label.config(text='')  # clear the start position
    update_buttons()
    end_positions_label.config(text='')  # clear the end positions

def save_sequence():
    saved_words.append(''.join(state['sequence']))
    saved_text.configure(state='normal')  # allow text modification
    saved_text.delete('1.0', tk.END)  # clear current text
    saved_text.insert(tk.END, '\n'.join(saved_words))  # insert new text
    saved_text.configure(state='disabled')  # prevent further text modification
    clear_sequence()  # After saving, we clear the current sequence
    start_position_label.config(text='')  # clear the start position
    end_positions_label.config(text='')  # clear the end positions


def update_state_label(letter):
    state_label.config(text=positions[letter][1])

def update_buttons():
    for letter, button in buttons.items():
        if can_follow(letter):
            button['state'] = 'normal'
        else:
            button['state'] = 'disabled'

def get_positional_outcome(sequence):
    end_positions = [positions[lt][1] for lt in sequence]
    return ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')

def update_end_positions_label():
    end_positions_str = get_positional_outcome(state['sequence'])
    end_positions_label.config(text=end_positions_str)

def append_positional_outcome(letter):
    end_positions = [positions[lt][1] for lt in state['sequence'].copy()]  # create a copy of the sequence
    end_positions.append(positions[letter][1])
    end_positions_str = ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
    return end_positions_str

def show_positional_outcome(event, letter):
    if event.type == "7":  # Mouse enters the button
        end_positions_label.config(text=append_positional_outcome(letter))
    elif event.type == "8":  # Mouse leaves the button
        update_end_positions_label()

original_end_positions = ""

def on_enter(e):
    global original_end_positions
    letter = e.widget.cget('text')
    original_end_positions = end_positions_label.cget('text')
    append_positional_outcome(letter)

def on_leave(e):
    end_positions_label.config(text=original_end_positions)

buttons_frame = tk.Frame(root)
buttons_frame.grid(row=0, column=0, rowspan=len(letter_rows), sticky='nw')
buttons = {}
style = ttk.Style()
style.configure('TButton', font=('Helvetica', '20'), anchor='center')

for i, row in enumerate(letter_rows):
    row_frame = tk.Frame(buttons_frame)
    row_frame.grid(row=i, column=0, sticky='w')
    for letter in row:
        button = tk.Button(row_frame, text=letter, 
                           command=lambda letter=letter: update_state(letter),
                           height=1, width=2, font=('Helvetica', '20'), 
                           background='gray', foreground='white')
        button.pack(side=tk.LEFT)
        buttons[letter] = button
        button.bind("<Enter>", lambda e, letter=letter: show_positional_outcome(e, letter))  
        button.bind("<Leave>", lambda e, letter=letter: show_positional_outcome(e, letter))

root.mainloop()