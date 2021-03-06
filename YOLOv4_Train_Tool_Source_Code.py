# -*- Encoding: UTF-8 -*-

"""
@File        : IVT-Train-Tool

@Contact     : xiaofei.smile365@Gmail.com
@Author      : 苏晓飞
@Call        ：8610-2484/8690-0070
@IDE         : PyCharm

@Version     : 2.0
@Modify Time : 8/6/20 08:00 AM
@友达光电（苏州）有限公司 AUSZ-S06
"""

import sys
import os

import cv2

import socket

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QLabel, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout, \
    QPushButton, QGridLayout, QMessageBox, QInputDialog, QFileDialog
from PyQt5.QtGui import QIcon, QPalette, QBrush, QPixmap, QFont

import datetime
import shutil
from Train.labelImg import *
import glob
import xml.dom.minidom
import random

import xml.etree.ElementTree as ET
import pickle
from os import listdir, getcwd
from os.path import join
from Train.scripts import classes as class_names
import signal


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.screen = QDesktopWidget().screenGeometry()

        self.resize(1024, 768)
        self.setWindowIcon(QIcon("./Train/ico/train.png"))
        self.setWindowTitle("TVT-train Tool")

        self.palette = QPalette()
        self.palette.setBrush(QPalette.Background, QBrush(QPixmap("./Train/background/auobg.png").scaled(self.width(), self.height())))
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)

        self.size = self.geometry()
        self.move((self.screen.width() - self.size.width()) / 2, (self.screen.height() - self.size.height()) / 2)

        self.status = self.statusBar()

        self.setFixedSize(1024, 768)

        self.label_set()
        self.layout_set()

        self.qtm_real_time = QtCore.QTimer()
        self.qtm_real_time.timeout.connect(self.real_time)
        self.qtm_real_time.start(1000)

        self.main_frame = QWidget()
        self.main_frame.setLayout(self.layout_v_windows)
        self.setCentralWidget(self.main_frame)

        self.login()
        self.status.showMessage("The IVT-train Tool Starting", 2000)

    def login(self):
        self.password = 0

        def get_host_ip():
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.s.connect(('8.8.8.8', 80))
                self.ip = self.s.getsockname()[0]
            finally:
                self.s.close()
            return self.ip

        self.ip = get_host_ip()
        password, ok = QInputDialog.getText(self, "请输入密码", "你的IP是：%s" % self.ip)
        if ok:
            self.password = str(password)

    def validation(self):
        self.ip_ascii = 0
        for m in range(0, len(self.ip)):
            if self.ip[0-m-1] != ".":
                self.ip_ascii = ord(self.ip[0-m-1]) + self.ip_ascii
            else:
                break
        self.actual_password = self.ip_ascii
        if self.password != str(self.actual_password):
            self.close()

    def label_set(self):
        self.label_title = QLabel()
        self.label_title.setText("<b>智眸-视频AI一体化开发平台<b>")
        self.label_title.setFont(QFont("SanSerif", 24))
        self.label_title.setStyleSheet("Color: RGB(64, 224, 208)")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setFixedSize(400, 60)
        self.layout_h_label_title = QHBoxLayout()
        self.layout_h_label_title.addWidget(self.label_title)

        self.label_designer = QLabel()
        self.label_designer.setText("Designer:Xiaofei")
        self.label_designer.setFont(QFont("SanSerif", 10))
        self.label_designer.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_designer.setAlignment(Qt.AlignRight)
        self.label_designer.setFixedSize(140, 20)
        self.layout_h_label_designer = QHBoxLayout()
        self.layout_h_label_designer.addWidget(self.label_designer)

        self.label_time = QLabel()
        self.label_time.setText("1997/01/01 00:00:00")
        self.label_time.setFont(QFont("SanSerif", 10))
        self.label_time.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_time.setAlignment(Qt.AlignLeft)
        self.label_time.setFixedSize(130, 20)
        self.layout_h_label_time = QHBoxLayout()
        self.layout_h_label_time.addWidget(self.label_time)

        self.label_image_camera = QLabel()
        self.label_image_camera.setPixmap(QPixmap("./Train/image_in_ui/camera.png").scaled(100, 100))
        self.label_image_camera.setAlignment(Qt.AlignCenter)
        self.label_image_camera.setFixedSize(100, 100)
        self.layout_h_label_image_camera = QHBoxLayout()
        self.layout_h_label_image_camera.addWidget(self.label_image_camera)

        self.label_image_labelimage = QLabel()
        self.label_image_labelimage.setPixmap(QPixmap("./Train/image_in_ui/labelimg.png").scaled(100, 100))
        self.label_image_labelimage.setAlignment(Qt.AlignCenter)
        self.label_image_labelimage.setFixedSize(100, 100)
        self.layout_h_label_image_labelimage = QHBoxLayout()
        self.layout_h_label_image_labelimage.addWidget(self.label_image_labelimage)

        self.label_image_train = QLabel()
        self.label_image_train.setPixmap(QPixmap("./Train/image_in_ui/train.png").scaled(100, 100))
        self.label_image_train.setAlignment(Qt.AlignCenter)
        self.label_image_train.setFixedSize(100, 100)
        self.layout_h_label_image_train = QHBoxLayout()
        self.layout_h_label_image_train.addWidget(self.label_image_train)

        self.label_image_test = QLabel()
        self.label_image_test.setPixmap(QPixmap("./Train/image_in_ui/test.png").scaled(100, 100))
        self.label_image_test.setAlignment(Qt.AlignCenter)
        self.label_image_test.setFixedSize(100, 100)
        self.layout_h_label_image_test = QHBoxLayout()
        self.layout_h_label_image_test.addWidget(self.label_image_test)

        self.label_video_acquisition = QLabel()
        self.label_video_acquisition.setText("视频采集")
        self.label_video_acquisition.setFont(QFont("SanSerif", 16))
        self.label_video_acquisition.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_video_acquisition.setAlignment(Qt.AlignCenter)
        self.label_video_acquisition.setFixedSize(100, 30)
        self.layout_h_label_video_acquisition = QHBoxLayout()
        self.layout_h_label_video_acquisition.addWidget(self.label_video_acquisition)

        self.label_picture_label = QLabel()
        self.label_picture_label.setText("图片标注")
        self.label_picture_label.setFont(QFont("SanSerif", 16))
        self.label_picture_label.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_picture_label.setAlignment(Qt.AlignCenter)
        self.label_picture_label.setFixedSize(100, 30)
        self.layout_h_label_picture_label = QHBoxLayout()
        self.layout_h_label_picture_label.addWidget(self.label_picture_label)

        self.label_model_train = QLabel()
        self.label_model_train.setText("模型训练")
        self.label_model_train.setFont(QFont("SanSerif", 16))
        self.label_model_train.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_model_train.setAlignment(Qt.AlignCenter)
        self.label_model_train.setFixedSize(100, 30)
        self.layout_h_label_model_train = QHBoxLayout()
        self.layout_h_label_model_train.addWidget(self.label_model_train)

        self.label_model_test = QLabel()
        self.label_model_test.setText("模型测试")
        self.label_model_test.setFont(QFont("SanSerif", 16))
        self.label_model_test.setStyleSheet("Color: RGB(128, 128, 0)")
        self.label_model_test.setAlignment(Qt.AlignCenter)
        self.label_model_test.setFixedSize(100, 30)
        self.layout_h_label_model_test = QHBoxLayout()
        self.layout_h_label_model_test.addWidget(self.label_model_test)

        self.button_open_camera = QPushButton()
        self.button_open_camera.setText("打开设备")
        self.button_open_camera.setFont(QFont("SanSerif", 8))
        self.button_open_camera.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_open_camera.setIcon(QIcon("./Train/ico/open_camera.png"))
        self.button_open_camera.setFixedSize(100, 30)
        self.button_open_camera.clicked.connect(self.open_camera)
        self.layout_h_button_open_camera = QHBoxLayout()
        self.layout_h_button_open_camera.addWidget(self.button_open_camera)

        self.button_start_recording = QPushButton()
        self.button_start_recording.setText("开始录制")
        self.button_start_recording.setFont(QFont("Sanserif", 8))
        self.button_start_recording.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_start_recording.setIcon(QIcon("./Train/ico/start_recording.png"))
        self.button_start_recording.setFixedSize(100, 30)
        self.button_start_recording.clicked.connect(self.start_recording)
        self.layout_h_button_start_recording = QHBoxLayout()
        self.layout_h_button_start_recording.addWidget(self.button_start_recording)

        self.button_end_recording = QPushButton()
        self.button_end_recording.setText("结束录制")
        self.button_end_recording.setFont(QFont("Sanserif", 8))
        self.button_end_recording.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_end_recording.setIcon(QIcon("./Train/ico/end_recording.png"))
        self.button_end_recording.setFixedSize(100, 30)
        self.button_end_recording.clicked.connect(self.end_recording)
        self.layout_h_button_end_recording = QHBoxLayout()
        self.layout_h_button_end_recording.addWidget(self.button_end_recording)

        self.button_import_picture = QPushButton()
        self.button_import_picture.setText("导入图片")
        self.button_import_picture.setFont(QFont("Sanserif", 8))
        self.button_import_picture.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_import_picture.setIcon(QIcon("./Train/ico/import_picture.png"))
        self.button_import_picture.setFixedSize(100, 30)
        self.button_import_picture.clicked.connect(self.import_picture)
        self.layout_h_button_import_picture = QHBoxLayout()
        self.layout_h_button_import_picture.addWidget(self.button_import_picture)

        self.button_start_label = QPushButton()
        self.button_start_label.setText("开始标注")
        self.button_start_label.setFont(QFont("Sanserif", 8))
        self.button_start_label.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_start_label.setIcon(QIcon("./Train/ico/start_label.png"))
        self.button_start_label.setFixedSize(100, 30)
        self.button_start_label.clicked.connect(self.start_label)
        self.layout_h_button_button_start_label = QHBoxLayout()
        self.layout_h_button_button_start_label.addWidget(self.button_start_label)

        self.button_coversition_format = QPushButton()
        self.button_coversition_format.setText("转换格式")
        self.button_coversition_format.setFont(QFont("Sanserif", 8))
        self.button_coversition_format.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_coversition_format.setIcon(QIcon("./Train/ico/coversition_format.png"))
        self.button_coversition_format.setFixedSize(100, 30)
        self.button_coversition_format.clicked.connect(self.coversition_format)
        self.layout_h_button_button_coversition_format = QHBoxLayout()
        self.layout_h_button_button_coversition_format.addWidget(self.button_coversition_format)

        self.button_configuration_parameter = QPushButton()
        self.button_configuration_parameter.setText("配置参数")
        self.button_configuration_parameter.setFont(QFont("Sanserif", 8))
        self.button_configuration_parameter.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_configuration_parameter.setIcon(QIcon("./Train/ico/configuration_parameter.png"))
        self.button_configuration_parameter.setFixedSize(100, 30)
        self.button_configuration_parameter.clicked.connect(self.configuration_parameter)
        self.layout_h_button_button_configuration_parameter = QHBoxLayout()
        self.layout_h_button_button_configuration_parameter.addWidget(self.button_configuration_parameter)

        self.button_start_train = QPushButton()
        self.button_start_train.setText("开始训练")
        self.button_start_train.setFont(QFont("Sanserif", 8))
        self.button_start_train.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_start_train.setIcon(QIcon("./Train/ico/start_train.png"))
        self.button_start_train.setFixedSize(100, 30)
        self.button_start_train.clicked.connect(self.start_train)
        self.layout_h_button_button_start_train = QHBoxLayout()
        self.layout_h_button_button_start_train.addWidget(self.button_start_train)

        self.button_derived_model = QPushButton()
        self.button_derived_model.setText("导出模型")
        self.button_derived_model.setFont(QFont("Sanserif", 8))
        self.button_derived_model.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_derived_model.setIcon(QIcon("./Train/ico/derived_model.png"))
        self.button_derived_model.setFixedSize(100, 30)
        self.button_derived_model.clicked.connect(self.derived_model)
        self.layout_h_button_button_derived_model = QHBoxLayout()
        self.layout_h_button_button_derived_model.addWidget(self.button_derived_model)

        self.button_select_type = QPushButton()
        self.button_select_type.setText("选择类型")
        self.button_select_type.setFont(QFont("Sanserif", 8))
        self.button_select_type.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_select_type.setIcon(QIcon("./Train/ico/select_type.png"))
        self.button_select_type.setFixedSize(100, 30)
        self.button_select_type.clicked.connect(self.select_type)
        self.layout_h_button_button_select_type = QHBoxLayout()
        self.layout_h_button_button_select_type.addWidget(self.button_select_type)

        self.button_start_test = QPushButton()
        self.button_start_test.setText("开始测试")
        self.button_start_test.setFont(QFont("Sanserif", 8))
        self.button_start_test.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_start_test.setIcon(QIcon("./Train/ico/start_test.png"))
        self.button_start_test.setFixedSize(100, 30)
        self.button_start_test.clicked.connect(self.start_test)
        self.layout_h_button_button_start_test = QHBoxLayout()
        self.layout_h_button_button_start_test.addWidget(self.button_start_test)

        self.button_end_test = QPushButton()
        self.button_end_test.setText("结束测试")
        self.button_end_test.setFont(QFont("Sanserif", 8))
        self.button_end_test.setStyleSheet("background-color: RGB(0, 78, 97)")
        self.button_end_test.setIcon(QIcon("./Train/ico/end_test.png"))
        self.button_end_test.setFixedSize(100, 30)
        self.button_end_test.clicked.connect(self.end_test)
        self.layout_h_button_button_end_test = QHBoxLayout()
        self.layout_h_button_button_end_test.addWidget(self.button_end_test)

        self.layout_g_button_all = QGridLayout()
        self.layout_g_button_all.addLayout(self.layout_h_button_open_camera, 0, 0)
        self.layout_g_button_all.addLayout(self.layout_h_button_start_recording, 1, 0)
        self.layout_g_button_all.addLayout(self.layout_h_button_end_recording, 2, 0)
        self.layout_g_button_all.addLayout(self.layout_h_button_import_picture, 0, 1)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_start_label, 1, 1)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_coversition_format, 2, 1)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_configuration_parameter, 0, 2)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_start_train, 1, 2)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_derived_model, 2, 2)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_select_type, 0, 3)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_start_test, 1, 3)
        self.layout_g_button_all.addLayout(self.layout_h_button_button_end_test, 2, 3)

        self.label_image_run_information = QLabel(self)
        self.label_image_run_information.setFixedSize(900, 300)
        self.label_image_run_information.setPixmap(QPixmap("./Train/image_in_ui/run_code.jpg").scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))
        self.label_image_run_information.setAlignment(Qt.AlignCenter)
        self.label_image_run_information.setFrameShape(QtWidgets.QFrame.Box)
        self.label_image_run_information.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_image_run_information.setLineWidth(3)
        self.label_image_run_information.setStyleSheet('background-color: rgb(0, 78, 97)')
        self.label_image_run_information.setScaledContents(True)
        self.h_box_label_image_run_information = QHBoxLayout()
        self.h_box_label_image_run_information.addWidget(self.label_image_run_information)

    def layout_set(self):
        self.layout_h_title = QHBoxLayout()
        self.layout_h_title.addLayout(self.layout_h_label_title)

        self.layout_h_designer_and_time = QHBoxLayout()
        self.layout_h_designer_and_time.addLayout(self.layout_h_label_designer)
        self.layout_h_designer_and_time.addStretch(1)
        self.layout_h_designer_and_time.addLayout(self.layout_h_label_time)

        self.layout_h_image_camera_labelimage_train_test = QHBoxLayout()
        self.layout_h_image_camera_labelimage_train_test.addLayout(self.layout_h_label_image_camera)
        self.layout_h_image_camera_labelimage_train_test.addLayout(self.layout_h_label_image_labelimage)
        self.layout_h_image_camera_labelimage_train_test.addLayout(self.layout_h_label_image_train)
        self.layout_h_image_camera_labelimage_train_test.addLayout(self.layout_h_label_image_test)

        self.layout_h_text_camera_labelimage_train_test = QHBoxLayout()
        self.layout_h_text_camera_labelimage_train_test.addLayout(self.layout_h_label_video_acquisition)
        self.layout_h_text_camera_labelimage_train_test.addLayout(self.layout_h_label_picture_label)
        self.layout_h_text_camera_labelimage_train_test.addLayout(self.layout_h_label_model_train)
        self.layout_h_text_camera_labelimage_train_test.addLayout(self.layout_h_label_model_test)

        self.layout_v_windows = QVBoxLayout()

        self.layout_v_windows.addLayout(self.layout_h_title)
        self.layout_v_windows.addLayout(self.layout_h_designer_and_time)
        self.layout_v_windows.addLayout(self.layout_h_image_camera_labelimage_train_test)
        self.layout_v_windows.addLayout(self.layout_h_text_camera_labelimage_train_test)
        self.layout_v_windows.addLayout(self.layout_g_button_all)
        self.layout_v_windows.addLayout(self.h_box_label_image_run_information)

    def real_time(self):
        self.real_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.label_time.setText(self.real_time)

        self.validation()

    def open_camera(self):
        print("\nOpen Camera in %s" % self.real_time)
        self.status.showMessage("Open Camera", 1000)

        self.camera_path = 0
        self.cap = cv2.VideoCapture(self.camera_path)
        if self.cap.isOpened() != 1:
            print("The Camera Port 0 is noRun in %s" % self.real_time)
            self.video_path_backup = 1
            self.cap = cv2.VideoCapture(self.video_path_backup)
            if self.cap.isOpened() != 1:
                print("The Camera Port 1 is also noRun in %s" % self.real_time)
                self.status.showMessage("The Camera Port is error(0 and 1 have been tried", 1000)
                QMessageBox.about(self, "Error", "The Camera Port is error(0 and 1 have been tried.)")
            elif self.cap.isOpened() == 1:
                print("The Camera Port 1 is Run in %s" % self.real_time)
        elif self.cap.isOpened() == 1:
            print("The Camera Port 0 is Run in %s" % self.real_time)

            self.camera_size = [int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
            self.label_image_run_information.setFixedSize((self.camera_size[0]/self.camera_size[1])*300, 300)

            self.button_open_camera.setEnabled(False)
            self.button_open_camera.setText("正常运行")

            self.qtm_camera_show = QtCore.QTimer()
            self.qtm_camera_show.timeout.connect(self.camera_show)
            self.qtm_camera_show.start(100)

    def camera_show(self):
        self.ret, self.frame = self.cap.read()
        self.video_out_frame = self.frame
        if self.ret is True:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = QtGui.QImage(self.frame[:], self.frame.shape[1], self.frame.shape[0], self.frame.shape[1] * 3, QtGui.QImage.Format_RGB888)

            self.label_image_run_information.setPixmap(QPixmap(self.frame).scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))
            if self.button_start_recording.text() == "开始录制":
                self.status.showMessage("Currently the camera is normally open", 100)
        elif self.ret is False:
            self.qtm_camera_show.stop()
            self.cap.release()
            self.button_open_camera.setText("设备异常")
            self.status.showMessage("Unknow error in camera device", 1000)
            QMessageBox.about(self, "Error", "Unknow error in camera device.")
            self.button_open_camera.setEnabled(True)
            self.button_open_camera.setText("打开设备")
            self.label_image_run_information.setPixmap(QPixmap("./Train/image_in_ui/run_code.jpg").scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))
            self.label_image_run_information.setFixedSize(900, 300)

    def start_recording(self):
        print("\nStart Recording in %s" % self.real_time)
        self.status.showMessage("Start Recording", 1000)

        if self.button_open_camera.text() == "正常运行":
            self.video_name_now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.video_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.video_out = cv2.VideoWriter("./Train/video_camera_recording/" + self.video_name_now_time + '.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 25.0, self.video_size)

            self.button_start_recording.setEnabled(False)
            self.button_start_recording.setText("正常录制")

            self.qtm_video_out = QtCore.QTimer()
            self.qtm_video_out.timeout.connect(self.video_save)
            self.qtm_video_out.start(100)
        elif self.button_open_camera.text() == "打开设备":
            self.status.showMessage("Please first open the device", 1000)
            QMessageBox.about(self, "Error", "Please first open the device.")

    def video_save(self):
        if self.ret is True:
            self.video_out.write(self.video_out_frame)
            self.status.showMessage("Video is currently in normal recording", 100)
        elif self.ret is False:
            self.qtm_video_out.stop()
            self.cap.release()
            self.button_start_recording.setText("录制异常")
            self.status.showMessage("Error saving video this time", 1000)
            QMessageBox.about(self, "Error", "Error saving video this time.")
            self.button_start_recording.setEnabled(True)
            self.button_start_recording.setText("开始录制")

    def end_recording(self):
        print("\nEnd Recording in %s" % self.real_time)
        self.status.showMessage("End Recording", 1000)

        if self.button_open_camera.text() == "正常运行" and self.button_start_recording.text() == "正常录制":
            self.video_out.release()
            self.cap.release()
            self.qtm_video_out.stop()
            self.qtm_camera_show.stop()

            self.button_open_camera.setEnabled(True)
            self.button_open_camera.setText("打开设备")
            self.button_start_recording.setEnabled(True)
            self.button_start_recording.setText("开始录制")
            self.label_image_run_information.setPixmap(QPixmap("./Train/image_in_ui/run_code.jpg").scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))
            self.label_image_run_information.setFixedSize(900, 300)
            self.status.showMessage("The camera has been turned off normally", 1000)
        elif self.button_open_camera.text() == "打开设备" or self.button_start_recording.text() == "开始录制":
            self.status.showMessage("Please make sure the camera is turned on and start recording", 1000)
            QMessageBox.about(self, "Error", "Please make sure the camera is turned on and start recording.")

    def import_picture(self):
        print("\nStart importing pictures in %s" % self.real_time)
        self.status.showMessage("Start importing pictures", 1000)
        self.button_import_picture.setEnabled(False)
        self.button_import_picture.setText("正在导入")
        self.label_file_path = "None"
        self.get_item_video()
        if self.label_file_path != "None":
            if self.label_file_path == "Video from this system":
                print("The user's select is %s" % self.label_file_path)
                self.frame_frequency = 10
                self.get_int_frame()
                print("The user's intercept frame raye is %s" % self.frame_frequency)
                self.label_file_path = "./Train/video_camera_recording/"
                self.pictures_out_dir = "./Train/pictures_label_file/"
                self.video_2_picture()
            if self.label_file_path == "Video from other paths":
                print("The user's select is %s" % self.label_file_path)
                self.get_video_files()
                self.frame_frequency = 10
                self.get_int_frame()
                print("The user's intercept frame raye is %s" % self.frame_frequency)
                self.label_file_path = "./Train/video_camera_recording/"
                self.pictures_out_dir = "./Train/pictures_label_file/"
                self.video_2_picture()
            if self.label_file_path == "Pictures from other paths":
                print("The user's select is %s" % self.label_file_path)
                self.pictures_out_dir = "./Train/pictures_label_file/"
                self.get_pictures_file()
        else:
            self.status.showMessage("Any annotation data has not been selected", 1000)
            QMessageBox.about(self, "Warning", "Any annotation data has not been selected.")
            self.button_import_picture.setEnabled(True)
            self.button_import_picture.setText("导入图片")

    def get_item_video(self):
        items = ("Video from this system", "Video from other paths", "Pictures from other paths")
        item, ok = QInputDialog.getItem(self, "请选择标注资料来源", "标注资料来源", items, 0, False)
        if ok and item:
            self.label_file_path = item

    def get_int_frame(self):
        num, ok = QInputDialog.getInt(self, "Intercept frame raye", "选择帧率（默认为10）", 10)
        if ok:
            self.frame_frequency = num

    def video_2_picture(self):
        if not os.listdir(self.label_file_path):
            self.status.showMessage("Any annotation data has not been collected in this system", 1000)
            QMessageBox.about(self, "Warning", "Any annotation data has not been collected in this system.")
            self.button_import_picture.setEnabled(True)
            self.button_import_picture.setText("导入图片")
        else:
            print('Start video_2_pictures in %s' % self.real_time)
            self.button_import_picture.setEnabled(False)
            self.button_import_picture.setText("正在导入")
            for self.file_names in os.listdir(self.label_file_path):
                self.file_names = str(self.file_names[0:14])
                video_path = self.label_file_path + self.file_names + ".mp4"
                output_dir = self.pictures_out_dir + self.file_names + "_image/"
                if not os.path.exists(output_dir):
                    print('Create output paths in %s' % self.real_time)
                    os.makedirs(output_dir)
                times = 0
                camera = cv2.VideoCapture(video_path)
                while True:
                    times += 1
                    res, image = camera.read()
                    if not res:
                        break
                    if times % self.frame_frequency == 0:
                        img_index = times // self.frame_frequency
                        cv2.imwrite(output_dir + self.file_names + '_' + str(img_index) + '.jpg', image)
                camera.release()
            print('End video_2_pictures in %s' % self.real_time)
            self.button_import_picture.setEnabled(True)
            self.button_import_picture.setText("导入图片")

    def get_video_files(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "选择视频文件", ".", "Video files(*.mp4)")
        for fname in fnames:
            self.video_file_path = fname
            self.video_file_path_ivt = "./Train/video_camera_recording/%s.mp4" % datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            try:
                result = os.system("cp %s %s" % (self.video_file_path, self.video_file_path_ivt))
            except:
                result = os.system("copy %s %s" % (self.video_file_path, self.video_file_path_ivt))
            if result is 0:
                print("Video file copied successfully in %s" % self.real_time)
            else:
                self.status.showMessage("Video file copy failed", 1000)
                QMessageBox.about(self, "Warning", "Video file copy failed.")
                self.button_import_picture.setEnabled(True)
                self.button_import_picture.setText("导入图片")

    def get_pictures_file(self):
        files_path = QFileDialog.getExistingDirectory(self, "选择图片所在文件夹", ".")
        if int(len(str(files_path))) > 0:
            target_path = self.pictures_out_dir + "%s" % datetime.datetime.now().strftime('%Y%m%d%H%M%S') + "_image/"
            if not os.path.exists(target_path):
                os.makedirs(target_path)
                print('Create target path in %s' % self.real_time)
            try:
                if os.path.exists(files_path):
                    for root, dirs, files in os.walk(files_path):
                        for file in files:
                            if str(file)[-3:] == "jpg" or str(file)[-3:] == "jpg":
                                src_file = os.path.join(root, file)
                                shutil.copy(src_file, target_path)
            except:
                self.status.showMessage("Pictures files copy failed", 1000)
                QMessageBox.about(self, "Warning", "Pictures files copy failed.")
                self.button_import_picture.setEnabled(True)
                self.button_import_picture.setText("导入图片")
            print("Pictures copied successfully in %s" % self.real_time)
            self.button_import_picture.setEnabled(True)
            self.button_import_picture.setText("导入图片")
        else:
            self.status.showMessage("No picture folder has been selected", 1000)
            QMessageBox.about(self, "Warning", "No picture folder has been selected.")
            self.button_import_picture.setEnabled(True)
            self.button_import_picture.setText("导入图片")

    def start_label(self):
        print("\nStart label in %s" % self.real_time)

        self.status.showMessage("Tagging in progress", 10000)
        self.button_start_label.setEnabled(False)
        self.button_start_label.setText("正在标注")

        self.argv = sys.argv
        self.the_label_window = MainWindow_label(self.argv[1] if len(self.argv) >= 2 else None, self.argv[2] if len(self.argv) >= 3 else os.path.join(os.path.dirname(sys.argv[0]), 'libs', 'predefined_classes.txt'), self.argv[3] if len(self.argv) >= 4 else None)
        self.the_label_window.show()

        self.qtm_button_start_label_set = QtCore.QTimer()
        self.qtm_button_start_label_set.timeout.connect(self.button_start_label_set)
        self.qtm_button_start_label_set.start(10000)

    def button_start_label_set(self):
        self.button_start_label.setEnabled(True)
        self.button_start_label.setText("开始标注")

        self.qtm_button_start_label_set.stop()

    def coversition_format(self):
        print("\nFile format start conversion in %s" % self.real_time)
        self.status.showMessage("File format start conversion", 1000)
        self.button_coversition_format.setEnabled(False)
        self.button_coversition_format.setText("正在转换")

        self.pictures_num = 0
        self.xml_num = 0

        dst_file_image = "./Train/scripts/VOCdevkit/VOC2007/JPEGImages/"
        dst_file_xml = "./Train/scripts/VOCdevkit/VOC2007/Annotations/"
        dst_file_label = "./Train/scripts/VOCdevkit/VOC2007/labels/"

        current_list = glob.glob(os.path.join(dst_file_image, '*'))
        for x in current_list:
            os.remove(x)

        current_list = glob.glob(os.path.join(dst_file_xml, '*'))
        for x in current_list:
            os.remove(x)

        current_list = glob.glob(os.path.join(dst_file_label, '*'))
        for x in current_list:
            os.remove(x)

        src_file = "./Train/pictures_label_file/"

        current_list = glob.glob(os.path.join(src_file, '*'))
        for x in current_list:
            current_list2 = glob.glob(os.path.join(x, '*'))
            for y in current_list2:
                if y[-3:] == 'jpg':
                    shutil.copy(y, dst_file_image)
                    self.pictures_num = self.pictures_num + 1
                if y[-3:] == 'xml':
                    shutil.copy(y, dst_file_xml)
                    self.xml_num = self.xml_num + 1

        rootdir = dst_file_xml
        list = os.listdir(rootdir)

        classes_list = []
        for i in range(0, len(list)):
            path = os.path.join(rootdir, list[i])
            if os.path.isfile(path):
                dom = xml.dom.minidom.parse(path)
                root = dom.documentElement
                cc = dom.getElementsByTagName('name')
                for i in range(len(cc)):
                    c1 = cc[i]
                    if classes_list.count(c1.firstChild.data) == 0:
                        classes_list.append(c1.firstChild.data)
        self.classes_list = classes_list
        self.status.showMessage("The pictures total is %s and The xml total is %s|Your classes total is %s and they are %s" % (self.pictures_num, self.xml_num, len(classes_list), classes_list), 3000)

        if os.path.exists("./Train/scripts/classes.py"):
            os.remove("./Train/scripts/classes.py")
        classes_file = open("./Train/scripts/classes.py", 'w')
        classes_name = "classes = "
        for classes_num in range(0, len(classes_list)):
            if len(classes_list) == 1:
                classes_name = classes_name + "[\"%s\"]" % classes_list[classes_num]
            else:
                if classes_num == 0:
                    classes_name = classes_name + "[\"%s\", " % classes_list[classes_num]
                elif (len(classes_list) - 1) > classes_num > 0:
                    classes_name = classes_name + "\"%s\", " % classes_list[classes_num]
                elif classes_num == (len(classes_list) - 1):
                    classes_name = classes_name + "\"%s\"]" % classes_list[classes_num]
        classes_file.write(classes_name)
        classes_file.close()

        reply = QMessageBox.question(self, "请确认重要信息", "请确认Classes类别名称&其他信息是否符合你的实际需求？\n符合请选择Yes进行下一步，\n存在错误请选择No或关闭弹窗。\n请确认如下信息：\n你的照片数量是：%s\n你的xml文件数量是：%s\n你的Classes数量是%s\n你的Classes类别是：%s" % (self.pictures_num, self.xml_num, len(classes_list), classes_list), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            print("The Classes Information is Yes in %s" % self.real_time)
            print("The Classes.py is OK in %s" % self.real_time)
            self.coversition()
        elif reply == QtWidgets.QMessageBox.No:
            print("The Classes Information is No in %s" % self.real_time)
            QMessageBox.about(self, "请联系平台开发者", "Developer: 苏晓飞\nTelephone: 8610-2484")

    def coversition(self):
        trainval_percent = 0.1
        train_percent = 0.9
        xmlfilepath = './Train/scripts/VOCdevkit/VOC2007/Annotations'
        txtsavepath = './Train/scripts/VOCdevkit/VOC2007/ImageSets\Main'
        total_xml = os.listdir(xmlfilepath)

        num = len(total_xml)
        list = range(num)
        tv = int(num * trainval_percent)
        tr = int(tv * train_percent)
        trainval = random.sample(list, tv)
        train = random.sample(trainval, tr)

        ftrainval = open('./Train/scripts/VOCdevkit/VOC2007/ImageSets/Main/trainval.txt', 'w')
        ftest = open('./Train/scripts/VOCdevkit/VOC2007/ImageSets/Main/test.txt', 'w')
        ftrain = open('./Train/scripts/VOCdevkit/VOC2007/ImageSets/Main/train.txt', 'w')
        fval = open('./Train/scripts/VOCdevkit/VOC2007/ImageSets/Main/val.txt', 'w')

        for i in list:
            name = total_xml[i][:-4] + '\n'
            if i in trainval:
                ftrainval.write(name)
                if i in train:
                    ftest.write(name)
                else:
                    fval.write(name)
            else:
                ftrain.write(name)

        ftrainval.close()
        ftrain.close()
        fval.close()
        ftest.close()
        print("The Main TXT files is OK in %s" % self.real_time)

        sets = [('2007', 'train'), ('2007', 'val'), ('2007', 'test')]

        classes = class_names.classes

        def convert(size, box):
            dw = 1. / (size[0])
            dh = 1. / (size[1])
            x = (box[0] + box[1]) / 2.0 - 1
            y = (box[2] + box[3]) / 2.0 - 1
            w = box[1] - box[0]
            h = box[3] - box[2]
            x = x * dw
            w = w * dw
            y = y * dh
            h = h * dh
            return (x, y, w, h)

        def convert_annotation(year, image_id):
            in_file = open('./Train/scripts/VOCdevkit/VOC%s/Annotations/%s.xml' % (year, image_id))
            out_file = open('./Train/scripts/VOCdevkit/VOC%s/labels/%s.txt' % (year, image_id), 'w')
            tree = ET.parse(in_file)
            root = tree.getroot()
            size = root.find('size')
            w = int(size.find('width').text)
            h = int(size.find('height').text)

            for obj in root.iter('object'):
                difficult = obj.find('difficult').text
                cls = obj.find('name').text
                if cls not in classes or int(difficult) == 1:
                    continue
                cls_id = classes.index(cls)
                xmlbox = obj.find('bndbox')
                b = (
                    float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
                    float(xmlbox.find('ymax').text))
                bb = convert((w, h), b)
                out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

        wd = getcwd()

        for year, image_set in sets:
            if not os.path.exists('./Train/scripts/VOCdevkit/VOC%s/labels/' % (year)):
                os.makedirs('./Train/scripts/VOCdevkit/VOC%s/labels/' % (year))
            image_ids = open(
                './Train/scripts/VOCdevkit/VOC%s/ImageSets/Main/%s.txt' % (year, image_set)).read().strip().split()
            list_file = open('./Train/scripts/%s_%s.txt' % (year, image_set), 'w')
            for image_id in image_ids:
                list_file.write('%s/Train/scripts/VOCdevkit/VOC%s/JPEGImages/%s.jpg\n' % (wd, year, image_id))
                convert_annotation(year, image_id)
            list_file.close()

        os.system("cat ./Train/scripts/2007_train.txt ./Train/scripts/2007_val.txt > ./Train/scripts/train.txt")
        os.system(
            "cat ./Train/scripts/2007_train.txt ./Train/scripts/2007_val.txt ./Train/scripts/2007_test.txt > ./Train/scripts/train.all.txt")
        print("The Train files is OK in %s" % self.real_time)

        print("File format conversion complete in %s" % self.real_time)
        self.status.showMessage("File format conversion complete", 1000)
        self.button_coversition_format.setEnabled(True)
        self.button_coversition_format.setText("转换格式")

    def configuration_parameter(self):
        print("\nBegin to config paramters in %s" % self.real_time)
        self.status.showMessage("Begin to config paramters", 1000)
        self.button_configuration_parameter.setEnabled(False)
        self.button_configuration_parameter.setText("正在配置")

        items = ("YOLOv4-Tiny", "YOLOv4")
        item, ok = QInputDialog.getItem(self, "选择模型类别", "模型类别", items, 0, False)
        if ok and item:
            print("Your choice is %s" % item)

            if item == "YOLOv4-Tiny":
                shutil.copy("./Train/yolov4-tiny.conv.29", "./Train/cfg/train_cfg/yolov4-tiny.conv.29")

                shutil.copy("./Train/cfg/yolov4-tiny.cfg", "./Train/cfg/train_cfg/yolov4-tiny.cfg")

                dst_file_xml = "./Train/scripts/VOCdevkit/VOC2007/Annotations/"
                rootdir = dst_file_xml
                list = os.listdir(rootdir)

                classes_list = []
                for i in range(0, len(list)):
                    path = os.path.join(rootdir, list[i])
                    if os.path.isfile(path):
                        dom = xml.dom.minidom.parse(path)
                        root = dom.documentElement
                        cc = dom.getElementsByTagName('name')
                        for i in range(len(cc)):
                            c1 = cc[i]
                            if classes_list.count(c1.firstChild.data) == 0:
                                classes_list.append(c1.firstChild.data)
                self.classes_list = classes_list

                cfg_tiny_file = open("./Train/cfg/train_cfg/yolov4-tiny.cfg", 'r+')
                cfg_tiny_file_list = cfg_tiny_file.readlines()
                cfg_tiny_file_list[5] = 'batch=4\n'
                cfg_tiny_file_list[211] = 'filters=%s\n' % (3 * (len(self.classes_list) + 5))
                cfg_tiny_file_list[219] = 'classes=%s\n' % (len(self.classes_list))
                cfg_tiny_file_list[262] = 'filters=%s\n' % (3 * (len(self.classes_list) + 5))
                cfg_tiny_file_list[268] = 'classes=%s\n' % (len(self.classes_list))
                cfg_tiny_file = open("./Train/cfg/train_cfg/yolov4-tiny.cfg", 'w+')
                cfg_tiny_file.writelines(cfg_tiny_file_list)
                cfg_tiny_file.close()

                shutil.copy("./Train/data/voc.names", "./Train/cfg/train_cfg/voc.names")

                voc_names_tiny_file = open("./Train/cfg/train_cfg/voc.names", 'r+')
                voc_names_tiny_file.truncate()
                for m in range(len(self.classes_list)):
                    voc_names_tiny_file.write(self.classes_list[m] + "\n")
                voc_names_tiny_file.close()

                shutil.copy("./Train/cfg/voc.data", "./Train/cfg/train_cfg/voc.data")

                voc_data_tiny_file = open("./Train/cfg/train_cfg/voc.data", 'r+')
                voc_data_tiny_file_list = voc_data_tiny_file.readlines()
                voc_data_tiny_file_list[0] = 'classes= %s\n' % (len(self.classes_list))
                voc_data_tiny_file_list[1] = 'train  = %s\n' % "./Train/scripts/train.txt"
                voc_data_tiny_file_list[2] = 'valid  = %s\n' % "./Train/scripts/2007_test.txt"
                voc_data_tiny_file_list[3] = 'names = %s\n' % "./Train/cfg/train_cfg/voc.names"
                voc_data_tiny_file_list[4] = 'backup = %s\n' % "./Train/backup/"
                voc_data_tiny_file = open("./Train/cfg/train_cfg/voc.data", 'w+')
                voc_data_tiny_file.writelines(voc_data_tiny_file_list)
                voc_data_tiny_file.close()

                print("Config paramters is OK in %s" % self.real_time)
                self.status.showMessage("Config paramters is OK", 1000)
                self.button_configuration_parameter.setEnabled(True)
                self.button_configuration_parameter.setText("配置参数")

            if item == "YOLOv4":
                shutil.copy("./Train/yolov4.conv.137", "./Train/cfg/train_cfg/yolov4.conv.137")

                shutil.copy("./Train/cfg/yolov4.cfg", "./Train/cfg/train_cfg/yolov4.cfg")

                dst_file_xml = "./Train/scripts/VOCdevkit/VOC2007/Annotations/"
                rootdir = dst_file_xml
                list = os.listdir(rootdir)

                classes_list = []
                for i in range(0, len(list)):
                    path = os.path.join(rootdir, list[i])
                    if os.path.isfile(path):
                        dom = xml.dom.minidom.parse(path)
                        root = dom.documentElement
                        cc = dom.getElementsByTagName('name')
                        for i in range(len(cc)):
                            c1 = cc[i]
                            if classes_list.count(c1.firstChild.data) == 0:
                                classes_list.append(c1.firstChild.data)
                self.classes_list = classes_list

                cfg_voc_file = open("./Train/cfg/train_cfg/yolov4.cfg", 'r+')
                cfg_voc_file_list = cfg_voc_file.readlines()
                cfg_voc_file_list[1] = 'batch=4\n'
                cfg_voc_file_list[2] = 'subdivisions=1\n'
                cfg_voc_file_list[960] = 'filters=%s\n' % (3 * (len(self.classes_list) + 5))
                cfg_voc_file_list[967] = 'classes=%s\n' % (len(self.classes_list))
                cfg_voc_file_list[1048] = 'filters=%s\n' % (3 * (len(self.classes_list) + 5))
                cfg_voc_file_list[1055] = 'classes=%s\n' % (len(self.classes_list))
                cfg_voc_file_list[1136] = 'filters=%s\n' % (3 * (len(self.classes_list) + 5))
                cfg_voc_file_list[1143] = 'classes=%s\n' % (len(self.classes_list))
                cfg_voc_file = open("./Train/cfg/train_cfg/yolov4.cfg", 'w+')
                cfg_voc_file.writelines(cfg_voc_file_list)
                cfg_voc_file.close()

                shutil.copy("./Train/data/voc.names", "./Train/cfg/train_cfg/voc.names")

                voc_names_tiny_file = open("./Train/cfg/train_cfg/voc.names", 'r+')
                voc_names_tiny_file.truncate()
                for m in range(len(self.classes_list)):
                    voc_names_tiny_file.write(self.classes_list[m] + "\n")
                voc_names_tiny_file.close()

                shutil.copy("./Train/cfg/voc.data", "./Train/cfg/train_cfg/voc.data")

                voc_data_tiny_file = open("./Train/cfg/train_cfg/voc.data", 'r+')
                voc_data_tiny_file_list = voc_data_tiny_file.readlines()
                voc_data_tiny_file_list[0] = 'classes= %s\n' % (len(self.classes_list))
                voc_data_tiny_file_list[1] = 'train  = %s\n' % "./Train/scripts/train.txt"
                voc_data_tiny_file_list[2] = 'valid  = %s\n' % "./Train/scripts/2007_test.txt"
                voc_data_tiny_file_list[3] = 'names = %s\n' % "./Train/cfg/train_cfg/voc.names"
                voc_data_tiny_file_list[4] = 'backup = %s\n' % "./Train/backup/"
                voc_data_tiny_file = open("./Train/cfg/train_cfg/voc.data", 'w+')
                voc_data_tiny_file.writelines(voc_data_tiny_file_list)
                voc_data_tiny_file.close()

                print("Config paramters is OK in %s" % self.real_time)
                self.status.showMessage("Config paramters is OK", 1000)
                self.button_configuration_parameter.setEnabled(True)
                self.button_configuration_parameter.setText("配置参数")

        else:
            print("Config paramters is None in %s" % self.real_time)
            self.status.showMessage("Config paramters is None", 1000)
            self.button_configuration_parameter.setEnabled(True)
            self.button_configuration_parameter.setText("配置参数")

    def start_train(self):
        print("\nStart train in %s" % self.real_time)
        self.status.showMessage("Start train", 1000)
        self.button_start_train.setEnabled(False)
        self.button_start_train.setText("正在训练")

        self.qtm_train = QtCore.QTimer()
        self.qtm_train.timeout.connect(self.train)
        self.qtm_train.start(10)

        self.qtm_button_train_set = QtCore.QTimer()
        self.qtm_button_train_set.timeout.connect(self.button_train_set)
        self.qtm_button_train_set.start(3600000)

        self.qtm_train_chart_put = QtCore.QTimer()
        self.qtm_train_chart_put.timeout.connect(self.train_chart_put)
        self.qtm_train_chart_put.start(10000)

    def train(self):
        items = ("YOLOv4-Tiny", "YOLOv4")
        item, ok = QInputDialog.getItem(self, "选择模型类别", "模型类别", items, 0, False)
        if ok and item:
            print("Your choice is %s" % item)

            if item == "YOLOv4-Tiny":
                subprocess.Popen("./Train/darknet detector train ./Train/cfg/train_cfg/voc.data ./Train/cfg/train_cfg/yolov4-tiny.cfg ./Train/cfg/train_cfg/yolov4-tiny.conv.29", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.qtm_train.stop()
            if item == "YOLOv4":
                subprocess.Popen("./Train/darknet detector train ./Train/cfg/train_cfg/voc.data ./Train/cfg/train_cfg/yolov4.cfg ./Train/cfg/train_cfg/yolov4.conv.137", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.qtm_train.stop()
        else:
            self.qtm_train.stop()
            self.qtm_train_chart_put.stop()
            self.qtm_button_train_set.stop()

            print("Cancel train in %s" % self.real_time)
            self.status.showMessage("Cancel train", 1000)
            self.button_start_train.setEnabled(True)
            self.button_start_train.setText("开始训练")

    def button_train_set(self):
        self.qtm_train_chart_put.stop()
        print("End train in %s" % self.real_time)
        self.status.showMessage("End train", 1000)
        self.button_start_train.setEnabled(True)
        self.button_start_train.setText("开始训练")
        self.label_image_run_information.setPixmap(QPixmap("./Train/image_in_ui/run_code.jpg").scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))
        self.qtm_button_train_set.stop()

    def train_chart_put(self):
        if os.path.exists("./chart.png") is True:
            self.label_image_run_information.setPixmap(QPixmap("./chart.png").scaled(self.label_image_run_information.width(), self.label_image_run_information.height()))

    def derived_model(self):
        print("\nStart derived model in %s" % self.real_time)
        self.status.showMessage("Start derived model", 1000)
        self.button_derived_model.setEnabled(False)
        self.button_derived_model.setText("正在导出")

        files_path = "./Train/backup/"
        if int(len(str(files_path))) > 0:
            target_path = "./Your_Model_%s/" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            if not os.path.exists(target_path):
                os.makedirs(target_path)
                print('Create target path in %s' % self.real_time)

            if os.path.exists(files_path):
                for root, dirs, files in os.walk(files_path):
                    for file in files:
                        src_file = os.path.join(root, file)
                        shutil.copy(src_file, target_path)

        print("End derived model in %s" % self.real_time)
        self.status.showMessage("End derived model", 1000)
        self.button_derived_model.setEnabled(True)
        self.button_derived_model.setText("导出模型")

    def select_type(self):
        print("\nStart select type in %s" % self.real_time)
        self.status.showMessage("Start select type", 1000)
        self.button_select_type.setEnabled(False)
        self.button_select_type.setText("正在选择")

        items = ("YOLOv4-Tiny", "YOLOv4", "自有模型&相关资料")
        item, ok = QInputDialog.getItem(self, "选择模型类别", "模型类别", items, 0, False)
        if ok and item:
            print("Your choice is %s" % item)

            if item == "YOLOv4-Tiny":
                current_list = glob.glob(os.path.join("./Train/cfg/test_cfg/", '*'))
                for x in current_list:
                    os.remove(x)

                if os.path.exists("./Train/backup/yolov4-tiny_last.weights") is True:
                    shutil.copy("./Train/backup/yolov4-tiny_last.weights", "./Train/cfg/test_cfg/yolov4-tiny_last.weights")
                else:
                    print("The yolov4-tiny_last.weights is No in %s" % self.real_time)
                    QMessageBox.about(self, "请联系平台开发者", "Developer: 苏晓飞\nTelephone: 8610-2484")

                shutil.copy("./Train/cfg/train_cfg/yolov4-tiny.cfg", "./Train/cfg/test_cfg/yolov4-tiny.cfg")

                cfg_tiny_file = open("./Train/cfg/test_cfg/yolov4-tiny.cfg", 'r+')
                cfg_tiny_file_list = cfg_tiny_file.readlines()
                cfg_tiny_file_list[2] = 'batch=1\n'
                cfg_tiny_file_list[3] = 'subdivisions=1\n'
                cfg_tiny_file_list[5] = '# batch=4\n'
                cfg_tiny_file_list[6] = '# subdivisions=1\n'
                cfg_tiny_file = open("./Train/cfg/test_cfg/yolov4-tiny.cfg", 'w+')
                cfg_tiny_file.writelines(cfg_tiny_file_list)
                cfg_tiny_file.close()

                shutil.copy("./Train/cfg/train_cfg/voc.names", "./Train/cfg/test_cfg/voc.names")

                shutil.copy("./Train/cfg/train_cfg/voc.data", "./Train/cfg/test_cfg/voc.data")

                print("Select type is ok in %s" % self.real_time)
                self.status.showMessage("Select type is OK", 1000)
                self.button_select_type.setEnabled(True)
                self.button_select_type.setText("选择类型")

            if item == "YOLOv4":
                current_list = glob.glob(os.path.join("./Train/cfg/test_cfg/", '*'))
                for x in current_list:
                    os.remove(x)

                if os.path.exists("./Train/backup/yolov4_last.weights") is True:
                    shutil.copy("./Train/backup/yolov4_last.weights", "./Train/cfg/test_cfg/yolov4_last.weights")
                else:
                    print("The yolov4_last.weights is No in %s" % self.real_time)
                    QMessageBox.about(self, "请联系平台开发者", "Developer: 苏晓飞\nTelephone: 8610-2484")

                shutil.copy("./Train/cfg/train_cfg/yolov4.cfg", "./Train/cfg/test_cfg/yolov4.cfg")

                cfg_voc_file = open("./Train/cfg/test_cfg/yolov4.cfg", 'r+')
                cfg_voc_file_list = cfg_voc_file.readlines()
                cfg_voc_file_list[1] = 'batch=1\n'
                cfg_voc_file_list[2] = 'subdivisions=1\n'
                cfg_voc_file = open("./Train/cfg/train_cfg/yolov4.cfg", 'w+')
                cfg_voc_file.writelines(cfg_voc_file_list)
                cfg_voc_file.close()

                shutil.copy("./Train/cfg/train_cfg/voc.names", "./Train/cfg/test_cfg/voc.names")

                shutil.copy("./Train/cfg/train_cfg/voc.data", "./Train/cfg/test_cfg/voc.data")

                print("Select type is ok in %s" % self.real_time)
                self.status.showMessage("Select type is OK", 1000)
                self.button_select_type.setEnabled(True)
                self.button_select_type.setText("选择类型")

            if item == "自有模型&相关资料":
                current_list = glob.glob(os.path.join("./Train/cfg/test_cfg/", '*'))
                for x in current_list:
                    os.remove(x)

                weight, _ = QFileDialog.getOpenFileName(self, "选择模型文件", ".", "Model files(*.weights)")
                self.weight = weight
                self.weight_test = "./Train/cfg/test_cfg/yolov4-tiny_last.weights"

                try:
                    result = os.system("cp %s %s" % (self.weight, self.weight_test))
                except:
                    result = os.system("copy %s %s" % (self.weight, self.weight_test))
                if result is 0:
                    print("Weight file copied successfully in %s" % self.real_time)
                else:
                    self.status.showMessage("Weight file copy failed", 1000)
                    QMessageBox.about(self, "Warning", "Weight file copy failed.")
                    self.button_select_type.setEnabled(True)
                    self.button_select_type.setText("选择类型")

                cfg, _ = QFileDialog.getOpenFileName(self, "选择cfg文件", ".", "cfg files(*.cfg)")
                self.cfg = cfg
                self.cfg_test = "./Train/cfg/test_cfg/yolov4-tiny.cfg"

                try:
                    result = os.system("cp %s %s" % (self.cfg, self.cfg_test))
                except:
                    result = os.system("copy %s %s" % (self.cfg, self.cfg_test))
                if result is 0:
                    print("cfg file copied successfully in %s" % self.real_time)
                else:
                    self.status.showMessage("cfg file copy failed", 1000)
                    QMessageBox.about(self, "Warning", "cfg file copy failed.")
                    self.button_select_type.setEnabled(True)
                    self.button_select_type.setText("选择类型")

                data, _ = QFileDialog.getOpenFileName(self, "选择data文件", ".", "cfg files(*.data)")
                self.data = data
                self.data_test = "./Train/cfg/test_cfg/voc.data"

                try:
                    result = os.system("cp %s %s" % (self.data, self.data_test))
                except:
                    result = os.system("copy %s %s" % (self.data, self.data_test))

                voc_data_tiny_file = open("./Train/cfg/test_cfg/voc.data", 'r+')
                voc_data_tiny_file_list = voc_data_tiny_file.readlines()
                voc_data_tiny_file_list[3] = 'names = %s\n' % "./Train/cfg/test_cfg/voc.names"
                voc_data_tiny_file = open("./Train/cfg/test_cfg/voc.data", 'w+')
                voc_data_tiny_file.writelines(voc_data_tiny_file_list)
                voc_data_tiny_file.close()

                if result is 0:
                    print("data file copied successfully in %s" % self.real_time)
                else:
                    self.status.showMessage("data file copy failed", 1000)
                    QMessageBox.about(self, "Warning", "data file copy failed.")
                    self.button_select_type.setEnabled(True)
                    self.button_select_type.setText("选择类型")

                names, _ = QFileDialog.getOpenFileName(self, "选择names文件", ".", "names files(*.names)")
                self.names = names
                self.names_test = "./Train/cfg/test_cfg/voc.names"

                try:
                    result = os.system("cp %s %s" % (self.names, self.names_test))
                except:
                    result = os.system("copy %s %s" % (self.names, self.names_test))
                if result is 0:
                    print("names file copied successfully in %s" % self.real_time)

                    print("Select type is ok in %s" % self.real_time)
                    self.status.showMessage("Select type is OK", 1000)
                    self.button_select_type.setEnabled(True)
                    self.button_select_type.setText("选择类型")
                else:
                    self.status.showMessage("names file copy failed", 1000)
                    QMessageBox.about(self, "Warning", "names file copy failed.")
                    self.button_select_type.setEnabled(True)
                    self.button_select_type.setText("选择类型")
        else:
            print("Select type is None in %s" % self.real_time)
            self.status.showMessage("Select type is None", 1000)
            self.button_select_type.setEnabled(True)
            self.button_select_type.setText("选择类型")

    def start_test(self):
        print("\nStart test in %s" % self.real_time)
        self.status.showMessage("Start test", 1000)
        self.button_start_test.setEnabled(False)
        self.button_start_test.setText("正在测试")

        self.test()

    def test(self):
        cameras = ("本地视频测试", "现场摄像测试")
        camera, ok = QInputDialog.getItem(self, "选择测试类型", "测试类型", cameras, 0, False)
        if ok and camera:
            print("Your choice is %s" % camera)
            if camera == "本地视频测试":
                test_video, _ = QFileDialog.getOpenFileName(self, "选择测试视频文件", ".", "Test_video files(*.mp4)")
                self.test_video = test_video
                self.test_video_test = "./Train/cfg/test_cfg/test.mp4"

                try:
                    result = os.system("cp %s %s" % (self.test_video, self.test_video_test))
                except:
                    result = os.system("copy %s %s" % (self.test_video, self.test_video_test))
                if result is 0:
                    print("Test_video file copied successfully in %s" % self.real_time)

                    items = ("YOLOv4-Tiny", "YOLOv4")
                    item, ok = QInputDialog.getItem(self, "选择模型类别", "模型类别", items, 0, False)
                    if ok and item:
                        print("Your choice is %s" % item)

                        try:
                            if item == "YOLOv4-Tiny":
                                self.qtm_test = QtCore.QTimer()
                                self.qtm_test.timeout.connect(self.video_yolo_tiny_test)
                                self.qtm_test.start(10)
                            if item == "YOLOv4":
                                self.qtm_test = QtCore.QTimer()
                                self.qtm_test.timeout.connect(self.video_yolo_test)
                                self.qtm_test.start(10)
                        except:
                            self.qtm_test.stop()
                            QMessageBox.about(self, "请联系平台开发者", "Developer: 苏晓飞\nTelephone: 8610-2484")

                    else:
                        print("Cancel test in %s" % self.real_time)
                        self.status.showMessage("Cancel test", 1000)
                        self.button_start_test.setEnabled(True)
                        self.button_start_test.setText("开始测试")
                else:
                    self.status.showMessage("Test_video file copy failed", 1000)
                    QMessageBox.about(self, "Warning", "Test_video file copy failed.")
                    self.button_start_test.setEnabled(True)
                    self.button_start_test.setText("开始测试")

            if camera == "现场摄像测试":
                items = ("YOLOv4-Tiny", "YOLOv4")
                item, ok = QInputDialog.getItem(self, "选择模型类别", "模型类别", items, 0, False)
                if ok and item:
                    print("Your choice is %s" % item)

                    try:
                        if item == "YOLOv4-Tiny":
                            self.qtm_test = QtCore.QTimer()
                            self.qtm_test.timeout.connect(self.camera_yolo_tiny_test)
                            self.qtm_test.start(10)
                        if item == "YOLOv4":
                            self.qtm_test = QtCore.QTimer()
                            self.qtm_test.timeout.connect(self.camera_yolo_test)
                            self.qtm_test.start(10)
                    except:
                        self.qtm_test.stop()
                        QMessageBox.about(self, "请联系平台开发者", "Developer: 苏晓飞\nTelephone: 8610-2484")

                else:
                    print("Cancel test in %s" % self.real_time)
                    self.status.showMessage("Cancel test", 1000)
                    self.button_start_test.setEnabled(True)
                    self.button_start_test.setText("开始测试")
        else:
            print("Cancel test in %s" % self.real_time)
            self.status.showMessage("Cancel test", 1000)
            self.button_start_test.setEnabled(True)
            self.button_start_test.setText("开始测试")

    def video_yolo_tiny_test(self):
        self.ret = subprocess.Popen("./Train/darknet detector demo ./Train/cfg/test_cfg/voc.data ./Train/cfg/test_cfg/yolov4-tiny.cfg ./Train/cfg/test_cfg/yolov4-tiny_last.weights ./Train/cfg/test_cfg/test.mp4", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.qtm_test.stop()

    def video_yolo_test(self):
        self.ret = subprocess.Popen("./Train/darknet detector demo ./Train/cfg/test_cfg/voc.data ./Train/cfg/test_cfg/yolov4.cfg ./Train/cfg/test_cfg/yolov4_last.weights ./Train/cfg/test_cfg/test.mp4", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.qtm_test.stop()

    def camera_yolo_tiny_test(self):
        self.ret = subprocess.Popen("./Train/darknet detector demo ./Train/cfg/test_cfg/voc.data ./Train/cfg/test_cfg/yolov4-tiny.cfg ./Train/cfg/test_cfg/yolov4-tiny_last.weights -c 0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.qtm_test.stop()

    def camera_yolo_test(self):
        self.ret = subprocess.Popen("./Train/darknet detector demo ./Train/cfg/test_cfg/voc.data ./Train/cfg/test_cfg/yolov4.cfg ./Train/cfg/test_cfg/yolov4_last.weights -c 0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.qtm_test.stop()

    def end_test(self):
        print("\nEnd test in %s" % self.real_time)
        self.status.showMessage("End test", 1000)
        self.button_end_test.setEnabled(False)
        self.button_end_test.setText("正在结束")

        QMessageBox.about(self, "请点击确定以结束模型测试！", "Developer: 苏晓飞\nTelephone: 8610-2484")

        self.kill_pid()

        self.button_start_test.setEnabled(True)
        self.button_start_test.setText("开始测试")

        self.button_end_test.setEnabled(True)
        self.button_end_test.setText("结束测试")

    def kill_pid(self):
        for i in range(0, 100):
            self.ret.kill()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
