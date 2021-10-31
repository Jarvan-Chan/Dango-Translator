# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui.switch import OfflineSwitch, SwitchOCR, SwitchFontType, ShowSwitch, SwitchDirection
from ui.desc import Desc
from ui.key import Key
from ui.hotkey import HotKey
import utils
from utils import MessageBox, detectPort, testOfflineOCR, postConfigURL

from translator.ocr.baidu import getAccessToken
from translator.all import resetWeb
from ui import image

import os
import qtawesome
import webbrowser
import threading


OCR_CMD_PATH = "E:/DangoTranslate-Ver3.6.2/DangoOCR-Ver1.2/startOCR.cmd"
LOGO_ICON_PATH = "./config/icon/logo.ico"
PIXMAP_ICON_PATH = "./config/icon/pixmap.png"
OCR_ICON_PATH = "./config/icon/ocr.png"
ABOUT_ICON_PATH = "./config/icon/about.png"
STYPE_ICON_PATH = "./config/icon/stype.png"
TRANSLATE_ICON_PATH = "./config/icon/translate.png"
GOOD_ICON_PATH = "./config/icon/good.png"
HOLLOW_IMG_PATH = "./config/other/描边.png"
SOLID_IMG_PATH = "./config/other/实心.png"


# 重构QTabWidget使其竖直选项卡文字水平
class TabBar(QTabBar):

    def tabSizeHint(self, index):

        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s


    def paintEvent(self, event):

        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


# 重构QTabWidget使其竖直选项卡文字水平
class TabWidget(QTabWidget):

    def __init__(self, *args, **kwargs):

        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))


