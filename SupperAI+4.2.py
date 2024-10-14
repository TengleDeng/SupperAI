import sys
import os
import json
import time
import pyautogui
import pyperclip
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QHBoxLayout,
    QVBoxLayout, QTextEdit, QPushButton, QLabel,
    QAction, QToolBar, QComboBox, QMenu, QSizePolicy,
    QMessageBox, QTabWidget, QListWidget,
    QListWidgetItem, QSplitter, QDialog, QTabBar, QFrame, QDockWidget, QShortcut, QInputDialog, QActionGroup, QLineEdit, QToolButton, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,QAbstractItemView
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import Qt, QUrl, QStandardPaths, QTimer, QSize, QRect, QPoint
from PyQt5.QtGui import QIcon, QColor, QPalette, QKeySequence, QCursor, QScreen, QTextCharFormat, QFont, QFontMetrics

class CoordinateSettingDialog(QDialog):
    # 保持不变
    def __init__(self, platform_name, current_coords, parent=None):
        super().__init__(parent)
        self.platform_name = platform_name
        self.setWindowTitle(f"设置 {platform_name} 的坐标和发送方式")
        self.current_coords = current_coords  # Dict with possible keys: 'textbox', 'send_button', 'send_method', 'zoom_factor'
        self.initUI()

    def initUI(self):
        # 保持不变
        layout = QVBoxLayout()

        self.info_label = QLabel("点击 '设置' 按钮，然后在 5 秒内移动鼠标到目标位置并点击。")
        layout.addWidget(self.info_label)

        self.textbox_btn = QPushButton("设置文本框坐标")
        self.textbox_btn.clicked.connect(self.set_textbox_coordinate)
        layout.addWidget(self.textbox_btn)

        self.send_btn = QPushButton("设置发送按钮坐标")
        self.send_btn.clicked.connect(self.set_send_button_coordinate)
        layout.addWidget(self.send_btn)

        self.send_method_label = QLabel("选择发送方式:")
        layout.addWidget(self.send_method_label)

        self.send_method_combo = QComboBox()
        self.send_method_combo.addItem("JavaScript 注入发送", "javascript")
        self.send_method_combo.addItem("按回车键发送", "enter")
        self.send_method_combo.addItem("点击发送按钮", "button")
        layout.addWidget(self.send_method_combo)

        # 添加缩放比例设置
        self.zoom_factor_label = QLabel("设置浏览器缩放比例 (例如 1.0, 1.25, 1.5):")
        layout.addWidget(self.zoom_factor_label)
        self.zoom_factor_input = QLineEdit()
        layout.addWidget(self.zoom_factor_input)

        self.confirm_btn = QPushButton("完成")
        self.confirm_btn.clicked.connect(self.accept)
        layout.addWidget(self.confirm_btn)

        self.setLayout(layout)

        # 初始化发送方式
        if 'send_method' in self.current_coords:
            index = self.send_method_combo.findData(self.current_coords['send_method'])
            if index != -1:
                self.send_method_combo.setCurrentIndex(index)

        # 初始化缩放比例
        if 'zoom_factor' in self.current_coords:
            self.zoom_factor_input.setText(str(self.current_coords['zoom_factor']))
        else:
            self.zoom_factor_input.setText('1.0')  # 默认值

        self.new_textbox_coordinate = None
        self.new_send_button_coordinate = None

    def set_textbox_coordinate(self):
        QMessageBox.information(self, "设置文本框坐标", "请在 5 秒内移动鼠标到文本框位置并点击。")
        QTimer.singleShot(5000, self.capture_textbox_coordinate)

    def capture_textbox_coordinate(self):
        x, y = pyautogui.position()
        self.new_textbox_coordinate = (x, y)
        QMessageBox.information(self, "坐标已捕获", f"文本框坐标已设置为：{self.new_textbox_coordinate}")

    def set_send_button_coordinate(self):
        QMessageBox.information(self, "设置发送按钮坐标", "请在 5 秒内移动鼠标到发送按钮位置并点击。")
        QTimer.singleShot(5000, self.capture_send_button_coordinate)

    def capture_send_button_coordinate(self):
        x, y = pyautogui.position()
        self.new_send_button_coordinate = (x, y)
        QMessageBox.information(self, "坐标已捕获", f"发送按钮坐标已设置为：{self.new_send_button_coordinate}")

    def get_coordinates(self):
        # 返回设置的坐标和参数
        send_method = self.send_method_combo.currentData()
        zoom_factor_text = self.zoom_factor_input.text()
        try:
            zoom_factor = float(zoom_factor_text)
        except ValueError:
            zoom_factor = self.current_coords.get('zoom_factor', 1.0)

        return {
            'textbox': self.new_textbox_coordinate if self.new_textbox_coordinate else self.current_coords.get('textbox'),
            'send_button': self.new_send_button_coordinate if self.new_send_button_coordinate else self.current_coords.get('send_button'),
            'send_method': send_method if send_method else self.current_coords.get('send_method', 'enter'),
            'zoom_factor': zoom_factor
        }


class HistoryListItem(QWidget):
    # 保持不变
    def __init__(self, text, timestamp=None, parent=None, max_lines=3):
        super().__init__(parent)
        self.text = text
        self.timestamp = timestamp
        self.max_lines = max_lines
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setToolTip(self.text)  # Show full text on hover
        self.text_label.setStyleSheet("""
            QLabel {
                qproperty-alignment: AlignLeft;
            }
        """)
        # 设置文本，限制行数
        self.setTextWithLineLimit(self.text_label, self.text, self.max_lines)
        layout.addWidget(self.text_label)

        self.time_label = QLabel(self.timestamp)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.time_label.setFixedWidth(100)
        layout.addWidget(self.time_label)

        self.favorite_button = QPushButton("收藏")
        self.favorite_button.setFixedWidth(50)
        layout.addWidget(self.favorite_button)

        self.setLayout(layout)

    def setTextWithLineLimit(self, label, text, max_lines):
        font_metrics = QFontMetrics(label.font())
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            words = line.split()
            current_line = ''
            for word in words:
                if font_metrics.width(current_line + ' ' + word) > label.width():
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line += ' ' + word if current_line else word
                if len(lines) >= max_lines:
                    break
            else:
                lines.append(current_line)
            if len(lines) >= max_lines:
                break
        display_text = '\n'.join(lines)
        if len(lines) >= max_lines:
            display_text += '...'
        label.setText(display_text)


