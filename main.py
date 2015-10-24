try:
    from AppKit import NSApp, NSApplication
except:
    pass

import cyglfw3 as glfw

from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy as np

import pyaudio
import wave

import pyrr

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
            ], dtype='f')

        self.colors = np.array([
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            (0, 1, 1),
            ], dtype='f')

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
            ], dtype=np.uint8)
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
            glVertexAttribPointer(v_color, 3, GL_FLOAT, False, 0, None)

            self.index_bo.bind()

    def draw(self):
        with self.vao:
            glDrawElements(GL_LINES, 24, GL_UNSIGNED_BYTE, None)

class WindowingContext(object):
    def __enter__(self):
        glfw.SetErrorCallback(self.error_callback)

        if not glfw.Init():
            exit()

        glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.WindowHint(glfw.SAMPLES, 4)
        glfw.WindowHint(glfw.RESIZABLE, True)

        self.size = (500, 500)
        self.window = glfw.CreateWindow(self.size[0], self.size[1], "")

        if not self.window:
            glfw.Terminate()
            exit()

        glfw.MakeContextCurrent(self.window)
        glfw.SwapInterval(1)

        glfw.SetKeyCallback(self.window, self.key_callback)
        glfw.SetFramebufferSizeCallback(self.window, self.resize_callback)

        self.previous_seconds = 0

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=2,
                rate=44100,
                output=True,
                stream_callback=self.audio_callback)

        self.stream.start_stream()

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()

        glfw.Terminate()

    def run(self):
        w, h = glfw.GetFramebufferSize(self.window)
        while not glfw.WindowShouldClose(self.window):
            ct = glfw.GetTime()
            dt = ct - self.previous_seconds
            self.previous_seconds = ct

            estimated_frame_rate = 60
            dt *= estimated_frame_rate

            self.update(dt)
            self.draw()

            glfw.SwapBuffers(self.window)
            glfw.PollEvents()

    def audio_callback(self, in_data, frame_count, time_info, status):
        data = np.zeros(frame_count)
        return (data, pyaudio.paContinue)

    def update(self, dt):
        pass

    def draw(self):
        pass

    def key_callback(self, window, key, scancode, action, mods):
        pass

    def resize_callback(self, window, w, h):
        self.size = (w, h)

    def error_callback(self, window, error, description):
        print error, description

def mag(v):
    return np.sqrt(np.vdot(v, v))

def normalize(v):
    return v / mag(v)

class CubeApp(WindowingContext):
    def __enter__(self):
        super(CubeApp, self).__enter__()

        VERTEX_SHADER = shaders.compileShader("""
        #version 330
        in vec3 v_position;
        in vec3 v_color;
        out vec3 f_color;
        uniform mat4 v_model;
        uniform mat4 v_view;
        uniform mat4 v_projection;
        void main() {
            gl_Position = v_projection * v_view * v_model * vec4(v_position, 1.0);
            f_color = v_color;
        }
        """, GL_VERTEX_SHADER)

        FRAGMENT_SHADER = shaders.compileShader("""
        #version 330
        in vec3 f_color;
        out vec4 frag_color;
        void main() {
            frag_color = vec4(f_color, 1.0);
        }
        """, GL_FRAGMENT_SHADER)

        self.shader = ShaderProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        self.cube = Cube(self.shader)

        self.time = 0

        return self

    def update(self, dt):
        self.time += dt

    def draw(self):
        eye = np.array([5, 5, 5], dtype=np.float32)
        target = np.array([0, 0, 0], dtype=np.float32)
        up = np.array([0, 1, 0], dtype=np.float32)

        forward = normalize(eye - target)
        side = normalize(np.cross(up, forward))
        up = normalize(np.cross(forward, side))

        view_matrix = np.matrix([
            [side[0],            up[0],            forward[0],            0.],
            [side[1],            up[1],            forward[1],            0.],
            [side[2],            up[2],            forward[2],            0.],
            [-np.dot(side, eye), -np.dot(up, eye), -np.dot(forward, eye), 1.],
            ], dtype=np.float32)

        aspect = self.size[0] / float(self.size[1])
        projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(60.0, aspect, 0.001, 100)

        scale = 2
        scale_matrix = pyrr.matrix44.create_from_scale(np.array([scale, scale, scale]))
        angle_matrix = pyrr.matrix44.create_from_x_rotation(self.time * 0.01)
        position_matrix = pyrr.matrix44.create_from_translation(np.array([0, 0, 0]))
        model_matrix = np.dot(np.dot(scale_matrix, angle_matrix), position_matrix)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        with self.shader:
            glUniformMatrix4fv(glGetUniformLocation(self.shader.index, "v_projection"),
                    1, False, projection_matrix)
            glUniformMatrix4fv(glGetUniformLocation(self.shader.index, "v_view"),
                    1, False, view_matrix)
            glUniformMatrix4fv(glGetUniformLocation(self.shader.index, "v_model"),
                    1, False, model_matrix)

            self.cube.draw()

    def resize_callback(self, window, w, h):
        super(CubeApp, self).resize_callback(window, w, h)
        glViewport(0, 0, w, h)

def main():
    with CubeApp() as ca:
        ca.run()

if __name__ == "__main__":
    main()
