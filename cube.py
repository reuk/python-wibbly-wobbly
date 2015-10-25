from opengl_helpers import VAO

from OpenGL.arrays import vbo
from OpenGL.GL import *

import numpy as np
import random
from palette import PALETTE

class Cube(object):
    def __init__(self, shader):
        self.vertices = np.array([
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1),
            ], dtype=np.float32)

        self.colors = np.array([
            random.choice(PALETTE) for i in self.vertices
            ], dtype=np.float32)

        self.indices = np.array([
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7),
            ], dtype=np.uint32)
        self.vertex_bo = vbo.VBO(self.vertices)
        self.color_bo  = vbo.VBO(self.colors)
        self.index_bo = vbo.VBO(self.indices, target=GL_ELEMENT_ARRAY_BUFFER)

        self.vao = VAO()
        with self.vao:
            v_position = glGetAttribLocation(shader.index, "v_position")
            glEnableVertexAttribArray(v_position)
            self.vertex_bo.bind()
            glVertexAttribPointer(v_position, 3, GL_FLOAT, False, 0, None)

            v_color = glGetAttribLocation(shader.index, "v_color")
            glEnableVertexAttribArray(v_color)
            self.color_bo.bind()
            glVertexAttribPointer(v_color, 4, GL_FLOAT, False, 0, None)

            self.index_bo.bind()

    def draw(self):
        with self.vao:
            glDrawElements(GL_LINES, self.indices.size, GL_UNSIGNED_INT, None)
