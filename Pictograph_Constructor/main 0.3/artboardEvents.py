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

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setInteractive(True)
        scene.setBackgroundBrush(Qt.white)

    def resizeEvent(self, event):
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
            dropped_svg = event.mimeData().text()

            self.arrow_item = Arrow_Logic(dropped_svg, self)
            self.arrow_item.setScale(8.0)

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
            self.drag = Update_Arrow_Drag_Preview(self, self.dragging)


        else:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.dragging = None

        if event.button() == Qt.LeftButton and not items:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToScene(event.pos()) - self.dragOffset
            movement = new_pos - self.dragging.pos()
            for item in self.scene().selectedItems():
                item.setPos(item.pos() + movement)

                if isinstance(item, Arrow_Logic):
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
                    base_name = os.path.basename(item.svg_file)

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
                        new_svg = item.svg_file 

                    new_renderer = QSvgRenderer(new_svg)

                    if new_renderer.isValid():
                        item.setSharedRenderer(new_renderer)
                        item.svg_file = new_svg
                    else:
                        print("Failed to load SVG file:", new_svg)

    def mouseReleaseEvent(self, event):
        self.dragging = None
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

        new_svg = f'images\\arrows\\red\\r\\anti\\red_anti_r_{quadrant}.svg'

        new_renderer = QSvgRenderer(new_svg)

        if new_renderer.isValid():
            pixmap = QPixmap(self.pixmap().size())
            painter = QPainter(pixmap)
            new_renderer.render(painter)
            painter.end()
            self.setPixmap(pixmap)