class PromptTab(QWidget):
    def __init__(self, prompt_manager, parent=None, title="提示词"):
        super().__init__(parent)
        self.prompt_manager = prompt_manager
        self.title = title
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 添加格式工具栏
        formatting_toolbar = QToolBar()
        formatting_toolbar.setIconSize(QSize(16, 16))

        # Bold action
        self.bold_action = QAction("B", self)
        self.bold_action.setShortcut(QKeySequence.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.toggle_bold)
        formatting_toolbar.addAction(self.bold_action)

        # Italic action
        self.italic_action = QAction("I", self)
        self.italic_action.setShortcut(QKeySequence.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.toggle_italic)
        formatting_toolbar.addAction(self.italic_action)

        # Underline action
        self.underline_action = QAction("U", self)
        self.underline_action.setShortcut(QKeySequence.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.toggle_underline)
        formatting_toolbar.addAction(self.underline_action)

        # Font size combo box
        self.font_size_combo = QComboBox()
        font_sizes = [str(size) for size in range(8, 30)]
        self.font_size_combo.addItems(font_sizes)
        self.font_size_combo.setCurrentText(str(int(QApplication.font().pointSize())))
        self.font_size_combo.currentIndexChanged[str].connect(self.change_font_size)
        formatting_toolbar.addWidget(self.font_size_combo)

        # 保存历史对话按钮
        self.save_history_button = QPushButton("保存历史对话")
        self.save_history_button.clicked.connect(self.save_chat_history)
        formatting_toolbar.addWidget(self.save_history_button)

        # 将“复制所有划线内容到提示词”按钮移动到格式工具栏旁边
        self.copy_all_highlights_button = QPushButton("复制所有划线内容到提示词")
        self.copy_all_highlights_button.clicked.connect(self.copy_all_highlights)
        formatting_toolbar.addWidget(self.copy_all_highlights_button)

        layout.addWidget(formatting_toolbar)

        self.text_edit = QTextEdit()
        self.text_edit.installEventFilter(self)
        self.text_edit.setPlaceholderText("请输入提示词...")
        self.text_edit.setAcceptRichText(True)  # 允许富文本
        self.text_edit.cursorPositionChanged.connect(self.update_formatting_buttons)

        # 按钮布局
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        # 移除了原来的copy_all_highlights_button
        # self.copy_all_highlights_button = QPushButton("复制所有划线内容到提示词")
        # self.copy_all_highlights_button.clicked.connect(self.copy_all_highlights)
        # button_layout.addWidget(self.copy_all_highlights_button)

        self.send_button = QPushButton("发送提示词")
        self.send_button.clicked.connect(self.send_prompt)
        button_layout.addWidget(self.send_button)

        self.voice_button = QPushButton("语音输入")
        self.voice_button.clicked.connect(self.voice_input)
        button_layout.addWidget(self.voice_button)

        button_layout.addStretch()

        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 历史提示词弹出窗口
        self.history_popup = QListWidget()
        self.history_popup.setWindowFlags(Qt.ToolTip)
        self.history_popup.itemClicked.connect(self.complete_prompt)

    def save_chat_history(self):
        # 获取第一个浏览器的标题
        if not self.prompt_manager.main_window.ai_platform_widgets:
            QMessageBox.warning(self, "提示", "没有AI平台可获取标题。")
            return
        first_browser = self.prompt_manager.main_window.ai_platform_widgets[0]
        def get_title_callback(title):
            # 弹出对话框，允许用户修改标题
            text, ok = QInputDialog.getText(self, "保存历史对话", "请输入历史对话标题：", text=title)
            if ok and text:
                # 获取所有浏览器的当前实际访问的网址
                urls = [widget.browser.url().toString() for widget in self.prompt_manager.main_window.ai_platform_widgets]
                # 保存到历史对话
                self.prompt_manager.add_to_chat_history(text, urls)
                QMessageBox.information(self, "保存成功", "历史对话已保存。")
        first_browser.browser.page().runJavaScript("document.title;", get_title_callback)

    def toggle_bold(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if not fmt.fontWeight() == QFont.Bold else QFont.Normal)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_underline(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.text_edit.setCurrentCharFormat(fmt)

    def change_font_size(self, size):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontPointSize(float(size))
        self.text_edit.setCurrentCharFormat(fmt)

    def update_formatting_buttons(self):
        fmt = self.text_edit.currentCharFormat()
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())
        self.font_size_combo.setCurrentText(str(int(fmt.fontPointSize())))

    def copy_all_highlights(self):
        self.prompt_manager.main_window.copy_highlights_to_prompt()

    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Slash:
                self.show_history_popup()
                return True
            elif event.key() == Qt.Key_Return and (event.modifiers() & Qt.ControlModifier):
                self.send_button.click()
                return True
            elif event.key() == Qt.Key_Return and self.history_popup.isVisible():
                self.complete_prompt()
                return True
            else:
                self.history_popup.hide()
        return super().eventFilter(obj, event)

    def show_history_popup(self):
        cursor_rect = self.text_edit.cursorRect()
        global_pos = self.text_edit.mapToGlobal(cursor_rect.bottomRight())
        self.history_popup.move(global_pos)
        self.update_history_popup()
        self.history_popup.show()

    def update_history_popup(self):
        text = self.text_edit.toPlainText()
        filtered = [p['prompt'] for p in self.prompt_manager.history if text.lower() in p['prompt'].lower()]
        self.history_popup.clear()
        for prompt in filtered:
            item = QListWidgetItem(prompt)
            self.history_popup.addItem(item)

    def complete_prompt(self):
        item = self.history_popup.currentItem()
        if item:
            self.text_edit.setPlainText(item.text())
            self.history_popup.hide()

    def send_prompt(self):
        # 获取纯文本内容
        prompt = self.text_edit.toPlainText().strip()
        if prompt:
            self.prompt_manager.send_prompt(prompt)
            self.text_edit.clear()
        else:
            QMessageBox.warning(self, "提示", "提示词不能为空！")

    def voice_input(self):
        QMessageBox.information(self, "语音输入", "语音输入功能待实现。")