class Settin(QMainWindow):

    def __init__(self, config, logger, window):

        super(Settin, self).__init__()

        self.config = config
        self.logger = logger
        self.translation_ui = window

        self.getInitConfig()
        self.ui()
        # 初始化密钥界面
        self.key_ui = Key(self.config, self)


    def ui(self):

        # 窗口尺寸及不可拉伸
        self.resize(self.window_width, self.window_height)
        self.setMinimumSize(QSize(self.window_width, self.window_height))
        self.setMaximumSize(QSize(self.window_width, self.window_height))
        # 窗口置顶及关闭窗口最小化最大化
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        # 窗口标题
        self.setWindowTitle("团子翻译器 Ver4.0 - 设置")

        # 窗口图标
        icon = QIcon()
        icon.addPixmap(QPixmap(LOGO_ICON_PATH), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)

        # 鼠标样式
        pixmap = QPixmap(PIXMAP_ICON_PATH)
        pixmap = pixmap.scaled(int(30*self.rate),
                               int(34*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        cursor = QCursor(pixmap, 0, 0)
        self.setCursor(cursor)

        # 设置字体
        self.setStyleSheet("font: 10pt '华康方圆体W7'; color: %s" % self.color_1)

        # 顶部工具栏
        self.tabWidget = TabWidget(self)
        self.tabWidget.setGeometry(QRect(0, -1, self.window_width+5, self.window_height+5))
        self.tabWidget.setTabPosition(QTabWidget.West)
        # 工具栏样式
        self.tabWidget.setStyleSheet("QTabBar:tab { min-width: %dpx;"
                                                   "background: rgba(255, 255, 255, 1); }"
                                     "QTabBar:tab:selected { background: rgba(62, 62, 62, 0.01); }"
                                     "QTabWidget::pane { border-image: url(./config/background/settin.jpg); }"
                                     "QPushButton { background: %s;"
                                                   "border-radius: %spx;"
                                                   "color: rgb(255, 255, 255); }"
                                     "QPushButton:hover { background-color: #83AAF9; }"
                                     "QPushButton:pressed { background-color: #4480F9;"
                                                           "padding-left: 3px;"
                                                           "padding-top: 3px; }"
                                     "QTextEdit { background: transparent;"
                                                 "border-width: 0;"
                                                 "border-style: outset;"
                                                 "border-bottom: 2px solid %s; }"
                                     "QTextEdit:focus { border-bottom: 2px;"
                                                       "dashed %s; }"
                                     "QSlider:groove:horizontal { height: %spx;"
                                                                 "border-radius: %spx;"
                                                                 "margin-left: %spx;"
                                                                 "margin-right: %spx;"
                                                                 "background: rgba(89, 89, 89, 0.3); }"
                                     "QSlider:handle:horizontal { width: %spx;"
                                                                  "height: %spx;"
                                                                  "margin-top: %spx;"
                                                                  "margin-left: %spx;"
                                                                  "margin-bottom: %spx;"
                                                                  "margin-right: %spx;"
                                                                  "border-image: url(./config/icon/logo.ico); }"
                                     "QSlider::sub-page:horizontal { height: %spx;"
                                                                    "border-radius: %spx;"
                                                                    "margin-left: %spx;"
                                                                    "background: %s; }"
                                     "QSpinBox { background: rgba(255, 255, 255, 0.3); }"
                                     "QFontComboBox { background: rgba(255, 255, 255, 0.3); }"
                                     "QDoubleSpinBox { background: rgba(255, 255, 255, 0.3); }"
                                     %(80*self.rate, self.color_2, 6.66*self.rate, self.color_2, self.color_2,
                                       8.66*self.rate, 4*self.rate, 13.33*self.rate, 13.33*self.rate,
                                       33.33*self.rate, 33.33*self.rate, -13.33*self.rate, -13.33*self.rate,
                                       -13.33*self.rate, -13.33*self.rate, 8.66*self.rate, 4*self.rate,
                                       10*self.rate, self.color_2
                                       ))

        # 选项卡
        self.setTabOne()
        self.setTabTwo()
        self.setTabThree()
        self.setTabFour()
        self.setTabFive()

        # 离线OCR标签
        label = QLabel(self)
        self.customSetGeometry(label, 530, 380, 200, 15)
        label.setText("背景图 pixiv id: 92140553")
        label.setStyleSheet("font-size: 9pt; color: %s"%self.color_2)


    # OCR设定标签页
    def setTabOne(self) :

        # 选项卡界面
        self.tab_1 = QWidget()
        self.customSetGeometry(self.tab_1, 0, 0, self.window_width, self.window_height)
        self.tabWidget.addTab(self.tab_1, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), "OCR设定")

        # 分割线
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 0, 0, 1, 400)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; "
                            "border-style: solid; "
                            "border-color: rgba(62, 62, 62, 0.2);")

        # 选项卡图标
        icon = QIcon()
        pixmap = QPixmap(OCR_ICON_PATH)
        pixmap = pixmap.scaled(int(15*self.rate),
                               int(15*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_1), icon)

        # 此Label用于雾化工具栏1的背景图
        label = QLabel(self.tab_1)
        label.setGeometry(QRect(0, -1, self.window_width+5, self.window_height+5))
        label.setStyleSheet("background: rgba(255, 255, 255, 0.5);")

        # OCR说明
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 480, 25, 65, 20)
        button.setStyleSheet("color: %s;"
                             "background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("什么是OCR")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("OCR"))

        # OCR说明?号
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_1)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 545, 25, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("OCR"))

        # 离线OCR标签
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 25, 60, 20)
        label.setText("离线OCR")

        # 离线OCR说明按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 80, 25, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("offlineOCR"))

        # 离线OCR说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_1)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 105, 25, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("offlineOCR"))

        # 离线OCR状态开关
        self.offline_ocr_switch = OfflineSwitch(self.tab_1, startX=(65-20)*self.rate)
        self.customSetGeometry(self.offline_ocr_switch, 20, 60, 65, 20)
        self.offline_ocr_switch.checkedChanged.connect(self.changeOfflineSwitch)
        self.offline_ocr_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 离线OCR运行按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 105, 60, 60, 20)
        button.setText("运行")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(self.runOfflineOCR)

        # 离线OCR测试按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 185, 60, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(self.testOfflineOCR)

        # 离线OCR教程按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 265, 60, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(self.openOfflineOCRTutorial)

        # 在线OCR标签
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 120, 60, 20)
        label.setText("在线OCR")

        # 在线OCR说明按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 80, 120, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("onlineOCR"))

        # 在线OCR说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_1)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 105, 120, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("onlineOCR"))

        # 在线OCR状态开关
        self.online_ocr_switch = SwitchOCR(self.tab_1, self.online_ocr_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.online_ocr_switch, 20, 155, 65, 20)
        self.online_ocr_switch.checkedChanged.connect(self.changeOnlineSwitch)
        self.online_ocr_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 在线OCR测试按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 105, 155, 60, 20)
        button.setText("购买")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 在线OCR购买按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 185, 155, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 在线OCR教程按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 265, 155, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 百度OCR标签
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 215, 60, 20)
        label.setText("百度OCR")

        # 百度OCR说明标签
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 80, 215, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("baiduOCR"))

        # 百度OCR说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_1)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 105, 215, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("baiduOCR"))

        # 百度OCR状态开关
        self.baidu_ocr_switch = SwitchOCR(self.tab_1, self.baidu_ocr_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.baidu_ocr_switch, 20, 250, 65, 20)
        self.baidu_ocr_switch.checkedChanged.connect(self.changeBaiduSwitch)
        self.baidu_ocr_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 百度OCR测试按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 105, 250, 60, 20)
        button.setText("密钥")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showKey("baiduOCR"))

        # 百度OCR教程按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 185, 250, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人百度翻译密钥按钮
        button = QPushButton(self.tab_1)
        self.customSetGeometry(button, 265, 250, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # OCR识别语种标签
        label = QLabel(self.tab_1)
        self.customSetGeometry(label, 20, 310, 150, 20)
        label.setText("选择要翻译的原语种:")

        # OCR识别语种comboBox
        self.language_comboBox = QComboBox(self.tab_1)
        self.customSetGeometry(self.language_comboBox, 160, 310, 130, 20)
        self.language_comboBox.addItem("")
        self.language_comboBox.addItem("")
        self.language_comboBox.addItem("")
        self.language_comboBox.setItemText(0, "日语（Japanese）")
        self.language_comboBox.setItemText(1, "英语（English）")
        self.language_comboBox.setItemText(2, "韩语（Korean）")
        self.language_comboBox.setStyleSheet("background: rgba(255, 255, 255, 1);")
        if self.config["language"] == "ENG":
            self.language_comboBox.setCurrentIndex(1)
        elif self.config["language"] == "KOR":
            self.language_comboBox.setCurrentIndex(2)
        else:
            self.language_comboBox.setCurrentIndex(0)


    # 翻译设定标签栏
    def setTabTwo(self) :

        # 选项卡界面
        self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), " 翻译设定")

        # 分割线
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 0, 0, 1, 400)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; border-style: solid; border-color: rgba(62, 62, 62, 0.2);")

        # 选项卡图标
        icon = QIcon()
        pixmap = QPixmap(TRANSLATE_ICON_PATH)
        pixmap = pixmap.scaled(int(20*self.rate),
                               int(20*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_2), icon)

        # 此Label用于雾化工具栏2的背景图
        imageLabel = QLabel(self.tab_2)
        imageLabel.setGeometry(QRect(0, -1, self.window_width+5, self.window_height+5))
        imageLabel.setStyleSheet("background: rgba(255, 255, 255, 0.5);")

        # 公共翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 25, 70, 20)
        label.setText("公共翻译")
        label.setCursor(QCursor(Qt.PointingHandCursor))

        # 公共翻译说明标签
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 90, 25, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("publicTranslate"))

        # 公共翻译说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_2)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 115, 25, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("publicTranslate"))

        # 公共翻译教程按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 160, 25, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 有道翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 70, 35, 20)
        label.setText("有道:")

        # 有道翻译开关
        self.youdao_switch = SwitchOCR(self.tab_2, sign=self.youdao_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.youdao_switch, 65, 70, 65, 20)
        self.youdao_switch.checkedChanged.connect(self.changeYoudaoSwitch)
        self.youdao_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 有道翻译颜色选择
        self.youdao_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.youdao_color), "", self.tab_2)
        self.customSetIconSize(self.youdao_color_button, 20, 20)
        self.customSetGeometry(self.youdao_color_button, 140, 70, 20, 20)
        self.youdao_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.youdao_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.youdao_color_button.clicked.connect(lambda: self.ChangeTranslateColor("youdao", self.youdao_color))

        # 百度翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 200, 70, 35, 20)
        label.setText("百度:")

        # 百度翻译开关
        self.baidu_switch = SwitchOCR(self.tab_2, sign=self.baidu_web_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.baidu_switch, 245, 70, 65, 20)
        self.baidu_switch.checkedChanged.connect(self.changeBaiduWebSwitch)
        self.baidu_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 百度翻译颜色选择
        self.baidu_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.baidu_web_color), "", self.tab_2)
        self.customSetIconSize(self.baidu_color_button, 20, 20)
        self.customSetGeometry(self.baidu_color_button, 320, 70, 20, 20)
        self.baidu_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.baidu_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.baidu_color_button.clicked.connect(lambda: self.ChangeTranslateColor("baidu", self.baidu_web_color))

        # 腾讯翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 380, 70, 35, 20)
        label.setText("腾讯:")

        # 腾讯翻译开关
        self.tencent_switch = SwitchOCR(self.tab_2, sign=self.tencent_web_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.tencent_switch, 425, 70, 65, 20)
        self.tencent_switch.checkedChanged.connect(self.changeTencentWebSwitch)
        self.tencent_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 腾讯翻译颜色选择
        self.tencent_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.tencent_web_color), "", self.tab_2)
        self.customSetIconSize(self.tencent_color_button, 20, 20)
        self.customSetGeometry(self.tencent_color_button, 500, 70, 20, 20)
        self.tencent_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.tencent_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.tencent_color_button.clicked.connect(lambda: self.ChangeTranslateColor("tencent", self.tencent_web_color))

        # DeepL翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 120, 40, 20)
        label.setText("DeepL:")

        # DeepL翻译开关
        self.deepl_switch = SwitchOCR(self.tab_2, sign=self.deepl_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.deepl_switch, 65, 120, 65, 20)
        self.deepl_switch.checkedChanged.connect(self.changeDeepLSwitch)
        self.deepl_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # DeepL翻译颜色选择
        self.deepl_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.deepl_color), "", self.tab_2)
        self.customSetIconSize(self.deepl_color_button, 20, 20)
        self.customSetGeometry(self.deepl_color_button, 140, 120, 20, 20)
        self.deepl_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.deepl_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.deepl_color_button.clicked.connect(lambda: self.ChangeTranslateColor("deepl", self.deepl_color))

        # 谷歌翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 200, 120, 35, 20)
        label.setText("谷歌:")

        # 谷歌翻译开关
        self.google_switch = SwitchOCR(self.tab_2, sign=self.google_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.google_switch, 245, 120, 65, 20)
        self.google_switch.checkedChanged.connect(self.changeGoogleSwitch)
        self.google_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 谷歌翻译颜色选择
        self.google_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.google_color), "", self.tab_2)
        self.customSetIconSize(self.google_color_button, 20, 20)
        self.customSetGeometry(self.google_color_button, 320, 120, 20, 20)
        self.google_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.google_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.google_color_button.clicked.connect(lambda: self.ChangeTranslateColor("google", self.google_color))

        # 彩云翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 380, 120, 35, 20)
        label.setText("彩云:")

        # 彩云翻译开关
        self.caiyun_switch = SwitchOCR(self.tab_2, sign=self.caiyun_web_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.caiyun_switch, 425, 120, 65, 20)
        self.caiyun_switch.checkedChanged.connect(self.changeCaiyunWebSwitch)
        self.caiyun_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 彩云翻译颜色选择
        self.caiyun_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.caiyun_web_color), "", self.tab_2)
        self.customSetIconSize(self.caiyun_color_button, 20, 20)
        self.customSetGeometry(self.caiyun_color_button, 500, 120, 20, 20)
        self.caiyun_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.caiyun_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.caiyun_color_button.clicked.connect(lambda: self.ChangeTranslateColor("caiyun", self.caiyun_web_color))

        # 私人翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 185, 70, 20)
        label.setText("私人翻译")

        # 私人翻译说明标签
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 90, 185, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);"%self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("privateTranslate"))

        # 私人翻译说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_2)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 115, 185, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("privateTranslate"))

        # 私人腾讯翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 230, 35, 20)
        label.setText("腾讯:")

        # 私人腾讯翻译开关
        self.tencent_private_switch = SwitchOCR(self.tab_2, sign=self.tencent_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.tencent_private_switch, 65, 230, 65, 20)
        self.tencent_private_switch.checkedChanged.connect(self.changeTencentSwitch)
        self.tencent_private_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人腾讯翻译颜色选择
        self.tencent_private_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.tencent_color), "", self.tab_2)
        self.customSetIconSize(self.tencent_private_color_button, 20, 20)
        self.customSetGeometry(self.tencent_private_color_button, 140, 230, 20, 20)
        self.tencent_private_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.tencent_private_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.tencent_private_color_button.clicked.connect(lambda: self.ChangeTranslateColor("tencent_private", self.tencent_use))

        # 私人腾讯翻译密钥按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 180, 230, 60, 20)
        button.setText("密钥")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showKey("tencentTranslate"))

        # 私人腾讯翻译测试按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 260, 230, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人腾讯翻译教程按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 340, 230, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人百度翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 280, 35, 20)
        label.setText("百度:")

        # 私人百度翻译开关
        self.baidu_private_switch = SwitchOCR(self.tab_2, sign=self.baidu_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.baidu_private_switch, 65, 280, 65, 20)
        self.baidu_private_switch.checkedChanged.connect(self.changeBaiduTranslaterSwitch)
        self.baidu_private_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人百度翻译颜色选择
        self.baidu_private_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.baidu_color), "", self.tab_2)
        self.customSetIconSize(self.baidu_private_color_button, 20, 20)
        self.customSetGeometry(self.baidu_private_color_button, 140, 280, 20, 20)
        self.baidu_private_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.baidu_private_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.baidu_private_color_button.clicked.connect(lambda: self.ChangeTranslateColor("baidu_private", self.baidu_color))

        # 私人百度翻译密钥按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 180, 280, 60, 20)
        button.setText("密钥")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showKey("baiduTranslate"))

        # 私人百度翻译测试按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 260, 280, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人百度翻译教程按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 340, 280, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人彩云翻译标签
        label = QLabel(self.tab_2)
        self.customSetGeometry(label, 20, 330, 35, 20)
        label.setText("彩云:")

        # 私人彩云翻译开关
        self.caiyun_private_switch = SwitchOCR(self.tab_2, sign=self.caiyun_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.caiyun_private_switch, 65, 330, 65, 20)
        self.caiyun_private_switch.checkedChanged.connect(self.changeCaiyunSwitch)
        self.caiyun_private_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人彩云翻译颜色选择
        self.caiyun_private_color_button = QPushButton(qtawesome.icon("fa5s.paint-brush", color=self.caiyun_color), "", self.tab_2)
        self.customSetIconSize(self.caiyun_private_color_button, 20, 20)
        self.customSetGeometry(self.caiyun_private_color_button, 140, 330, 20, 20)
        self.caiyun_private_color_button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        self.caiyun_private_color_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.caiyun_private_color_button.clicked.connect(lambda: self.ChangeTranslateColor("caiyun_private", self.caiyun_color))

        # 私人彩云翻译密钥按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 180, 330, 60, 20)
        button.setText("密钥")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showKey("caiyunTranslate"))

        # 私人彩云翻译测试按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 260, 330, 60, 20)
        button.setText("测试")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # 私人彩云翻译教程按钮
        button = QPushButton(self.tab_2)
        self.customSetGeometry(button, 340, 330, 60, 20)
        button.setText("教程")
        button.setCursor(QCursor(Qt.PointingHandCursor))


    # 其他设定标签页
    def setTabThree(self) :

        # 选项卡界面
        self.tab_3 = QWidget()
        self.tabWidget.addTab(self.tab_3, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), " 其他设定")

        # 分割线
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 0, 0, 1, 400)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; border-style: solid; border-color: rgba(62, 62, 62, 0.2);")

        # 选项卡图标
        icon = QIcon()
        pixmap = QPixmap(STYPE_ICON_PATH)
        pixmap = pixmap.scaled(int(20*self.rate),
                               int(20*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_3), icon)

        # 此Label用于雾化工具栏1的背景图
        imageLabel = QLabel(self.tab_3)
        imageLabel.setGeometry(QRect(0, -1, self.window_width + 5, self.window_height + 5))
        imageLabel.setStyleSheet("background: rgba(255, 255, 255, 0.5);")

        # 翻译框透明度设定标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 20, 90, 20)
        label.setText("翻译框透明度:")

        # 翻译框透明度设定
        self.horizontal_slider = QSlider(self.tab_3)
        self.customSetGeometry(self.horizontal_slider, 120, 18, 320, 25)
        self.horizontal_slider.setMaximum(100)
        self.horizontal_slider.setOrientation(Qt.Horizontal)
        self.horizontal_slider.setValue(0)
        self.horizontal_slider.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontal_slider.setValue(self.horizontal)
        self.horizontal_slider.valueChanged.connect(self.changeHorizontal)

        # 翻译框透明度数值标签
        self.horizontal_slider_label = QLabel(self.tab_3)
        self.customSetGeometry(self.horizontal_slider_label, 450, 20, 30, 20)
        self.horizontal_slider_label.setText("{}%".format(self.horizontal))

        # 翻译框透明度说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 490, 20, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("horizontalSlider"))

        # 翻译框透明度说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 515, 20, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("horizontalSlider"))

        # 翻译字体大小设定标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 70, 145, 16)
        label.setText("字体大小:")

        # 翻译字体大小设定
        self.fontSize_spinBox = QSpinBox(self.tab_3)
        self.customSetGeometry(self.fontSize_spinBox, 95, 65, 40, 25)
        self.fontSize_spinBox.setMinimum(10)
        self.fontSize_spinBox.setMaximum(30)
        self.fontSize_spinBox.setValue(self.fontSize)

        # 翻译字体类型设定标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 70, 145, 20)
        label.setText("字体类型:")

        # 翻译字体类型设定
        self.font_comboBox = QFontComboBox(self.tab_3)
        self.customSetGeometry(self.font_comboBox, 350, 65, 185, 25)
        self.font_comboBox.activated[str].connect(self.getFontType)
        self.comboBox_font = QFont(self.font_type)
        self.font_comboBox.setCurrentFont(self.comboBox_font)

        # 字体样式设定标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 120, 60, 20)
        label.setText("字体样式:")

        # 字体样式设定开关
        self.font_type_switch = SwitchFontType(self.tab_3, sign=self.font_color_type, startX=(65-20)*self.rate)
        self.customSetGeometry(self.font_type_switch, 95, 120, 65, 20)
        self.font_type_switch.checkedChanged.connect(self.changeFontColorTypeSwitch)
        self.font_type_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 字体样式设定说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 175, 120, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("fontType"))

        # 字体样式设定说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 200, 120, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("fontType"))

        # 自动翻译间隔标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 120, 150, 20)
        label.setText("自动模式刷新间隔(秒):")

        # 自动模式速率设定
        self.auto_speed_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.auto_speed_spinBox, 430, 115, 45, 25)
        self.auto_speed_spinBox.setDecimals(1)
        self.auto_speed_spinBox.setMinimum(0.5)
        self.auto_speed_spinBox.setMaximum(10.0)
        self.auto_speed_spinBox.setSingleStep(0.1)
        self.auto_speed_spinBox.setValue(self.translate_speed)

        # 自动模式速率设定说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 490, 120, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("autoSpeed"))

        # 自动模式速率设定说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 515, 120, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("autoSpeed"))

        # 显示原文标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 170, 60, 20)
        label.setText("显示原文:")

        # 显示原文标签开关
        self.show_original_switch = ShowSwitch(self.tab_3, sign=self.show_original_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.show_original_switch, 95, 170, 65, 20)
        self.show_original_switch.checkedChanged.connect(self.changeShowOriginalSwitch)
        self.show_original_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 显示原文说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 175, 170, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("showOriginal"))

        # 显示原文说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 200, 170, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("showOriginal"))

        # 原文自动复制到剪贴板标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 170, 150, 20)
        label.setText("原文自动复制到剪贴板:")

        # 原文自动复制到剪贴板开关
        self.auto_copy_original_switch = SwitchOCR(self.tab_3, sign=self.auto_clipboard_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.auto_copy_original_switch, 430, 170, 65, 20)
        self.auto_copy_original_switch.checkedChanged.connect(self.changeAutoCopyOriginalSwitch)
        self.auto_copy_original_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 文字方向标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 220, 80, 20)
        label.setText("文字方向:")

        # 文字方向开关
        self.text_direction_switch = SwitchDirection(self.tab_3, sign=self.text_direction_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.text_direction_switch, 95, 220, 65, 20)
        self.text_direction_switch.checkedChanged.connect(self.changeTextDirectionSwitch)
        self.text_direction_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 文字方向说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 175, 220, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("textDirection"))

        # 文字方向说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 200, 220, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("textDirection"))

        # 翻译快捷键标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 270, 80, 20)
        label.setText("翻译热键:")

        # 翻译快捷键开关
        self.translate_hotkey_switch = SwitchOCR(self.tab_3, sign=self.translate_hotkey_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.translate_hotkey_switch, 95, 270, 65, 20)
        self.translate_hotkey_switch.checkedChanged.connect(self.changeTranslateHotkeySwitch)
        self.translate_hotkey_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 翻译快捷键设定按钮
        self.translate_hotkey_button = QPushButton(self.tab_3)
        self.customSetGeometry(self.translate_hotkey_button, 175, 270, 60, 20)
        self.translate_hotkey_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.translate_hotkey_button.setText(self.config["showHotKeyValue1"])
        self.translate_hotkey_button.clicked.connect(lambda: self.setHotKey("translate"))

        # 范围快捷键标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 270, 80, 20)
        label.setText("范围热键:")

        # 范围快捷键开关
        self.range_hotkey_switch = SwitchOCR(self.tab_3, sign=self.range_hotkey_use, startX=(65-20)*self.rate)
        self.customSetGeometry(self.range_hotkey_switch, 350, 270, 65, 20)
        self.range_hotkey_switch.checkedChanged.connect(self.changeRangeHotkeySwitch)
        self.range_hotkey_switch.setCursor(QCursor(Qt.PointingHandCursor))

        # 范围快捷键设定按钮
        self.range_hotkey_button = QPushButton(self.tab_3)
        self.customSetGeometry(self.range_hotkey_button, 430, 270, 60, 20)
        self.range_hotkey_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.range_hotkey_button.setText(self.config["showHotKeyValue2"])
        self.range_hotkey_button.clicked.connect(lambda: self.setHotKey("range"))

        # 图像相似度标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 20, 320, 150, 20)
        label.setText("图像相似度(%):")

        # 图像相似度设定
        self.image_refresh_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.image_refresh_spinBox, 130, 317, 45, 25)
        self.image_refresh_spinBox.setDecimals(0)
        self.image_refresh_spinBox.setMinimum(80)
        self.image_refresh_spinBox.setMaximum(100)
        self.image_refresh_spinBox.setSingleStep(1)
        self.image_refresh_spinBox.setValue(self.image_refresh_score)

        # 图像相似度说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 190, 320, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("imageRefresh"))

        # 图像相似度说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 215, 320, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("imageRefresh"))

        # 文字相似度标签
        label = QLabel(self.tab_3)
        self.customSetGeometry(label, 275, 320, 150, 20)
        label.setText("文字相似度(%):")

        # 文字相似度设定
        self.text_refresh_spinBox = QDoubleSpinBox(self.tab_3)
        self.customSetGeometry(self.text_refresh_spinBox, 385, 317, 45, 25)
        self.text_refresh_spinBox.setDecimals(0)
        self.text_refresh_spinBox.setMinimum(80)
        self.text_refresh_spinBox.setMaximum(100)
        self.text_refresh_spinBox.setSingleStep(1)
        self.text_refresh_spinBox.setValue(self.text_refresh_score)

        # 文字相似度说明标签
        button = QPushButton(self.tab_3)
        self.customSetGeometry(button, 445, 320, 25, 20)
        button.setStyleSheet("color: %s; font-size: 9pt; background: rgba(255, 255, 255, 0);" % self.color_2)
        button.setText("说明")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("textRefresh"))

        # 文字相似度说明?号图标
        button = QPushButton(qtawesome.icon("fa.question-circle", color=self.color_2), "", self.tab_3)
        self.customSetIconSize(button, 20, 20)
        self.customSetGeometry(button, 470, 320, 20, 20)
        button.setStyleSheet("background: rgba(255, 255, 255, 0);")
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.showDesc("textRefresh"))


    # 关于标签页
    def setTabFour(self) :

        # 选项卡界面
        self.tab_4 = QWidget()
        self.tabWidget.addTab(self.tab_4, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), "关于   ")

        # 分割线
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 0, 0, 1, 400)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; border-style: solid; border-color: rgba(62, 62, 62, 0.2);")

        # 选项卡图标
        icon = QIcon()
        pixmap = QPixmap(ABOUT_ICON_PATH)
        pixmap = pixmap.scaled(int(20*self.rate),
                               int(20*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_4), icon)

        # 此Label用于雾化工具栏1的背景图
        imageLabel = QLabel(self.tab_4)
        imageLabel.setGeometry(QRect(0, -1, self.window_width + 5, self.window_height + 5))
        imageLabel.setStyleSheet("background: rgba(255, 255, 255, 0.5);")

        # 项目地址标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 110, 25, 300, 20)
        label.setText("本软件已在github开源 (欢迎来点小星星)")

        # 项目地址按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 25, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("项目地址")
        button.clicked.connect(lambda: webbrowser.open(self.dango_translator_url))

        # 在线教程标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 110, 75, 300, 20)
        label.setText("软件完整使用教程 (要好好阅读哦)")

        # 在线教程按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 75, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("在线文档")
        button.clicked.connect(lambda: webbrowser.open(self.tutorial_url))

        # 添加作者标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 110, 125, 300, 20)
        label.setText("联系作者 (QQ好友申请)")

        # 添加作者按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 125, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("胖次团子")
        button.clicked.connect(lambda: webbrowser.open(self.add_author_url))

        # 添加交流群标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 110, 175, 300, 20)
        label.setText("加入交流群 (QQ群申请)")

        # 添加交流群按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 175, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("交流群")
        button.clicked.connect(lambda: self.showDesc("qqGroup"))

        # 更新日志标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 110, 225, 300, 20)
        label.setText("查看本软件更新日志")

        # 更新日志按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 226, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("更新日志")
        button.clicked.connect(lambda: webbrowser.open(self.update_log))

        # 特别鸣谢标签
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 280, 300, 20)
        label.setText("特别鸣谢 (本软件受到以下人员和项目的帮助)")

        # PaddleOCR主页按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 20, 320, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("PaddleOCR‭")
        button.clicked.connect(lambda: webbrowser.open(self.PaddleOCR_github_url))

        # GT-Zhang主页按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 130, 320, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("GT-Zhang")
        button.clicked.connect(lambda: webbrowser.open(self.gt_github_url))

        # C4a15Wh主页按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 240, 320, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("C4a15Wh")
        button.clicked.connect(lambda: webbrowser.open(self.c44_github_url))

        # C4a15Wh主页按钮
        button = QPushButton(self.tab_4)
        self.customSetGeometry(button, 350, 320, 70, 20)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setText("Cypas‭")
        button.clicked.connect(lambda: webbrowser.open(self.cy_github_url))


    # 支持作者标签页
    def setTabFive(self) :

        # 选项卡界面
        self.tab_5 = QWidget()
        self.tabWidget.addTab(self.tab_5, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), " 支持作者")

        # 分割线
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 0, 0, 1, 400)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameShape(QFrame.Box)
        label.setStyleSheet("border-width: 1px; border-style: solid; border-color: rgba(62, 62, 62, 0.2);")

        # 选项卡图标
        icon = QIcon()
        pixmap = QPixmap(GOOD_ICON_PATH)
        pixmap = pixmap.scaled(int(20*self.rate),
                               int(20*self.rate),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_5), icon)

        # 此Label用于雾化工具栏1的背景图
        imageLabel = QLabel(self.tab_5)
        imageLabel.setGeometry(QRect(0, -1, self.window_width + 5, self.window_height + 5))
        imageLabel.setStyleSheet("background: rgba(255, 255, 255, 0.5);")

        # 充电独白标签
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 30, 20, 400, 145)
        label.setText("<html><head/><body><p>你好呀, 这里是胖次团子 ❤\
                       </p><p>不知不觉软件已经更新到Ver4.0了, 这是团子最自豪的版本!\
                       </p><p>然后感谢你也成为团子用户的一员 ~\
                       </p><p>软件是免费的, 希望你没有被第三方渠道坑到 ~\
                       </p><p>欢迎你的投喂 ~ 团子会非常开心的! \
                       </p><p>这会是团子不断更新优化的动力 ~</p></body></html>")

        # 放置微信收款图片
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 20, 180, 150, 150)
        label.setStyleSheet("border-image: url(:/image/weixin.jpg);")

        # 放置支付宝收款图片
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 180, 180, 150, 150)
        label.setStyleSheet("border-image: url(:/image/zhifubao.jpg);")

        # 微信充电标签
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 65, 330, 80, 20)
        label.setStyleSheet("font: 12pt")
        label.setText("微信充电")

        # 支付宝充电标签
        label = QLabel(self.tab_5)
        self.customSetGeometry(label, 215, 330, 80, 20)
        label.setStyleSheet("font: 12pt")
        label.setText("支付宝充电")


    # 初始化配置
    def getInitConfig(self):

        # 界面缩放比例
        self.rate = self.config["screenScaleRate"]
        # 界面尺寸
        self.window_width = int(700*self.rate)
        self.window_height = int(400*self.rate)
        # 所使用的颜色
        self.color_1 = "#595959"  # 灰色
        self.color_2 = "#5B8FF9"  # 蓝色
        # 存被开启的翻译源
        self.translate_list = []

        # OCR各开关
        self.offline_ocr_use = False
        self.online_ocr_use = self.config["onlineOCR"]
        self.baidu_ocr_use = self.config["baiduOCR"]

        # 公共有道翻译开关
        self.youdao_use = eval(self.config["youdaoUse"])
        if self.youdao_use :
            self.translate_list.append("youdao")
        # 公共百度翻译开关
        self.baidu_web_use = eval(self.config["baiduwebUse"])
        if self.baidu_web_use :
            self.translate_list.append("baidu")
        # 公共腾讯翻译开关
        self.tencent_web_use = eval(self.config["tencentwebUse"])
        if self.tencent_web_use :
            self.translate_list.append("tencent")
        # 公共DeepL翻译开关
        self.deepl_use = eval(self.config["deeplUse"])
        if self.deepl_use :
            self.translate_list.append("deepl")
        # 公共谷歌翻译开关
        self.google_use = eval(self.config["googleUse"])
        if self.google_use :
            self.translate_list.append("google")
        # 公共彩云翻译开关
        self.caiyun_web_use = eval(self.config["caiyunUse"])
        if self.caiyun_web_use :
            self.translate_list.append("caiyun")
        # 私人腾讯翻译开关
        self.tencent_use = eval(self.config["tencentUse"])
        if self.tencent_use :
            self.translate_list.append("tencent_private")
        # 私人百度翻译开关
        self.baidu_use = eval(self.config["baiduUse"])
        if self.baidu_use :
            self.translate_list.append("baidu_private")
        # 私人彩云翻译开关
        self.caiyun_use = eval(self.config["caiyunPrivateUse"])
        if self.caiyun_use :
            self.translate_list.append("caiyun_private")

        # 字体颜色 公共有道
        self.youdao_color = self.config["fontColor"]["youdao"]
        # 字体颜色 公共百度
        self.baidu_web_color = self.config["fontColor"]["baiduweb"]
        # 字体颜色 公共腾讯
        self.tencent_web_color = self.config["fontColor"]["tencentweb"]
        # 字体颜色 公共DeepL
        self.deepl_color = self.config["fontColor"]["deepl"]
        # 字体颜色 公共谷歌
        self.google_color = self.config["fontColor"]["google"]
        # 字体颜色 公共彩云
        self.caiyun_web_color = self.config["fontColor"]["caiyun"]
        # 字体颜色 私人腾讯
        self.tencent_color = self.config["fontColor"]["tencent"]
        # 字体颜色 私人百度
        self.baidu_color = self.config["fontColor"]["baidu"]
        # 字体颜色 私人彩云
        self.caiyun_color = self.config["fontColor"]["caiyunPrivate"]

        # 翻译界面透明度
        self.horizontal = self.config["horizontal"]
        # 翻译字体大小
        self.fontSize = self.config["fontSize"]
        # 翻译字体类型
        self.font_type = self.config["fontType"]
        # 字体样式开关
        self.font_color_type = eval(self.config["showColorType"])
        # 自动翻译间隔设定
        self.translate_speed = self.config["translateSpeed"]
        # 显示原文开关
        self.show_original_use = eval(self.config["showOriginal"])
        # 原文自动复制到剪贴板开关
        self.auto_clipboard_use = eval(self.config["showClipboard"])
        # 文字方向
        self.text_direction_use = eval(self.config["showTranslateRow"])
        # 翻译快捷键开关
        self.translate_hotkey_use = eval(self.config["showHotKey1"])
        # 范围快捷键开关
        self.range_hotkey_use = eval(self.config["showHotKey2"])
        # 自动翻译图片刷新相似度
        self.image_refresh_score = self.config["imageSimilarity"]
        # 自动翻译文字刷新相似度
        self.text_refresh_score = self.config["textSimilarity"]

        # 团子翻译器开源地址
        self.dango_translator_url = "https://github.com/PantsuDango/Dango-Translator"
        # 添加作者QQ好友链接
        self.add_author_url = "tencent://AddContact/?fromId=45&fromSubId=1&subcmd=all&uin=394883561&website=www.oicqzone.com"
        # 在线教程地址
        self.tutorial_url = "https://docs.ayano.top"
        # GT-Zhang个人主页
        self.gt_github_url = "https://github.com/GT-ZhangAcer"
        # C4a15Wh个人主页
        self.c44_github_url = "https://c4a15wh.cn/"
        # Cypas_Nya‭个人主页
        self.cy_github_url = "https://blog.ayano.top"
        # PaddleOCR项目主页
        self.PaddleOCR_github_url = "https://github.com/PaddlePaddle/PaddleOCR"
        # 更新日志
        self.update_log = "https://github.com/PantsuDango/Dango-Translator/blob/master/docx/%E6%9B%B4%E6%96%B0%E6%97%A5%E5%BF%97.md"


    # 根据分辨率定义控件位置尺寸
    def customSetGeometry(self, object, x, y, w, h) :

        object.setGeometry(QRect(int(x*self.rate),
                                 int(y*self.rate), int(w*self.rate),
                                 int(h*self.rate)))


    # 根据分辨率定义图标位置尺寸
    def customSetIconSize(self, object, w, h) :

        object.setIconSize(QSize(int(w * self.rate),
                                 int(h * self.rate)))


    # 控件加入阴影
    def setShadow(self, object, color) :

        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(5, 5)
        shadow.setBlurRadius(50)
        shadow.setColor(color)
        object.setGraphicsEffect(shadow)


    # 改变离线OCR开关状态
    def changeOfflineSwitch(self, checked) :

        if checked :
            if self.online_ocr_use == True :
                self.resetSwitch("onlineOCR")
            if self.baidu_ocr_use == True :
                self.resetSwitch("baiduOCR")
            self.offline_ocr_use = True
        else:
            self.offline_ocr_use = False


    # 改变在线OCR开关状态
    def changeOnlineSwitch(self, checked):

        if checked :
            if self.offline_ocr_use == True :
                self.resetSwitch("offlineOCR")
            if self.baidu_ocr_use == True :
                self.resetSwitch("baiduOCR")
            self.online_ocr_use = True
        else:
            self.online_ocr_use = False


    # 改变百度OCR开关状态
    def changeBaiduSwitch(self, checked):

        if checked :
            if self.offline_ocr_use == True :
                self.resetSwitch("offlineOCR")
            if self.online_ocr_use == True :
                self.resetSwitch("onlineOCR")
            self.baidu_ocr_use = True
        else :
            self.baidu_ocr_use = False


    # 改变公共有道翻译开关状态
    def changeYoudaoSwitch(self, checked):

        if checked :
            self.youdao_use = True
            self.translate_list.append("youdao")
            self.checkTranslaterUse()
        else:
            self.youdao_use = False
            self.translate_list.remove("youdao")


    # 改变公共百度翻译开关状态
    def changeBaiduWebSwitch(self, checked):

        if checked :
            self.baidu_web_use = True
            self.translate_list.append("baidu")
            self.checkTranslaterUse()
        else:
            self.baidu_web_use = False
            self.translate_list.remove("baidu")


    # 改变公共腾讯翻译开关状态
    def changeTencentWebSwitch(self, checked):

        if checked :
            self.tencent_web_use = True
            self.translate_list.append("tencent")
            self.checkTranslaterUse()
        else:
            self.tencent_web_use = False
            self.translate_list.remove("tencent")


    # 改变公共DeepL翻译开关状态
    def changeDeepLSwitch(self, checked):

        if checked :
            self.deepl_use = True
            self.translate_list.append("deepl")
            self.checkTranslaterUse()
        else:
            self.deepl_use = False
            self.translate_list.remove("deepl")


    # 改变公共Google翻译开关状态
    def changeGoogleSwitch(self, checked):

        if checked :
            self.google_use = True
            self.translate_list.append("google")
            self.checkTranslaterUse()
        else:
            self.google_use = False
            self.translate_list.remove("google")


    # 改变公共彩云翻译开关状态
    def changeCaiyunWebSwitch(self, checked):

        if checked :
            self.caiyun_web_use = True
            self.translate_list.append("caiyun")
            self.checkTranslaterUse()
        else:
            self.caiyun_web_use = False
            self.translate_list.remove("caiyun")


    # 改变私人腾讯翻译开关状态
    def changeTencentSwitch(self, checked):

        if checked :
            self.tencent_use = True
            self.translate_list.append("tencent_private")
            self.checkTranslaterUse()
        else:
            self.tencent_use = False
            self.translate_list.remove("tencent_private")


    # 改变私人百度翻译开关状态
    def changeBaiduTranslaterSwitch(self, checked):

        if checked :
            self.baidu_use = True
            self.translate_list.append("baidu_private")
            self.checkTranslaterUse()
        else:
            self.baidu_use = False
            self.translate_list.remove("baidu_private")


    # 改变私人彩云翻译开关状态
    def changeCaiyunSwitch(self, checked):

        if checked :
            self.caiyun_use = True
            self.translate_list.append("caiyun_private")
            self.checkTranslaterUse()
        else:
            self.caiyun_use = False
            self.translate_list.remove("caiyun_private")


    # 改变字体样式开关状态
    def changeFontColorTypeSwitch(self, checked):

        if checked :
            self.font_color_type = True
        else:
            self.font_color_type = False


    # 改变显示原文开关状态
    def changeShowOriginalSwitch(self, checked):

        if checked :
            self.show_original_use = True
        else:
            self.show_original_use = False


    # 改变自动复制剪贴板开关状态
    def changeAutoCopyOriginalSwitch(self, checked):

        if checked :
            self.auto_clipboard_use = True
        else:
            self.auto_clipboard_use = False


    # 改变自动复制剪贴板开关状态
    def changeTextDirectionSwitch(self, checked):

        if checked :
            self.text_direction_use = True
        else:
            self.text_direction_use = False


    # 改变翻译热键开关状态
    def changeTranslateHotkeySwitch(self, checked):

        if checked :
            self.translate_hotkey_use = True
        else:
            self.translate_hotkey_use = False


    # 改变范围热键开关状态
    def changeRangeHotkeySwitch(self, checked):

        if checked :
            self.range_hotkey_use = True
        else:
            self.range_hotkey_use = False



    # 重置开关状态
    def resetSwitch(self, switch_type) :

        if switch_type == "offlineOCR" :
            self.offline_ocr_switch.mousePressEvent(1)
            self.offline_ocr_switch.updateValue()
        elif switch_type == "onlineOCR" :
            self.online_ocr_switch.mousePressEvent(1)
            self.online_ocr_switch.updateValue()
        elif switch_type == "baiduOCR" :
            self.baidu_ocr_switch.mousePressEvent(1)
            self.baidu_ocr_switch.updateValue()


    # 运行离线OCR
    def runOfflineOCR(self) :

        sign, message = detectPort(6666)
        if message :
            print(message)
        elif sign :
            MessageBox("这是来自团子的警告~", "离线OCR已经在运行中了\n"
                                             "请不要重复运行哦ヽ(･ω･´ﾒ)     ")
            return

        os.startfile(OCR_CMD_PATH)


    # 测试离线OCR
    def testOfflineOCR(self) :

        sign, message = detectPort(6666)
        if message:
            print(message)
        elif not sign :
            MessageBox("测试离线OCR失败", "离线OCR还没运行成功，不可以进行测试哦\n"
                                         "请先启动离线OCR，并保证其运行正常\n"
                                         "使用期间可以缩小黑窗，但不可以退出哦(〃'▽'〃)     ")
            return

        testOfflineOCR()


    # 打开离线OCR教程
    def openOfflineOCRTutorial(self) :

        config_json, errorMsg = postConfigURL()
        if errorMsg :
            print(errorMsg)
        else :
            url = config_json.get("ocr_register", {}).get("offline_ocr", "https://docs.ayano.top/#/basic/ocr?id=%e7%a6%bb%e7%ba%bfocr%e8%af%b4%e6%98%8e")
            webbrowser.open(url, new=0, autoraise=True)


    # 翻译源字体颜色
    def ChangeTranslateColor(self, type, color_str) :

        color = QColorDialog.getColor(QColor(color_str), None, "设定所选翻译显示时的颜色")
        if not color.isValid() :
            return

        if type == "youdao" :
            self.youdao_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.youdao_color = color.name()
        elif type == "baidu" :
            self.baidu_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.baidu_web_color = color.name()
        elif type == "tencent" :
            self.tencent_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.tencent_web_color = color.name()
        elif type == "deepl" :
            self.deepl_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.deepl_color = color.name()
        elif type == "google" :
            self.google_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.google_color = color.name()
        elif type == "caiyun" :
            self.caiyun_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.caiyun_web_color = color.name()
        elif type == "tencent_private" :
            self.tencent_private_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.tencent_color = color.name()
        elif type == "baidu_private" :
            self.baidu_private_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.baidu_color = color.name()
        elif type == "caiyun_private" :
            self.caiyun_private_color_button.setIcon(qtawesome.icon("fa5s.paint-brush", color=color.name()))
            self.caiyun_color = color.name()


    # 说明窗口
    def showDesc(self, object) :

        self.desc = Desc(self.config)

        # OCR说明
        if object == "OCR" :
            self.desc.setWindowTitle("OCR说明")
            self.desc.desc_text.append("\n首先区别OCR和翻译是两个模块。")
            self.desc.desc_text.append("\nOCR即为文字识别技术, 用于提取图片内要翻译的文字.")
            self.desc.desc_text.append("\n翻译器通过对所框选的范围进行截图, 然后利用OCR将截图内要翻译的文字识别出来, 再发送给翻译模块翻译。")

        # 离线OCR说明
        elif object == "offlineOCR" :
            self.desc.setWindowTitle("离线OCR说明")
            self.desc.desc_text.append("\n特性: \n依赖自身CPU性能, CPU性能越高，识别速度越快.")
            self.desc.desc_text.append("识别精度一般.")
            self.desc.desc_text.append("\n优点:\n1. 无额度限制, 完全免费, 可无限次使用;")
            self.desc.desc_text.append("\n缺点:\n1. 对电脑配置较低的用户不友好, 可能会导致电脑很卡;")
            self.desc.desc_text.append("2. 可能会因为环境配置问题导致安装失败, 不支持10年以前发行的CPU;")
            self.desc.desc_text.append("\n详细使用方式见教程.")

        # 在线OCR说明
        elif object == "onlineOCR":
            self.desc.setWindowTitle("在线OCR说明")
            self.desc.desc_text.append("\n特性: \n团子在大佬们的帮助下自行搭建的OCR在线服务.")
            self.desc.desc_text.append("识别精度较好.")
            self.desc.desc_text.append("\n优点:\n1. 不消耗电脑配置, 仅需联网;")
            self.desc.desc_text.append("2. 性价比高, 服务期内无使用次数限制;")
            self.desc.desc_text.append("\n缺点:\n1. 不免费, 需要氪点金金;")
            self.desc.desc_text.append("\n详细使用方式见教程.")

        # 在线OCR说明
        elif object == "baiduOCR":
            self.desc.setWindowTitle("百度OCR说明")
            self.desc.desc_text.append("\n特性: \n百度智能云的OCR服务.")
            self.desc.desc_text.append("识别精度优秀.")
            self.desc.desc_text.append("\n优点:\n1. 不消耗电脑配置, 仅需联网;")
            self.desc.desc_text.append("\n缺点:\n1. 使用次数有限制;")
            self.desc.desc_text.append("2. 不免费, 且价格较贵;")
            self.desc.desc_text.append("\n详细使用方式见教程.")

        # 公共翻译说明
        elif object == "publicTranslate" :
            self.desc.setWindowTitle("公共翻译说明")
            self.desc.desc_text.append("\n没有次数限制, 不需要注册, 可直接使用, 但不保证使用稳定性, 可能会抽风.")
            self.desc.desc_text.append('\n使用需要电脑装有"最新版本的" Chorem(谷歌)浏览器、Firefox(火狐)浏览器、Edga(微软)浏览器 至少一款.')
            self.desc.desc_text.append('\n翻译器原理上, 是通过后台启动相应的浏览器, 自动打开翻译网站去实现翻译.')
            self.desc.desc_text.append("\n详细使用方式见教程.")

        # 私人翻译说明
        elif object == "privateTranslate" :
            self.desc.setWindowTitle("私人翻译说明")
            self.desc.desc_text.append("\n有次数限制, 使用前需要注册, 但使用稳定性, 基本上不会抽风.")
            self.desc.desc_text.append("\n翻译器原理上, 是通过请求相应的云API接口去获取翻译结果")
            self.desc.desc_text.append("\n详细使用方式见教程.")

        # 翻译框透明度说明
        elif object == "horizontalSlider" :
            self.desc.setWindowTitle("翻译框透明度说明")
            self.desc.desc_text.append("\n用于调节显示翻译结果的翻译框透明度.")
            self.desc.desc_text.append("数值0为全透明")
            self.desc.desc_text.append("数值100为完全不透明")

        # 字体样式设定说明
        elif object == "fontType" :
            self.desc.setWindowTitle("字体样式设定说明")
            self.desc.desc_text.append("描边字体为字体中间镂空白底, 描边带颜色:\n")
            self.desc.desc_text.insertHtml('<img src={} width="{}" >'.format(HOLLOW_IMG_PATH, 195*self.rate))
            self.desc.desc_text.append("\n实心字体为纯色字体:\n")
            self.desc.desc_text.insertHtml('<img src="{}" width="{}" >'.format(SOLID_IMG_PATH, 195*self.rate))
            self.desc.desc_text.append("\n顺便一提团子喜欢描边字体~")

        # 自动翻译设定说明
        elif object == "autoSpeed" :
            self.desc.setWindowTitle("自动翻译设定说明")
            self.desc.desc_text.append("\n自动翻译模式下, 每隔该设定时间, 便会检测一次所框的范围内图像是否发生变化, 若发生变化则识别并刷新翻译")

        # 显示原文说明
        elif object == "showOriginal" :
            self.desc.setWindowTitle("显示原文说明")
            self.desc.desc_text.append("\n开启后, 会将OCR识别到的原文显示在翻译框.")

        # 文字方向说明
        elif object == "textDirection":
            self.desc.setWindowTitle("文字方向说明")
            self.desc.desc_text.append("\n正常都是横向的呢, 竖向多用于漫画翻译的情况.")

        # 图像相似度说明
        elif object == "imageRefresh":
            self.desc.setWindowTitle("图像相似度说明")
            self.desc.desc_text.append("\n自动翻译模式下, 每隔设定的时间间隔, 会重新检测范围区域的图像. "
                                       "只有当当前图像, 与前一次图像比较的相似度小于该设定的值时, 才会重新调取OCR识别该图像.")
            self.desc.desc_text.append("\n如果觉得OCR频繁重复识别, 翻译框出现了'闪烁'的话, 可以调低此参数.")
            self.desc.desc_text.append("\n如果看不懂请不要轻易修改此参数, 建议值为98.")

        # 文字相似度说明
        elif object == "textRefresh":
            self.desc.setWindowTitle("文字相似度说明")
            self.desc.desc_text.append("\n自动翻译模式下, 每隔设定的时间间隔, OCR识别结果刷新后. "
                                       "如果当前OCR识别出的原文, 与前一次识别的原文比较, 其相似度小于该设定的值时, "
                                       "才会重新调取翻译并刷新至翻译界面.")
            self.desc.desc_text.append("\n如果觉得频繁重复翻译, 翻译框出现了'闪烁'的话, 可以调低此参数.")
            self.desc.desc_text.append("\n如果看不懂请不要轻易修改此参数, 建议值为90.")

        # QQ交流群
        elif object == "qqGroup":
            self.desc.setWindowTitle("加入交流群")
            self.desc.qq_group_image.show()

        self.desc.show()


    # 密钥窗口
    def showKey(self, object) :

        # 百度OCR
        if object == "baiduOCR" :
            self.key_ui.setWindowTitle("百度OCR - 密钥编辑")
            self.key_ui.baidu_ocr_key_textEdit.show()
            self.key_ui.baidu_ocr_secret_textEdit.show()

        # 私人腾讯翻译
        elif object == "tencentTranslate" :
            self.key_ui.setWindowTitle("私人腾讯翻译 - 密钥编辑")
            self.key_ui.tencent_private_key_textEdit.show()
            self.key_ui.tencent_private_secret_textEdit.show()

        # 私人腾讯翻译
        elif object == "baiduTranslate" :
            self.key_ui.setWindowTitle("私人百度翻译 - 密钥编辑")
            self.key_ui.baidu_private_key_textEdit.show()
            self.key_ui.baidu_private_secret_textEdit.show()

        # 私人彩云翻译
        elif object == "caiyunTranslate" :
            self.key_ui.setWindowTitle("私人彩云翻译 - 密钥编辑")
            self.key_ui.caiyun_private_key_textEdit.show()

        self.key_ui.show()


    # 翻译框透明度
    def changeHorizontal(self) :

        self.horizontal = self.horizontal_slider.value()
        self.horizontal_slider_label.setText("{}%".format(self.horizontal))


    # 设定字体样式
    def getFontType(self, text) :

        self.font_type = text


    # 设定快捷键
    def setHotKey(self, key_type) :

        # 快捷键界面
        self.hotkey = HotKey(self.config)

        if key_type == "translate" :
            self.hotkey.setWindowTitle("设定翻译快捷键")
            self.hotkey.label.setText(self.translate_hotkey_button.text())
            self.hotkey.key = self.translate_hotkey_button.text()
            self.hotkey.sure_button.clicked.connect(lambda: self.hotkey.sure(self.translate_hotkey_button))

        if key_type == "range" :
            self.hotkey.setWindowTitle("设定范围快捷键")
            self.hotkey.label.setText(self.range_hotkey_button.text())
            self.hotkey.key = self.range_hotkey_button.text()
            self.hotkey.sure_button.clicked.connect(lambda: self.hotkey.sure(self.range_hotkey_button))

        width = self.hotkey.label.width()
        self.hotkey.customSetGeometry(self.hotkey.label, (300-width)//2, 80, width, 20)
        self.hotkey.show()


    # 校验翻译开关状态
    def checkTranslaterUse(self) :

        if len(self.translate_list) <= 2 :
            return

        for val in self.translate_list :
            if val == "baidu" :
                self.baidu_switch.mousePressEvent(1)
                self.baidu_switch.updateValue()

            elif val == "tencent" :
                self.tencent_switch.mousePressEvent(1)
                self.tencent_switch.updateValue()

            elif val == "caiyun" :
                self.caiyun_switch.mousePressEvent(1)
                self.caiyun_switch.updateValue()

            elif val == "deepl" :
                self.deepl_switch.mousePressEvent(1)
                self.deepl_switch.updateValue()

            elif val == "google" :
                self.google_switch.mousePressEvent(1)
                self.google_switch.updateValue()

            elif val == "youdao" :
                self.youdao_switch.mousePressEvent(1)
                self.youdao_switch.updateValue()

            elif val == "tencent_private" :
                self.tencent_private_switch.mousePressEvent(1)
                self.tencent_private_switch.updateValue()

            elif val == "baidu_private" :
                self.baidu_private_switch.mousePressEvent(1)
                self.baidu_private_switch.updateValue()

            elif val == "caiyun_private" :
                self.caiyun_private_switch.mousePressEvent(1)
                self.caiyun_private_switch.updateValue()

            if len(self.translate_list) <= 2 :
                break


    # 重置翻译引擎
    def resetWebdriver(self) :

        # 重置开关
        tmp_sign_1 = False
        tmp_sign_2 = False
        self.translation_ui.webdriver_1.open_sign = False
        self.translation_ui.webdriver_2.open_sign = False

        # 刷新翻译
        translater_list = ["youdaoUse", "baiduwebUse", "tencentwebUse", "deeplUse", "googleUse", "caiyunUse"]
        for val in translater_list :
            if self.config[val] == "False" :
                continue

            if not tmp_sign_2 :
                tmp_sign_2 = True
                self.translation_ui.webdriver_1.open_sign = True
            else :
                self.translation_ui.webdriver_2.open_sign = True

            # 避免重复开启
            web_type = val.replace("Use", "").replace("web", "")
            if web_type == self.translation_ui.webdriver_1_type or web_type == self.translation_ui.webdriver_2_type :
                continue

            if not tmp_sign_1 :
                # 刷新翻译引擎1
                tmp_sign_1 = True
                self.translation_ui.webdriver_1_type = web_type
                webdriver_thread = threading.Thread(target=resetWeb,
                                                    args=(self.translation_ui.webdriver_1, web_type))
                webdriver_thread.setDaemon(True)
                webdriver_thread.start()

            else :
                # 刷新翻译引擎2
                self.translation_ui.webdriver_2_type = web_type
                webdriver_thread = threading.Thread(target=resetWeb,
                                                    args=(self.translation_ui.webdriver_2, web_type))
                webdriver_thread.setDaemon(True)
                webdriver_thread.start()


    # 退出前保存设置
    def saveConfig(self) :

        # OCR开关
        self.config["offlineOCR"] = self.offline_ocr_use
        self.config["onlineOCR"] = self.online_ocr_use
        self.config["baiduOCR"] = self.baidu_ocr_use

        # 翻译语种
        if self.language_comboBox.currentIndex() == 1 :
            self.config["language"] = "ENG"
        elif self.language_comboBox.currentIndex() == 2 :
            self.config["language"] = "KOR"
        else:
            self.config["language"] = "JAP"

        # 公共有道翻译开关
        self.config["youdaoUse"] = str(self.youdao_use)
        # 公共百度翻译开关
        self.config["baiduwebUse"] = str(self.baidu_web_use)
        # 公共腾讯翻译开关
        self.config["tencentwebUse"] = str(self.tencent_web_use)
        # 公共DeepL翻译开关
        self.config["deeplUse"] = str(self.deepl_use)
        # 公共谷歌翻译开关
        self.config["googleUse"] = str(self.google_use)
        # 公共彩云翻译开关
        self.config["caiyunUse"] = str(self.caiyun_web_use)
        # 私人腾讯翻译开关
        self.config["tencentUse"] = str(self.tencent_use)
        # 私人百度翻译开关
        self.config["baiduUse"] = str(self.baidu_use)
        # 私人彩云翻译开关
        self.config["caiyunPrivateUse"] = str(self.caiyun_use)

        # 字体颜色 公共有道
        self.config["fontColor"]["youdao"] = self.youdao_color
        # 字体颜色 公共百度
        self.config["fontColor"]["baiduweb"] = self.baidu_web_color
        # 字体颜色 公共腾讯
        self.config["fontColor"]["tencentweb"] = self.tencent_web_color
        # 字体颜色 公共DeepL
        self.config["fontColor"]["deepl"] = self.deepl_color
        # 字体颜色 公共谷歌
        self.config["fontColor"]["google"] = self.google_color
        # 字体颜色 公共彩云
        self.config["fontColor"]["caiyun"] = self.caiyun_web_color
        # 字体颜色 私人腾讯
        self.config["fontColor"]["tencent"] = self.tencent_color
        # 字体颜色 私人百度
        self.config["fontColor"]["baidu"] = self.baidu_color
        # 字体颜色 私人彩云
        self.config["fontColor"]["caiyunPrivate"] = self.caiyun_color

        # 翻译框透明度
        self.config["horizontal"] = self.horizontal
        # 翻译字体大小
        self.config["fontSize"] = self.fontSize_spinBox.value()
        # 翻译字体类型
        self.config["fontType"] = self.font_type
        # 字体样式开关
        self.config["showColorType"] = str(self.font_color_type)
        # 自动翻译间隔
        self.config["translateSpeed"] = self.auto_speed_spinBox.value()
        # 显示原文开关
        self.config["showOriginal"] = str(self.show_original_use)
        # 原文自动复制到剪贴板开关
        self.config["showClipboard"] = str(self.auto_clipboard_use)
        # 文字方向
        self.config["showTranslateRow"] = str(self.text_direction_use)
        # 翻译快捷键开关
        self.config["showHotKey1"] = str(self.translate_hotkey_use)
        # 翻译快捷键
        self.config["showHotKeyValue1"] = self.translate_hotkey_button.text()
        # 范围快捷键开关
        self.config["showHotKey2"] = str(self.range_hotkey_use)
        # 范围快捷键
        self.config["showHotKeyValue2"] = self.range_hotkey_button.text()
        # 自动翻译图片刷新相似度
        self.config["imageSimilarity"] = self.image_refresh_spinBox.value()
        # 自动翻译文字刷新相似度
        self.config["textSimilarity"] = self.text_refresh_spinBox.value()

        if self.translate_hotkey_use :
            self.translation_ui.translate_shortcut.setKey(self.config["showHotKeyValue1"])
        if self.range_hotkey_use :
            self.translation_ui.range_shortcut.setKey(self.config["showHotKeyValue2"])


        # 窗口关闭处理
    def closeEvent(self, event) :

        # 保存设置至本地文件
        self.saveConfig()

        # 重置翻译引擎
        try :
            self.resetWebdriver()
        except Exception :
            pass

        # 刷新百度OCR的AccessToken
        if self.baidu_ocr_use :
            sign, access_token = getAccessToken(self.config["OCR"]["Key"], self.config["OCR"]["Secret"], self.logger)
            if sign :
                self.config["AccessToken"] = access_token

        # 设置页面配置更新至主模块
        self.translation_ui.config = self.config

        # 设置上传云端
        utils.postSaveSettin(self.config, self.logger)

        # 重置翻译界面
        self.translation_ui.translateText.setStyleSheet("border-width:0;\
                                                         border-style:outset;\
                                                         border-top:0px solid #e8f3f9;\
                                                         color:white;\
                                                         font-weight: bold;\
                                                         background-color:rgba(62, 62, 62, %s)"
                                                        %(self.horizontal))
        # 重置状态栏界面
        self.translation_ui.statusbar.setStyleSheet("font: 10pt '华康方圆体W7';"
                                                    "color: white;"
                                                    "background-color: rgba(62, 62, 62, 0.1)")

        self.close()
        self.translation_ui.show()