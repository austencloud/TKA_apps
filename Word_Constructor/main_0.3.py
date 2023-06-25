import tkinter as tk
import tkinter.ttk as ttk
import random
from random import choice

root = tk.Tk()
root.geometry('1000x800')

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

def on_auto_fill_mode_toggle():
    if auto_fill_mode.get():
        interpolation_label.grid(row=4, column=3, sticky='w')  # show the label
        interpolation_input.grid(row=5, column=3, sticky='w')  # show the input
        interpolation_button.grid(row=6, column=3, sticky='w')  # show the button
    else:
        interpolation_label.grid_remove()  # hide the label
        interpolation_input.grid_remove()  # hide the input
        interpolation_button.grid_remove()  # hide the button
    update_buttons()



state_label = tk.Label(root, text='', font=('Helvetica', '20'))
state_label.grid(row=3, column=3, sticky='nw', padx=50)

sequence_label = tk.Text(root, font=('Helvetica', '32'), height=1, width=30)

sequence_label.tag_config('red', foreground='red')
sequence_label.tag_config('black', foreground='black')
sequence_label.config(state='disabled')  # disable user input
sequence_label.grid(row=2, column=3, sticky='w',)

start_position_label = tk.Label(root, text='', font=('Helvetica', '20'))
start_position_label.grid(row=0, column=3, sticky='w')

end_positions_label = tk.Label(root, text='', font=('Helvetica', '20'))
end_positions_label.grid(row=1, column=3, sticky='w')  # change row to 3

saved_label = tk.Label(root, text='Saved:', font=('Helvetica', '20'))
saved_label.grid(row=7, column=3, sticky='w')  # change row to 4

buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=0, sticky='w', padx=50)

clear_button = tk.Button(root, text="Clear", command=lambda: clear_sequence(), height=2, width=4, font=('Helvetica', '20'))
clear_button.grid(row=5, column=2, sticky='w', padx=50)

save_button = tk.Button(root, text="Save", command=lambda: save_sequence(), height=2, width=4, font=('Helvetica', '20'))
save_button.grid(row=6, column=2, sticky='w', padx=50)

auto_fill_mode = tk.BooleanVar(value=False)
auto_fill_checkbox = tk.Checkbutton(root, text="Autofill Mode", variable=auto_fill_mode,
                                    command=on_auto_fill_mode_toggle, font=('Helvetica', '20'))
auto_fill_checkbox.grid(row=3, column=3, sticky='nw')

# Create the interpolation label but don't grid it yet
interpolation_label = tk.Label(root, text='Type a Word:', font=('Helvetica', '20'))

interpolation_input = tk.Entry(root, font=('Helvetica', '20'))
interpolation_button = tk.Button(root, text="Generate", command=lambda: interpolate_sequence(), height=1, width=8, font=('Helvetica', '20'))

saved_text = tk.Text(root, font=('Helvetica', '20'), height=10, width=30)
saved_text.grid(row=8, column=3, sticky='w')  # change row to 5

# put text at the beginning of the saved label that says "saved:" and then a new line

def on_key_press(event):
    if event.char.upper() in buttons:  # if the key pressed is one of the letters
        update_state(event.char.upper())
    elif event.keysym == 'BackSpace':  # if the backspace key is pressed
        state['sequence'].pop()
        sequence_label.config(state='normal')
        sequence_label.delete('end - 2c')  # remove the last character
        sequence_label.config(state='disabled')
    # For any other key press, do nothing.
    
sequence_label.bind("<KeyPress>", on_key_press)

def find_interpolation(start, end):
    valid_letters = [letter for letter, pos in positions.items() if pos[0] == positions[start][1] and pos[1] == positions[end][0]]
    if valid_letters:
        return choice(valid_letters)
    return None

def interpolate_sequence():
    sequence = interpolation_input.get().upper()
    interpolation_input.delete(0, 'end')  # clear the input field
    interpolated_sequence = []
    for i in range(len(sequence) - 1):
        start = sequence[i]
        end = sequence[i + 1]
        interpolated_sequence.append((start, False))  # the user-typed letters are not interpolated
        if positions[start][1] != positions[end][0]:  # checks if the end position of current letter != start position of next letter
            interpolated = find_interpolation(start, end)
            if interpolated:
                interpolated_sequence.append((interpolated, True))  # the interpolated letters are marked as interpolated
    interpolated_sequence.append((sequence[-1], False))  # append the last letter

    # save the interpolated sequence
    saved_words.append(interpolated_sequence)
    update_saved_words_label()

def update_saved_words_label():
    saved_text.config(state='normal')
    saved_text.delete('1.0', tk.END)  # clear the existing text
    for word in saved_words:
        for letter in word:
            if letter[1]:
                saved_text.insert('end', letter[0], 'red')
            else:
                saved_text.insert('end', letter[0], 'black')
        saved_text.insert('end', '\n')  # newline after each word
    saved_text.config(state='disabled')

