from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from arrows import Arrow_Logic
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtSvg import QSvgRenderer
import os
from PyQt5.QtGui import QDrag, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QTimer, Qt

class Artboard_Events(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, grid, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.dragging = None
        self.grid = grid 

        # Set the drag mode to QGraphicsView::RubberBandDrag
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Set the QGraphicsView to interactive mode
        self.setInteractive(True)

        # Set a background for the QGraphicsScene
        scene.setBackgroundBrush(Qt.white)

    def resizeEvent(self, event):
        # Adjust the scene's rectangle to match the view's rectangle
        self.setSceneRect(QRectF(self.rect()))
        super().resizeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()

            # Get the SVG file from the MIME data
            dropped_svg = event.mimeData().text()

            # Create a new DraggableSvg item
            self.arrow_item = Arrow_Logic(dropped_svg)
            self.arrow_item.setScale(8.0)

            # Add the new DraggableSvg item to the scene at the drop location
            self.scene().addItem(self.arrow_item)
            self.arrow_item.setPos(self.mapToScene(event.pos()))

            # Determine the quadrant of the scene the arrow is in
            if self.arrow_item.pos().y() < self.sceneRect().height() / 2:
                if self.arrow_item.pos().x() < self.sceneRect().width() / 2:
                    quadrant = 'nw'
                else:
                    quadrant = 'ne'
            else:
                if self.arrow_item.pos().x() < self.sceneRect().width() / 2:
                    quadrant = 'sw'
                else:
                    quadrant = 'se'

            # Get the base name of the file path
            base_name = os.path.basename(self.arrow_item.svg_file)

            # Replace the arrow with the corresponding form
            if base_name.startswith('red_anti'):
                new_svg = f'images\\arrows\\red\\{self.arrow_item.orientation}\\anti\\red_anti_{self.arrow_item.orientation}_{quadrant}.svg'
            elif base_name.startswith('red_iso'):
                new_svg = f'images\\arrows\\red\\{self.arrow_item.orientation}\\iso\\red_iso_{self.arrow_item.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_anti'):
                new_svg = f'images\\arrows\\blue\\{self.arrow_item.orientation}\\anti\\blue_anti_{self.arrow_item.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_iso'):
                new_svg = f'images\\arrows\\blue\\{self.arrow_item.orientation}\\iso\\blue_iso_{self.arrow_item.orientation}_{quadrant}.svg'
            else:
                print(f"Unexpected svg_file: {self.arrow_item.svg_file}")
                new_svg = self.arrow_item.svg_file  # use the current svg file as a fallback

            # Create a new QSvgRenderer
            new_renderer = QSvgRenderer(new_svg)

            # Check if the new renderer is valid
            if new_renderer.isValid():
                # If the new renderer is valid, set it as the shared renderer of the item
                self.arrow_item.setSharedRenderer(new_renderer)
                # Update the svg_file attribute of the item
                self.arrow_item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        items = self.items(event.pos())
        if items and items[0].flags() & QGraphicsItem.ItemIsMovable:
            if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
                # If the Control key is pressed, toggle the selection of the item under the cursor
                items[0].setSelected(not items[0].isSelected())
            elif not items[0].isSelected():
                # If the item under the cursor is not already selected, select it and deselect all other items
                for item in self.scene().selectedItems():
                    item.setSelected(False)
                items[0].setSelected(True)
            self.dragging = items[0]
            self.dragOffset = self.mapToScene(event.pos()) - self.dragging.pos()
            self.drag = Update_Arrow_Drag_Preview(self, self.dragging)


        else:
            # If there is no item under the cursor, deselect all items
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.dragging = None

        # Call the base class's mousePressEvent if the left button is pressed and there are no items under the cursor.
        if event.button() == Qt.LeftButton and not items:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Calculate the new position for the dragging item
            new_pos = self.mapToScene(event.pos()) - self.dragOffset

            # Calculate the movement vector
            movement = new_pos - self.dragging.pos()

            # Move all selected items by the movement vector
            for item in self.scene().selectedItems():
                item.setPos(item.pos() + movement)

                # Check if the item is an Arrow_Logic instance
                if isinstance(item, Arrow_Logic):
                    # Determine the quadrant of the scene the arrow is in
                    if item.pos().y() < self.sceneRect().height() / 2:
                        if item.pos().x() < self.sceneRect().width() / 2:
                            quadrant = 'nw'
                        else:
                            quadrant = 'ne'
                    else:
                        if item.pos().x() < self.sceneRect().width() / 2:
                            quadrant = 'sw'
                        else:
                            quadrant = 'se'

                    # Get the base name of the file path
                    base_name = os.path.basename(item.svg_file)

                    # Replace the arrow with the corresponding form
                    if base_name.startswith('red_anti'):
                        new_svg = f'images\\arrows\\red\\{item.orientation}\\anti\\red_anti_{item.orientation}_{quadrant}.svg'
                    elif base_name.startswith('red_iso'):
                        new_svg = f'images\\arrows\\red\\{item.orientation}\\iso\\red_iso_{item.orientation}_{quadrant}.svg'
                    elif base_name.startswith('blue_anti'):
                        new_svg = f'images\\arrows\\blue\\{item.orientation}\\anti\\blue_anti_{item.orientation}_{quadrant}.svg'
                    elif base_name.startswith('blue_iso'):
                        new_svg = f'images\\arrows\\blue\\{item.orientation}\\iso\\blue_iso_{item.orientation}_{quadrant}.svg'
                    else:
                        print(f"Unexpected svg_file: {item.svg_file}")
                        new_svg = item.svg_file  # use the current svg file as a fallback

                    # Create a new QSvgRenderer
                    new_renderer = QSvgRenderer(new_svg)

                    # Check if the new renderer is valid
                    if new_renderer.isValid():
                        # If the new renderer is valid, set it as the shared renderer of the item
                        item.setSharedRenderer(new_renderer)
                        # Update the svg_file attribute of the item
                        item.svg_file = new_svg
                    else:
                        print("Failed to load SVG file:", new_svg)

    def mouseReleaseEvent(self, event):
        self.dragging = None
        # Clear the rubber band
        self.setRubberBandSelectionMode(Qt.ContainsItemShape)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        super().mouseReleaseEvent(event)