class PromptManager(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("提示词管理")
        self.initUI()

    def initUI(self):
        self.resize(1000, 600)  # 默认大小

        # 初始化数据
        self.history = []
        self.favorites = []
        self.chat_history = []  # 历史对话
        self.common_ai_data = []  # 常用AI

        self.load_history()
        self.load_favorites()
        self.load_chat_history()
        self.load_common_ai()

        splitter = QSplitter(Qt.Horizontal)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(splitter)

        # 左侧：提示词输入区域，支持多标签
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        splitter.addWidget(self.tabs)

        # 添加默认的提示词标签页 (不可关闭)
        self.add_prompt_tab(title="提示词", closable=False)

        # 添加剪贴板标签页 (不可关闭)
        self.clipboard_tab = QTextEdit()
        self.clipboard_tab.setPlaceholderText("剪贴板内容")
        self.clipboard_tab.setReadOnly(False)
        index = self.tabs.addTab(self.clipboard_tab, "剪贴板")
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, None)  # 移除关闭按钮

        # 添加浏览器标签页
        self.browser_tabs = QTabWidget()
        self.browser_tabs.setTabsClosable(True)
        self.browser_tabs.tabCloseRequested.connect(self.close_browser_tab)
        self.browser_tabs.setMovable(True)
        self.add_browser_tab()
        index = self.tabs.addTab(self.browser_tabs, "浏览器")
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, None)  # 移除关闭按钮

        # 右侧：历史、收藏和历史对话区域，占30%
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        # 创建可拖动的标签页
        self.right_tabs = QTabWidget()
        self.right_tabs.setTabsClosable(False)
        self.right_tabs.setMovable(True)
        self.right_tabs.setTabPosition(QTabWidget.North)
        right_layout.addWidget(self.right_tabs)

        # 历史提示词列表
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        self.history_list.itemDoubleClicked.connect(self.handle_history_item_double_clicked)

        # 收藏提示词列表
        self.favorites_list = QListWidget()
        self.favorites_list.setSelectionMode(QListWidget.SingleSelection)
        self.favorites_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self.show_favorites_context_menu)
        self.favorites_list.itemDoubleClicked.connect(self.handle_favorites_item_double_clicked)

        # 历史对话列表
        self.chat_history_list = QListWidget()
        self.chat_history_list.setSelectionMode(QListWidget.SingleSelection)
        self.chat_history_list.setToolTip("双击历史对话恢复")
        self.chat_history_list.setUniformItemSizes(True)
        self.chat_history_list.itemDoubleClicked.connect(self.load_chat_history_item)

        # 添加到右侧标签页
        self.right_tabs.addTab(self.create_searchable_list_widget(self.history_list), "历史提示词")
        self.right_tabs.addTab(self.create_searchable_list_widget(self.favorites_list), "收藏提示词")
        self.right_tabs.addTab(self.create_searchable_list_widget(self.chat_history_list), "历史对话")
        self.right_tabs.addTab(self.create_common_ai_tab(), "常用AI")

        # 加载用户的标签顺序
        self.load_tab_order()

        # 添加排序选项
        sort_layout = QHBoxLayout()
        sort_label = QLabel("排序:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("按时间排序 (新到旧)", "time_desc")
        self.sort_combo.addItem("按时间排序 (旧到新)", "time_asc")
        self.sort_combo.addItem("按内容排序 (A-Z)", "content_asc")
        self.sort_combo.addItem("按内容排序 (Z-A)", "content_desc")
        self.sort_combo.currentIndexChanged.connect(self.sort_history)
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        right_layout.addLayout(sort_layout)

        self.update_history_list()
        self.update_favorites_list()
        self.update_chat_history_list()

        # 初始化剪贴板监视
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        # 监听标签顺序变化
        self.right_tabs.tabBar().tabMoved.connect(self.save_tab_order)

    def create_common_ai_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 工具栏
        toolbar = QToolBar()
        add_action = QAction("添加", self)
        add_action.triggered.connect(self.add_common_ai)
        toolbar.addAction(add_action)

        # 搜索框
        self.common_ai_search = QLineEdit()
        self.common_ai_search.setPlaceholderText("搜索")
        self.common_ai_search.textChanged.connect(self.filter_common_ai_tree)

        # 常用AI树形结构
        self.common_ai_tree = QTreeWidget()
        self.common_ai_tree.setHeaderHidden(True)
        self.common_ai_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.common_ai_tree.customContextMenuRequested.connect(self.show_common_ai_context_menu)
        self.common_ai_tree.setDragDropMode(QAbstractItemView.InternalMove)  # 允许拖放
        self.common_ai_tree.itemDoubleClicked.connect(lambda item, column: self.open_common_ai_item(item, 'prompt_browser'))  # 修改为在提示词管理区打开

        # 添加图标区分文件夹和网页
        self.folder_icon = QIcon.fromTheme("folder")
        self.web_icon = QIcon.fromTheme("applications-internet")

        layout.addWidget(toolbar)
        layout.addWidget(self.common_ai_search)
        layout.addWidget(self.common_ai_tree)
        widget.setLayout(layout)

        # 加载常用AI数据
        self.update_common_ai_tree()
        return widget

    def show_common_ai_context_menu(self, position):
        item = self.common_ai_tree.itemAt(position)
        menu = QMenu()
        if item:
            if item.childCount() > 0:
                # 这是一个文件夹
                open_folder_action = QAction("打开文件夹", self)
                open_folder_action.triggered.connect(lambda: self.common_ai_tree.expandItem(item))
                menu.addAction(open_folder_action)
            else:
                # 这是一个网页
                open_action = QAction("在提示词管理区打开", self)
                open_action.triggered.connect(lambda: self.open_common_ai_item(item, 'prompt_browser'))
                open_ai_browser_action = QAction("在AI浏览器区域打开", self)
                open_ai_browser_action.triggered.connect(lambda: self.open_common_ai_item(item, 'ai_browser'))
                menu.addAction(open_action)
                menu.addAction(open_ai_browser_action)
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self.delete_common_ai_item(item))
            rename_action = QAction("重命名", self)
            rename_action.triggered.connect(lambda: self.rename_common_ai_item(item))
            menu.addAction(delete_action)
            menu.addAction(rename_action)
        else:
            add_folder_action = QAction("新建文件夹", self)
            add_folder_action.triggered.connect(self.add_common_ai_folder)
            menu.addAction(add_folder_action)
        menu.exec_(self.common_ai_tree.viewport().mapToGlobal(position))

    def open_common_ai_item(self, item, area='prompt_browser'):
        if item.childCount() == 0:
            url = item.data(0, Qt.UserRole)
            if area == 'ai_browser':
                # 在AI浏览器区域打开
                # 假设有一个特定的AI浏览器标签
                if not hasattr(self, 'ai_browser_tab'):
                    self.ai_browser_tab = QWebEngineView()
                    index = self.tabs.addTab(self.ai_browser_tab, "AI 浏览器")
                self.tabs.setCurrentWidget(self.ai_browser_tab)
                self.ai_browser_tab.load(QUrl(url))
            elif area == 'prompt_browser':
                # 在提示词管理器的浏览器中打开
                self.add_browser_tab(url)
        elif area == 'prompt_browser':
            # 展开或折叠文件夹
            if self.common_ai_tree.isExpanded(item):
                self.common_ai_tree.collapseItem(item)
            else:
                self.common_ai_tree.expandItem(item)

    def add_common_ai_folder(self):
        name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称：")
        if ok and name:
            new_folder = {'name': name, 'children': []}
            self.common_ai_data.append(new_folder)
            self.update_common_ai_tree()
            self.save_common_ai()

    def add_common_ai(self, item=None):
        name, ok = QInputDialog.getText(self, "添加AI", "请输入AI名称：")
        if ok and name:
            url, ok = QInputDialog.getText(self, "添加AI", "请输入AI网址：")
            if ok and url:
                if item:
                    # 添加到选中的文件夹
                    node = self.get_node_from_item(item)
                    if 'children' not in node:
                        node['children'] = []
                    node['children'].append({'name': name, 'url': url})
                else:
                    # 添加到根目录
                    self.common_ai_data.append({'name': name, 'url': url})
                self.update_common_ai_tree()
                self.save_common_ai()

    def get_node_from_item(self, item):
        path = []
        while item:
            path.insert(0, item.text(0))
            item = item.parent()
        node = {'children': self.common_ai_data}
        for name in path:
            for child in node['children']:
                if child['name'] == name:
                    node = child
                    break
        return node

    def delete_common_ai_item(self, item):
        reply = QMessageBox.question(self, "删除", "确定要删除此项吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            parent_item = item.parent()
            if parent_item:
                parent_node = self.get_node_from_item(parent_item)
                child_node = self.get_node_from_item(item)
                parent_node['children'].remove(child_node)
            else:
                node = self.get_node_from_item(item)
                self.common_ai_data.remove(node)
            self.update_common_ai_tree()
            self.save_common_ai()

    def rename_common_ai_item(self, item):
        name, ok = QInputDialog.getText(self, "重命名", "请输入新的名称：", text=item.text(0))
        if ok and name:
            node = self.get_node_from_item(item)
            node['name'] = name
            self.update_common_ai_tree()
            self.save_common_ai()

    def filter_common_ai_tree(self, text):
        # 简单的过滤功能
        def filter_item(item):
            match = text.lower() in item.text(0).lower()
            item.setHidden(not match)
            for i in range(item.childCount()):
                child = item.child(i)
                child_match = filter_item(child)
                if child_match:
                    item.setHidden(False)
                    match = True
            return match

        for i in range(self.common_ai_tree.topLevelItemCount()):
            top_item = self.common_ai_tree.topLevelItem(i)
            filter_item(top_item)

    def update_common_ai_tree(self):
        self.common_ai_tree.clear()

        def add_items(parent, items):
            for item_data in items:
                item = QTreeWidgetItem(parent)
                item.setText(0, item_data['name'])
                if 'url' in item_data:
                    item.setData(0, Qt.UserRole, item_data['url'])
                    item.setIcon(0, self.web_icon)
                else:
                    item.setIcon(0, self.folder_icon)
                if 'children' in item_data:
                    add_items(item, item_data['children'])

        add_items(self.common_ai_tree, self.common_ai_data)
        self.common_ai_tree.expandAll()

    def save_common_ai(self):
        with open('common_ai.json', 'w', encoding='utf-8') as f:
            json.dump(self.common_ai_data, f, indent=4, ensure_ascii=False)

    def load_common_ai(self):
        if os.path.exists('common_ai.json'):
            with open('common_ai.json', 'r', encoding='utf-8') as f:
                self.common_ai_data = json.load(f)
        else:
            self.common_ai_data = []

    def load_tab_order(self):
        order = self.main_window.config.get('right_tab_order', [])
        if order:
            tabs = {'历史提示词': self.right_tabs.widget(0), '收藏提示词': self.right_tabs.widget(1),
                    '历史对话': self.right_tabs.widget(2), '常用AI': self.right_tabs.widget(3)}
            self.right_tabs.clear()
            for tab_name in order:
                if tab_name in tabs:
                    self.right_tabs.addTab(tabs[tab_name], tab_name)
        else:
            pass  # 使用默认顺序

    def save_tab_order(self):
        order = [self.right_tabs.tabText(i) for i in range(self.right_tabs.count())]
        self.main_window.config['right_tab_order'] = order

    def add_browser_tab(self, url=None):
        browser_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 地址栏
        address_bar = QLineEdit()
        if url:
            address_bar.setText(url)
        else:
            address_bar.setText("https://www.baidu.com")
        address_bar.returnPressed.connect(lambda: self.load_browser_url(browser, address_bar.text()))
        layout.addWidget(address_bar)

        # 浏览器
        browser = QWebEngineView()
        browser.load(QUrl(address_bar.text()))
        browser.urlChanged.connect(lambda url: address_bar.setText(url.toString()))
        browser.loadFinished.connect(lambda: self.update_browser_tab_title(browser))

        # 移除无效的 linkClicked 信号连接
        # browser.page().linkClicked.connect(lambda url: browser.setUrl(url))  # 已删除

        layout.addWidget(browser)
        browser_widget.setLayout(layout)

        # 获取标题
        self.update_browser_tab_title(browser)

        index = self.browser_tabs.addTab(browser_widget, "新标签页")
        self.browser_tabs.setCurrentIndex(index)


    def update_browser_tab_title(self, browser):
        def set_title(title):
            # 使用常用AI的标题
            url = browser.url().toString()
            common_ai_titles = self.get_common_ai_titles()
            tab_title = common_ai_titles.get(url, title[:5] if title else "新标签页")
            index = self.browser_tabs.indexOf(browser.parent())
            if index != -1:
                self.browser_tabs.setTabText(index, tab_title)
        browser.page().runJavaScript("document.title", set_title)

    def load_browser_url(self, browser, url):
        if not url.startswith('http'):
            url = 'http://' + url
        browser.load(QUrl(url))

    def close_browser_tab(self, index):
        if self.browser_tabs.count() > 1:
            self.browser_tabs.removeTab(index)
        else:
            QMessageBox.warning(self, "提示", "无法关闭最后一个标签页。")

    def get_common_ai_titles(self):
        # 返回常用AI的URL和名称映射
        url_title_map = {}

        def extract_items(items):
            for item in items:
                if 'url' in item:
                    url_title_map[item['url']] = item['name']
                if 'children' in item:
                    extract_items(item['children'])

        extract_items(self.common_ai_data)
        return url_title_map

    def create_searchable_list_widget(self, list_widget):
        # 创建一个包含搜索栏和列表的部件
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("搜索")
        layout.addWidget(search_bar)
        layout.addWidget(list_widget)
        widget.setLayout(layout)

        # 连接搜索栏的信号到过滤函数
        def filter_list(text):
            text = text.lower()
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_text = item.text().lower()
                if text in item_text:
                    item.setHidden(False)
                else:
                    item.setHidden(True)
        search_bar.textChanged.connect(filter_list)

        return widget

    def add_prompt_tab(self, title="新建标签页", closable=True):
        new_tab = PromptTab(self)
        index = self.tabs.addTab(new_tab, title)
        if not closable:
            self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, None)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        # 确保前两个标签页不能被关闭
        if index < 2:
            return
        self.tabs.removeTab(index)

    def send_prompt(self, prompt):
        self.current_prompt = prompt  # Save current prompt for checking
        self.add_to_history(prompt)
        self.main_window.send_prompt_to_all(prompt)
        # After sending, check if AI text boxes are empty
        QTimer.singleShot(1000, self.check_ai_textboxes)

    def check_ai_textboxes(self):
        resend_needed = False
        for ai_widget in self.main_window.ai_platform_widgets:
            if not ai_widget.has_cleared_text():
                resend_needed = True
                ai_widget.send_prompt(self.current_prompt)
        # No message prompts as per requirement

    def load_history(self):
        # 整合 prompt_history.log 和 prompt_send.log
        if os.path.exists('prompt_history.log'):
            with open('prompt_history.log', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            timestamp, prompt = line.strip().split('\t', 1)
                            self.history.append({'timestamp': timestamp, 'prompt': prompt})
                        except ValueError:
                            pass  # 忽略格式错误的行
        # 移除对 prompt_send.log 的依赖
        # if os.path.exists('prompt_send.log'):
        #     with open('prompt_send.log', 'r', encoding='utf-8') as f:
        #         for line in f:
        #             if line.strip():
        #                 timestamp, prompt = line.strip().split('\t', 1)
        #                 self.history.append({'timestamp': timestamp, 'prompt': prompt})
        else:
            self.history = []

    def load_favorites(self):
        if os.path.exists('prompt_favorites.log'):
            with open('prompt_favorites.log', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            timestamp, prompt = line.strip().split('\t', 1)
                            self.favorites.append({'timestamp': timestamp, 'prompt': prompt})
                        except ValueError:
                            pass  # 忽略格式错误的行
        else:
            self.favorites = []

    def load_chat_history(self):
        if os.path.exists('chat_history.log'):
            with open('chat_history.log', 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)
        else:
            self.chat_history = []

    def save_chat_history(self):
        with open('chat_history.log', 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, indent=4, ensure_ascii=False)

    def add_to_chat_history(self, title, urls):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.chat_history.insert(0, {'title': title, 'urls': urls, 'time': timestamp})
        # 限制历史对话记录数量
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[:100]
        self.update_chat_history_list()
        self.save_chat_history()

    def update_chat_history_list(self):
        self.chat_history_list.clear()
        for index, chat in enumerate(self.chat_history):
            item = QListWidgetItem(f"{chat['title']} ({chat['time']})")
            if index % 2 == 0:
                item.setBackground(QColor('#f0f0f0'))
            else:
                item.setBackground(QColor('#ffffff'))
            item.setForeground(QColor('#000000'))
            item.setSizeHint(QSize(item.sizeHint().width(), 30))
            self.chat_history_list.addItem(item)

    def load_chat_history_item(self, item):
        index = self.chat_history_list.row(item)
        chat = self.chat_history[index]
        # 加载对应的浏览器网址
        self.main_window.load_chat_history(chat)

    def add_to_history(self, prompt):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, {'timestamp': timestamp, 'prompt': prompt})
        # Limit history size to 100
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.update_history_list()
        # Save to file
        with open('prompt_history.log', 'w', encoding='utf-8') as f:
            for item in self.history:
                f.write(f"{item['timestamp']}\t{item['prompt']}\n")

    def update_history_list(self):
        self.history_list.clear()
        for index, item in enumerate(self.history):
            # 显示最多3行内容
            display_text = '\n'.join(item['prompt'].splitlines()[:3])
            list_item = QListWidgetItem(display_text)
            list_item.setToolTip(f"{item['timestamp']}\n{item['prompt']}")  # 悬停显示完整内容和时间
            # 背景颜色交替显示
            if index % 2 == 0:
                list_item.setBackground(QColor('#f0f0f0'))
            else:
                list_item.setBackground(QColor('#ffffff'))
            list_item.setForeground(QColor('#000000'))
            self.history_list.addItem(list_item)

    def update_favorites_list(self):
        self.favorites_list.clear()
        for index, item in enumerate(self.favorites):
            # 显示最多3行内容
            display_text = '\n'.join(item['prompt'].splitlines()[:3])
            list_item = QListWidgetItem(display_text)
            list_item.setToolTip(f"{item['timestamp']}\n{item['prompt']}")  # 悬停显示完整内容和时间
            # 背景颜色交替显示
            if index % 2 == 0:
                list_item.setBackground(QColor('#f0f0f0'))
            else:
                list_item.setBackground(QColor('#ffffff'))
            list_item.setForeground(QColor('#000000'))
            self.favorites_list.addItem(list_item)

    def favorite_history_item(self):
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        index = self.history_list.row(item)
        prompt = self.history[index]['prompt']
        self.add_to_favorites(prompt)

    def add_to_favorites(self, prompt):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if not any(fav['prompt'] == prompt for fav in self.favorites):
            self.favorites.append({'timestamp': timestamp, 'prompt': prompt})
            self.update_favorites_list()
            # Save to file
            with open('prompt_favorites.log', 'w', encoding='utf-8') as f:
                for item in self.favorites:
                    f.write(f"{item['timestamp']}\t{item['prompt']}\n")
            QMessageBox.information(self, "收藏成功", f"已将提示词添加到收藏列表。")

    def delete_history_item(self):
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        index = self.history_list.row(item)
        del self.history[index]
        self.update_history_list()
        # 保存更新后的历史提示词
        with open('prompt_history.log', 'w', encoding='utf-8') as f:
            for item in self.history:
                f.write(f"{item['timestamp']}\t{item['prompt']}\n")

    def delete_favorite_item(self):
        selected_items = self.favorites_list.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        index = self.favorites_list.row(item)
        del self.favorites[index]
        self.update_favorites_list()
        # 保存更新后的收藏列表
        with open('prompt_favorites.log', 'w', encoding='utf-8') as f:
            for item in self.favorites:
                f.write(f"{item['timestamp']}\t{item['prompt']}\n")

    def show_history_context_menu(self, position):
        menu = QMenu()
        favorite_action = QAction("收藏", self)
        favorite_action.triggered.connect(self.favorite_history_item)
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_history_item)
        menu.addAction(favorite_action)
        menu.addAction(delete_action)
        menu.exec_(self.history_list.viewport().mapToGlobal(position))

    def show_favorites_context_menu(self, position):
        menu = QMenu()
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_favorite_item)
        menu.addAction(delete_action)
        menu.exec_(self.favorites_list.viewport().mapToGlobal(position))

    def handle_history_item_double_clicked(self, item):
        index = self.history_list.row(item)
        prompt_text = self.history[index]['prompt']
        self.set_current_prompt(prompt_text)

    def handle_favorites_item_double_clicked(self, item):
        index = self.favorites_list.row(item)
        prompt_text = self.favorites[index]['prompt']
        self.set_current_prompt(prompt_text)

    def set_current_prompt(self, text):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, PromptTab):
            current_tab.text_edit.setPlainText(text)

    def on_clipboard_change(self):
        data = self.clipboard.mimeData()
        if data.hasText():
            text = data.text()
            source_info = f"（复制于 {time.strftime('%Y-%m-%d %H:%M:%S')}）"
            # Append at the end
            self.clipboard_tab.append(text + '\n' + source_info + '\n')
            # Scroll to the end
            cursor = self.clipboard_tab.textCursor()
            cursor.movePosition(cursor.End)
            self.clipboard_tab.setTextCursor(cursor)

    def sort_history(self):
        sort_mode = self.sort_combo.currentData()
        if sort_mode == "time_desc":
            self.history.sort(reverse=True, key=lambda x: x['timestamp'])
        elif sort_mode == "time_asc":
            self.history.sort(key=lambda x: x['timestamp'])
        elif sort_mode == "content_asc":
            self.history.sort(key=lambda x: x['prompt'].lower())
        elif sort_mode == "content_desc":
            self.history.sort(reverse=True, key=lambda x: x['prompt'].lower())
        self.update_history_list()

