from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

class VAO(object):
    def __init__(self):
        self.index = GLuint(0)
        glGenVertexArrays(1, self.index)

    def __enter__(self):
        glBindVertexArray(self.index)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        glBindVertexArray(0)

class Program(object):
    def __init__(self):
        self.index = glCreateProgram()

    def __enter__(self):
        glUseProgram(self.index)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        glUseProgram(0)

    def attach(self, i):
        glAttachShader(self.index, i)

    def link(self):
        glLinkProgram(self.index)

class ShaderProgram(Program):
    def __init__(self, v, f):
        super(ShaderProgram, self).__init__()
        self.attach(v)
        self.attach(f)
        self.link()

