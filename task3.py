import math
import random
import threading
from scipy.integrate import odeint
from multiprocessing import Process
import time
import copy
import cythonVerle
import openclVerle
import sys  # sys нужен для передачи argv в QApplication
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import QMainWindow


# import test

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Speed:
    def __init__(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w


class SpeedUp:
    def __init__(self, ax, ay, az):
        self.ax = ax
        self.ay = ay
        self.az = az


class Particle(Position, Speed, Color):
    def __init__(self, position, speed, color, mass, radius, lifetime):
        Position.__init__(self, position.x, position.y, position.z)
        Speed.__init__(self, speed.u, speed.v, speed.w)
        Color.__init__(self, color.r, color.g, color.b)

        self.mass = mass
        self.radius = radius / 1000
        self.lifetime = lifetime

k1 = 2e+12  # коэффициент для отображения данных
timerStep = 10
moment1 = 0
moment2 = 0
fulltime = 0
t = 0
G = 6.67408e-11
result = []
positions = [[], []]
speeds = [[], []]
speedups = [[], []]

positionsOde = [[], []]
speedsOde = [[], []]
speedupsOde = [[], []]

particleList = [Particle(Position(0, 0, 0), Speed(0, 0, 0), Color(1, 1, 0), 1.989e+30, 20, 2000000),  # Солнце
                Particle(Position(0, 5.791e+10, 0), Speed(47360, 0, 0), Color(1, 0, 1), 3.285e+23, 4, 2000000),  # Меркурий
                Particle(Position(0, 1.082e+11, 0), Speed(35020, 0, 0), Color(0, 1, 1), 4.869e+24, 7, 2000000),  # Венера
                Particle(Position(0, 1.496e+11, 0), Speed(29783, 0, 0), Color(0, 0, 1), 5.974e+24, 8, 2000000),  # Земля
                Particle(Position(0, 2.279e+11, 0), Speed(24100, 0, 0), Color(0, 1, 1), 6.419e+23, 6, 2000000),  # Марс
                Particle(Position(0, 7.78e+11, 0), Speed(13070, 0, 0), Color(0, 1, 0), 1.899e+27, 30, 2000000),  # Юпитер
                Particle(Position(0, 1.427e+12, 0), Speed(9690, 0, 0), Color(1, 0, 1), 5.685e+26, 20, 2000000),  # Сатурн
                Particle(Position(0, 2.871e+12, 0), Speed(6810, 0, 0), Color(1, 1, 1), 8.685e+25, 20, 2000000),  # Уран
                Particle(Position(0, 4.497e+12, 0), Speed(5430, 0, 0), Color(0, 0, 1), 1.024e+26, 20, 2000000)]  # Нептун

particleList1 = np.array(particleList, dtype=Particle)

for part in particleList:
    positions[0].append(Position(part.x, part.y, part.z))
    positions[1].append(Position(part.x, part.y, part.z))
    speeds[0].append(Speed(part.u, part.v, part.w))
    speeds[1].append(Speed(part.u, part.v, part.w))
    speedups[0].append(SpeedUp(0, 0, 0))
    speedups[1].append(SpeedUp(0, 0, 0))

    positionsOde[0].append(Position(part.x, part.y, part.z))
    positionsOde[1].append(Position(part.x, part.y, part.z))
    speedsOde[0].append(Speed(part.u, part.v, part.w))
    speedsOde[1].append(Speed(part.u, part.v, part.w))
    speedupsOde[0].append(SpeedUp(0, 0, 0))
    speedupsOde[1].append(SpeedUp(0, 0, 0))



def verle(delta):
    global particleList, speeds, speedups, positions

    for i in range(len(particleList)):
        speedups[0][i] = SpeedUp(speedups[1][i].ax, speedups[1][i].ay, speedups[1][i].az)
        for j in range(len(particleList)):
            speedups[1][i].ax = 0
            speedups[1][i].ay = 0
            speedups[1][i].az = 0
        for j in range(len(particleList)):
            if i != j:
                # ускорения

                distance = ((positions[0][j].x - positions[0][i].x) ** 2 +
                            (positions[0][j].y - positions[0][i].y) ** 2 +
                            (positions[0][j].z - positions[0][i].z) ** 2) ** 0.5
                if (distance - 1000) > 0:
                    speedups[1][i].ax += G * particleList[j].mass * (
                            positions[0][j].x - positions[0][i].x) / distance ** 3
                    speedups[1][i].ay += G * particleList[j].mass * (
                            positions[0][j].y - positions[0][i].y) / distance ** 3
                    speedups[1][i].az += G * particleList[j].mass * (
                            positions[0][j].z - positions[0][i].z) / distance ** 3

        # координаты
        positions[0][i] = Position(positions[1][i].x, positions[1][i].y, positions[1][i].z)
        positions[1][i].x = positions[0][i].x + speeds[0][i].u * delta + 0.5 * speedups[0][i].ax * delta ** 2
        positions[1][i].y = positions[0][i].y + speeds[0][i].v * delta + 0.5 * speedups[0][i].ay * delta ** 2
        positions[1][i].z = positions[0][i].z + speeds[0][i].w * delta + 0.5 * speedups[0][i].az * delta ** 2

        # скорости
        speeds[0][i] = Speed(speeds[1][i].u, speeds[1][i].v, speeds[1][i].w)
        speeds[1][i].u = speeds[0][i].u + 0.5 * (speedups[1][i].ax + speedups[0][i].ax) * delta
        speeds[1][i].v = speeds[0][i].v + 0.5 * (speedups[1][i].ay + speedups[0][i].ay) * delta
        speeds[1][i].w = speeds[0][i].w + 0.5 * (speedups[1][i].az + speedups[0][i].az) * delta

def verleOdeint(delta, purp):
    global particleList, speeds, speedups, positions, result, speedsOde, speedupsOde, positionsOde
    tGrid = np.linspace(0, 1 * delta, 2)

    N = len(particleList)

    def odeFun(y, t):
        system = []

        for i in range(N):
            system.append(y[3 * N + 3 * i])  # u
            system.append(y[3 * N + 3 * i + 1])  # v
            system.append(y[3 * N + 3 * i + 2])  # w

        for i in range(N):
            sum1 = 0
            sum2 = 0
            sum3 = 0
            for j in range(N):
                distance = ((y[3 * j] - y[3 * i]) ** 2 +
                            (y[3 * j + 1] - y[3 * i + 1]) ** 2 +
                            (y[3 * j + 2] - y[3 * i + 2]) ** 2) ** 0.5
                if i != j:
                    sum1 += G * particleList[j].mass * (y[3 * j] - y[3 * i]) / distance ** 3
                    sum2 += G * particleList[j].mass * (y[3 * j + 1] - y[3 * i + 1]) / distance ** 3
                    sum3 += G * particleList[j].mass * (y[3 * j + 2] - y[3 * i + 2]) / distance ** 3
            system.append(sum1)
            system.append(sum2)
            system.append(sum3)

        return system

    init = []

    if purp == 1: # для отображения
        for i in range(N):
            init.append(positions[1][i].x)
            init.append(positions[1][i].y)
            init.append(positions[1][i].z)
        for i in range(N):
            init.append(speeds[1][i].u)
            init.append(speeds[1][i].v)
            init.append(speeds[1][i].w)
        result = odeint(odeFun, init, tGrid)

        for i in range(N):
            positions[0][i] = Position(positions[1][i].x, positions[1][i].y, positions[1][i].z)
            speedups[0][i] = SpeedUp(speedups[1][i].ax, speedups[1][i].ay, speedups[1][i].az)
            positions[1][i].x = result[1, 3 * i]
            positions[1][i].y = result[1, 3 * i + 1]
            positions[1][i].z = result[1, 3 * i + 2]
            speeds[1][i].u = result[1, 3 * N + 3 * i]
            speeds[1][i].v = result[1, 3 * N + 3 * i + 1]
            speeds[1][i].w = result[1, 3 * N + 3 * i + 2]
    else: # подсчеты для тестов
        for i in range(N):
            init.append(positionsOde[1][i].x)
            init.append(positionsOde[1][i].y)
            init.append(positionsOde[1][i].z)
        for i in range(N):
            init.append(speedsOde[1][i].u)
            init.append(speedsOde[1][i].v)
            init.append(speedsOde[1][i].w)
        result = odeint(odeFun, init, tGrid)

        for i in range(N):
            positionsOde[0][i] = Position(positionsOde[1][i].x, positionsOde[1][i].y, positionsOde[1][i].z)
            speedupsOde[0][i] = SpeedUp(speedupsOde[1][i].ax, speedupsOde[1][i].ay, speedupsOde[1][i].az)
            positionsOde[1][i].x = result[1, 3 * i]
            positionsOde[1][i].y = result[1, 3 * i + 1]
            positionsOde[1][i].z = result[1, 3 * i + 2]
            speedsOde[1][i].u = result[1, 3 * N + 3 * i]
            speedsOde[1][i].v = result[1, 3 * N + 3 * i + 1]
            speedsOde[1][i].w = result[1, 3 * N + 3 * i + 2]


###############################################

def verleThreadPart1(i1, i2):
    global particleList, speeds, speedups, positions
    for i in range(i1, i2 + 1):
        speedups[0][i] = SpeedUp(speedups[1][i].ax, speedups[1][i].ay, speedups[1][i].az)
        for j in range(len(particleList)):
            speedups[1][i].ax = 0
            speedups[1][i].ay = 0
            speedups[1][i].az = 0
        for j in range(len(particleList)):
            if i != j:
                # ускорения

                distance = ((positions[0][j].x - positions[0][i].x) ** 2 +
                            (positions[0][j].y - positions[0][i].y) ** 2 +
                            (positions[0][j].z - positions[0][i].z) ** 2) ** 0.5

                speedups[1][i].ax += G * particleList[j].mass * (
                        positions[0][j].x - positions[0][i].x) / distance ** 3
                speedups[1][i].ay += G * particleList[j].mass * (
                        positions[0][j].y - positions[0][i].y) / distance ** 3
                speedups[1][i].az += G * particleList[j].mass * (
                        positions[0][j].z - positions[0][i].z) / distance ** 3


def verleThreadPart2(i1, i2, delta):
    global particleList, speeds, speedups, positions
    for i in range(i1, i2 + 1):
        # координаты
        positions[0][i] = Position(positions[1][i].x, positions[1][i].y, positions[1][i].z)
        positions[1][i].x = positions[0][i].x + speeds[0][i].u * delta + 0.5 * speedups[0][i].ax * delta ** 2
        positions[1][i].y = positions[0][i].y + speeds[0][i].v * delta + 0.5 * speedups[0][i].ay * delta ** 2
        positions[1][i].z = positions[0][i].z + speeds[0][i].w * delta + 0.5 * speedups[0][i].az * delta ** 2

        # скорости
        speeds[0][i] = Speed(speeds[1][i].u, speeds[1][i].v, speeds[1][i].w)
        speeds[1][i].u = speeds[0][i].u + 0.5 * (speedups[1][i].ax + speedups[0][i].ax) * delta
        speeds[1][i].v = speeds[0][i].v + 0.5 * (speedups[1][i].ay + speedups[0][i].ay) * delta
        speeds[1][i].w = speeds[0][i].w + 0.5 * (speedups[1][i].az + speedups[0][i].az) * delta

        particleList[i].x = positions[1][i].x
        particleList[i].y = positions[1][i].y
        particleList[i].z = positions[1][i].z
        particleList[i].u = speeds[1][i].u
        particleList[i].v = speeds[1][i].v
        particleList[i].w = speeds[1][i].w
        particleList[i].ax = speedups[1][i].ax
        particleList[i].ay = speedups[1][i].ay
        particleList[i].az = speedups[1][i].az


def verleThreads(delta):
    global t, particleList, speeds, speedups, positions, timerStep
    thrNum = 2
    block = int(len(particleList) / thrNum)

    # первый этап
    threads = []
    for i in range(thrNum - 1):
        thr = threading.Thread(target=verleThreadPart1, args=(i * block, i * block + block - 1,))
        threads.append(thr)
    # последнюю нить пускаем отдельно, если в остатке останутся элементы
    thr = threading.Thread(target=verleThreadPart1, args=((thrNum - 1) * block, (thrNum - 1) * block + block - 1 +
                                                          int(len(particleList) % thrNum), ))
    threads.append(thr)

    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()

    # второй этап
    threads = []
    for i in range(thrNum - 1):
        thr = threading.Thread(target=verleThreadPart2, args=(i * block, i * block + block - 1, delta, ))
        threads.append(thr)
    # последнюю нить пускаем отдельно, если в остатке останутся элементы
    thr = threading.Thread(target=verleThreadPart2, args=((thrNum - 1) * block, (thrNum - 1) * block + block - 1 +
                                                          int(len(particleList) % thrNum), delta,))
    threads.append(thr)

    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()

###############################################


class MainWindow(QMainWindow):
    def __init__(self):
        global timerStep
        super(MainWindow, self).__init__()

        uic.loadUi('test1.ui', self)
        self.GLWidget = glWidget(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.draw)
        self.timer.start(timerStep)

        self.button1.clicked.connect(self.addSphere)
        self.button2.clicked.connect(self.deleteSphere)
        self.closeButton.clicked.connect(self.close)
        self.slider_m.valueChanged.connect(self.sliderValueChange)

        self.initializeInput()

        # фиксация размеров, задание цвета фона
        self.setFixedSize(self.size())
        background_color = QColor()
        background_color.setNamedColor('#aee6cd')
        p = self.palette()
        p.setColor(self.backgroundRole(), background_color)
        self.setPalette(p)

        '''
        for i in range(1):
            self.addSphere()

        for i in range(9):
            self.deleteSphere()
        '''



    def initializeInput(self):
        global k1
        self.slider_m.setValue(random.randint(10, 1000))
        self.input_radius.setPlainText(str(random.randint(10, 100)))
        #self.input_lifetime.setPlainText(str(random.randint(1000, 10000)))
        self.input_lifetime.setPlainText(str(random.randint(100000, 1000000)))
        self.input_x.setPlainText(str(round(-0.5 + random.random(), 3) * 2*k1))
        self.input_y.setPlainText(str(round(-0.5 + random.random(), 3) * 2*k1))
        self.input_z.setPlainText(str(round(-0.5 + random.random(), 3) * 2*k1))
        self.input_u.setPlainText(str(round(-50000 + 100000 * random.random(), 3)))
        self.input_v.setPlainText(str(round(-50000 + 100000 * random.random(), 3)))
        self.input_w.setPlainText(str(round(-50000 + 100000 * random.random(), 3)))
        self.input_r.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))
        self.input_g.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))
        self.input_b.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))

    def sliderValueChange(self):
        self.input_m.setPlainText(str(self.slider_m.value()))  # + "e+21")

    def draw(self):
        self.timer.stop()
        global t, particleList, speeds, speedups, positions, timerStep, moment1, moment2, fulltime
        t += 1
        delta = 10000

        deleteNums = []
        for i in range(len(particleList)):
            particleList[i].lifetime -= timerStep
            if particleList[i].lifetime <= 0:
                deleteNums.append(i)

        deleteNums.sort(reverse=True)
        for i in deleteNums:
            del particleList[i]
            del positions[0][i]
            del positions[1][i]
            del speeds[0][i]
            del speeds[1][i]
            del speedups[0][i]
            del speedups[1][i]

        #'''
        if self.radio0.isChecked():
            verleOdeint(delta, 1)
        if self.radio1.isChecked():
            verle(delta)
        if self.radio2.isChecked():
            verleThreads(delta)
        if self.radio3.isChecked():
            cythonVerle.verle(delta, particleList, speeds, speedups, positions)
        if self.radio4.isChecked():
            openclVerle.verle(delta, particleList, speeds, speedups, positions)
        #'''

        # замеры времени
        '''
        moment1 = time.time()
        openclVerle.verle(delta, particleList, speeds, speedups, positions)
        moment2 = time.time()
        fulltime += moment2 - moment1
        if t % 50 == 0:
            print(str(fulltime / 5).replace('.', ','))
            self.close()
        '''

        self.output_count.setText(str(len(particleList)))
        self.output_time.setText(str(t))
        self.GLWidget.update()
        self.timer.start(timerStep)

    def addSphere(self):
        self.timer.stop()
        for i in range(100):
            global positions, speeds, speedups, particleList, timerStep
            x = float(self.input_x.toPlainText())
            y = float(self.input_y.toPlainText())
            z = float(self.input_z.toPlainText())
            u = float(self.input_u.toPlainText())
            v = float(self.input_v.toPlainText())
            w = float(self.input_w.toPlainText())
            r = float(self.input_r.toPlainText())
            g = float(self.input_g.toPlainText())
            b = float(self.input_b.toPlainText())
            mass = float(self.slider_m.value()) * 1.e+24
            radius = float(self.input_radius.toPlainText())
            lifetime = float(self.input_lifetime.toPlainText())

            particleList.append(Particle(Position(x, y, z), Speed(u, v, w), Color(r, g, b), mass, radius, lifetime))
            positions[0].append(Position(x, y, z))
            positions[1].append(Position(x, y, z))
            speeds[0].append(Speed(u, v, w))
            speeds[1].append(Speed(u, v, w))
            speedups[0].append(SpeedUp(0, 0, 0))
            speedups[1].append(SpeedUp(0, 0, 0))

            self.initializeInput()

        self.GLWidget.update()
        self.timer.start(timerStep)

    def deleteSphere(self):
        self.timer.stop()
        global timerStep
        if particleList:
            del particleList[len(particleList) - 1]
            del positions[0][len(particleList) - 1]
            del positions[1][len(particleList) - 1]
            del speeds[0][len(particleList) - 1]
            del speeds[1][len(particleList) - 1]
            del speedups[0][len(particleList) - 1]
            del speedups[1][len(particleList) - 1]
        self.GLWidget.update()
        self.timer.start(timerStep)


class glWidget(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(900, 900)
        self.move(0, 0)

    def initializeGL(self):
        glClearColor(0.1, 0.2, 0.3, 1.0)

    def resizeGL(self, width, height):
        # this tells openGL how many pixels it should be drawing into
        glViewport(0, 0, width, height)

    def paintGL(self):
        global k1
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        for i in range(len(particleList)):
            pos = Position(positions[1][i].x / k1, positions[1][i].y / k1, positions[1][i].z / k1)

            qobj = gluNewQuadric()
            gluQuadricDrawStyle(qobj, GLU_FILL)
            glTranslatef(pos.x, pos.y, pos.z)
            glColor3f(particleList[i].r, particleList[i].g, particleList[i].b)
            gluSphere(qobj, particleList[i].radius, 50, 50)
            gluDeleteQuadric(qobj)
            glTranslatef(-pos.x, -pos.y, -pos.z)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
