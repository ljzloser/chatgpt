from PyQt5.QtCore import QTextStream, QFileInfo, Qt
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox


class SingleApplication(QApplication):

    def __init__(self, *args, **kwargs):
        super(SingleApplication, self).__init__(*args, **kwargs)
        self.localServer = None
        self.mainWindow: QMainWindow
        self.instanceRunning = False
        # 一般来说是取引用程序名作为 localServer 的进程服务名
        # 目前程序的进程名是根据文件名来的，但是一旦用于更改了文件名，那么进程名就不准确了，
        # 所以通过文件名来判断是进程服务是不可靠的，应该写死在代码里
        self.serverName = QFileInfo(self.applicationFilePath()).fileName()
        self.initLocalConnection()

    def initLocalConnection(self):
        instanceRunning = False
        socket = QLocalSocket()
        # 将套接字连接至进程服务，参数即为进程服务名
        socket.connectToServer(self.serverName)
        # 若在500ms内连接至进程服务，说明进程服务已运行
        if socket.waitForConnected(500):
            instanceRunning = True

            # 其他处理，如：将启动参数发送到进程服务端
            stream = QTextStream(socket)
            args = self.arguments()
            if len(args) > 1:
                stream << args[-1]
            else:
                stream << ""
            stream.flush()
            socket.waitForBytesWritten()
        else:
            self.newLocalServer()
        socket.close()

    # 创建LocalServer
    def newLocalServer(self):
        self.localServer = QLocalServer()
        self.localServer.newConnection.connect(self.newLocalConnection)
        if not self.localServer.listen(self.serverName):
            # 此时监听失败，可能是程序崩溃时,残留进程服务导致的,移除之
            if self.localServer.serverError() == QLocalServer.AddressInUseError:
                QLocalServer.removeServer(self.serverName)  # 移除进程服务
                self.localServer.listen(self.serverName)  # 再次监听

    def newLocalConnection(self):
        # 监听进程服务，当有数据进来时，可以通过 nextPendingConnection() 获取套接字
        socket = self.localServer.nextPendingConnection()
        if socket is None:
            return
        socket.waitForReadyRead(1000)
        # 其他处理
        stream = QTextStream(socket)
        socket.close()
        if self.mainWindow is not None:
            # 当主窗口对象不为空时，说明有可能主窗口被隐藏了，所以需要将其展示在桌面，同时给予用户提示
            self.mainWindow.raise_()
            self.mainWindow.activateWindow()
            self.mainWindow.setWindowState((self.mainWindow.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.mainWindow.show()
            QMessageBox.warning(self.mainWindow, "警告", "程序已经启动！")
