import tkinter as tk
root = tk.Tk()

end_positions_label = tk.Label(root, text='', font=('Helvetica', '20'))
end_positions_label.pack()

sequence_label = tk.Label(root, text='', font=('Helvetica', '32'))
sequence_label.pack()

saved_label = tk.Label(root, text='', font=('Helvetica', '20'))
saved_label.pack()




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

state = {
    'sequence': [],
}

saved_words = []


def update_state(letter):
    state['sequence'].append(letter)
    sequence_label.config(text=''.join(state['sequence']))
    update_buttons()
    update_end_positions_label()


def can_follow(letter):
    if not state['sequence']:
        return positions[letter][0] in ['alpha', 'beta', 'gamma']
    last_letter = state['sequence'][-1]
    return positions[last_letter][1] == positions[letter][0]





buttons_frame = tk.Frame(root)
buttons_frame.pack()

def on_enter(e):
    letter = e.widget.cget('text')
    update_state_label(letter)

def on_leave(e):
    if state['sequence']:
        last_letter = state['sequence'][-1]
    else:
        last_letter = 'A'  # Or whatever default you want
    update_state_label(last_letter)
buttons = {}

for letter in positions:
    button = tk.Button(buttons_frame, text=letter, command=lambda letter=letter: update_state(letter),
                    height=2, width=2, font=('Helvetica', '25'), background='gray', foreground='white')
    button.pack(side=tk.LEFT)
    button.bind('<Enter>', lambda event, letter=letter: show_positional_outcome(event, letter))
    button.bind('<Leave>', lambda event, letter=letter: show_positional_outcome(event, letter))
    buttons[letter] = button




def update_buttons():
    for letter, button in buttons.items():
        if can_follow(letter):
            button['state'] = 'normal'
        else:
            button['state'] = 'disabled'

def clear_sequence():
    state['sequence'].clear()
    sequence_label.config(text='')
    update_buttons()
    
def save_sequence():
    saved_words.append(''.join(state['sequence']))
    saved_label.config(text='Saved sequences: ' + ', '.join(saved_words)) 
    clear_sequence()  # After saving, we clear the current sequence

def update_state_label(letter):
    state_label.config(text='Current state: ' + positions[letter][1])

def update_end_positions_label():
    end_positions = [positions[letter][1] for letter in state['sequence']]
    end_positions_str = ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
    end_positions_label.config(text=end_positions_str)

def append_positional_outcome(letter):
    end_positions = [positions[lt][1] for lt in state['sequence']]
    end_positions.append(positions[letter][1])
    end_positions_str = ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
    end_positions_label.config(text=end_positions_str)

def show_positional_outcome(event, letter):
    if event.type == "7":  # Mouse enters the button
        append_positional_outcome(letter)
    elif event.type == "8":  # Mouse leaves the button
        update_end_positions_label()




clear_button = tk.Button(root, text="Clear", command=clear_sequence, height=2, width=4, font=('Helvetica', '20'))
clear_button.pack(side=tk.LEFT)

save_button = tk.Button(root, text="Save", command=save_sequence, height=2, width=4, font=('Helvetica', '20'))
save_button.pack(side=tk.LEFT)


state_label = tk.Label(root, text='', font=('Helvetica', '20'))
state_label.pack()



root.mainloop()
