class Info_Tracker():
    def __init__(self, view, InfoTracker):
        self.view = view
        self.InfoTracker = InfoTracker

    def updateInfoTracker(self):
        selectedItems = self.view.scene().selectedItems()
        text = ""
        for item in selectedItems:
            if isinstance(item, Arrow_Logic):
                attributes = item.get_attributes()
                text += f"Color: {attributes['color']}\n"
                text += f"Quadrant: {attributes['quadrant'].upper()}\n"
                text += f"Rotation: {attributes['rotation']}\n"
                text += f"Type: {attributes['type'].capitalize()}\n"
                text += "\n"
            self.InfoTracker.setText(text)
            
            for i in range(len(selectedItems)):
                for j in range(i+1, len(selectedItems)):
                    item1 = selectedItems[i]
                    item2 = selectedItems[j]
                    if isinstance(item1, Arrow_Logic) and isinstance(item2, Arrow_Logic):
                        # Check the properties of item1 and item2 to determine the letter
                        if item1.rotation == item2.rotation:
                            if item1.type == item2.type == "iso":
                                text += "Letter: A\n"
                            elif item1.type == item2.type == "anti":
                                text += "Letter: B\n"
                        elif item1.type != item2.type:
                            text += "Letter: C\n"
            
