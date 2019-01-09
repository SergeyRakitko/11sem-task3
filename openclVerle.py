#from __future__ import absolute_import, print_function
import pyopencl as cl
import numpy as np


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
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    mf = cl.mem_flags

    speeds_u_prev = np.asarray([])
    speeds_u_next = np.asarray([])
    speeds_v_prev = np.asarray([])
    speeds_v_next = np.asarray([])
    speeds_w_prev = np.asarray([])
    speeds_w_next = np.asarray([])

    speedups_x_prev = np.asarray([])
    speedups_x_next = np.asarray([])
    speedups_y_prev = np.asarray([])
    speedups_y_next = np.asarray([])
    speedups_z_prev = np.asarray([])
    speedups_z_next = np.asarray([])

    positions_x_prev = np.asarray([])
    positions_x_next = np.asarray([])
    positions_y_prev = np.asarray([])
    positions_y_next = np.asarray([])
    positions_z_prev = np.asarray([])
    positions_z_next = np.asarray([])

    massValues = np.asarray([])

    for i in range(len(particleList)):
        massValues = np.append(massValues, particleList[i].mass)

        speeds_u_prev = np.append(speeds_u_prev, speeds[0][i].u)
        speeds_u_next = np.append(speeds_u_next, speeds[1][i].u)
        speeds_v_prev = np.append(speeds_v_prev, speeds[0][i].v)
        speeds_v_next = np.append(speeds_v_next, speeds[1][i].v)
        speeds_w_prev = np.append(speeds_w_prev, speeds[0][i].w)
        speeds_w_next = np.append(speeds_w_next, speeds[1][i].w)

        speedups_x_prev = np.append(speedups_x_prev, speedups[0][i].ax)
        speedups_x_next = np.append(speedups_x_next, speedups[1][i].ax)
        speedups_y_prev = np.append(speedups_y_prev, speedups[0][i].ay)
        speedups_y_next = np.append(speedups_y_next, speedups[1][i].ay)
        speedups_z_prev = np.append(speedups_z_prev, speedups[0][i].az)
        speedups_z_next = np.append(speedups_z_next, speedups[1][i].az)

        positions_x_prev = np.append(positions_x_prev, positions[0][i].x)
        positions_x_next = np.append(positions_x_next, positions[1][i].x)
        positions_y_prev = np.append(positions_y_prev, positions[0][i].y)
        positions_y_next = np.append(positions_y_next, positions[1][i].y)
        positions_z_prev = np.append(positions_z_prev, positions[0][i].z)
        positions_z_next = np.append(positions_z_next, positions[1][i].z)



    speeds_u_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_u_prev)
    speeds_u_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_u_next)
    speeds_v_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_v_prev)
    speeds_v_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_v_next)
    speeds_w_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_w_prev)
    speeds_w_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speeds_w_next)

    speedups_x_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_x_prev)
    speedups_x_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_x_next)
    speedups_y_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_y_prev)
    speedups_y_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_y_next)
    speedups_z_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_z_prev)
    speedups_z_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=speedups_z_next)

    positions_x_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_x_prev)
    positions_x_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_x_next)
    positions_y_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_y_prev)
    positions_y_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_y_next)
    positions_z_prev1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_z_prev)
    positions_z_next1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=positions_z_next)

    massValues1 = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=massValues)

    prg = cl.Program(ctx, """ 
    __kernel void verle(__global float *speeds_u_prev1, __global float *speeds_u_next1,
                        __global float *speeds_v_prev1, __global float *speeds_v_next1,
                        __global float *speeds_w_prev1, __global float *speeds_w_next1,
                        __global float *speedups_x_prev1, __global float *speedups_x_next1, 
                        __global float *speedups_y_prev1, __global float *speedups_y_next1, 
                        __global float *speedups_z_prev1, __global float *speedups_z_next1,
                        __global float *positions_x_prev1, __global float *positions_x_next1, 
                        __global float *positions_y_prev1, __global float *positions_y_next1, 
                        __global float *positions_z_prev1, __global float *positions_z_next1,
                        __global float *massValues1)
    {
        int gid = get_global_id(0);
        int size = sizeof(massValues1) / sizeof(float);
        int i;
        float distance;
        float G = 6.67e-11;

        speedups_x_prev1[gid] = speedups_x_next1[gid];
        speedups_y_prev1[gid] = speedups_y_next1[gid];
        speedups_z_prev1[gid] = speedups_z_next1[gid];

        speedups_x_next1[gid] = 0;
        speedups_y_next1[gid] = 0;
        speedups_z_next1[gid] = 0;

        for (i = 0; i < size; i++) {
            if (i != gid) {

                distance = sqrt((positions_x_prev1[i] - positions_x_prev1[gid])*(positions_x_prev1[i] - positions_x_prev1[gid])+
                             (positions_y_prev1[i] - positions_y_prev1[gid]) * (positions_y_prev1[i] - positions_y_prev1[gid])+
                             (positions_x_prev1[i] - positions_z_prev1[gid]) * (positions_z_prev1[i] - positions_z_prev1[gid]));

                speedups_x_next1[i] += G * massValues1[i] * (positions_x_prev1[i] - positions_x_prev1[gid]) /
                    (distance * distance * distance);
                speedups_y_next1[i] += G * massValues1[i] * (positions_y_prev1[i] - positions_y_prev1[gid]) /
                    (distance * distance * distance);
                speedups_z_next1[i] += G * massValues1[i] * (positions_z_prev1[i] - positions_z_prev1[gid]) /
                    (distance * distance * distance);

            }
        }

    }
    """).build()

    prg.verle(queue, massValues.shape, None,
              speeds_u_prev1, speeds_u_next1, speeds_v_prev1, speeds_v_next1, speeds_w_prev1, speeds_w_next1,
              speedups_x_prev1, speedups_x_next1, speedups_y_prev1, speedups_y_next1, speedups_z_prev1, speedups_z_next1,
              positions_x_prev1, positions_x_next1, positions_y_prev1, positions_y_next1, positions_z_prev1, positions_z_next1,
              massValues1)

    cl.enqueue_copy(queue, speedups_x_next, speedups_x_next1)
    cl.enqueue_copy(queue, speedups_y_next, speedups_y_next1)
    cl.enqueue_copy(queue, speedups_z_next, speedups_z_next1)
    cl.enqueue_copy(queue, speedups_x_prev, speedups_x_prev1)
    cl.enqueue_copy(queue, speedups_y_prev, speedups_y_prev1)
    cl.enqueue_copy(queue, speedups_z_prev, speedups_z_prev1)


    for i in range(len(particleList)):
        speedups[0][i].ax = speedups_x_prev[i]
        speedups[0][i].ay = speedups_y_prev[i]
        speedups[0][i].az = speedups_z_prev[i]
        speedups[1][i].ax = speedups_x_next[i]
        speedups[1][i].ay = speedups_y_next[i]
        speedups[1][i].az = speedups_z_next[i]


    for i in range(len(particleList)):
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






    '''
    res_np = np.empty_like(a_np)
    cl.enqueue_copy(queue, res_np, res_g)

    speeds = speeds1.tolist()
    speedups = speedups1.tolist()
    positions = positions1.tolist()



----------------------------------------------------------------------------

    

----------------------------------------------------------------------------

    


----------------------------------------------------------------------------        

    /*                
        
        */
    '''