from unittest import TestCase
import task3 as t3

framesNum = 500
delta = 0.1
precision = 1e-8


class TestPlanets(TestCase):
    def testVerle(self):
        check = True
        for t in range(framesNum):
            t3.verle(delta)
            t3.verleOdeint(delta, 2)
            frameError = 0
            for i in range(1, len(t3.particleList)):
                frameError += (abs(t3.positions[1][i].x - t3.positionsOde[1][i].x) +
                               abs(t3.positions[1][i].y - t3.positionsOde[1][i].y) +
                               abs(t3.positions[1][i].z - t3.positionsOde[1][i].z)) / \
                              ((t3.positionsOde[1][i].x + t3.positionsOde[1][i].y + t3.positionsOde[1][i].z) / 3.0)
            check = check and (frameError < precision)

        self.assertTrue(check)

    def testVerleThreads(self):
        check = True
        for t in range(framesNum):
            t3.verleThreads(delta)
            t3.verleOdeint(delta, 2)
            frameError = 0
            for i in range(1, len(t3.particleList)):
                frameError += (abs(t3.positions[1][i].x - t3.positionsOde[1][i].x) +
                               abs(t3.positions[1][i].y - t3.positionsOde[1][i].y) +
                               abs(t3.positions[1][i].z - t3.positionsOde[1][i].z)) / \
                              ((t3.positionsOde[1][i].x + t3.positionsOde[1][i].y + t3.positionsOde[1][i].z) / 3.0)
            check = check and (frameError < precision)

        self.assertTrue(check)

    def testVerleCython(self):
        check = True
        for t in range(framesNum):
            t3.cythonVerle.verle(delta, t3.particleList, t3.speeds, t3.speedups, t3.positions)
            t3.verleOdeint(delta, 2)
            frameError = 0
            for i in range(1, len(t3.particleList)):
                frameError += (abs(t3.positions[1][i].x - t3.positionsOde[1][i].x) +
                               abs(t3.positions[1][i].y - t3.positionsOde[1][i].y) +
                               abs(t3.positions[1][i].z - t3.positionsOde[1][i].z)) / \
                              ((t3.positionsOde[1][i].x + t3.positionsOde[1][i].y + t3.positionsOde[1][i].z) / 3.0)
            check = check and (frameError < precision)

        self.assertTrue(check)

    def testVerleOpenCL(self):
        check = True
        for t in range(100):
            t3.openclVerle.verle(delta, t3.particleList, t3.speeds, t3.speedups, t3.positions)
            t3.verleOdeint(delta, 2)
            frameError = 0
            for i in range(1, len(t3.particleList)):
                frameError += (abs(t3.positions[1][i].x - t3.positionsOde[1][i].x) +
                               abs(t3.positions[1][i].y - t3.positionsOde[1][i].y) +
                               abs(t3.positions[1][i].z - t3.positionsOde[1][i].z)) / \
                              ((t3.positionsOde[1][i].x + t3.positionsOde[1][i].y + t3.positionsOde[1][i].z) / 3.0)
            check = check and (frameError < precision)

        self.assertTrue(check)

'''
# вывод
if (t + 1) % 100 == 0:
    print("t = ", t, ", error = ", frameError)                      
'''
