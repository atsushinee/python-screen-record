# _*_ coding:utf-8 _*_
import shutil

from PIL import ImageGrab
from PyQt5.QtCore import QCoreApplication, Qt, qAbs, QRect, QPoint
from PyQt5.QtGui import QPen, QPainter, QIcon, QFont
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QCheckBox, QMessageBox, QFileDialog, QDialog, \
    QApplication, QWidget

from base import Base
from config import ABSOLUTE_PATH
from screen_record_thread import ScreenRecordThread, SaveMp4Thread


class ScreenBar(Base):
    def __init__(self):
        super(ScreenBar, self).__init__()
        self.box = QVBoxLayout()
        self.btn_box = QHBoxLayout()
        self.tip_label = QLabel(' 屏幕录制 - by lichun ')
        self.is_record_full = QCheckBox()
        self.open_btn = QPushButton()
        self.start_btn = QPushButton()
        self.end_btn = QPushButton()
        self.close_btn = QPushButton()
        self.recording_thread = ScreenRecordThread()
        self.bind()
        self.set_style()

    def set_style(self):
        self.start_btn.setEnabled(False)
        self.end_btn.setEnabled(False)
        self.tip_label.setFont(QFont('Arial', 10))
        self.start_btn.setIcon(QIcon('res/start.png'))
        self.end_btn.setIcon(QIcon('res/stop.png'))
        self.close_btn.setIcon(QIcon('res/close.png'))
        self.is_record_full.setIcon(QIcon('res/full.png'))
        self.open_btn.setIcon(QIcon('res/rect.png'))
        self.btn_box.addWidget(self.is_record_full, 0)
        self.btn_box.addWidget(self.open_btn, 0)
        self.btn_box.addWidget(self.start_btn, 0)
        self.btn_box.addWidget(self.end_btn, 0)
        self.btn_box.addWidget(self.close_btn, 0)
        self.box.addWidget(self.tip_label)
        self.box.addLayout(self.btn_box)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.setWindowOpacity(0.7)
        self.frameGeometry()
        self.move(QApplication.desktop().frameGeometry().width() - 300,
                  QApplication.desktop().frameGeometry().height() - 150)
        self.setLayout(self.box)

    def thread_trigger_signal(self, list, fps, gif_list):
        def show_success_message(str):
            QMessageBox.information(self, "提示", str, QMessageBox.Yes)
            self.end_btn.setEnabled(False)
            self.open_btn.setEnabled(True)
            self.is_record_full.setEnabled(True)

        path, tmp = QFileDialog.getSaveFileName(self,
                                                "文件保存",
                                                '%s/video.mp4' % ABSOLUTE_PATH,
                                                "All Files (*);")
        if not '' == path:
            self.save_mp4_thread = SaveMp4Thread(list, fps, path, gif_list)
            self.save_mp4_thread.trigger.connect(lambda: show_success_message("保存成功"))
            self.save_mp4_thread.start()
        else:
            show_success_message("取消保存")
            shutil.rmtree('temp')

    def bind(self):
        def open_signal():
            self.screen_label = ScreenLabel()
            self.screen_label.show()
            self.start_btn.setEnabled(True)
            self.is_record_full.setEnabled(False)

        def start_signal():
            self.open_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.end_btn.setEnabled(True)
            self.recording_thread.recording = True
            if self.is_record_full.isChecked():
                self.recording_thread.area = None
                self.recording_thread.start()
            else:
                fq = self.screen_label._rect
                x1 = fq.topLeft().x() + 2
                y1 = fq.topLeft().y() + 2
                x2 = fq.bottomRight().x() - 2
                y2 = fq.bottomRight().y() - 2
                if (x2 - x1) % 2:
                    x2 += 1
                if (y2 - y1) % 2:
                    y2 -= 1
                self.recording_thread.area = (x1, y1, x2, y2)
                self.recording_thread.start()
                self.screen_label.close()
                self.screen_label.deleteLater()

        def end_signal():
            self.recording_thread.recording = False

        def record_full_signal():
            if self.is_record_full.isChecked():
                self.open_btn.setEnabled(False)
                self.start_btn.setEnabled(True)
            else:
                self.open_btn.setEnabled(True)
                self.start_btn.setEnabled(False)

        self.open_btn.clicked.connect(open_signal)
        self.start_btn.clicked.connect(start_signal)
        self.end_btn.clicked.connect(end_signal)
        self.close_btn.clicked.connect(QCoreApplication.instance().quit)
        self.is_record_full.stateChanged.connect(record_full_signal)
        self.recording_thread.trigger.connect(self.thread_trigger_signal)


