from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QMainWindow, QLabel, QPushButton, QVBoxLayout

from widgets.timer import TimerWidget

class CounterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        w, h = 450, 150
        self.setWindowTitle('Counter App')
        self.setGeometry(100, 100, w, h)
        self.setFixedSize(w, h)

        central_widget = QWidget(self)

        main_layout = QHBoxLayout()
        
        counter_frame = QWidget(self)
        counter_layout = QVBoxLayout()
        self.timer_widget = TimerWidget(counter_frame)
        counter_layout.addWidget(self.timer_widget)
        counter_frame.setLayout(counter_layout)
        main_layout.addWidget(counter_frame)

        button_frame = QWidget(self)
        button_layout = QGridLayout()

        play_pause_button = QPushButton('Play/Pause', counter_frame)
        play_pause_button.clicked.connect(self.timer_widget.toggle)
        
        reset_button = QPushButton('Reset', counter_frame)
        reset_button.clicked.connect(self.timer_widget.reset)
        
        button_layout.addWidget(play_pause_button, 0, 0)
        button_layout.addWidget(reset_button, 0, 1)
        button_frame.setLayout(button_layout)
        main_layout.addWidget(button_frame)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)