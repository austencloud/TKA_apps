
import tkinter as tk
import tkinter.ttk as ttk
import random
from data import *


class UIInitializer:
    def __init__(self, root, buttons, interpolation, interpolation_label, interpolation_input, interpolation_button, event_handler, auto_fill_mode, random_word_button):
        self.buttons = buttons
        self.interpolation = interpolation
        self.interpolation_label = interpolation_label
        self.interpolation_input = interpolation_input
        self.interpolation_button = interpolation_button
        self.event_handler = event_handler
        self.auto_fill_mode = auto_fill_mode
        self.random_word_button = random_word_button
        self.random_word_button.config(command=lambda: event_handler.generate_random_word())
        random_word_button.config(command=lambda: event_handler.generate_random_word())



    def initialize_ui(self):
        self.interpolation_input.bind('<Return>', lambda event: self.interpolation.interpolate_sequence())
        self.interpolation_button.config(command=lambda: self.interpolation.interpolate_sequence())

        for letter, button in self.buttons.items():
            button.config(command=lambda letter=letter: self.interpolation.update_state(letter, self.auto_fill_mode))
            button.bind("<Enter>", lambda e: self.event_handler.on_enter(e))
            button.bind("<Leave>", lambda e: self.event_handler.on_leave(e))


class UIUpdater:
    def __init__(self, root, sequence_label, saved_text, state_label, start_position_label, end_positions_label, buttons, scrollbar, auto_fill_mode, interpolation):
        self.root = root
        self.sequence_label = sequence_label
        self.saved_text = saved_text
        self.state_label = state_label
        self.start_position_label = start_position_label
        self.end_positions_label = end_positions_label
        self.buttons = buttons
        self.scrollbar = scrollbar
        self.auto_fill_mode = auto_fill_mode
        self.interpolation = interpolation

        self.bind_button_events()


    def bind_button_events(self):
        for letter, button in self.buttons.items():
            button.bind("<Enter>", lambda e, lt=letter: self.show_positional_outcome(e, lt))
            button.bind("<Leave>", self.restore_positional_outcome)

    def restore_positional_outcome(self, event):
        if event.type == "8":  # Mouse leaves the button
            self.update_end_positions_label()

    def save_sequence(self):
        saved_words.append(state['sequence'].copy())
        self.update_saved_words_label()
        self.clear_sequence()

    def update_end_positions_label(self):
        end_positions_str = self.interpolation.get_positional_outcome(state['sequence'])
        self.end_positions_label.config(text=end_positions_str)

    def update_saved_words_label(self):
        self.saved_text.config(state='normal')
        self.saved_text.delete('1.0', tk.END)
        for word in saved_words:
            for letter in word:
                if letter[1]:
                    self.saved_text.insert('end', letter[0], 'red')
                else:
                    self.saved_text.insert('end', letter[0], 'black')
            self.saved_text.insert('end', '\n')
        self.saved_text.config(state='disabled')

        # Check if scrollbar is needed
        self.check_scrollbar_needed()

    def check_scrollbar_needed(self):
        yview = self.saved_text.yview(tk.END)
        if yview and yview[1] > 1:
            self.scrollbar.pack(side="right", fill="y")  # pack the scrollbar to make it visible
        else:
            self.scrollbar.pack_forget()  # forget the scrollbar to hide it


    def update_buttons(self):
        for letter, button in self.buttons.items():
            if not state['sequence']:  # If sequence is empty, then all 'alpha', 'beta', and 'gamma' start positions are possible
                button['state'] = 'normal'
                button['foreground'] = 'black'  # Add this line to change the button text color to black
            elif self.auto_fill_mode.get():  # Auto-fill mode is enabled
                last_letter = state['sequence'][-1]
                if positions[last_letter[0]][1] == positions[letter][0]:  # Can follow without interpolation
                    button['state'] = 'normal'
                    button['foreground'] = 'black'
                else:  # Needs interpolation
                    button['state'] = 'normal'
                    button['foreground'] = 'white'
            else:  # Auto-fill mode is not enabled
                if self.interpolation.can_follow(letter):  # Can follow without interpolation
                    button['state'] = 'normal'
                    button['foreground'] = 'black'
                else:  # Cannot follow
                    button['state'] = 'disabled'
                    button['foreground'] = 'black'


    def update_state_label(self, letter, auto_fill_mode):
        self.state_label.config(text=positions[letter][1])
        self.auto_fill_mode = auto_fill_mode

    def clear_sequence(self):
        state['sequence'].clear()
        self.sequence_label.config(state='normal')
        self.sequence_label.delete('1.0', tk.END)
        self.sequence_label.config(state='disabled')
        self.start_position_label.config(text='')
        self.update_buttons()
        self.end_positions_label.config(text='')

        if len(saved_words) == 0:
            self.scrollbar.config(state='disabled')

    def clear_saved(self):
        self.saved_text.config(state='normal')
        self.saved_text.delete('1.0', tk.END)
        self.saved_text.config(state='disabled')
        saved_words.clear()
        # Check if scrollbar is needed
        self.check_scrollbar_needed()


