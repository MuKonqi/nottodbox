# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2025 MuKonqi (Muhammed S.)

# Nottodbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nottodbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nottodbox.  If not, see <https://www.gnu.org/licenses/>.
    

import os
from PySide6.QtCore import QEvent, QMargins, QModelIndex, QRect, QSize, Slot
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPalette, QPixmap, QStandardItem, QStandardItemModel, QPainter, QPainterPath, QPen, Qt
from PySide6.QtWidgets import *
from .widgets.controls import HSeperator, Label, ToolButton
from .resources import icons # noqa: F401


class Sidebar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.old_index = 0
        
        self.icons = ["home", "settings", "about", "focus"]
        
        self.buttons = [
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 0), self.tr("Home"), True, None, 60),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 1), self.tr("Settings"), True, None, 60),
            ToolButton(self, lambda checked: self.setCurrentIndex(checked, 2), self.tr("About"), True, None, 60),
            ToolButton(self, lambda: self.parent_.home.selector.setVisible(False if self.parent_.home.selector.isVisible() else True), self.tr("Focus"), True, None, 60)
        ]
        
        self.list_view = ListView(self)
        
        self.row_spinbox = QSpinBox(self)
        self.row_spinbox.setMinimum(1)
        self.row_spinbox.valueChanged.connect(lambda value: self.parent_.home.area.setArea(value, self.column_spinbox.value()))

        self.layout_label = Label(self, "x")
        self.layout_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.column_spinbox = QSpinBox(self)
        self.column_spinbox.setMinimum(1)
        self.column_spinbox.valueChanged.connect(lambda value: self.parent_.home.area.setArea(self.row_spinbox.value(), value))
        
        self.layout_ = QVBoxLayout(self)

        for button in self.buttons:
            self.layout_.addWidget(button)
            
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.list_view)
        self.layout_.addWidget(HSeperator(self))
        self.layout_.addWidget(self.row_spinbox)
        self.layout_.addWidget(self.layout_label)
        self.layout_.addWidget(self.column_spinbox)
        self.layout_.setContentsMargins(5, 5, 5, 5)
        
        self.setFixedWidth(70)
        self.buttons[0].setChecked(True)
       
    @Slot(bool, int) 
    def setCurrentIndex(self, checked: bool, index: int) -> None:
        if (checked and index != 0) or (not checked and self.old_index != 0):
            self.buttons[-1].setVisible(False)
            
        else:
            self.buttons[-1].setVisible(True)
        
        self.buttons[self.old_index].setChecked(False if checked else True)
        
        self.old_index = index
        
        self.parent_.setCurrentIndex(checked, index)
    
    def makeIcon(self, name: str) -> QIcon:
        return QIcon(QPixmap(f":/icons/{name}-{'dark' if QApplication.palette().color(QPalette.ColorRole.WindowText).lightness() > QApplication.palette().color(QPalette.ColorRole.Window).lightness() else 'light'}"))

    
    def refresh(self) -> None:
        for i in range(4):
            self.buttons[i].setIcon(self.makeIcon(self.icons[i]))
    
    
class ListView(QListView):
    def __init__(self, parent: Sidebar) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.items = {}

        self.model_ = QStandardItemModel(self)
        
        self.delegate = ButtonDelegate(self)
        
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setModel(self.model_)
        self.setItemDelegate(self.delegate)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
    def addItem(self, index: QModelIndex) -> None:
        item = QStandardItem()
        item.setData(False, Qt.ItemDataRole.UserRole + 1)
        item.setData(index, Qt.ItemDataRole.UserRole + 2)
        
        self.model_.appendRow(item)
        
        self.items[index] = item
        
    def removeItem(self, index: QModelIndex) -> None:
        self.model_.removeRow(self.items[index].row())
        
        del self.items[index]
        
        
class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent: ListView) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()  
                
        name = index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 101)
        
        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)
        name_fontmetrics = QFontMetrics(name_font)
        name_padding = name_fontmetrics.lineSpacing()
        
        name_rect = QRect(option.rect)
        name_rect.setLeft(option.rect.left() + name_padding)
        name_rect.setTop(option.rect.top() + name_padding)
        name_rect.setRight(option.rect.width() - name_padding)
        name_rect.setHeight(name_fontmetrics.lineSpacing())
        
        border_rect = QRect(option.rect.marginsRemoved(QMargins(5, 5, 5, 5)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 1, 1)
    
        situations = [
            bool(index.data(Qt.ItemDataRole.UserRole + 1) and index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 2) == "document"), 
            bool(option.state & QStyle.StateFlag.State_MouseOver), 
            bool(True)
            ]
        
        defaults = [
            [option.palette.base().color(), option.palette.text().color(), option.palette.text().color()],
            [option.palette.button().color(), option.palette.text().color(), option.palette.buttonText().color()],
            [option.palette.link().color(), option.palette.text().color(), option.palette.linkVisited().color()]
            ]
        
        colors = []
        
        i = 2
        
        for status in situations:
            if status:
                for j in range(3):
                    if index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 27 + j * 3 + i)[1] == None:
                        colors.append(defaults[i][j])
                        
                    else:
                        colors.append(QColor(index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 27 + j * 3 + i)[1]))
                        
                break
                    
            i -= 1
        
        border_pen = QPen(colors[2], 5)
        painter.setPen(border_pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawPath(border_path)
        painter.fillPath(border_path, colors[0])
        
        painter.restore()

        painter.setPen(colors[1])
        painter.setFont(name_font)
        painter.drawText(name_rect, QFontMetrics(name_font).elidedText(name, Qt.TextElideMode.ElideRight, name_rect.width()))
        
    def editorEvent(self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            indexes = [item.index() for item in self.parent_.items.values()]
            indexes.remove(index)
            
            for index_ in indexes:
                model.setData(index_, False, Qt.ItemDataRole.UserRole + 1)
            
            model.setData(index, True, Qt.ItemDataRole.UserRole + 1)
            
            index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 10)(index.data(Qt.ItemDataRole.UserRole + 2))
            
            if index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 2) == "document":
                index.data(Qt.ItemDataRole.UserRole + 2).data(Qt.ItemDataRole.UserRole + 11)(index.data(Qt.ItemDataRole.UserRole + 2), "normal", True)

        return super().editorEvent(event, model, option, index)
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), option.rect.width())