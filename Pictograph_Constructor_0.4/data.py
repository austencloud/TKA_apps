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

compass_mapping = {
    "alpha": ("n", "s"),
    "alpha": ("w", "e"),
    "beta": ("e", "e"),
    "beta": ("s", "s"),
    "beta": ("w", "w"),
    "beta": ("n", "n"),
    "gamma": ("n", "e"),
    "gamma": ("e", "s"),
    "gamma": ("s", "w"),
    "gamma": ("w", "n"),
}

def generate_variations(arrow_combination):
    # Define the mappings for rotations and reflections
    rotation_mapping = {"n": "e", "e": "s", "s": "w", "w": "n"}
    vertical_reflection_mapping = {"n": "s", "s": "n", "e": "e", "w": "w"}
    horizontal_reflection_mapping = {"n": "n", "s": "s", "e": "w", "w": "e"}

    # Generate the rotated versions
    rotated_versions = [arrow_combination]
    for _ in range(3):
        arrow_combination = [{**arrow, "start_position": rotation_mapping[arrow["start_position"]],
                              "end_position": rotation_mapping[arrow["end_position"]]} for arrow in arrow_combination]
        rotated_versions.append(arrow_combination)

    # Generate the reflected versions
    reflected_versions = []
    for version in rotated_versions:
        vertical_reflected_version = [{**arrow, "start_position": vertical_reflection_mapping[arrow["start_position"]],
                                       "end_position": vertical_reflection_mapping[arrow["end_position"]]} for arrow in version]
        horizontal_reflected_version = [{**arrow, "start_position": horizontal_reflection_mapping[arrow["start_position"]],
                                         "end_position": horizontal_reflection_mapping[arrow["end_position"]]} for arrow in version]
        reflected_versions.extend([vertical_reflected_version, horizontal_reflected_version])

    return rotated_versions + reflected_versions