class ButtonEventHandlers:

    def __init__(self, root, buttons, ui_updater, interpolation, auto_fill_mode, interpolation_label, interpolation_input, interpolation_button, context_menu_sequence, context_menu_saved, sequence_label, saved_text, end_positions_label, random_word_length_input, end_at_start_position_var):
        self.root = root
        self.buttons = buttons
        self.ui_updater = ui_updater
        self.interpolation = interpolation
        self.auto_fill_mode = auto_fill_mode
        self.interpolation_label = interpolation_label
        self.interpolation_input = interpolation_input
        self.interpolation_button = interpolation_button
        self.context_menu_sequence = context_menu_sequence
        self.context_menu_saved = context_menu_saved
        self.sequence_label = sequence_label
        self.saved_text = saved_text
        self.end_positions_label = end_positions_label
        self.random_word_length_input = random_word_length_input
        self.end_at_start_position_var = end_at_start_position_var

    def copy_saved_text(self):
        saved_sequences = self.saved_text.get("1.0", 'end-1c')  # Get the text from the "Saved Sequences" textbox
        self.root.clipboard_clear()  # Clear the clipboard
        self.root.clipboard_append(saved_sequences)  # Append the text to the clipboard

    def on_auto_fill_mode_toggle(self):
        if self.auto_fill_mode.get():
            self.interpolation_label.grid(row=4, column=3, sticky='w')  # show the label
            self.interpolation_input.grid(row=5, column=3, sticky='w')  # show the input
            self.interpolation_button.grid(row=6, column=3, sticky='w')  # show the button
        else:
            self.interpolation_label.grid_remove()  # hide the label
            self.interpolation_input.grid_remove()  # hide the input
            self.interpolation_button.grid_remove()  # hide the button
        self.ui_updater.update_buttons()

    def show_context_menu(self, event, widget):
        if widget == self.sequence_label:
            self.context_menu_sequence.tk_popup(event.x_root, event.y_root)
        elif widget == self.saved_text:
            self.context_menu_saved.tk_popup(event.x_root, event.y_root)

    def copy_text(self, widget):
        try:
            selected_text = widget.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # Nothing selected, do nothing


    def on_key_press(self, event):
        if event.char.upper() in self.buttons:  # if the key pressed is one of the letters
            self.interpolation.update_state(event.char.upper(), self.auto_fill_mode)
        elif event.keysym == 'BackSpace':  # if the backspace key is pressed
            state['sequence'].pop()
            self.sequence_label.config(state='normal')
            self.sequence_label.delete('end - 2c')  # remove the last character
            self.sequence_label.config(state='disabled')

    def show_positional_outcome(self, event, letter):
        if event.type == "7":  # Mouse enters the button
            self.end_positions_label.config(text=self.interpolation.append_positional_outcome(letter))
        elif event.type == "8":  # Mouse leaves the button
            self.ui_updater.update_end_positions_label()

    def on_enter(self, e):
        letter = e.widget.cget('text')

        # Check if the letter is valid
        if self.interpolation.can_follow(letter):
            self.original_end_positions = self.end_positions_label.cget('text')

            # Get the outcome as a string
            outcome = self.interpolation.append_positional_outcome(letter)

            # Replace position names with Greek variables
            outcome = outcome.replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')

            # Append the new outcome to the original sequence
            new_positions = f"{outcome}"

            # Set the label text
            self.end_positions_label.config(text=new_positions)

    def on_leave(self, e):
        self.ui_updater.update_end_positions_label()

    def generate_random_word(self):
        if self.random_word_length_input.get().isdigit():
            word_length = int(self.random_word_length_input.get())
        else:
            word_length = 4
        if self.end_at_start_position_var.get():
            word = self.interpolation.generate_word_ending_at_start_position(word_length)  # If checkbox is checked, generate word ending at start position
        else:
            word = self.interpolation.generate_word(word_length)  # If checkbox is not checked, generate word normally

        # Add the generated word to the saved_words list
        saved_words.append([(char, False) for char in word])  # We are adding the word as a list of tuples (letter, interpolated)

        # Update the saved_words label
        self.ui_updater.update_saved_words_label()


