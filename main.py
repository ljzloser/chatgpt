from PyQt5.QtCore import QTranslator

from MainWindow import MainWindow
from singleApplication import SingleApplication

if __name__ == '__main__':
    import sys
    import os
    import ctypes

    # 设置任务栏图标
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    app = SingleApplication(sys.argv)
    if not app.instanceRunning:
        window = MainWindow()
        app.mainWindow = window
        app.setQuitOnLastWindowClosed(False)
        # 加载中文翻译
        if os.path.exists('res/qt_zh_CN.qm'):
            translator = QTranslator()
            translator.load('res/qt_zh_CN.qm')
            app.installTranslator(translator)
            window.setDebug(debug=f'加载 qt_zh_CN.qm 翻译文件加载成功！', isShow=False, isLog=True)
        else:
            window.setDebug(debug='加载qt_zh_CN.qm 翻译文件加载失败！', isShow=True, isLog=True)

        # 加载样式表
        if os.path.exists('res/style.qss'):
            with open('res/style.qss', 'r', encoding='UTF-8') as f:
                app.setStyleSheet(f.read())
                window.setDebug(debug=f'加载 style.qss 样式表加载成功！', isShow=False, isLog=True)
        else:
            window.setDebug(debug='加载 style.qss 样式表加载失败！', isShow=True, isLog=True)
        try:
            # window.show()
            window.setDebug(debug='程序启动成功！', isShow=False, isLog=True)
        except Exception as e:
            window.setDebug(debug='程序启动失败！' + str(e), isShow=True, isLog=True)
        sys.exit(app.exec_())
    else:
        sys.exit(0)
