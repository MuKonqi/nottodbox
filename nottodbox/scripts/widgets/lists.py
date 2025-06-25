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


from PySide6.QtCore import QEvent, QMargins, QModelIndex, QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen, QStandardItemModel
from PySide6.QtWidgets import *


class ButtonDelegateBase(QStyledItemDelegate):
    menu_requested = Signal(QModelIndex)

    button_size = 24

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        
        name = index.data(Qt.ItemDataRole.UserRole + 101)
        
        if index.data(Qt.ItemDataRole.UserRole + 20)[1] == "completed":
            name = f"[+] {name}"
            
        elif index.data(Qt.ItemDataRole.UserRole + 20)[1] == "uncompleted":
            name = f"[-] {name}"
        
        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)
        name_fontmetrics = QFontMetrics(name_font)
        name_padding = name_fontmetrics.lineSpacing()

        name_rect = QRect(option.rect)
        name_rect.setLeft(name_rect.left() + name_padding)
        name_rect.setTop(name_rect.top() + name_padding)
        name_rect.setRight(option.rect.width())
        name_rect.setHeight(name_fontmetrics.lineSpacing())
        
        content = index.data(Qt.ItemDataRole.UserRole + 104)
        
        content_rect = QRect(option.rect)
        content_rect.setLeft(content_rect.left() + name_padding)
        content_rect.setTop(name_rect.bottom() + name_padding / 2)
        content_rect.setRight(option.rect.width() + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0) - 10)
        content_rect.setHeight(name_fontmetrics.lineSpacing())
        
        creation_date = index.data(Qt.ItemDataRole.UserRole + 102)
        
        creation_rect = QRect(option.rect)
        creation_rect.setLeft(creation_rect.left() + name_padding)
        creation_rect.setTop(content_rect.bottom() + name_padding / 2)
        creation_rect.setRight(QFontMetrics(QFont(option.font)).horizontalAdvance(creation_date) + creation_rect.left() + name_padding)
        creation_rect.setHeight(name_fontmetrics.lineSpacing())
        
        modification_date = index.data(Qt.ItemDataRole.UserRole + 103)

        modification_rect = QRect(option.rect)
        modification_rect.setLeft(option.rect.width() - QFontMetrics(QFont(option.font)).horizontalAdvance(modification_date) + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0))
        modification_rect.setTop(content_rect.bottom() + name_padding / 2)
        modification_rect.setRight(option.rect.width() + (name_padding if index.data(Qt.ItemDataRole.UserRole + 2) == "document" else 0))
        modification_rect.setHeight(name_fontmetrics.lineSpacing())
                
        painter.save()
        
        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)
        
        situations = [
            bool(index.data(Qt.ItemDataRole.UserRole + 1) and index.data(Qt.ItemDataRole.UserRole + 2) == "document"), 
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
                    if index.data(Qt.ItemDataRole.UserRole + 26 + j * 3 + i)[1] == None:
                        colors.append(defaults[i][j])
                        
                    else:
                        colors.append(QColor(index.data(Qt.ItemDataRole.UserRole + 26 + j * 3 + i)[1]))
                        
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
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignLeading, name_fontmetrics.elidedText(name, Qt.TextElideMode.ElideRight, name_rect.width()))
        
        painter.setFont(option.font)

        painter.drawText(content_rect, Qt.AlignmentFlag.AlignLeading, QFontMetrics(QFont(option.font)).elidedText(content, Qt.TextElideMode.ElideRight, content_rect.width()))
        
        painter.drawText(creation_rect, Qt.AlignmentFlag.AlignLeading, creation_date)
        painter.drawText(modification_rect, Qt.AlignmentFlag.AlignLeading, modification_date)

        painter.restore()

        button_rect = self.getButtonRect(option)
        
        painter.save()
        painter.setBrush(option.palette.text().color())
        
        dot_size = 4
        dot_padding = 8
        center_y = button_rect.center().y()
        center_x = button_rect.center().x()

        painter.drawEllipse(center_x - dot_size / 2, center_y - dot_padding - dot_size / 2, dot_size, dot_size)
        painter.drawEllipse(center_x - dot_size / 2, center_y - dot_size / 2, dot_size, dot_size)
        painter.drawEllipse(center_x - dot_size / 2, center_y + dot_padding - dot_size / 2, dot_size, dot_size)

        painter.restore()
              
    def editorEvent(self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            button_rect = self.getButtonRect(option)
            
            if event.button() == Qt.MouseButton.LeftButton:
                if button_rect.contains(event.position().toPoint()):
                    self.menu_requested.emit(index)
                    return True
                
                else:
                    model.setData(index, not index.data(Qt.ItemDataRole.UserRole + 1), Qt.ItemDataRole.UserRole + 1)

        return super().editorEvent(event, model, option, index)

    def getButtonRect(self, option: QStyleOptionViewItem) -> QRect:
        return QRect(option.rect.topRight().x() - self.button_size - 10, option.rect.topRight().y(), self.button_size, option.rect.height())

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), 108)
    

class TreeViewBase(QTreeView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
    @Slot(QModelIndex, QModelIndex)
    def rowChanged(self, new: QModelIndex, old: QModelIndex) -> None:
        self.model().setData(old, False, Qt.ItemDataRole.UserRole + 1)