class CustomWebEnginePage(QWebEnginePage):
    # 保持不变
    def __init__(self, *args, ai_platform=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_platform = ai_platform

    def certificateError(self, error):
        # 忽略证书错误
        error.ignoreCertificateError()
        return True

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 捕获控制台消息，可以用于获取 AI 平台的回复内容
        if "AI_REPLY:" in message:
            reply_content = message.replace("AI_REPLY:", "")
            self.ai_platform.handle_ai_reply(reply_content)


class AIPlatform(QWidget):
    def __init__(self, name, url, profile_manager, common_urls, window_index, config, main_window, parent=None):
        super(AIPlatform, self).__init__(parent)
        self.name = name
        self.url = url
        self.profile_manager = profile_manager
        self.common_urls = common_urls
        self.window_index = window_index  # 窗口索引，从1开始
        self.config = config
        self.main_window = main_window
        self.is_page_loaded = False
        self.pending_prompts = []
        self.current_highlight_color = 'yellow'  # 默认划线颜色
        self.zoom_factor = 1.0  # 默认缩放比例
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        # 地址栏
        self.address_bar = QLineEdit()
        self.address_bar.setText(self.url)
        self.address_bar.returnPressed.connect(self.load_url)
        layout.addWidget(self.address_bar)

        # 浏览器
        self.browser = QWebEngineView()
        domain = QUrl(self.url).host()
        self.profile = self.profile_manager.get_profile(domain)
        self.page = CustomWebEnginePage(self.profile, self.browser, ai_platform=self)
        self.browser.setPage(self.page)
        self.browser.load(QUrl(self.url))
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(self.update_address_bar)

        # 设置浏览器的 User-Agent 为最新的 Chrome
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        self.profile.setHttpUserAgent(user_agent)

        # 初始缩放比例
        self.browser.setZoomFactor(self.zoom_factor)

        # 浏览器字体设置
        settings = self.browser.settings()
        settings.setFontFamily(QWebEngineSettings.StandardFont, QFont().defaultFamily())
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, QFont().pointSize())

        # 坐标设置按钮
        self.coordinate_btn = QPushButton()
        self.coordinate_btn.clicked.connect(self.open_coordinate_dialog)
        self.update_coordinate_btn_text()

        # 添加复制划线内容按钮，替换划线颜色按钮
        self.copy_highlights_btn = QPushButton("复制划线内容")
        self.copy_highlights_btn.clicked.connect(self.copy_highlights_to_clipboard)

        # 清除划线按钮
        self.clear_highlights_btn = QPushButton("清除划线")
        self.clear_highlights_btn.clicked.connect(self.clear_highlights)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.coordinate_btn)
        btn_layout.addWidget(self.copy_highlights_btn)  # 替换为复制划线内容按钮
        btn_layout.addWidget(self.clear_highlights_btn)
        btn_layout.addStretch()

        layout.addWidget(self.browser)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # 加载坐标和缩放比例
        self.load_coordinates()

        # 设置右键菜单
        self.browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.show_context_menu)

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def copy_highlights_to_clipboard(self):
        # 获取当前浏览器的划线内容并复制到剪贴板
        def callback(text):
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "复制成功", "所有划线内容已复制到剪贴板。")
            else:
                QMessageBox.information(self, "提示", "没有划线内容可复制。")

        self.get_highlighted_text(callback)

    def clear_highlights(self):
        js_code = """
        (function() {
            var highlights = document.querySelectorAll('span.highlight');
            highlights.forEach(function(span) {
                var parent = span.parentNode;
                while(span.firstChild) {
                    parent.insertBefore(span.firstChild, span);
                }
                parent.removeChild(span);
            });
        })();
        """
        self.browser.page().runJavaScript(js_code)

    def show_context_menu(self, position):
        menu = QMenu()
        highlight_action = QAction("划线", self)
        highlight_action.triggered.connect(self.highlight_selection)
        menu.addAction(highlight_action)

        delete_highlight_action = QAction("删除当前划线", self)
        delete_highlight_action.triggered.connect(self.delete_current_highlight)
        menu.addAction(delete_highlight_action)

        color_menu = QMenu("选择划线颜色", menu)
        color_group = QActionGroup(self)
        for color_name, color_value in [('黄色', 'yellow'), ('绿色', 'green'), ('青色', 'cyan'), ('粉色', 'pink'), ('橙色', 'orange')]:
            color_action = QAction(color_name, self)
            color_action.setCheckable(True)
            color_action.setData(color_value)
            if self.current_highlight_color == color_value:
                color_action.setChecked(True)
            color_action.triggered.connect(self.change_highlight_color)
            color_group.addAction(color_action)
            color_menu.addAction(color_action)
        menu.addMenu(color_menu)

        menu.exec_(self.browser.mapToGlobal(position))

    def highlight_selection(self):
        # 先移除选区内已有的高亮
        js_remove_highlight = """
        (function() {
            var selection = window.getSelection();
            if (!selection.isCollapsed) {
                var range = selection.getRangeAt(0);
                var contents = range.cloneContents();
                var spans = contents.querySelectorAll('span.highlight');
                spans.forEach(function(span) {
                    var parent = span.parentNode;
                    while(span.firstChild) {
                        parent.insertBefore(span.firstChild, span);
                    }
                    parent.removeChild(span);
                });
            }
        })();
        """
        self.browser.page().runJavaScript(js_remove_highlight, lambda _: self.apply_highlight())

    def apply_highlight(self):
        js_apply_highlight = f"""
        (function() {{
            var selection = window.getSelection();
            if (!selection.isCollapsed) {{
                var range = selection.getRangeAt(0);
                var newNode = document.createElement('span');
                newNode.style.backgroundColor = '{self.current_highlight_color}';
                newNode.className = 'highlight';
                try {{
                    range.surroundContents(newNode);
                }} catch(e) {{
                    alert('无法应用高亮：' + e);
                }}
                selection.removeAllRanges();
            }}
        }})();
        """
        self.browser.page().runJavaScript(js_apply_highlight)

    def delete_current_highlight(self):
        js_code = """
        (function() {
            var selection = window.getSelection();
            if (!selection.isCollapsed) {
                var range = selection.getRangeAt(0);
                var node = range.startContainer.parentNode;
                if (node && node.classList.contains('highlight')) {
                    var parent = node.parentNode;
                    while(node.firstChild) {
                        parent.insertBefore(node.firstChild, node);
                    }
                    parent.removeChild(node);
                }
                selection.removeAllRanges();
            }
        })();
        """
        self.browser.page().runJavaScript(js_code)

    def show_highlight_color_menu(self):
        menu = QMenu()
        color_group = QActionGroup(self)
        for color_name, color_value in [('黄色', 'yellow'), ('绿色', 'green'), ('青色', 'cyan'), ('粉色', 'pink'), ('橙色', 'orange')]:
            color_action = QAction(color_name, self)
            color_action.setCheckable(True)
            color_action.setData(color_value)
            if self.current_highlight_color == color_value:
                color_action.setChecked(True)
            color_action.triggered.connect(self.change_highlight_color)
            color_group.addAction(color_action)
            menu.addAction(color_action)
        menu.exec_(self.copy_highlights_btn.mapToGlobal(QPoint(0, self.copy_highlights_btn.height())))

    def change_highlight_color(self):
        action = self.sender()
        if action:
            self.current_highlight_color = action.data()
            js_code = f"window.currentHighlightColor = '{self.current_highlight_color}';"
            self.browser.page().runJavaScript(js_code)
            self.copy_highlights_btn.setText(f"复制划线内容 ({action.text()})")

    def update_coordinate_btn_text(self):
        if hasattr(self, 'send_method'):
            if self.send_method == 'javascript':
                self.coordinate_btn.setText("使用 JavaScript 注入发送")
            else:
                if hasattr(self, 'textbox_coordinate') and self.textbox_coordinate and \
                   hasattr(self, 'send_button_coordinate') and self.send_button_coordinate:
                    self.coordinate_btn.setText(f"坐标已设置")
                else:
                    self.coordinate_btn.setText("坐标未设置，点击设置")
        else:
            self.coordinate_btn.setText("发送方式未设置，点击设置")

    def load_url(self):
        url = self.address_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
            self.address_bar.setText(url)
        if url != self.url:
            self.url = url
            # 设置坐标可能需要更新，设置标志
            self.coordinates_valid = False
            self.update_coordinate_btn_text()
            # 提示用户
            QMessageBox.information(self, "网址已更改", f"您已更改 {self.name} 的网址，请确保坐标和发送方式正确。")
        self.is_page_loaded = False
        self.browser.load(QUrl(url))

    def on_load_finished(self):
        self.is_page_loaded = True
        # 注入划线标记的脚本
        self.inject_highlight_script()
        # If there are pending prompts, send them
        if self.pending_prompts:
            prompt = self.pending_prompts.pop(0)
            self.send_prompt(prompt)

    def send_prompt(self, prompt):
        if not self.is_page_loaded:
            # 页面未加载完成，等待加载完成后再发送
            self.pending_prompts.append(prompt)
            return
        if self.send_method == 'javascript':
            self.execute_js(prompt)
        else:
            self.send_prompt_with_pyautogui(prompt)

    def open_coordinate_dialog(self):
        current_coords = {
            'textbox': self.textbox_coordinate,
            'send_button': self.send_button_coordinate,
            'send_method': getattr(self, 'send_method', 'enter'),
            'zoom_factor': getattr(self, 'zoom_factor', 1.0)
        }
        dialog = CoordinateSettingDialog(self.name, current_coords)
        if dialog.exec_():
            new_coords = dialog.get_coordinates()
            # Update only if new coordinates are provided
            if new_coords['textbox']:
                self.textbox_coordinate = new_coords['textbox']
            if new_coords['send_button']:
                self.send_button_coordinate = new_coords['send_button']
            if new_coords['send_method']:
                self.send_method = new_coords['send_method']
            if new_coords['zoom_factor']:
                self.zoom_factor = new_coords['zoom_factor']
                # 应用新的缩放比例
                self.browser.setZoomFactor(self.zoom_factor)
            # Update the validity flag
            if self.send_method != 'javascript':
                self.coordinates_valid = bool(
                    hasattr(self, 'textbox_coordinate') and self.textbox_coordinate and
                    hasattr(self, 'send_button_coordinate') and self.send_button_coordinate
                )
            else:
                self.coordinates_valid = True  # JavaScript 方式不需要坐标
            self.update_coordinate_btn_text()
            # Save coordinates to config
            self.save_coordinates()
        else:
            self.update_coordinate_btn_text()

    def save_coordinates(self):
        if 'platform_coordinates' not in self.config:
            self.config['platform_coordinates'] = {}
        platform_coords = self.config['platform_coordinates'].get(self.name, {})
        if hasattr(self, 'textbox_coordinate') and self.textbox_coordinate:
            platform_coords['textbox'] = self.textbox_coordinate
        if hasattr(self, 'send_button_coordinate') and self.send_button_coordinate:
            platform_coords['send_button'] = self.send_button_coordinate
        if hasattr(self, 'send_method') and self.send_method:
            platform_coords['send_method'] = self.send_method
        if hasattr(self, 'zoom_factor') and self.zoom_factor:
            platform_coords['zoom_factor'] = self.zoom_factor
        platform_coords['url'] = self.url
        self.config['platform_coordinates'][self.name] = platform_coords
        # Save to config file
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def load_coordinates(self):
        self.textbox_coordinate = None
        self.send_button_coordinate = None
        self.send_method = "enter"
        self.zoom_factor = 1.0  # 默认缩放比例
        self.coordinates_valid = False  # 初始为 False，加载后可能变为 True
        if 'platform_coordinates' in self.config:
            platform_coords = self.config['platform_coordinates'].get(self.name, {})
            self.textbox_coordinate = platform_coords.get('textbox', None)
            self.send_button_coordinate = platform_coords.get('send_button', None)
            self.send_method = platform_coords.get('send_method', "enter")
            self.zoom_factor = platform_coords.get('zoom_factor', 1.0)
            self.url = platform_coords.get('url', self.url)
            self.address_bar.setText(self.url)
            self.browser.load(QUrl(self.url))
            if self.send_method != 'javascript':
                if self.textbox_coordinate and self.send_button_coordinate:
                    self.coordinates_valid = True
            else:
                self.coordinates_valid = True  # JavaScript 方式不需要坐标
            # 应用缩放比例
            self.browser.setZoomFactor(self.zoom_factor)
        self.update_coordinate_btn_text()

    def send_prompt_with_pyautogui(self, prompt):
        # Check if coordinates are valid
        if not self.coordinates_valid:
            QMessageBox.warning(self, "坐标未设置", f"{self.name} 的坐标可能需要重新设置。")
            return
        # Ensure window is in front
        self.main_window.raise_()
        self.main_window.activateWindow()
        QApplication.processEvents()

        # Move to textbox and click
        x, y = self.textbox_coordinate
        pyautogui.moveTo(x, y)
        pyautogui.click()
        # Clear existing text
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        # Paste prompt using clipboard
        pyperclip.copy(prompt)
        pyautogui.hotkey('ctrl', 'v')

        # Send prompt
        if self.send_method == "enter":
            pyautogui.press('enter')
        elif self.send_method == "button":
            # Move to send button and click
            x, y = self.send_button_coordinate
            pyautogui.moveTo(x, y)
            pyautogui.click()
        else:
            # Default to pressing enter
            pyautogui.press('enter')

        print(f"{self.name} 提示词发送完成")

    def has_cleared_text(self):
        # 根据发送方式判断
        if self.send_method == 'javascript':
            # Implement JavaScript check
            # For now, we assume the prompt has been sent successfully
            return True
        else:
            # Assume pyautogui method always succeeds
            return True

    def handle_ai_reply(self, reply_content):
        # 处理 AI 平台的回复内容
        reply_log = f"[{self.name}] {time.strftime('%Y-%m-%d %H:%M:%S')}\n{reply_content}\n字数：{len(reply_content)}\n"
        with open('ai_reply.log', 'a', encoding='utf-8') as f:
            f.write(reply_log)

    def execute_js(self, prompt):
        # 获取当前页面的URL
        url = self.browser.url().toString()
        domain = QUrl(url).host()

        # 定义用于转义 JavaScript 字符串的函数
        def escape_js_string(s):
            return s.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

        # 对 prompt 进行转义
        escaped_prompt = escape_js_string(prompt)
        # 对 prompt 进行 JSON 编码
        prompt_js = json.dumps(prompt)

        # 针对不同的平台，编写特定的 JavaScript 代码
        js_code = ''
        if 'chatglm.cn' in domain:
            # ChatGLM
            js_code = f"""
            (function() {{
                var textarea = document.querySelector('.input-box-inner textarea');
                if (textarea) {{
                    textarea.focus();
                    // 使用浏览器原生的 value setter
                    var nativeTextareaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeTextareaValueSetter.call(textarea, '{escaped_prompt}');
                    // 触发输入事件
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    textarea.dispatchEvent(inputEvent);
                    // 模拟点击发送按钮
                    setTimeout(function() {{
                        var btn = document.querySelector('.input-box-inner .input-box-icon');
                        if (btn) {{
                            btn.click();
                        }} else {{
                            console.log('未找到发送按钮');
                        }}
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """
        elif 'yuanbao.tencent.com' in domain:
            # 元宝
            js_code = f"""
            (function() {{
                var editor = document.querySelector('.ql-editor[contenteditable="true"]');
                if (editor) {{
                    // 清空内容
                    editor.innerHTML = '';
                    // 插入新内容
                    editor.focus();
                    document.execCommand('insertText', false, {prompt_js});
                    // 触发输入事件
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    editor.dispatchEvent(inputEvent);
                    // 模拟点击发送按钮
                    setTimeout(function() {{
                        var btn = document.querySelector('a.style__send-btn___GVH0r');
                        if (!btn) {{
                            // 尝试使用其他选择器
                            btn = document.querySelector('a[class^="style__send-btn"]');
                        }}
                        if (btn) {{
                            btn.click();
                        }} else {{
                            console.log('未找到发送按钮');
                        }}
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """
        elif 'doubao.com' in domain:
            # 豆包
            js_code = f"""
            (function() {{
                var textarea = document.querySelector('textarea.semi-input-textarea');
                if (textarea) {{
                    textarea.focus();
                    var nativeTextareaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeTextareaValueSetter.call(textarea, {prompt_js});
                    // 触发输入事件
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    textarea.dispatchEvent(inputEvent);
                    // 模拟点击发送按钮
                    setTimeout(function() {{
                        var btn = document.querySelector('#flow-end-msg-send');
                        if (btn) {{
                            btn.click();
                        }} else {{
                            console.log('未找到发送按钮');
                        }}
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """
        elif 'moonshot.cn' in domain:
            # Kimi
            js_code = f"""
            (function() {{
                var editor = document.querySelector('[data-testid="msh-chatinput-editor"][contenteditable="true"]');
                if (editor) {{
                    // 清空内容
                    editor.innerHTML = '';
                    // 插入新内容
                    editor.focus();
                    document.execCommand('insertText', false, {prompt_js});
                    // 触发输入事件
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    editor.dispatchEvent(inputEvent);
                    /* 延时后模拟按下 Enter 键 */
                    setTimeout(function() {{
                        var enterEvent = new KeyboardEvent('keydown', {{
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }});
                        editor.dispatchEvent(enterEvent);
                        var keyupEvent = new KeyboardEvent('keyup', {{
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        }});
                        editor.dispatchEvent(keyupEvent);
                        // 检查发送是否成功
                        setTimeout(function() {{
                            if (editor.textContent.trim() !== '') {{
                                editor.dispatchEvent(enterEvent);
                                editor.dispatchEvent(keyupEvent);
                            }}
                        }}, 500);
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """
        elif 'chatgpt.com' in domain:
            # ChatGPT
            js_code = f"""
            (function() {{
                var textarea = document.querySelector('textarea');
                if (textarea) {{
                    textarea.focus();
                    var nativeTextareaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeTextareaValueSetter.call(textarea, '{escaped_prompt}');
                    // 触发输入事件
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    textarea.dispatchEvent(inputEvent);
                    // 模拟点击发送按钮
                    setTimeout(function() {{
                        var btn = document.querySelector('button[aria-label="发送消息"]');
                        if (!btn) {{
                            // 尝试其他选择器
                            btn = document.querySelector('button:has(svg.icon-md)');
                        }}
                        if (btn) {{
                            btn.click();
                        }} else {{
                            console.log('未找到发送按钮');
                        }}
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """
        else:
            # 默认处理方式
            js_code = f"""
            (function() {{
                var textarea = document.querySelector('textarea');
                if (textarea) {{
                    textarea.focus();
                    var nativeTextareaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeTextareaValueSetter.call(textarea, '{escaped_prompt}');
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    textarea.dispatchEvent(inputEvent);
                    // 尝试点击发送按钮
                    setTimeout(function() {{
                        var btn = document.querySelector('button[type="submit"], button.send');
                        if (btn) {{
                            btn.click();
                        }} else {{
                            console.log('未找到发送按钮，尝试模拟按下 Enter 键');
                            // 模拟按下 Enter 键
                            var enterEvent = new KeyboardEvent('keydown', {{
                                key: 'Enter',
                                code: 'Enter',
                                keyCode:13,
                                which:13,
                                bubbles: true,
                                cancelable: true
                            }});
                            textarea.dispatchEvent(enterEvent);
                        }}
                    }}, 500);
                    return 'success';
                }} else {{
                    return '未找到输入框';
                }}
            }})();
            """

        # 定义回调函数，处理执行结果和错误
        def js_callback(result):
            if result != 'success':
                error_message = f"{self.name} 执行 JavaScript 出错：{result}"
                print(error_message)
                with open('javascript_errors.log', 'a', encoding='utf-8') as f:
                    f.write(error_message + '\n')
            else:
                print(f"{self.name} 提示词发送成功")

        # 执行 JavaScript 代码
        self.browser.page().runJavaScript(js_code, js_callback)

    def inject_highlight_script(self):
        # JavaScript 脚本，用于实现划线标记功能
        js_code = f"""
        window.currentHighlightColor = '{self.current_highlight_color}';
        """
        self.browser.page().runJavaScript(js_code)

    def set_highlight_color(self, color):
        self.current_highlight_color = color
        js_code = f"window.currentHighlightColor = '{color}';"
        self.browser.page().runJavaScript(js_code)
        self.copy_highlights_btn.setText(f"复制划线内容 ({color})")

    def get_highlighted_text(self, callback):
        js_code = """
        (function() {
            var highlights = document.querySelectorAll('span.highlight');
            var texts = [];
            highlights.forEach(function(span) {
                texts.push(span.innerText);
            });
            return texts.join('\\n');
        })();
        """
        self.browser.page().runJavaScript(js_code, callback)

    def copy_highlights_to_prompt(self):
        # 已在 PromptTab 中实现，因此此方法可以移除或保留为空
        pass