class ScreenLabel(QWidget):
    def __init__(self):
        super(ScreenLabel, self).__init__()
        self.box = QHBoxLayout()
        self.box.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.box.addWidget(self.label, 0)
        self.setLayout(self.box)
        self.setMouseTracking(True)
        self.m_isMousePress = False
        self.m_beginPoint = QPoint()
        self.m_endPoint = QPoint()
        self.m_painter = QPainter()
        self.pixmap = ImageGrab.grab().toqpixmap()
        self.cap = self.pixmap
        self._rect = QRect(0, 0, 0, 0)
        self.label.setPixmap(self.pixmap)
        self.setWindowState(Qt.WindowActive | Qt.WindowFullScreen)
        self.show()
        # self.resize(600, 600)
        self.label.setStyleSheet(
            'border:1px solid red;')
        self.setWindowOpacity(0.9)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Enter:
            self.close()
            self.deleteLater()

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.m_isMousePress = True
            self.m_beginPoint = QMouseEvent.pos()
        elif QMouseEvent.button() == Qt.RightButton:
            self.close()
            # self.deleteLater()

        return super().mousePressEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        if self.m_isMousePress:
            self.m_endPoint = QMouseEvent.pos()
            self.update()
        return super().mouseMoveEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_endPoint = QMouseEvent.pos()
        self.m_isMousePress = False
        return super().mouseReleaseEvent(QMouseEvent)

    def paintEvent(self, PaintEvent):
        self.m_painter.begin(self.pixmap)
        # shadowColor = QColor(0, 0, 0, 100)  # 阴影颜色设置;
        self.m_painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine, Qt.FlatCap))  # 设置画笔;
        # self.m_painter.fillRect(self.pixmap.rect(), shadowColor)  # 画影罩效果

        if self.m_isMousePress:
            self.selectedRect = self.getRect()
            self.cap = self.pixmap.copy(self.selectedRect)
            self.m_painter.drawPixmap(self.selectedRect.x(), self.selectedRect.y(), self.selectedRect.width(),
                                      self.selectedRect.height(), self.cap)
            self.label.move(self.selectedRect.topLeft())
            self.label.resize(self.cap.size())
            self.label.setPixmap(self.cap)
            self._rect = self.selectedRect
        else:
            self.selectedRect = self._rect
            self.label.move(self.selectedRect.topLeft())
            self.label.resize(self.cap.size())
            self.label.setPixmap(self.cap)
        self.m_painter.end()  # 重绘结束;

    def getRect(self):
        width = qAbs(self.m_beginPoint.x() - self.m_endPoint.x())
        height = qAbs(self.m_beginPoint.y() - self.m_endPoint.y())
        x = self.m_beginPoint.x() if self.m_beginPoint.x() < self.m_endPoint.x() else self.m_endPoint.x()
        y = self.m_beginPoint.y() if self.m_beginPoint.y() < self.m_endPoint.y() else self.m_endPoint.y()

        selectedRect = QRect(x, y, width, height)
        if selectedRect.width() == 0:
            selectedRect.setWidth(1)
        if selectedRect.height() == 0:
            selectedRect.setHeight(1)
        return selectedRect
