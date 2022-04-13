import asyncio
import torch
import matplotlib.pyplot as plt
import torchvision
import time
import threading

from pythonosc import dispatcher
from pythonosc import osc_server

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image


import time

use_gpu = True if torch.cuda.is_available() else False

def random_face(addr: str, *args) -> None:
    # print("[{0}] ~ {1}".format(addr, args))

    # start = time.time()
    global noise
    noise, _ = model.buildNoiseData(num_images)
    # end = time.time()

    # print("build noise data: {0:.3g}s".format(end-start))

def run_server(dispatch):
    server = osc_server.ThreadingOSCUDPServer(
        (ip, port), dispatch)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


# figure, ax = plt.subplots()
# print("ax", ax)

# plt.ion()
# plt.show()

num_images = 1

# # matplotlib draw loop
# while True:
#     plt.show()

#     figure.canvas.draw()
#     figure.canvas.flush_events()
        
#     time.sleep(0.042) # 24 fps

ip = "127.0.0.1"
port = 5005

model = None
noise = None

###### OpenGL stuff ######
def main() -> None:
    # initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(512, 512, "My OpenGL window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    #           positions    colors          texture coords
    quad = [   -1, -1, 0.0,  0.0, 0.0, 0.0,  0.0, 0.0,
                1, -1, 0.0,  0.0, 0.0, 0.0,  1.0, 0.0,
                1,  1, 0.0,  0.0, 0.0, 0.0,  1.0, 1.0,
               -1,  1, 0.0,  0.0, 0.0, 0.0,  0.0, 1.0]

    quad = np.array(quad, dtype = np.float32)

    indices = [0, 1, 2,
               2, 3, 0]

    indices = np.array(indices, dtype= np.uint32)

    print(quad.itemsize * len(quad))
    print(indices.itemsize * len(indices))
    print(quad.itemsize * 8)

    vertex_shader = """
    #version 330
    in layout(location = 0) vec3 position;
    in layout(location = 1) vec3 color;
    in layout(location = 2) vec2 inTexCoords;

    out vec2 outTexCoords;
    void main()
    {
        gl_Position = vec4(position, 1.0f);
        outTexCoords = inTexCoords;
    }
    """

    fragment_shader = """
    #version 330
    in vec2 outTexCoords;

    out vec4 outColor;
    uniform sampler2D samplerTex;
    void main()
    {
        outColor = texture(samplerTex, outTexCoords);
    }
    """
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, quad.itemsize * len(quad), quad, GL_STATIC_DRAW)

    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)

    #position = glGetAttribLocation(shader, "position")
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, quad.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    #color = glGetAttribLocation(shader, "color")
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, quad.itemsize * 8, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    #texture_coords = glGetAttribLocation(shader, "inTexCoords")
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, quad.itemsize * 8, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    glUseProgram(shader)

    glClearColor(0.2, 0.3, 0.2, 1.0)

    texture = glGenTextures(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()


        # start = time.time()
        # noise, _ = model.buildNoiseData(num_images)
        # end = time.time()

        # print("build noise data: {0:.3g}s".format(end-start))

        # with torch.no_grad():
        #     start = time.time()
        #     generated_images = model.test(noise)
        #     generated_images = generated_images[0]
        #     generated_images = np.asarray(generated_images).transpose()
        #     generated_images = np.rot90(generated_images)
        #     end = time.time()

        #     print("generate image: {0:.3g}s".format(end-start))
        # start = time.time()
        with torch.no_grad():
            global noise
            generated_images = model.test(noise)
            generated_images = generated_images[0]
            generated_images = np.asarray(generated_images).transpose()
            generated_images = np.rot90(generated_images)


        # end = time.time()
        # print("generate image: {0:.3g}s".format(end-start))


        glBindTexture(GL_TEXTURE_2D, texture)
        #texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        #texture filtering params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # image = Image.open("img.png")
        #img_data = np.array(list(image.getdata()), np.uint8)
        # flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        # img_data = flipped_image.convert("RGBA").tobytes()
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 512, 512, 0, GL_RGB, GL_FLOAT, generated_images)
        #print(image.width, image.height)
        

        glClear(GL_COLOR_BUFFER_BIT)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)


    glfw.terminate()

# init_main sets up all the osc/opengl coroutines and closes things properly
def init_main():
    # trained on high-quality celebrity faces "celebA" dataset
    # this model outputs 512 x 512 pixel images
    global model
    model = torch.hub.load('facebookresearch/pytorch_GAN_zoo:hub',
                           'PGAN', model_name='celebAHQ-512',
                           pretrained=True, useGPU=use_gpu)

    global noise
    noise, _ = model.buildNoiseData(num_images)


    # for i in range(10):
    #     random_face('jfldks')
    #     time.sleep(5)

    dispatch = dispatcher.Dispatcher()
    dispatch.map("/face", random_face)

    server = osc_server.ThreadingOSCUDPServer(
        (ip, port), dispatch)
    x = threading.Thread(target=server.serve_forever)
    x.start()

    print("past server start")

    main()

    server.server_close()
    print("shutting down...")

if __name__ == "__main__":
    init_main()
