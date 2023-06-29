import random
import itertools


class Interpolation:
    def __init__(self, start_letters, positions):
        self.start_letters = start_letters
        self.positions = positions

    def find_interpolation(self, start, end):
        valid_letters = [letter for letter, pos in self.positions.items() 
                         if pos[0] == self.positions[start][1] and pos[1] == self.positions[end][0]]
        if valid_letters:
            return random.choice(valid_letters)
        return None

    def interpolate_sequence(self, sequence):
        interpolated_sequence = []
        for i in range(len(sequence) - 1):
            start = sequence[i]
            end = sequence[i + 1]
            interpolated_sequence.append(start)  # add the initial letter to the sequence
            if self.positions[start][1] != self.positions[end][0]:
                interpolated = self.find_interpolation(start, end)
                if interpolated:
                    interpolated_sequence.append(interpolated)
        interpolated_sequence.append(sequence[-1])  # append the last letter
        return interpolated_sequence


    def generate_word(self, length, circular=False):
        if circular:
            return self.generate_word_ending_at_start_position(length)
        
        letters = list(self.positions.keys())
        word = [random.choice(self.start_letters)]
        for _ in range(length-1):
            possible_next_letters = [letter for letter in letters if self.positions[word[-1]][1] == self.positions[letter][0]]
            next_letter = random.choice(possible_next_letters)
            word.append(next_letter)
        return ''.join(word)

    def generate_word_ending_at_start_position(self, word_length):
        if word_length == 1:
            return random.choice(self.start_letters)
        word = [random.choice(self.start_letters)]
        for _ in range(word_length - 2):
            current_position = self.positions[word[-1]][1]
            possible_letters = [letter for letter, pos in self.positions.items() if pos[0] == current_position]
            letter = random.choice(possible_letters)
            word.append(letter)
        start_position = self.positions[word[0]][0]
        possible_end_letters = [letter for letter, pos in self.positions.items() 
                                if pos[0] == self.positions[word[-1]][1] and pos[1] == start_position]
        letter = random.choice(possible_end_letters)
        word.append(letter)
        return ''.join(word)

    def generate_all_valid_words(self, length):
        letters = list(self.positions.keys())
        # Generate all combinations of letters of the given length
        all_combinations = list(itertools.product(letters, repeat=length))
        # Filter out the invalid combinations
        valid_combinations = [''.join(combination) for combination in all_combinations if self.is_word_valid(''.join(combination))]
        return valid_combinations
    
    def is_word_valid(self, word):
        for i in range(len(word) - 1):
            if self.positions[word[i]][1] != self.positions[word[i+1]][0]:
                return False
        return True

