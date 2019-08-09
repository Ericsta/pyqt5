# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from PyQt5.QtCore import QBasicTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
import time

class Ui_Form(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1092, 701)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(500, 0, 89, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.on_click())

        self.verticalLayoutWidget = QVideoWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(550, 30, 531, 611))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        # self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        # self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayoutWidget_2 = QVideoWidget(Form)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 30, 521, 611))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        # self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        # self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        # self.verticalLayout_2.setObjectName("verticalLayout_2")
        # self.progressBar = QtWidgets.QProgressBar(Form)
        # self.progressBar.setGeometry(QtCore.QRect(10, 670, 1071, 23))
        # self.progressBar.setProperty("value", 24)
        # self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(490, 650, 200, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(260, 10, 67, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(800, 10, 81, 17))
        self.label_3.setObjectName("label_3")
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "选取视屏文件"))
        self.label.setText(_translate("Form", "已使用时间"))
        self.label_2.setText(_translate("Form", "原视频"))
        self.label_3.setText(_translate("Form", "处理后视频"))



    def on_click(self):
        videopath=QFileDialog.getOpenFileUrl()[0]
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.verticalLayoutWidget_2)
        self.player.setMedia(QMediaContent(videopath))  # 选取视频文件
        self.player.play()

        videopath = str(videopath).split('\'')[1].split('\\\\')[-1]
        # print(videopath)
        # Initialize the parameters
        confThreshold = 0.5  # Confidence threshold
        nmsThreshold = 0.4  # Non-maximum suppression threshold
        inpWidth = 416  # Width of network's input image
        inpHeight = 416  # Height of network's input image

        # parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
        # parser.add_argument('--image', help='Path to image file.')
        # parser.add_argument('--video', help='Path to video file.')
        # args = parser.parse_args()

        # Load names of classes
        classesFile = "voc.names"
        classes = None
        with open(classesFile, 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')

        # Give the configuration and weight files for the model and load the network using them.
        modelConfiguration = "yolov2-voc.cfg"
        modelWeights = "yolov2-voc.weights"
        # net = cv.dnn.readNet()
        net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

        # Get the names of the output layers
        def getOutputsNames(net):
            # Get the names of all the layers in the network
            layersNames = net.getLayerNames()
            # Get the names of the output layers, i.e. the layers with unconnected outputs
            return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        # Draw the predicted bounding box
        def drawPred(classId, conf, left, top, right, bottom):
            # Draw a bounding box.
            cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

            label = '%.2f' % conf

            # Get the label for the class name and its confidence
            if classes:
                assert (classId < len(classes))
                label = '%s:%s' % (classes[classId], label)

            # Display the label at the top of the bounding box
            labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            top = max(top, labelSize[1])
            cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])),
                         (left + round(1.5 * labelSize[0]), top + baseLine),
                         (255, 255, 255), cv.FILLED)
            cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

        # Remove the bounding boxes with low confidence using non-maxima suppression
        def postprocess(frame, outs):
            frameHeight = frame.shape[0]
            frameWidth = frame.shape[1]

            # Scan through all the bounding boxes output from the network and keep only the
            # ones with high confidence scores. Assign the box's class label as the class with the highest score.
            classIds = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    classId = np.argmax(scores)
                    confidence = scores[classId]
                    if confidence > confThreshold:
                        center_x = int(detection[0] * frameWidth)
                        center_y = int(detection[1] * frameHeight)
                        width = int(detection[2] * frameWidth)
                        height = int(detection[3] * frameHeight)
                        left = int(center_x - width / 2)
                        top = int(center_y - height / 2)
                        classIds.append(classId)
                        confidences.append(float(confidence))
                        boxes.append([left, top, width, height])

            # Perform non maximum suppression to eliminate redundant overlapping boxes with
            # lower confidences.
            indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
            for i in indices:
                i = i[0]
                box = boxes[i]
                left = box[0]
                top = box[1]
                width = box[2]
                height = box[3]
                drawPred(classIds[i], confidences[i], left, top, left + width, top + height)

        # Process inputs1

        # winName = 'Deep learning object detection in OpenCV'
        # cv.namedWindow(winName, cv.WINDOW_NORMAL)

        outputFile = "yolo_out_py.avi"

        # if (args.image):
        #     # Open the image file
        #     if not os.path.isfile(args.image):
        #         print("Input image file ", args.image, " doesn't exist")
        #         sys.exit(1)
        #     cap = cv.VideoCapture(args.image)
        #     outputFile = args.image[:-4] + '_yolo_out_py.jpg'
        # elif (args.video):
        #     # Open the video file
        #     if not os.path.isfile(args.video):
        #         print("Input video file ", args.video, " doesn't exist")
        #         sys.exit(1)
        #     cap = cv.VideoCapture(args.video)
        #     outputFile = args.video[:-4] + '_yolo_out_py.avi'
        # else:
        #     # Webcam input
        #     cap = cv.VideoCapture(0)
        cap = cv.VideoCapture(videopath)
        outputFile = videopath[:-4] + '_yolo_out_py.avi'
        # Get the video writer initialized to save the output video
        # if (not args.image):
        vid_writer = cv.VideoWriter(outputFile, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                                        (round(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                                         round(cap.get(cv.CAP_PROP_FRAME_HEIGHT))))
        starttime = time.time()
        while cv.waitKey(1) < 0:
            # 开始计时了

            print('计时: ', round(time.time() - starttime, 1), '秒')
            # get frame from the video
            hasFrame, frame = cap.read()

            # Stop the program if reached end of video
            if not hasFrame:
                self.label.setText("已使用时间:"+str(round(time.time() - starttime, 1))+'秒')    
                print("Done processing !!!")
                print("Output file is stored as ", outputFile)
                cv.waitKey(3000)
                # Release device
                cap.release()
                break

            # Create a 4D blob from a frame.
            blob = cv.dnn.blobFromImage(frame, 1 / 255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)

            # Sets the input to the network
            net.setInput(blob)

            # Runs the forward pass to get output of the output layers
            outs = net.forward(getOutputsNames(net))

            # Remove the bounding boxes with low confidence
            postprocess(frame, outs)

            # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
            t, _ = net.getPerfProfile()
            label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
            cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

            # Write the frame with the detection boxes
            # if (args.image):
            #     cv.imwrite(outputFile, frame.astype(np.uint8))
            # else:

            vid_writer.write(frame.astype(np.uint8))
            # cv.imshow(winName, frame)
        outputFile = QtCore.QUrl(outputFile)
        print(outputFile)
        self.player1 = QMediaPlayer()
        self.player1.setVideoOutput(self.verticalLayoutWidget)
        self.player1.setMedia(QMediaContent(outputFile))  # 选取视频文件
        self.player1.play()




class Main(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())


# if __name__=="__main__":
#     import sys
#     from PyQt5.QtGui import QIcon
#     app=QtWidgets.QApplication(sys.argv)
#     widget=QtWidgets.QWidget()
#     ui=Ui_Form()
#     ui.setupUi(widget)
#     widget.setWindowIcon(QIcon('web.png'))#增加icon图标
#     widget.show()
#     sys.exit(app.exec_())