class Interpolation:
    def __init__(self, sequence_label, start_position_label, end_positions_label, interpolation_input, auto_fill_mode, start_letters, positions):
        self.sequence_label = sequence_label
        self.start_position_label = start_position_label
        self.end_positions_label = end_positions_label
        self.interpolation_input = interpolation_input
        self.auto_fill_mode = auto_fill_mode
        self.start_letters = start_letters
        self.positions = positions

    def set_ui_updater(self, ui_updater):
        self.ui_updater = ui_updater

    def find_interpolation(self, start, end):
        valid_letters = [letter for letter, pos in positions.items() if pos[0] == positions[start][1] and pos[1] == positions[end][0]]
        if valid_letters:
            return random.choice(valid_letters)
        return None

    def find_intermediate_letters(self, start, end):
        return [letter for letter, pos in positions.items() if pos[0] == start and pos[1] == end]

    def interpolate_sequence(self):
        sequence = self.interpolation_input.get().upper()
        self.interpolation_input.delete(0, 'end')  # clear the input field
        interpolated_sequence = []
        for i in range(len(sequence) - 1):
            start = sequence[i]
            end = sequence[i + 1]
            interpolated_sequence.append((start, False))  # the user-typed letters are not interpolated
            if positions[start][1] != positions[end][0]:  # checks if the end position of current letter != start position of next letter
                interpolated = self.find_interpolation(start, end)  # use self here
                if interpolated:
                    interpolated_sequence.append((interpolated, True))  # the interpolated letters are marked as interpolated
        interpolated_sequence.append((sequence[-1], False))  # append the last letter
        # save the interpolated sequence
        saved_words.append(interpolated_sequence)
        self.ui_updater.update_saved_words_label()  # use self.ui_updater

    def update_state(self, letter, auto_fill_mode):
        if not state['sequence'] or self.can_follow(letter):  # use self here
            state['sequence'].append((letter, False))
            self.sequence_label.config(state='normal')
            self.sequence_label.insert('end', letter, 'black')
            self.sequence_label.config(state='disabled')
        elif self.auto_fill_mode.get():
            prev_letter = state['sequence'][-1]
            intermediate_letters = self.find_intermediate_letters(positions[prev_letter[0]][1], positions[letter][0])  # use self here
            if intermediate_letters:
                intermediate_letter = random.choice(intermediate_letters)
                state['sequence'].append((intermediate_letter, True))
                self.sequence_label.config(state='normal')
                self.sequence_label.insert('end', intermediate_letter, 'red')
                self.sequence_label.config(state='disabled')
                state['sequence'].append((letter, False))
                self.sequence_label.config(state='normal')
                self.sequence_label.insert('end', letter, 'black')
                self.sequence_label.config(state='disabled')
        else:
            return
        self.ui_updater.update_end_positions_label()
        if len(state['sequence']) == 1:  # if it's the first character
            start_position_str = positions[letter][0].replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
            self.start_position_label.config(text=f'Start: {start_position_str}')
        self.ui_updater.update_buttons()

    def can_follow(self, letter):
        if not state['sequence']:
            return positions[letter][0] in ['alpha', 'beta', 'gamma']
        last_letter = state['sequence'][-1]
        return positions[last_letter[0]][1] == positions[letter][0]

    def get_positional_outcome(self, sequence):
        end_positions = [positions[lt[0]][1] for lt in sequence]
        return ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')

    def append_positional_outcome(self, letter):
        end_positions = [positions[lt[0]][1] for lt in state['sequence'].copy()]  # create a copy of the sequence
        end_positions.append(positions[letter][1])
        end_positions_str = ' '.join(end_positions).replace('alpha', 'α').replace('beta', 'β').replace('gamma', 'Γ')
        return end_positions_str

    def generate_word(self, word_length):
        # Pick a random start letter
        start_letter = random.choice(self.start_letters)
        word = [start_letter]

        # Get the start and end position of the start letter
        start_position, end_position = positions[start_letter]

        # Generate the rest of the word
        while len(word) < word_length: 
            # Pick a random letter whose start position is the current end position
            next_letters = [letter for letter, pos in positions.items() if pos[0] == end_position]
            next_letter = random.choice(next_letters)

            word.append(next_letter)

            # Update the end position
            end_position = positions[next_letter][1]

        return word  # return a list of letters, not a string

    def generate_word_ending_at_start_position(self, word_length):
        # Check if word_length is 1
        if word_length == 1:
            return random.choice(self.start_letters)

        # First letter
        word = [random.choice(self.start_letters)]

        # Generate the remaining letters
        for _ in range(word_length - 2):
            # Get the current position
            current_position = self.positions[word[-1]][1]

            # Get the possible letters
            possible_letters = [letter for letter, pos in self.positions.items() if pos[0] == current_position]

            # Choose a letter
            letter = random.choice(possible_letters)

            # Add the letter to the word
            word.append(letter)

        # Get the start position of the first letter
        start_position = self.positions[word[0]][0]

        # Get the possible letters
        possible_end_letters = [letter for letter, pos in self.positions.items() if pos[0] == self.positions[word[-1]][1] and pos[1] == start_position]

        # Choose a letter
        letter = random.choice(possible_end_letters)

        # Add the letter to the word
        word.append(letter)

        return ''.join(word)
