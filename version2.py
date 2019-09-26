# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


import sys

import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
import time





confThreshold = 0.5  # Confidence threshold
nmsThreshold = 0.4  # Non-maximum suppression threshold
inpWidth = 416  # Width of network's input image
inpHeight = 416  # Height of network's input image
# Load names of classes
classesFile = "voc.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
    modelConfiguration = "yolov2-voc.cfg"
    modelWeights = "yolov2-voc.weights"
    net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
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
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([center_x,center_y,width,height])
                if classId ==3:
                    print([center_x,center_y],width,height,"船")
                indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
                for i in indices:
                    i = i[0]
                    box = boxes[i]
                    x = box[0]
                    y = box[1]
                    width = box[2]
                    height = box[3]


imageopath = "/home/eric/lib_work/pyqt5/000241.jpg"
# Open the image file
if not os.path.isfile(imageopath):
    print("Input image file ", imageopath, " doesn't exist")
    sys.exit(1)
cap = cv.imread(imageopath,1)
outputFile = 'yolo_out_py.jpg'
blob = cv.dnn.blobFromImage(cap, 1./255, (inpWidth, inpHeight))
net.setInput(blob)
outs = net.forward(getOutputsNames(net))
postprocess(cap, outs)