class Update_Arrow_Drag_Preview(QDrag):
    def __init__(self, source, arrow_item, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.arrow_item = arrow_item
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePixmap)

    def exec_(self, *args, **kwargs):
        self.timer.start(100)  # Update the pixmap every 100 ms
        result = super().exec_(*args, **kwargs)
        self.timer.stop()
        return result


    def updatePixmap(self):
        # Determine the current mouse position relative to the artboard
        mouse_pos = self.source().mapFromGlobal(self.source().cursor().pos())

        # Determine the quadrant of the scene the arrow is in
        if mouse_pos.y() < self.source().sceneRect().height() / 2:
            if mouse_pos.x() < self.source().sceneRect().width() / 2:
                quadrant = 'nw'
            else:
                quadrant = 'ne'
        else:
            if mouse_pos.x() < self.source().sceneRect().width() / 2:
                quadrant = 'sw'
            else:
                quadrant = 'se'

        # Get the base name of the file path
        base_name = os.path.basename(self.mimeData().text())

        # Replace the arrow with the corresponding form

        if base_name.startswith('red_anti'):
            new_svg = f'images\\arrows\\red\\{self.arrow_item.orientation}\\anti\\red_anti_{self.arrow_item.orientation}_{quadrant}.svg'
        elif base_name.startswith('red_iso'):
            new_svg = f'images\\arrows\\red\\{self.arrow_item.orientation}\\iso\\red_iso_{self.arrow_item.orientation}_{quadrant}.svg'
        elif base_name.startswith('blue_anti'):
            new_svg = f'images\\arrows\\blue\\{self.arrow_item.orientation}\\anti\\blue_anti_{self.arrow_item.orientation}_{quadrant}.svg'
        elif base_name.startswith('blue_iso'):
            new_svg = f'images\\arrows\\blue\\{self.arrow_item.orientation}\\iso\\blue_iso_{self.arrow_item.orientation}_{quadrant}.svg'
        else:
            print(f"Unexpected svg_file: {self.arrow_item.svg_file}")
            new_svg = self.arrow_item.svg_file  # use the current svg file as a fallback

        new_svg = f'images\\arrows\\red\\r\\anti\\red_anti_r_{quadrant}.svg'

        # Create a new QSvgRenderer
        new_renderer = QSvgRenderer(new_svg)

        # Check if the new renderer is valid
        if new_renderer.isValid():
            # Create a new QPixmap and QPainter
            pixmap = QPixmap(self.pixmap().size())
            painter = QPainter(pixmap)

            # Render the new SVG file onto the QPixmap
            new_renderer.render(painter)

            # End the QPainter operation
            painter.end()

            # Set the new QPixmap as the pixmap of the drag object
            self.setPixmap(pixmap)
