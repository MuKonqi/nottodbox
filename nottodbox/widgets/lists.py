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


from PySide6.QtCore import QEvent, QMargins, QModelIndex, QRect, QSize, QPoint, Qt, Signal, Slot
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QPainterPath, QPen, QStandardItemModel
from PySide6.QtWidgets import *
from .controls import Action


class ButtonDelegate(QStyledItemDelegate):
    menu_requested = Signal(QModelIndex)

    button_size = 24

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        
        name = index.data(Qt.ItemDataRole.UserRole + 10)
        
        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)
        name_fontmetrics = QFontMetrics(name_font)
        name_padding = name_fontmetrics.lineSpacing()

        name_rect = QRect(option.rect)
        name_rect.setLeft(name_rect.left() + name_padding)
        name_rect.setTop(name_rect.top() + name_padding)
        name_rect.setRight(option.rect.width())
        name_rect.setHeight(name_fontmetrics.lineSpacing())
        
        content = index.data(Qt.ItemDataRole.UserRole + 11)
        
        content_rect = QRect(option.rect)
        content_rect.setLeft(content_rect.left() + name_padding)
        content_rect.setTop(name_rect.bottom() + name_padding / 2)
        content_rect.setRight(option.rect.width() + (name_padding if option.rect.width() == 268 else 0) - 10)
        content_rect.setHeight(name_fontmetrics.lineSpacing())
        
        creation_date = index.data(Qt.ItemDataRole.UserRole + 12)
        
        creation_rect = QRect(option.rect)
        creation_rect.setLeft(creation_rect.left() + name_padding)
        creation_rect.setTop(content_rect.bottom() + name_padding / 2)
        creation_rect.setRight(QFontMetrics(QFont(option.font)).horizontalAdvance(creation_date) + creation_rect.left() + name_padding)
        creation_rect.setHeight(name_fontmetrics.lineSpacing())
        
        modification_date = index.data(Qt.ItemDataRole.UserRole + 13)

        modification_rect = QRect(option.rect)
        modification_rect.setLeft(option.rect.width() - QFontMetrics(QFont(option.font)).horizontalAdvance(modification_date) + (name_padding if option.rect.width() == 268 else 0))
        modification_rect.setTop(content_rect.bottom() + name_padding / 2)
        modification_rect.setRight(option.rect.width() + (name_padding if option.rect.width() == 268 else 0))
        modification_rect.setHeight(name_fontmetrics.lineSpacing())
                
        painter.save()
        
        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)
        
        border_pen = QPen(option.palette.linkVisited().color() if index.data(Qt.ItemDataRole.UserRole + 1) else option.palette.buttonText().color() if option.state & QStyle.StateFlag.State_MouseOver else option.palette.text().color(), 5)
        painter.setPen(border_pen)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawPath(border_path)
        painter.fillPath(border_path, option.palette.link().color() if index.data(Qt.ItemDataRole.UserRole + 1) else option.palette.button().color() if option.state & QStyle.StateFlag.State_MouseOver else option.palette.base().color())
        
        painter.restore()

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
            if event.button() == Qt.MouseButton.LeftButton:
                button_rect = self.getButtonRect(option)
                
                if button_rect.contains(event.position().toPoint()):
                    self.menu_requested.emit(index)
                    
            model.setData(index, not index.data(Qt.ItemDataRole.UserRole + 1), Qt.ItemDataRole.UserRole + 1)

        return super().editorEvent(event, model, option, index)

    def getButtonRect(self, option: QStyleOptionViewItem) -> QRect:
        return QRect(option.rect.topRight().x() - self.button_size - 10, option.rect.topRight().y(), self.button_size, option.rect.height())

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), 108)
    

class TreeViewBase(QTreeView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.delegate = ButtonDelegate(self)
        self.delegate.menu_requested.connect(self.openMenu)
        
        self.setItemDelegate(self.delegate)
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customContextMenuRequested.connect(self.openMenu)
        
    @Slot(QPoint or QModelIndex)
    def openMenu(self, context_data: QPoint | QModelIndex):
        index = None
        position = None
        
        if isinstance(context_data, QModelIndex):
            index = context_data

            visual_rect = self.visualRect(index)
            global_pos = self.viewport().mapToGlobal(visual_rect.bottomRight())
            
            global_pos.setX(global_pos.x() - 16)
            global_pos.setY(global_pos.y() - 36)

        elif isinstance(context_data, QPoint):
            position = context_data
            index = self.indexAt(position)
            global_pos = self.viewport().mapToGlobal(position)
        
        if not index or not index.isValid():
            return
            
        menu = QMenu()
        menu.addAction(Action(self, lambda: self.createDocument(index), self.tr("Create Document")))
        menu.addAction(Action(self, lambda: self.createNotebook(index), self.tr("Create Notebook")))
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "document":
            menu.addSeparator()
            menu.addAction(Action(self, lambda: self.open(index), self.tr("Open")))
            menu.addAction(Action(self, lambda: self.showBackup(index), self.tr("Show Backup")))
            menu.addAction(Action(self, lambda: self.restoreContent(index), self.tr("Restore Content")))
            menu.addAction(Action(self, lambda: self.clearContent(index), self.tr("Clear Content")))
        
        menu.addSeparator()
        menu.addAction(Action(self, lambda: self.rename(index), self.tr("Rename")))
        menu.addAction(Action(self, lambda: self.delete(index), self.tr("Delete")))
        
        if index.data(Qt.ItemDataRole.UserRole + 2) == "notebook":
            menu.addSeparator()
            menu.addAction(Action(self, lambda: self.deleteAllDocuments(index), self.tr("Delete All Documents")))
                
        menu.exec(global_pos)
        
    @Slot(QModelIndex, QModelIndex)
    def rowChanged(self, new: QModelIndex, old: QModelIndex) -> None:
        self.model().setData(old, False, Qt.ItemDataRole.UserRole + 1)