from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from arrows import Arrow_Logic
from PyQt5.QtWidgets import QGraphicsItem


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
            arrow_item = Arrow_Logic(dropped_svg)
            arrow_item.setScale(8.0)

            # Add the new DraggableSvg item to the scene at the drop location
            self.scene().addItem(arrow_item)
            arrow_item.setPos(self.mapToScene(event.pos()))
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

    def mouseReleaseEvent(self, event):
        self.dragging = None
        # Clear the rubber band
        self.setRubberBandSelectionMode(Qt.ContainsItemShape)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        super().mouseReleaseEvent(event)
