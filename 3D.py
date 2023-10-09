import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from math import *
from pygame.locals import *
import pygame.mouse
import numpy as np
import struct
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SPEED = 0.1
ROTATION_SPEED = 0.1
map_data = np.array([
    [0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 1, 1]
])
def fast_inverse_square_root(number):
    i = struct.unpack('i', struct.pack('f', number))[0]
    i = 0x5f3759df - (i >> 1)
    y = struct.unpack('f', struct.pack('i', i))[0]
    return y
pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
pygame.mouse.set_visible(False) 
mouse_captured = True
camera_x, camera_y, camera_z = 0, 0, -5
camera_yaw, camera_pitch = 0, 0
cube_colors = np.random.rand(len(map_data) * len(map_data[0]), 3)
cubes = []
for row in range(len(map_data)):
    for col in range(len(map_data[0])):
        if map_data[row][col] == 1:
            x = col * 2
            z = row * 2
            y = 0
            distances = fast_inverse_square_root((x - camera_x) ** 2 + (y - camera_y) ** 2 + (z - camera_z) ** 2)
            cubes.append({"x": x, "y": y, "z": z, "color": cube_colors[row * len(map_data[0]) + col], "distance": distances})
cubes.sort(key=lambda cube: cube["distance"], reverse=True)
def draw_cube(x, y, z, color):
    glBegin(GL_QUADS)
    vertices = [
        (-1, -1, -1),
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, 1, 1),
    ]
    faces = [
        (0, 1, 2, 3),  # Front face
        (3, 2, 6, 7),  # Right face
        (7, 6, 5, 4),  # Back face
        (4, 5, 1, 0),  # Left face
        (1, 5, 6, 2),  # Top face
        (4, 0, 3, 7),  # Bottom face
    ]
    for i, face in enumerate(faces):
        glNormal3fv(vertices[face[0]])  # Calculate normals for lighting
        glColor3fv(color)  # Set the color for this face
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()
for cube in cubes:
    x, y, z = cube["x"], cube["y"], cube["z"]
    color = cube["color"]
    glPushMatrix()
    glTranslatef(x, y, z)
    draw_cube(x, y, z, color)
    glPopMatrix()
pygame.mouse.set_pos(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mouse_captured = not mouse_captured
    keys = pygame.key.get_pressed()
    if keys[K_w]:
        camera_x -= SPEED * sin(radians(camera_yaw))
        camera_z += SPEED * cos(radians(camera_yaw))
    if keys[K_s]:
        camera_x += SPEED * sin(radians(camera_yaw))
        camera_z -= SPEED * cos(radians(camera_yaw))
    if keys[K_a]:
        camera_x += SPEED * cos(radians(camera_yaw))
        camera_z += SPEED * sin(radians(camera_yaw))
    if keys[K_d]:
        camera_x -= SPEED * cos(radians(camera_yaw))
        camera_z -= SPEED * sin(radians(camera_yaw))
    dx, dy = pygame.mouse.get_rel()
    camera_yaw += dx * ROTATION_SPEED
    camera_pitch += dy * ROTATION_SPEED
    camera_pitch = max(-90, min(90, camera_pitch))
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(camera_pitch, 1, 0, 0)
    glRotatef(camera_yaw, 0, 1, 0)
    glTranslatef(camera_x, camera_y, camera_z)
    if mouse_captured:
        pygame.mouse.set_pos(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE)
    for row in range(len(map_data)):
        for col in range(len(map_data[0])):
            if map_data[row][col] == 1:
                x = col * 2
                z = row * 2
                y = 0
                glPushMatrix()
                glTranslatef(x, y, z)
                draw_cube(x, y, z, cube_colors[row * len(map_data[0]) + col])
                glPopMatrix()
    pygame.display.flip()
    pygame.time.wait(10)
