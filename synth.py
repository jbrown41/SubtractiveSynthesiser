import numpy as np
from PyQt5.QtCore import Qt,QByteArray, QIODevice, QThread, QObject, pyqtSignal,pyqtSlot,QIODevice 
from PyQt5.QtMultimedia import QAudioFormat, QAudioOutput 
from PyQt5.QtWidgets import QApplication, QWidget,QSlider,QPushButton, QMessageBox, QVBoxLayout,QHBoxLayout,QLabel
from PyQt5.QtGui import QPixmap
import sys
import mido
import random
import matplotlib.pyplot as pl
import Resonator as ResC

SAMPLE_RATE=32000
AUDIO_CHANS=1
SAMPLE_SIZE=16
CTRL_INTERVAL=100 #milliseconds of audio

class MidiPortReader(QObject):
    noteOn=pyqtSignal(int)
    noteVelocity=pyqtSignal(int)
    noteOff=pyqtSignal(int)
    def __init__(self):
        QObject.__init__(self)
        mido.set_backend(
            'mido.backends.rtmidi/LINUX_ALSA'
        )
        print(
            "Using MIDI APIs: {}".format(
                mido.backend.module.get_api_names()
            )
        )
        self.velocity=0
        self.state=0
    def listener(self):

        with mido.open_input(
            'pipes',
            virtual=True
        ) as mip:
            for mmsg in mip:
                print(mmsg.velocity) 
                print(mmsg.type)
                if mmsg.type=='note_on':
                    self.noteOn.emit(mmsg.note)
                elif mmsg.type=='note_off':
                    self.noteOff.emit(mmsg.note)
                self.noteVelocity.emit(mmsg.velocity)

class Generator(QIODevice):

    SAMPLES_PER_READ=1024

    def __init__(self,format,parent=None):
        self.format=format
        QIODevice.__init__(self,parent)
        self.data=QByteArray()
        self.state=0
        self.vel=0
        self.vol=0
        self.q=0
        self.d=0
    def start(self):
        self.open(QIODevice.ReadOnly)

    @pyqtSlot(int)
    def noteOn(self,d):
        self.state=1 
        f=(2**((d-69)/12))*440
        print(f) 
        self.resonator=ResC.Resonator(f,self.q,SAMPLE_RATE)
        print(self.voices) 

    @pyqtSlot(int)
    def noteVelocity(self,v):
        self.vel=v/100

    @pyqtSlot(int)
    def noteOff(self,s):
        print('note if off')
        self.state=0

    @pyqtSlot(int)
    def volSlide(self,volume):
        self.vol=volume/100

    @pyqtSlot(int)
    def qFactor(self,q):
        self.q=q
        print(q)

    def generate(self,NO_OF_SAMPLES):
        tone=np.zeros(NO_OF_SAMPLES)       
        for i in range(len(tone)):           
            tone[i]=self.resonator.filter()              
        tone=(self.vel*50*tone*self.state*self.vol).astype(np.int16) 
        return tone.tostring()
        
    def readData(self,bytes):
        if bytes>2*Generator.SAMPLES_PER_READ:
            bytes=2*Generator.SAMPLES_PER_READ
        return self.generate(bytes//2)

class Window(QWidget):
    volSlide=pyqtSignal(int)
    def __init__(self,parent=None):
        #UI
        QWidget.__init__(self,parent)
        self.create_UI(parent)
        #audio formatting
        format=QAudioFormat()
        format.setChannelCount(AUDIO_CHANS)
        format.setSampleRate(SAMPLE_RATE)
        format.setSampleSize(SAMPLE_SIZE)
        format.setCodec("audio/pcm")
        format.setByteOrder(
            QAudioFormat.LittleEndian
        )
        format.setSampleType(
            QAudioFormat.SignedInt
        )
        self.output=QAudioOutput(format,self)
        output_buffer_size=\
            int(2*SAMPLE_RATE \
                *CTRL_INTERVAL/1000)
        self.output.setBufferSize(
            output_buffer_size
        )
        self.generator=Generator(format,self)
        #THREADS
        self.midiListener=MidiPortReader()
        self.listenerThread=QThread()
        self.midiListener.moveToThread(
                self.listenerThread
        )
        self.listenerThread.started.connect(
                self.midiListener.listener
        )
        self.listenerThread.start()
        self.midiListener.noteOff.connect(self.generator.noteOff)
        self.midiListener.noteVelocity.connect(self.generator.noteVelocity)
        self.midiListener.noteOn.connect(self.generator.noteOn)
        self.volumeSlider.valueChanged.connect(self.generator.volSlide)
        self.qfacSlider.valueChanged.connect(self.generator.qFactor)
        self.generator.start()
        self.output.start(self.generator)

    def create_UI(self,parent):
        rockLabel=QLabel()
        rockLabel.setText("Let's ROCK!!!")
        volLabel=QLabel()
        volLabel.setText("Volume")
        self.volumeSlider=QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        qfacLabel=QLabel()
        qfacLabel.setText("Q-Factor")
        self.qfacSlider=QSlider(Qt.Horizontal)
        self.qfacSlider.setMinimum(0)
        self.qfacSlider.setMaximum(1000)
        self.qfacSlider.setValue(5000)
        self.quitButton=\
                QPushButton(self.tr('&Quit'))
        self.volSlide.emit(7)        
        self.lynch=QLabel()
        self.halfDown=QPushButton("+1")
        self.halfUp=QPushButton("-1")
        pixmap=QPixmap()
        pixmap.load('lynch2.jpeg')
        pixmap=pixmap.scaledToWidth(200)
        self.lynch.setPixmap(pixmap)
        vLayout=QVBoxLayout(self)
        h0Layout=QHBoxLayout()
        h0Layout.addWidget(rockLabel)
        h0Layout.addStretch(1)
        h0Layout.addWidget(self.lynch)
        vLayout.addLayout(h0Layout)
        hLayout=QHBoxLayout()
        hLayout.addWidget(volLabel)
        hLayout.addStretch(1)
        hLayout.addWidget(self.volumeSlider)
        vLayout.addLayout(hLayout)
        h2Layout=QHBoxLayout()
        h2Layout.addWidget(qfacLabel)
        h2Layout.addStretch(1)
        h2Layout.addWidget(self.qfacSlider)
        vLayout.addLayout(h2Layout)
        self.quitButton.clicked.connect(
                self.quitClicked
        )

    @pyqtSlot()
    def quitClicked(self):
        self.close()

if __name__== "__main__":
    app=QApplication(sys.argv)
    window=Window()
    window.show()
    sys.exit(app.exec_())

    
