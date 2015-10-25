from opengl_helpers import VAO

from OpenGL.arrays import vbo
from OpenGL.GL import *

import numpy as np
import random
from palette import PALETTE

from noise import snoise4

from scipy.interpolate import interp1d

def random_three_vector():
    phi = np.random.uniform(0, np.pi * 2)
    costheta = np.random.uniform(-1, 1)
    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return x, y, z

class Bar(object):
    def __init__(self):
        self.current = 0
        self.old = 0

    def update(self, n):
        self.old = self.current
        self.current = n

    def position(self):
        return self.current

    def velocity(self):
        return self.current - self.old

class Dot(object):
    def __init__(self, pos=2, vel=0, acc=-0.02):
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def update(self, bar):
        DAMPING = 0.99

        if self.pos <= bar.position():
            self.vel += bar.velocity()
            self.vel *= DAMPING
            self.pos = bar.position()
            self.pos += self.vel
        else:
            self.vel += self.acc
            self.vel *= DAMPING
            self.pos += self.vel

class Disruptor(object):
    def __init__(self):
        self.bar = Bar()
        self.dot = Dot()

    def update(self, height):
        self.bar.update(height)
        self.dot.update(self.bar)

    def position(self):
        return self.dot.pos

class PointSphere(object):
    def __init__(self, shader):
        self.phase = 0
        self.VERTICES = 10000
        self.vertices = np.array([
            random_three_vector() for i in range(self.VERTICES)
            ], dtype=np.float32)

        self.colors = np.array([
            random.choice(PALETTE) for i in range(self.VERTICES)
            ], dtype=np.float32)

        self.indices = np.array([
            i for i in range(self.VERTICES)
            ], dtype=np.uint32)
        self.vertex_bo = vbo.VBO(self.vertices)
        self.color_bo  = vbo.VBO(self.colors)
        self.index_bo = vbo.VBO(self.indices, target=GL_ELEMENT_ARRAY_BUFFER)

        self.disruptors = [Disruptor() for _ in range(self.VERTICES)]

        self.vao = VAO()
        with self.vao:
            with self.vertex_bo:
                v_position = glGetAttribLocation(shader.index, "v_position")
                glEnableVertexAttribArray(v_position)
                glVertexAttribPointer(v_position, 3, GL_FLOAT, False, 0, None)

            with self.color_bo:
                v_color = glGetAttribLocation(shader.index, "v_color")
                glEnableVertexAttribArray(v_color)
                glVertexAttribPointer(v_color, 4, GL_FLOAT, False, 0, None)

            self.index_bo.bind()

    def update(self, dt):
        self.phase += dt * 0.05
        for i, (x, y, z) in zip(self.disruptors, self.vertices):
            i.update(snoise4(x, y, z, self.phase) * 0.2 + 0.9)

        radii = np.array([
            i.position() for i in self.disruptors
            ], dtype=np.float32)

        data = np.transpose(np.transpose(self.vertices) * radii)
        with self.vertex_bo:
            self.vertex_bo.set_array(data)
            self.vertex_bo.copy_data()

    def draw(self):
        with self.vao:
            glDrawElements(GL_POINTS, self.indices.size, GL_UNSIGNED_INT, None)
