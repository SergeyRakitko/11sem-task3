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

G = 6.67e-11

def verle(delta, particleList, speeds, speedups, positions):

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

        particleList[i].x = positions[1][i].x
        particleList[i].y = positions[1][i].y
        particleList[i].z = positions[1][i].z
        particleList[i].u = speeds[1][i].u
        particleList[i].v = speeds[1][i].v
        particleList[i].w = speeds[1][i].w
        particleList[i].ax = speedups[1][i].ax
        particleList[i].ay = speedups[1][i].ay
        particleList[i].az = speedups[1][i].az