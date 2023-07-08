from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF
from objects import Arrow
from PyQt5.QtWidgets import QGraphicsItem, QToolTip
from PyQt5.QtSvg import QSvgRenderer
import os
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QFont, QPen, QColor, QBrush, QCursor, QTransform
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QTimer, Qt

class Artboard(QGraphicsView):
    arrowMoved = pyqtSignal()

    def __init__(self, scene: QGraphicsScene, grid, infotracker, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.dragging = None
        self.grid = grid

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setInteractive(True)
        scene.setBackgroundBrush(Qt.white) 
        self.infoTracker = infotracker

    def get_attributes(self):
        attributes = {}
        base_name = os.path.basename(self.svg_file)
        parts = base_name.split('_')

        attributes['color'] = parts[0]
        attributes['type'] = parts[1]
        attributes['rotation'] = 'Clockwise' if parts[2] == 'r' else 'Anticlockwise'
        attributes['quadrant'] = parts[3].split('.')[0]

        return attributes

    def resizeEvent(self, event):
        self.setSceneRect(QRectF(self.rect()))
        super().resizeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
        item = self.itemAt(event.pos())
        if isinstance(item, Arrow):
            item.in_artboard = True
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        self.last_known_pos = event.pos()  # Store the last known position
        if event.mimeData().hasFormat('text/plain'):
            dropped_svg = event.mimeData().text()
            base_name = os.path.basename(dropped_svg)
            color, type_, rotation, quadrant = base_name.split('_')[:4]
            for item in self.scene().items():
                if isinstance(item, Arrow):
                    if item.color == color:
                        event.ignore()
                        QToolTip.showText(QCursor.pos(), "Cannot add another arrow of the same color.")
                        return
            event.accept()
            QToolTip.hideText()  # Hide the tooltip when the event is accepted
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        item = self.itemAt(self.last_known_pos)
        if isinstance(item, Arrow):
            item.in_artboard = False
        super().dragLeaveEvent(event)
        
    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            dropped_svg = event.mimeData().text()

            self.arrow_item = Arrow(dropped_svg, self, self.infoTracker)
            self.arrow_item.setScale(10.0)
            

            self.scene().addItem(self.arrow_item)
            self.arrow_item.setPos(self.mapToScene(event.pos()))

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

            base_name = os.path.basename(self.arrow_item.svg_file)

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
                new_svg = self.arrow_item.svg_file

            new_renderer = QSvgRenderer(new_svg)

            if new_renderer.isValid():
                self.arrow_item.setSharedRenderer(new_renderer)
                self.arrow_item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        items = self.items(event.pos())
        if items and items[0].flags() & QGraphicsItem.ItemIsMovable:
            if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
                items[0].setSelected(not items[0].isSelected())
            elif not items[0].isSelected():
                for item in self.scene().selectedItems():
                    item.setSelected(False)
                items[0].setSelected(True)
            self.dragging = items[0]
            self.dragOffset = self.mapToScene(event.pos()) - self.dragging.pos()
            self.drag = Update_Quadrant_Preview(self, self.dragging)


        else:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.dragging = None

        if event.button() == Qt.LeftButton and not items:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.arrowMoved.emit()
            new_pos = self.mapToScene(event.pos()) - self.dragOffset
            movement = new_pos - self.dragging.pos()
            for item in self.scene().selectedItems():
                item.setPos(item.pos() + movement)

                if isinstance(item, Arrow):
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

                    item.quadrant = quadrant
                    base_name = os.path.basename(item.svg_file)

                    if base_name.startswith('red_anti'):
                        new_svg = f'images\\arrows\\red\\{item.rotation}\\anti\\red_anti_{item.rotation}_{quadrant}.svg'
                    elif base_name.startswith('red_iso'):
                        new_svg = f'images\\arrows\\red\\{item.rotation}\\iso\\red_iso_{item.rotation}_{quadrant}.svg'
                    elif base_name.startswith('blue_anti'):
                        new_svg = f'images\\arrows\\blue\\{item.rotation}\\anti\\blue_anti_{item.rotation}_{quadrant}.svg'
                    elif base_name.startswith('blue_iso'):
                        new_svg = f'images\\arrows\\blue\\{item.rotation}\\iso\\blue_iso_{item.rotation}_{quadrant}.svg'
                    else:
                        print(f"Unexpected svg_file: {item.svg_file}")
                        new_svg = item.svg_file 
                    
                    new_renderer = QSvgRenderer(new_svg)

                    if new_renderer.isValid():
                        item.setSharedRenderer(new_renderer)
                        item.svg_file = new_svg

                        # Update the start and end positions
                        item.update_positions()

                        item.replacement_arrow_printed = False
                            #print the qualities of the replacement arrow just once
                        if item.replacement_arrow_printed == False:
                            item.replacement_arrow_printed = True

                    else:
                        print("Failed to load SVG file:", new_svg)
                    self.arrowMoved.emit()  # emit the signal after the item's position has been updated
            self.arrowMoved.emit()

    def mouseReleaseEvent(self, event):
        self.dragging = None
        self.setRubberBandSelectionMode(Qt.ContainsItemShape)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        super().mouseReleaseEvent(event)

class Update_Quadrant_Preview(QDrag):
    def __init__(self, source, arrow_item, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.arrow_item = arrow_item
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePixmap)

    def exec_(self, *args, **kwargs):
        self.timer.start(100)
        result = super().exec_(*args, **kwargs)
        self.timer.stop()
        return result

    def updatePixmap(self):
        mouse_pos = self.source().mapFromGlobal(self.source().cursor().pos())

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

        base_name = os.path.basename(self.mimeData().text())

        if base_name.startswith('red_anti'):
            new_svg = f'images\\arrows\\red\\{self.arrow_item.rotation}\\anti\\red_anti_{self.arrow_item.rotation}_{quadrant}.svg'
        elif base_name.startswith('red_iso'):
            new_svg = f'images\\arrows\\red\\{self.arrow_item.rotation}\\iso\\red_iso_{self.arrow_item.rotation}_{quadrant}.svg'
        elif base_name.startswith('blue_anti'):
            new_svg = f'images\\arrows\\blue\\{self.arrow_item.rotation}\\anti\\blue_anti_{self.arrow_item.rotation}_{quadrant}.svg'
        elif base_name.startswith('blue_iso'):
            new_svg = f'images\\arrows\\blue\\{self.arrow_item.rotation}\\iso\\blue_iso_{self.arrow_item.rotation}_{quadrant}.svg'
        else:
            print(f"Unexpected svg_file: {self.arrow_item.svg_file}")
            new_svg = self.arrow_item.svg_file

        new_svg = f'images\\arrows\\red\\r\\anti\\red_anti_r_{quadrant}.svg'

        new_renderer = QSvgRenderer(new_svg)

        if new_renderer.isValid():
            pixmap = QPixmap(self.pixmap().size())
            painter = QPainter(pixmap)
            new_renderer.render(painter)
            painter.end()
            self.setPixmap(pixmap)


