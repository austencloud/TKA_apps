from svgutils.transform import fromfile, GroupElement

def rotate_and_mirror_svg(input_file, output_file, angle, mirror):
    # Load the original SVG
    svg = fromfile(input_file)
    root = svg.getroot()

    # Create a group and add all elements of the original SVG to this group
    group = GroupElement()
    for element in root.getchildren():
        group.append(element)

    # Apply rotation
    group.rotate(angle, *root.center)

    # Apply mirroring (scaling by -1 in the x direction)
    if mirror:
        group.scale(-1, 1)

    # Replace the original SVG elements with the transformed group
    root[:] = [group]

    # Save the transformed SVG
    svg.save(output_file)

# Test the function
rotate_and_mirror_svg('images\\arrows_copy\\blue_anti.svg', 'images\\arrows_copy\\blue_anti_rotated_and_mirrored.svg', 90, True)