class ProfileManager:
    # 保持不变
    def __init__(self):
        self.profiles = {}
        self.storage_location = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        os.makedirs(self.storage_location, exist_ok=True)

    def get_profile(self, domain):
        if domain not in self.profiles:
            storage_path = os.path.join(self.storage_location, 'SupperAI', domain)
            os.makedirs(storage_path, exist_ok=True)
            profile = QWebEngineProfile(domain, None)
            profile.setPersistentStoragePath(storage_path)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            # 设置缓存路径
            cache_path = os.path.join(storage_path, 'cache')
            profile.setCachePath(cache_path)
            self.profiles[domain] = profile
        return self.profiles[domain]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.initUI()

    def load_config(self):
        if not os.path.exists('config.json'):
            self.config = {
                "num_platforms": 4,
                "ai_platforms": [
                    {"name": "ChatGPT", "url": "https://chatgpt.com/"},
                    {"name": "元宝", "url": "https://yuanbao.tencent.com/"},
                    {"name": "豆包", "url": "https://www.doubao.com/"},
                    {"name": "Kimi", "url": "https://kimi.moonshot.cn/"}
                ],
                "common_urls": {
                    "ChatGPT": [
                        {"name": "ChatGPT", "url": "https://chatgpt.com/"}
                    ],
                    "ChatGLM": [
                        {"name": "ChatGLM", "url": "https://chatglm.cn/"}
                    ],
                    "腾讯": [
                        {"name": "元宝", "url": "https://yuanbao.tencent.com/"}
                    ],
                    "豆包": [
                        {"name": "豆包", "url": "https://www.doubao.com/"}
                    ],
                    "Kimi": [
                        {"name": "Kimi", "url": "https://kimi.moonshot.cn/"}
                    ]
                },
                "platform_coordinates": {},
                "window_geometry": None,
                "window_state": None,
                "prompt_manager_docked": True,  # Default docked
                "default_open_area": "ai_browser",  # 默认打开区域
                "right_tab_order": ["历史提示词", "收藏提示词", "历史对话", "常用AI"]
            }
            # 保存默认配置
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        else:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                # 确保 "ChatGPT" 在配置中
                if not any(p['name'] == 'ChatGPT' for p in self.config['ai_platforms']):
                    self.config['ai_platforms'].insert(0, {"name": "ChatGPT", "url": "https://chatgpt.com/"})
                if 'ChatGPT' not in self.config['common_urls']:
                    self.config['common_urls']['ChatGPT'] = [{"name": "ChatGPT", "url": "https://chatgpt.com/"}]
        # 默认数量
        self.num_platforms = self.config.get('num_platforms', len(self.config['ai_platforms']))

    def initUI(self):
        self.setWindowTitle('SupperAI+ (智汇共创)')
        self.resize(1200, 800)

        # 设置应用程序图标
        if os.path.exists('icon.png'):
            self.setWindowIcon(QIcon('icon.png'))
        else:
            self.setWindowIcon(QIcon())

        # 设置全局字体
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(10)
        QApplication.instance().setFont(font)

        # 创建主分割器（垂直）
        self.main_splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.main_splitter)

        # 创建 AI 平台容器
        self.ai_platform_container = QWidget()
        self.ai_platform_layout = QHBoxLayout()
        self.ai_platform_layout.setSpacing(2)
        self.ai_platform_layout.setContentsMargins(2, 2, 2, 2)
        self.ai_platform_container.setLayout(self.ai_platform_layout)

        self.main_splitter.addWidget(self.ai_platform_container)

        # 创建提示词管理器
        self.prompt_manager = PromptManager(self)
        self.main_splitter.addWidget(self.prompt_manager)

        # 创建工具栏，用于调整 AI 平台数量
        self.toolbar = QToolBar("工具栏")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # 添加快捷键切换划线颜色
        self.highlight_colors = ['yellow', 'green', 'cyan', 'pink', 'orange']
        self.current_highlight_color_index = 0
        self.current_highlight_color = self.highlight_colors[self.current_highlight_color_index]
        self.setup_shortcuts()

        # 创建菜单
        self.create_menus()

        self.profile_manager = ProfileManager()
        self.create_ai_platforms()

        # 恢复窗口几何和状态
        if self.config.get("window_geometry"):
            try:
                self.restoreGeometry(bytes.fromhex(self.config["window_geometry"]))
            except:
                pass
        if self.config.get("window_state"):
            try:
                self.restoreState(bytes.fromhex(self.config["window_state"]))
            except:
                pass

        # 恢复提示词管理器的停靠状态
        if self.config.get("prompt_manager_docked", True):
            self.dock_prompt_manager_action.setChecked(True)
            self.toggle_dock_prompt_manager(True)
        else:
            self.prompt_manager.show()

    def setup_shortcuts(self):
        # 切换到下一种划线颜色的快捷键：Ctrl+Shift+H
        next_color_shortcut = QShortcut(QKeySequence('Ctrl+Shift+H'), self)
        next_color_shortcut.activated.connect(self.next_highlight_color)

    def next_highlight_color(self):
        self.current_highlight_color_index = (self.current_highlight_color_index + 1) % len(self.highlight_colors)
        self.current_highlight_color = self.highlight_colors[self.current_highlight_color_index]
        # 将新的划线颜色设置到所有 AI 平台
        for ai_widget in self.ai_platform_widgets:
            ai_widget.set_highlight_color(self.current_highlight_color)
        print(f"划线颜色已切换为 {self.current_highlight_color}")

    def copy_highlights_to_prompt(self):
        all_highlighted_texts = []
        remaining_callbacks = len(self.ai_platform_widgets)

        def collect_text(text, name):
            nonlocal remaining_callbacks
            if text:
                all_highlighted_texts.append(f"{name}：{text}")
            remaining_callbacks -= 1
            if remaining_callbacks == 0:
                # 所有回调函数均已返回
                combined_text = '\n'.join(all_highlighted_texts)
                self.prompt_manager.set_current_prompt(combined_text)

        for ai_widget in self.ai_platform_widgets:
            ai_widget.get_highlighted_text(partial(collect_text, name=ai_widget.name))

    def create_menus(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu("视图")

        self.dock_prompt_manager_action = QAction("分离提示词管理器", self)
        self.dock_prompt_manager_action.setCheckable(True)
        self.dock_prompt_manager_action.setChecked(self.config.get("prompt_manager_docked", True))
        self.dock_prompt_manager_action.triggered.connect(self.toggle_dock_prompt_manager)
        view_menu.addAction(self.dock_prompt_manager_action)

        platform_number_menu = QMenu("设置浏览器窗口数量", self)
        self.platform_action_group = QActionGroup(self)
        for i in range(1, 7):
            action = QAction(f"{i} 个窗口", self)
            action.setData(i)
            action.setCheckable(True)
            action.setChecked(i == self.num_platforms)
            action.triggered.connect(self.change_num_platforms)
            self.platform_action_group.addAction(action)
            platform_number_menu.addAction(action)
        view_menu.addMenu(platform_number_menu)

    def change_num_platforms(self):
        action = self.sender()
        if action and action.data():
            self.num_platforms = action.data()
            # 更新菜单中的勾选状态
            for act in action.parent().actions():
                act.setChecked(act == action)
            # 重新创建 AI 平台窗口
            self.create_ai_platforms()
            self.config["num_platforms"] = self.num_platforms

    def toggle_dock_prompt_manager(self, checked):
        if checked:
            # 停靠提示词管理器
            self.main_splitter.addWidget(self.prompt_manager)
            self.main_splitter.setStretchFactor(0, 8)
            self.main_splitter.setStretchFactor(1, 2)
            self.config["prompt_manager_docked"] = True
            # 设置初始尺寸
            QTimer.singleShot(0, self.set_initial_splitter_sizes)
        else:
            # 分离提示词管理器并显示在屏幕中央，窗口大小默认为屏幕宽度与高度方向的60%
            index = self.main_splitter.indexOf(self.prompt_manager)
            if index != -1:
                self.main_splitter.widget(index).setParent(None)
            self.prompt_manager.setParent(None)
            self.prompt_manager.show()
            # 设置窗口大小和位置
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            width = screen_geometry.width() * 0.6
            height = screen_geometry.height() * 0.6
            x = (screen_geometry.width() - width) / 2
            y = (screen_geometry.height() - height) / 2
            self.prompt_manager.setGeometry(int(x), int(y), int(width), int(height))
            self.config["prompt_manager_docked"] = False

    def set_initial_splitter_sizes(self):
        total_height = self.main_splitter.height()
        ai_height = int(total_height * 0.8)
        prompt_height = total_height - ai_height
        self.main_splitter.setSizes([ai_height, prompt_height])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 在窗口大小变化时，重新设置分割器的尺寸
        if self.dock_prompt_manager_action.isChecked():
            total_height = self.main_splitter.height()
            ai_height = int(total_height * 0.8)
            prompt_height = total_height - ai_height
            self.main_splitter.setSizes([ai_height, prompt_height])

    def create_ai_platforms(self):
        # 清除现有的 AI 平台窗口
        for i in reversed(range(self.ai_platform_layout.count())):
            widget = self.ai_platform_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.ai_platform_widgets = []

        # 创建新的 AI 平台窗口
        platforms_to_create = self.config['ai_platforms'][:self.num_platforms]
        for idx, platform in enumerate(platforms_to_create):
            window_index = idx + 1  # Start index from 1
            ai_widget = AIPlatform(
                platform['name'],
                platform['url'],
                self.profile_manager,
                self.config.get('common_urls', {}),
                window_index,
                self.config,
                self
            )
            ai_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # 设置初始划线颜色
            ai_widget.set_highlight_color(self.current_highlight_color)
            self.ai_platform_widgets.append(ai_widget)
            self.ai_platform_layout.addWidget(ai_widget)
        # 浏览器的宽度按整体窗口宽度总是平均分配
        for i in range(len(self.ai_platform_widgets)):
            self.ai_platform_layout.setStretch(i, 1)

    def load_chat_history(self, chat):
        urls = chat['urls']
        num_urls = len(urls)
        self.num_platforms = num_urls
        self.create_ai_platforms()
        for idx, ai_widget in enumerate(self.ai_platform_widgets):
            ai_widget.url = urls[idx]
            ai_widget.address_bar.setText(ai_widget.url)
            ai_widget.browser.load(QUrl(ai_widget.url))

    def send_prompt_to_all(self, prompt):
        self.current_prompt = prompt  # Save current prompt for checking
        for ai_widget in self.ai_platform_widgets:
            ai_widget.send_prompt(prompt)
        # Record the sent prompt
        with open('prompt_send.log', 'a', encoding='utf-8') as f:
            f.write(f'发送提示词：{prompt}\n')

    def closeEvent(self, event):
        # Save prompt manager docked state
        self.config["prompt_manager_docked"] = self.dock_prompt_manager_action.isChecked()
        # Save window geometry and state
        self.config["window_geometry"] = self.saveGeometry().toHex().data().decode()
        self.config["window_state"] = self.saveState().toHex().data().decode()
        # Save platform coordinates are handled in AIPlatform.save_coordinates()
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set application icon
    if os.path.exists('icon.png'):
        app.setWindowIcon(QIcon('icon.png'))
    else:
        app.setWindowIcon(QIcon())

    # 设置全局字体
    font = QFont()
    font.setFamily('Arial')
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
