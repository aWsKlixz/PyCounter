import sys
from PyQt5.QtWidgets import QApplication

from app import CounterApp

def main():
    app = QApplication(sys.argv)

    window = CounterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()