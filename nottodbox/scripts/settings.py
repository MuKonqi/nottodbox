# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2024-2025 MuKonqi (Muhammed S.)

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


from PySide6.QtCore import QEvent, QMargins, QModelIndex, QRect, QSize, Qt, Slot
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QPainterPath, QPen, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import *
from .widgets.controls import HSeperator, PushButton, VSeperator


class Settings(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.pages = [self.makeScrollable(Appearance(self)), self.makeScrollable(DocumentSettings(self)), self.makeScrollable(ListSettings(self))]
        
        self.widget = QStackedWidget(self)
        
        for page in self.pages:
            self.widget.addWidget(page)
        
        self.buttons = QDialogButtonBox(self)
        
        self.reset_button = PushButton(self.buttons, self.reset, self.tr("Reset"))
        self.reset_button.clicked.connect(self.reset)
        
        self.apply_button = PushButton(self.buttons, self.apply, self.tr("Apply"))
        self.apply_button.clicked.connect(self.apply)
        
        self.cancel_button = PushButton(self.buttons, self.cancel, self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.cancel)
        
        self.buttons.addButton(self.reset_button, QDialogButtonBox.ButtonRole.ResetRole)
        self.buttons.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ApplyRole)
        self.buttons.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.layout_ = QGridLayout(self)
        self.layout_.addWidget(ListView(self), 0, 0, 3, 1)
        self.layout_.addWidget(VSeperator(self), 0, 1, 3, 1)
        self.layout_.addWidget(self.widget, 0, 2, 1, 1)
        self.layout_.addWidget(HSeperator(self), 1, 2, 1, 1)
        self.layout_.addWidget(self.buttons, 2, 2, 1, 1)
        
    def askFormat(self, page: QWidget, do_not_asked_before: bool, format_change_acceptted: bool) -> tuple[bool, bool]:
        if (type(page.widget()).__name__ == "DocumentSettings" and do_not_asked_before):
                do_not_asked_before = False
                
                question = QMessageBox.question(
                    self, self.tr("Question"), self.tr("If you have documents with the format setting set to global, this change may corrupt them.\nDo you really want to apply the format setting(s)?"))
                
                if question != QMessageBox.StandardButton.Yes:
                    format_change_acceptted = False
                    
        return do_not_asked_before, format_change_acceptted
        
    @Slot()
    def apply(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True
        
        pages = self.pages
        del pages[-1]
        
        for page in pages:
            do_not_asked_before, format_change_acceptted = self.askFormat(page, do_not_asked_before, format_change_acceptted)
            
            if not page.apply(format_change_acceptted):
                successful = False
        
        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All settings applied."))
            
            else:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All settings applied EXCEPT format settings."))
            
        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to apply setting(s)."))
    
    @Slot()
    def cancel(self) -> None:
        pages = self.pages
        del pages[-1]
        
        for page in pages:
            page.load()
            
    def makeScrollable(self, page: QWidget) -> QScrollArea:
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)
        
        scroll_area.apply = page.apply
        scroll_area.load = page.load
        scroll_area.reset = page.reset
        
        return scroll_area
    
    @Slot()
    def reset(self) -> None:
        successful = True
        do_not_asked_before = True
        format_change_acceptted = True
        
        pages = self.pages
        del pages[-1]
        
        for page in pages:
            do_not_asked_before, format_change_acceptted = self.askFormat(page, do_not_asked_before, format_change_acceptted)
                          
            if not page.reset(format_change_acceptted):
                successful = False
        
        if successful:
            if format_change_acceptted:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All setting reset."))
            
            else:
                QMessageBox.information(self, self.tr("Successful"), self.tr("All settings reset EXCEPT format settings."))
            
        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to reset setting(s)."))
        
        
class ListView(QListView):
    def __init__(self, parent: Settings) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
        self.indexes = []
        
        self.localizeds = [self.tr("Appearance"), self.tr("Documents"), self.tr("Lists")]

        self.model_ = QStandardItemModel(self)
        
        for i in range(3):
            item = QStandardItem(self.localizeds[i])
            item.setData(i, Qt.ItemDataRole.UserRole + 2)
            
            self.model_.appendRow(item)
            
            self.indexes.append(item.index())
        
        self.delegate = ButtonDelegate(self)
        
        self.setFixedWidth(108)
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setModel(self.model_)
        self.setItemDelegate(self.delegate)
        self.setCurrentIndex(self.indexes[0])
        self.model_.setData(self.indexes[0], True, Qt.ItemDataRole.UserRole + 1)
    
    
class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent: ListView) -> None:
        super().__init__(parent)
        
        self.parent_ = parent
        
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        
        name = index.data(Qt.ItemDataRole.DisplayRole)
                          
        name_font = QFont(option.font)
        name_font.setWeight(QFont.Weight.Bold)
        
        name_rect = QRect(option.rect)
        name_rect.setTop(name_rect.top() + (option.rect.height() - QFontMetrics(name_font).height()) / 2)
        name_rect.setLeft(name_rect.left() + (option.rect.width() - QFontMetrics(name_font).horizontalAdvance(name)) / 2)
        name_rect.setRight(name_rect.left() + QFontMetrics(name_font).horizontalAdvance(name))
        name_rect.setBottom(name_rect.top() + QFontMetrics(name_font).height())
        
        border_rect = QRect(option.rect.marginsRemoved(QMargins(10, 10, 10, 10)))

        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, 10, 10)
    
        situations = [
            bool(index.data(Qt.ItemDataRole.UserRole + 1)), 
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
                    colors.append(defaults[i][j])
                        
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
        
        painter.drawText(name_rect, name)
        
    def editorEvent(self, event: QEvent, model: QStandardItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            indexes = self.parent_.indexes.copy()
            indexes.remove(index)
            
            for index_ in indexes:
                model.setData(index_, False, Qt.ItemDataRole.UserRole + 1)
            
            model.setData(index, True, Qt.ItemDataRole.UserRole + 1)
            self.parent_.parent_.widget.setCurrentIndex(index.data(Qt.ItemDataRole.UserRole + 2))

        return super().editorEvent(event, model, option, index)
    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QRect:
        return QSize(option.rect.width(), option.rect.width())
    
    
class Appearance(QWidget):
    def __init__(self, parent: Settings) -> None:
        super().__init__(parent)
    
    @Slot()    
    def apply(self) -> bool:
        pass
    
    @Slot()
    def load(self) -> None:
        pass
    
    @Slot()
    def reset(self) -> bool:
        pass
        
        
class DocumentSettings(QWidget):
    def __init__(self, parent: Settings) -> None:
        super().__init__(parent)
        
        self.selectors = []
        
        self.layout_ = QVBoxLayout(self)
        
    @Slot()    
    def apply(self) -> bool:
        pass
    
    @Slot()
    def load(self) -> None:
        pass
    
    @Slot()
    def reset(self) -> bool:
        pass
        
        
class ListSettings(QWidget):
    def __init__(self, parent: Settings) -> None:
        super().__init__(parent)
        
        self.selectors = []
        
        self.layout_ = QVBoxLayout(self)
        
    @Slot()    
    def apply(self) -> bool:
        pass
    
    @Slot()
    def load(self) -> None:
        pass
    
    @Slot()
    def reset(self) -> bool:
        pass