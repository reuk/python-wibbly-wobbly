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

        self.channels = 2

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=44100,
                input=True,
                stream_callback=self.audio_callback)

        self.stream.start_stream()

        self.audio_frame = np.array([[0, 0]])

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
        result = np.fromstring(in_data, dtype=np.float32)
        self.audio_frame = np.reshape(result, (frame_count, self.channels))
        return None, pyaudio.paContinue

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

