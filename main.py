# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 23:26:24 2020

@author: gabe
"""
from PyQt5 import QtWidgets
import sys
from keras.models import load_model
from PyQt5.QtWidgets import QMessageBox
import thsr_GUI

#考慮thread?

print('model loading...')
model = load_model('./model/cnn_model.hdf5')
print('loading end')

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = thsr_GUI.Ui_Dialog(model)

ui.setupUi(MainWindow) 
MainWindow.show()
msg = QMessageBox()
sys.exit(app.exec_())