def find_intermediate_letters(start, end):
    return [letter for letter, pos in positions.items() if pos[0] == start and pos[1] == end]

def can_follow(letter):
    if not state['sequence']:
        return positions[letter][0] in ['alpha', 'beta', 'gamma']
    last_letter = state['sequence'][-1]
    return positions[last_letter[0]][1] == positions[letter][0]


def update_state(letter):
    if not state['sequence'] or can_follow(letter):
        state['sequence'].append((letter, False))
        sequence_label.config(state='normal')
        sequence_label.insert('end', letter, 'black')
        sequence_label.config(state='disabled')
    elif auto_fill_mode.get():
        prev_letter = state['sequence'][-1]
        intermediate_letters = find_intermediate_letters(positions[prev_letter[0]][1], positions[letter][0])
        if intermediate_letters:
            intermediate_letter = random.choice(intermediate_letters)
            state['sequence'].append((intermediate_letter, True))
            sequence_label.config(state='normal')
            sequence_label.insert('end', intermediate_letter, 'red')
            sequence_label.config(state='disabled')
            state['sequence'].append((letter, False))
            sequence_label.config(state='normal')
            sequence_label.insert('end', letter, 'black')
            sequence_label.config(state='disabled')
    else:
        return
    update_end_positions_label()
    if len(state['sequence']) == 1:  # if it's the first character
        start_position_str = positions[letter][0].replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
        start_position_label.config(text=f'Start: {start_position_str}')
    update_buttons()

def clear_sequence():
    state['sequence'].clear()
    sequence_label.config(state='normal')
    sequence_label.delete('1.0', tk.END)
    sequence_label.config(state='disabled')
    start_position_label.config(text='')  # clear the start position
    update_buttons()
    end_positions_label.config(text='')  # clear the end positions

def save_sequence():
    saved_words.append(state['sequence'].copy())  # Save the sequence with both letters and their state
    update_saved_words_label()
    clear_sequence()  # After saving, we clear the current sequence
    start_position_label.config(text='')  # clear the start position
    end_positions_label.config(text='')  # clear the end positions

def update_state_label(letter):
    state_label.config(text=positions[letter][1])

def update_buttons():
    for letter, button in buttons.items():
        if not state['sequence']:  # If sequence is empty, then all 'alpha', 'beta', and 'gamma' start positions are possible
            button['state'] = 'normal'
            button['foreground'] = 'black'  # Add this line to change the button text color to black
        elif auto_fill_mode.get():
            last_letter = state['sequence'][-1]
            if positions[last_letter[0]][1] == positions[letter][0]:  # Can follow without interpolation
                button['state'] = 'normal'
                button['foreground'] = 'black'
            else:
                intermediate_letters = find_intermediate_letters(positions[last_letter[0]][1], positions[letter][0])
                if intermediate_letters:  # Can follow with interpolation
                    button['state'] = 'normal'
                    button['foreground'] = 'white'  # Requires interpolation - change text color to white
                else:  # Cannot follow even with interpolation
                    button['state'] = 'disabled'
                    button['foreground'] = 'white'
        else:  # Without auto-fill mode
            if can_follow(letter):
                button['state'] = 'normal'
                button['foreground'] = 'black'
            else:
                button['state'] = 'disabled'
                button['foreground'] = 'white'



auto_fill_checkbox = tk.Checkbutton(root, text="Auto Fill Mode", variable=auto_fill_mode,
                                    command=on_auto_fill_mode_toggle, font=('Helvetica', '20'))

def get_positional_outcome(sequence):
    end_positions = [positions[lt[0]][1] for lt in sequence]
    return ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')

def update_end_positions_label():
    end_positions_str = get_positional_outcome(state['sequence'])
    end_positions_label.config(text=end_positions_str)

def append_positional_outcome(letter):
    end_positions = [positions[lt[0]][1] for lt in state['sequence'].copy()]  # create a copy of the sequence
    end_positions.append(positions[letter][0])
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
        # Modify the button's foreground color
        button = tk.Button(row_frame, text=letter, 
                        command=lambda letter=letter: update_state(letter),
                        height=1, width=2, font=('Helvetica', '20'), 
                        background='gray', foreground='black')  # Change foreground color to 'black'

        button.pack(side=tk.LEFT)
        buttons[letter] = button
        button.bind("<Enter>", lambda e, letter=letter: show_positional_outcome(e, letter))  
        button.bind("<Leave>", lambda e, letter=letter: show_positional_outcome(e, letter))

saved_text.tag_config('red', foreground='red')
saved_text.tag_config('black', foreground='black')

root.mainloop()