import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import os
import time

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
ANCHO        = 1111
ALTO         = 600
SCREEN_W     = ANCHO
SCREEN_H     = ALTO
FPS          = 60
GRAVITY      = 0.85
JUMP_FORCE   = -13
PLAYER_SPEED = 4
CAMERA_DEAD  = SCREEN_W // 3
ENEMY_W      = 36
ENEMY_H      = 42
PLAYER_W     = 50
PLAYER_H     = 100
jugador_invencible = 0
carpeta = os.path.dirname(os.path.abspath(__file__))
jug_img_walk1 = None
jug_img_walk2 = None
jug_anim_tick  = 0
jug_anim_frame = 0

# ══════════════════════════════════════════════════════════════════════════════
#  AUDIO
# ══════════════════════════════════════════════════════════════════════════════
musica_activa = True

def reproducir_cancion():
    pygame.mixer.init()
    audio = os.path.join(carpeta, "musica.mp3")  
    pygame.mixer.music.stop()
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play(-1)

def toggle_musica():
    global musica_activa
    musica_activa = not musica_activa
    if musica_activa:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDAD — cargar imagen
# ══════════════════════════════════════════════════════════════════════════════
def cargar_imagen(path, w=None, h=None):
    """Carga imagen con PIL y la convierte a PhotoImage. Retorna None si falla."""
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    if w and h:
        img = img.resize((w, h), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# ══════════════════════════════════════════════════════════════════════════════
#  CÁMARA — variables globales 
# ══════════════════════════════════════════════════════════════════════════════
cam_x           = 0
cam_level_width = 0

def inicializar_camara(level_width):
    global cam_x, cam_level_width
    cam_x           = 0
    cam_level_width = level_width

def actualizar_camara(player_x):
    global cam_x
    target = player_x - CAMERA_DEAD
    cam_x  = max(0, min(target, cam_level_width - SCREEN_W))

def camara_wx(world_x):
    #Convierte coordenada de mundo a coordenada de pantalla.
    return world_x - cam_x

# ══════════════════════════════════════════════════════════════════════════════
#  NIVEL — variables globales de medidas
# ══════════════════════════════════════════════════════════════════════════════
nivel_width    = 1870
nivel_bg       = None
nivel_img_plat = None

# Suelo: lista (x, y, ancho, alto)
fijo_floor = [
    (0, 540, 3200, 60),
]

fijo_enemigos = [ #(x, y, donde va a la izquierda, donde va a la derecha)
    (500,  540, 350,  750),
    (1200, 540, 1150, 1400),
    (1500, 430, 1400, 1700),
]

fijo_enemigos2 = [
    (800, 540, 700, 900),
    (200, 540, 100, 300)

]
# Plataformas: lista (x, y, ancho, alto)
fijo_platforms = [
    (400, 290, 200, 20),
    (1400, 340, 200, 20),

]

# Escaleras: lista (x, y, ancho, alto)
fijo_ladders = [
    (360,  300, 40, 240),
    (1360, 350, 40, 190),
    (2700, 300, 40, 220),
]

# Meta: (x, y, ancho, alto)
fijo_meta = (1825, 350, 40, 80)

# Spawn del jugador
fijo_spawn_x = 80
fijo_spawn_y = 540

#para nivel fijo
nivel_platforms = []
nivel_ladders   = []
nivel_spawn_x   = 0
nivel_spawn_y   = 0
nivel_meta      = (0, 0, 0, 0)
datos_enemigos  = []
datos_enemigos2 = []
nivel_floor = [(0, 540, 8000, 60)]

def inicializar_nivel():
    global nivel_bg, nivel_img_plat
    nivel_bg       = cargar_imagen(os.path.join(carpeta, "fondo_ingame.png"))
    nivel_img_plat = cargar_imagen(os.path.join(carpeta, "plataforma.png"), 220, 130)

# ══════════════════════════════════════════════════════════════════════════════
#  JUGADOR — variables globales simples
# ══════════════════════════════════════════════════════════════════════════════
jug_x         = 0.0
jug_y         = 0.0
jug_vx        = 0.0
jug_vy        = 0.0
jug_on_ground = False
jug_on_ladder = False
jug_facing    = 1
jug_lives     = 3
jug_score     = 0
jug_alive     = True
jug_img       = None
musica_ganar = None

def cargar_nivel_fijo():
    global nivel_platforms, nivel_ladders, nivel_spawn_x
    global nivel_spawn_y, nivel_meta, datos_enemigos, datos_enemigos2
    nivel_platforms = fijo_platforms[:]
    nivel_ladders   = fijo_ladders[:]
    nivel_spawn_x   = fijo_spawn_x
    nivel_spawn_y   = fijo_spawn_y
    nivel_meta      = fijo_meta
    datos_enemigos  = fijo_enemigos[:]
    datos_enemigos2 = fijo_enemigos2[:]

def inicializar_jugador():
    global jug_x, jug_y, jug_vx, jug_vy, jug_on_ground, jug_on_ladder
    global jug_facing, jug_lives, jug_score, jug_alive, jug_img, jug_img_walk1, jug_img_walk2, jug_img_walk1_izq, jug_img_walk2_izq
    jug_x         = float(nivel_spawn_x)
    jug_y         = float(nivel_spawn_y - PLAYER_H)
    jug_vx        = 0.0
    jug_vy        = 0.0
    jug_on_ground = False
    jug_on_ladder = False
    jug_facing    = 1
    jug_lives     = 3
    jug_score     = 0
    jug_alive     = True
    jug_img = cargar_imagen(os.path.join(carpeta, "pistonbot_original.png"), PLAYER_W, PLAYER_H)
    jug_img_walk1 = cargar_imagen(os.path.join(carpeta, "corriendo1.png"), PLAYER_W, PLAYER_H)
    jug_img_walk2 = cargar_imagen(os.path.join(carpeta, "corriendo2.png"), PLAYER_W, PLAYER_H)
    jug_img_walk1_izq = cargar_imagen(os.path.join(carpeta, "corriendo1izq.png"), PLAYER_W, PLAYER_H)
    jug_img_walk2_izq = cargar_imagen(os.path.join(carpeta, "corriendo2izq.png"), PLAYER_W, PLAYER_H)    

def respawnear_jugador():
    global jug_x, jug_y, jug_vx, jug_vy, jug_on_ground, jug_on_ladder, jug_alive
    jug_x         = float(nivel_spawn_x)
    jug_y         = float(nivel_spawn_y - PLAYER_H)
    jug_vx        = 0.0
    jug_vy        = 0.0
    jug_on_ground = False
    jug_on_ladder = False
    jug_alive     = True

def herir_jugador():
    global jug_lives, jug_alive, jugador_invencible
    if jugador_invencible > 0:
        return
    jug_lives -= 1
    jug_alive  = jug_lives > 0
    jugador_invencible = 60

def manejar_input(): #defino l que sucede con
    global jug_vx, jug_vy, jug_facing, jug_on_ground
    jug_vx = 0
    if tecla_a or tecla_left:
        jug_vx     = -PLAYER_SPEED
        jug_facing = -1
    if tecla_d or tecla_right:
        jug_vx     =  PLAYER_SPEED
        jug_facing =  1
    if (tecla_space or tecla_w) and jug_on_ground and not jug_on_ladder:
        jug_vy        = JUMP_FORCE
        jug_on_ground = False
    if jug_on_ladder:
        jug_vy = 0
        if tecla_w or tecla_up:
            jug_vy = -PLAYER_SPEED
        if tecla_space:
            jug_vy = -PLAYER_SPEED
        if tecla_s or tecla_down:
            jug_vy =  PLAYER_SPEED

def overlap_jug(rx, ry, rw, rh): # hitbox
    
    margen_x = 10
    margen_y = 10
    px1 = jug_x + margen_x
    py1 = jug_y + margen_y
    px2 = jug_x + PLAYER_W - margen_x
    py2 = jug_y + PLAYER_H - margen_y
    return px2 > rx and px1 < rx + rw and py2 > ry and py1 < ry + rh

def resolver_x_jugador(todas):
    global jug_x, jug_vx
    for px, py, pw, ph in todas:
        if overlap_jug(px, py, pw, ph):
            if jug_vx > 0:
                jug_x = px - PLAYER_W
            else:
                jug_x = px + pw
            jug_vx = 0

def resolver_y_jugador(todas):
    global jug_y, jug_vy, jug_on_ground
    margen_y = 10
    for px, py, pw, ph in todas:
        if overlap_jug(px, py, pw, ph):
            if jug_vy >= 0:
                jug_y         = py - PLAYER_H + margen_y
                jug_vy        = 0
                jug_on_ground = True
            else:
                jug_y  = py + ph
                jug_vy = 0

def actualizar_jugador(todas):
    global jug_x, jug_y, jug_vx, jug_vy, jug_on_ground, jug_on_ladder

    # Verificar escalera
    cx = jug_x + PLAYER_W / 2
    jug_on_ladder = False
    for lx, ly, lw, lh in nivel_ladders:
        if lx <= cx <= lx + lw and jug_y + PLAYER_H > ly and jug_y < ly + lh:
            jug_on_ladder = True
            break

    manejar_input()

    if not jug_on_ladder:
        jug_vy = min(jug_vy + GRAVITY, 20)

    jug_x += jug_vx
    resolver_x_jugador(todas)

    jug_on_ground = False
    jug_y += jug_vy
    resolver_y_jugador(todas)

    jug_x = max(0.0, min(jug_x, nivel_width - PLAYER_W))

    if jug_y > SCREEN_H + 300:
        herir_jugador()

# ══════════════════════════════════════════════════════════════════════════════
#  ENEMIGOS 
# ══════════════════════════════════════════════════════════════════════════════
en_x      = []
en_y      = []
en_vx     = []
en_vy     = []
en_left   = []
en_right  = []
en_alive  = []
en_img_der = None
en_img_izq = None

#enemigo 2 
en2_x      = []
en2_y      = []
en2_vx     = []
en2_vy     = []
en2_left   = []
en2_right  = []
en2_alive  = []
en2_img_der = None
en2_img_izq = None
EN2_W = 60   
EN2_H = 70

def inicializar_enemigos():
    global en_x, en_y, en_vx, en_vy, en_left, en_right, en_alive, en_img_der, en_img_izq 
    global en2_x, en2_y, en2_vx, en2_vy, en2_left, en2_right, en2_alive, en2_img_der, en2_img_izq
    
    en_x     = []
    en_y     = []
    en_vx    = []
    en_vy    = []
    en_left  = []
    en_right = []
    en_alive = []
    for x, y, left, right in datos_enemigos:
        en_x.append(float(x))
        en_y.append(float(y - ENEMY_H))
        en_vx.append(1.5)
        en_vy.append(0.0)
        en_left.append(left)
        en_right.append(right)
        en_alive.append(True)
    en_img_der = cargar_imagen(os.path.join(carpeta, "enemigo_moving.png"), ENEMY_W, ENEMY_H)
    en_img_izq = cargar_imagen(os.path.join(carpeta, "enemigo_standingder.png"), ENEMY_W, ENEMY_H)

def inicializar_enemigos2():
    global en2_x, en2_y, en2_vx, en2_vy, en2_left, en2_right, en2_alive
    global en2_img_der, en2_img_izq
    en2_x     = []
    en2_y     = []
    en2_vx    = []
    en2_vy    = []
    en2_left  = []
    en2_right = []
    en2_alive = []
    for x, y, left, right in datos_enemigos2:   # <- datos_enemigos2
        en2_x.append(float(x))
        en2_y.append(float(y - EN2_H))
        en2_vx.append(1.0)
        en2_vy.append(0.0)
        en2_left.append(left)
        en2_right.append(right)
        en2_alive.append(True)
    en2_img_der = cargar_imagen(os.path.join(carpeta, "enemigo2der.png"), EN2_W, EN2_H)
    en2_img_izq = cargar_imagen(os.path.join(carpeta, "enemigo2izq.png"), EN2_W, EN2_H)


def actualizar_enemigos(todas):
    for i in range(len(en_x)):
        if not en_alive[i]:
            continue
        en_x[i] += en_vx[i]
        if en_x[i] <= en_left[i] or en_x[i] + ENEMY_W >= en_right[i]:
            en_vx[i] *= -1
        en_vy[i] = min(en_vy[i] + GRAVITY, 20)
        en_y[i]  += en_vy[i]
        for px, py, pw, ph in todas:
            if (en_x[i] + ENEMY_W > px and en_x[i] < px + pw and en_vy[i] >= 0 and en_y[i] + ENEMY_H >= py and en_y[i] + ENEMY_H <= py + ph + 12):
                en_y[i]  = py - ENEMY_H
                en_vy[i] = 0

def actualizar_enemigos2(todas):
    for i in range(len(en2_x)):
        if not en2_alive[i]:
            continue
        en2_x[i] += en2_vx[i]
        if en2_x[i] <= en2_left[i] or en2_x[i] + EN2_W >= en2_right[i]:
            en2_vx[i] *= -1
        en2_vy[i] = min(en2_vy[i] + GRAVITY, 20)
        en2_y[i]  += en2_vy[i]
        for px, py, pw, ph in todas:
            if (en2_x[i] + EN2_W > px and en2_x[i] < px + pw and en2_vy[i] >= 0 and en2_y[i] + EN2_H >= py and en2_y[i] + EN2_H <= py + ph + 12):
                en2_y[i]  = py - EN2_H
                en2_vy[i] = 0

# ══════════════════════════════════════════════════════════════════════════════
#  TECLAS — variables globales simples
# ══════════════════════════════════════════════════════════════════════════════
tecla_a     = False
tecla_d     = False
tecla_w     = False
tecla_s     = False
tecla_space = False
tecla_up = False
tecla_down = False
tecla_right = False
tecla_left = False

# ══════════════════════════════════════════════════════════════════════════════
#  COLISIONES
# ══════════════════════════════════════════════════════════════════════════════
def verificar_colision_enemigos():
    global jug_vy, jug_score
    margen_x = 10
    margen_y = 10
    jx1 = jug_x + margen_x
    jy1 = jug_y + margen_y
    jx2 = jug_x + PLAYER_W - margen_x
    jy2 = jug_y + PLAYER_H - margen_y
    for i in range(len(en_x)):
        if not en_alive[i]:
            continue
        ex1 = en_x[i]
        ey1 = en_y[i]
        ex2 = en_x[i] + ENEMY_W
        ey2 = en_y[i] + ENEMY_H
        if jx2 > ex1 and jx1 < ex2 and jy2 > ey1 and jy1 < ey2:
            if jug_vy > 0 and jy2 - ey1 < 20:
                en_alive[i]  = False
                jug_vy       = JUMP_FORCE * 0.6
                jug_score   += 100
            else:
                herir_jugador()
                return
            
def verificar_colision_enemigos2():
    global jug_vy, jug_score
    margen_x = 10
    margen_y = 10
    jx1 = jug_x + margen_x
    jy1 = jug_y + margen_y
    jx2 = jug_x + PLAYER_W - margen_x
    jy2 = jug_y + PLAYER_H - margen_y
    for i in range(len(en2_x)):        # <- en2_x
        if not en2_alive[i]:           # <- en2_alive
            continue
        ex1 = en2_x[i]
        ey1 = en2_y[i]
        ex2 = en2_x[i] + EN2_W
        ey2 = en2_y[i] + EN2_H
        if jx2 > ex1 and jx1 < ex2 and jy2 > ey1 and jy1 < ey2:
            if jug_vy > 0 and jy2 - ey1 < 20:
                en2_alive[i]  = False  # <- en2_alive
                jug_vy        = JUMP_FORCE * 0.6
                jug_score    += 150
            else:
                herir_jugador()
                return

def verificar_meta():
    gx, gy, gw, gh = nivel_meta
    return (jug_x + PLAYER_W > gx and jug_x < gx + gw and
            jug_y + PLAYER_H > gy and jug_y < gy + gh)

# ══════════════════════════════════════════════════════════════════════════════
#  DIBUJO
# ══════════════════════════════════════════════════════════════════════════════
def dibujar_juego(canvas):
    global jug_anim_tick, jug_anim_frame
    canvas.delete("all")

    # ── Fondo ────────────────────────────────────────────────────────────────
    if nivel_bg:
        canvas.create_image(camara_wx(0), 0, anchor="nw", image=nivel_bg)
    else:
        canvas.create_rectangle(0, 0, SCREEN_W, SCREEN_H, fill="#4a7fd4", outline="")

    # ── Suelo ─────────────────────────────────────────────────────────────────
    for px, py, pw, ph in fijo_floor:
        sx = camara_wx(px)
       

    # ── Plataformas ───────────────────────────────────────────────────────────
    for px, py, pw, ph in nivel_platforms:
        sx = camara_wx(px)
        if sx + pw < 0 or sx > SCREEN_W:
            continue
        if nivel_img_plat:
            canvas.create_image(sx, py, anchor="nw", image=nivel_img_plat)
        else:
            canvas.create_rectangle(sx, py, sx + pw, py + ph, fill="#3a7d1e", outline="#1a3a0a")

    # ── Escaleras ─────────────────────────────────────────────────────────────
    for lx, ly, lw, lh in nivel_ladders:
        sx = camara_wx(lx)
        if sx + lw < 0 or sx > SCREEN_W:
            continue
        canvas.create_rectangle(sx + 4, ly, sx + 10, ly + lh, fill="#964B00", outline="")
        canvas.create_rectangle(sx + lw - 10, ly, sx + lw - 4, ly + lh, fill="#964B00", outline="")
        for sy in range(ly, ly + lh, 16):
            canvas.create_rectangle(sx + 4, sy, sx + lw - 4, sy + 5, fill="#964B00", outline="")

    # ── Meta ──────────────────────────────────────────────────────────────────
    gx, gy, gw, gh = nivel_meta
    sx = camara_wx(gx)
    canvas.create_rectangle(sx, gy, sx + gw, gy + gh, fill="#ffd700", outline="#aa8800", width=2)
    canvas.create_text(sx + gw // 2, gy - 14, text="META",
                       fill="#FFD700", font=("Perfect DOS VGA 437 Win", 10, "bold"))

    # ── Enemigos ──────────────────────────────────────────────────────────────
    for i in range(len(en_x)):
        if not en_alive[i]:
            continue
        sx = camara_wx(en_x[i])
        if sx + ENEMY_W < 0 or sx > SCREEN_W:
            continue
        if en_vx[i] > 0 and en_img_der:
            canvas.create_image(sx, en_y[i], anchor="nw", image=en_img_der)
        elif en_vx[i] <= 0 and en_img_izq:
            canvas.create_image(sx, en_y[i], anchor="nw", image=en_img_izq)
        else:
            canvas.create_rectangle(sx, en_y[i], sx + ENEMY_W, en_y[i] + ENEMY_H, fill="#6a006a", outline="#330033")

    for i in range(len(en2_x)):
        if not en2_alive[i]:
            continue
        sx = camara_wx(en2_x[i])
        if sx + EN2_W < 0 or sx > SCREEN_W:
            continue
        if en2_vx[i] > 0 and en2_img_der:
            canvas.create_image(sx, en2_y[i], anchor="nw", image=en2_img_der)
        elif en2_vx[i] <= 0 and en2_img_izq:
            canvas.create_image(sx, en2_y[i], anchor="nw", image=en2_img_izq)
        else:
            canvas.create_rectangle(sx, en2_y[i], sx + EN2_W, en2_y[i] + EN2_H, fill="#003366", outline="#0066cc")   

    # ── Jugador ───────────────────────────────────────────────────────────────
    sx = camara_wx(jug_x)

# Animacion
    if jug_vx != 0:
        jug_anim_tick += 1
        if jug_anim_tick >= 10:
            jug_anim_tick  = 0
            jug_anim_frame = 1 - jug_anim_frame
    else:
        jug_anim_tick  = 0    
        jug_anim_frame = 0    

# Elegir imagen segun estado
    if jug_vx > 0:
        if jug_anim_frame == 0:
            img = jug_img_walk1
        else:
            img = jug_img_walk2
    elif jug_vx < 0:
        if jug_anim_frame == 0:
            img = jug_img_walk1_izq
        else:
            img = jug_img_walk2_izq
    else:
        img = jug_img

    if img:
        canvas.create_image(sx, jug_y, anchor="nw", image=img)
    else:
        canvas.create_rectangle(sx, jug_y + 18, sx + PLAYER_W, jug_y + PLAYER_H, fill="#cc3300", outline="#881100")

    # ── HUD ───────────────────────────────────────────────────────────────────
    canvas.create_rectangle(8, 8, 340, 40, fill="#000000", outline="")
    corazones = "♥ " * jug_lives
    canvas.create_text(14, 24, anchor="w", text=f"{corazones}  Pts: {jug_score}", fill="#FFD700", font=("Perfect DOS VGA 437 Win", 13, "bold"))
    canvas.create_text(SCREEN_W - 8, SCREEN_H - 8, anchor="se", text="A/D=mover  W=saltar/subir  S=bajar  Espacio=saltar  ESC=salir", fill="#ffffff", font=("Courier", 8))

def guardar_puntaje(nombre, puntos):
    ruta = os.path.join(carpeta, "puntajes.txt")
# Leer puntajes existentes
    puntajes = []
    if os.path.exists(ruta):
        archivo = open(ruta, "r")
        for linea in archivo:
            linea = linea.strip()
            if linea:
                partes = linea.split(",")
                puntajes.append((partes[0], int(partes[1])))
        archivo.close()
    # Agregar el nuevo
    puntajes.append((nombre, puntos))
    # Ordenar y guardar solo top 5
    puntajes.sort(key=lambda x: x[1], reverse=True)
    puntajes = puntajes[:5]
    archivo = open(ruta, "w")
    for n, p in puntajes:
        archivo.write(f"{n},{p}\n")
    archivo.close()

def ventana_ganar(ventana_padre):
  
    pygame.mixer.init()
    pygame.mixer.music.stop()
    cancion = os.path.join(carpeta, "cancion_win.mp3")
    if os.path.exists(cancion):
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play()
    win = tk.Toplevel(ventana_padre)
    win.title ("Victoria")
    win.geometry("600x400")
    tk.Label(win, text= "Ganaste", font= ("Perfect DOS VGA 437 Win", 20)).pack(pady=10)
    tk.Label(win, text=f"Puntaje: {jug_score}", font=("Perfect DOS VGA 437 Win", 14)).pack(pady=5)
 

    tk.Label(win, text="Ingresa tu nombre:", font=("Perfect DOS VGA 437 Win", 12)).pack(pady=5)
    
    entrada = tk.Entry(win, font=("Perfect DOS VGA 437 Win", 12), width=20)
    entrada.pack(pady=5)
    win.protocol("WM_DELETE_WINDOW", lambda: [reproducir_cancion(), win.destroy()])

    def guardar():
        nombre = entrada.get().strip()
        if nombre == "":
            nombre = "Jugador"
        guardar_puntaje(nombre, jug_score)
        reproducir_cancion()
        win.destroy()

    tk.Button(win, text="Guardar", font=("Perfect DOS VGA 437 Win", 12), command=guardar).pack(pady=10)

def ventana_records(ventana_padre):
    ruta = os.path.join(carpeta, "puntajes.txt")
    print(ruta)
    win = tk.Toplevel(ventana_padre)
    win.title("Records")
    win.geometry("400x350")
    win.configure(bg="#111122")
    tk.Label(win, text="Mejores Puntajes", font=("Perfect DOS VGA 437 Win", 14), bg= "#111122", fg="white").pack(pady=15)

    puntajes = []
    if os.path.exists(ruta):
        archivo = open(ruta, "r")
        for linea in archivo:
            linea = linea.strip()
            if linea:
                partes = linea.split(",")
                puntajes.append((partes[0], int(partes[1])))
        archivo.close()
    print(puntajes)
    if not puntajes:
        tk.Label (win, text= "No hay puntajes aun", font=("Perfect, DOS VGA 437 Win", 14), bg="#111122", fg="white").pack(pady=10)
    else:
        posicion = ["1.", "2.", "3.", "4.", "5."]
        colores = ["#FFD700", "#cccccc", "#cc8800", "white", "white"]
        for i in range(len(puntajes)):
            nombre, pts = puntajes[i]
            tk.Label(win, text=f"{posicion[i]}  {nombre}  —  {pts} pts", font=("Perfect DOS VGA 437 Win", 12), bg="#111122", fg=colores[i]).pack(pady=4)
    tk.Button (win, text="Cerrar", font=("Perfect DOS VGA 437 Win", 11), bg="#220000", fg="black",command=win.destroy).pack(pady=15)
         

# ══════════════════════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def iniciar_juego(ventana_principal):
    global tecla_a, tecla_d, tecla_w, tecla_s, tecla_space, jugador_invencible
    pygame.mixer.music.stop()
    ventana = tk.Toplevel(ventana_principal) 
    ventana.title("Piston Power Adventure — Nivel 1")
    ventana.geometry(f"{SCREEN_W}x{SCREEN_H}")
    ventana.resizable(False, False)

    canvas = tk.Canvas(ventana, width=SCREEN_W, height=SCREEN_H, bg="#000", highlightthickness=0)
    canvas.pack()

    inicializar_nivel()
    inicializar_camara(nivel_width)
    inicializar_jugador()

    inicializar_enemigos()
    inicializar_enemigos2()


    activo = [True]
    last_t = [time.perf_counter()]

    def al_cerrar():
        reproducir_cancion()
        ventana_principal.deiconify()
        ventana.destroy()    

    # ── Teclado ───────────────────────────────────────────────────────────────
    def key_down(event):
        global tecla_a, tecla_d, tecla_w, tecla_s, tecla_space
        k = event.keysym.lower()
        if k == "a" or k == "left":     tecla_a     = True
        if k == "d" or k == "right":     tecla_d     = True
        if k == "w" or k == "up":     tecla_w     = True
        if k == "s" or k == "down":     tecla_s     = True
        if k == "space": tecla_space = True
        if k == "escape":
            activo[0] = False
            al_cerrar()
            ventana.destroy()
            



    def key_up(event):
        global tecla_a, tecla_d, tecla_w, tecla_s, tecla_space
        k = event.keysym.lower()
        if k == "a" or k == "left":     tecla_a     = False
        if k == "d" or k == "right":    tecla_d     = False
        if k == "w" or k == "up":       tecla_w     = False
        if k == "s" or k == "down":     tecla_s     = False
        if k == "space":                 tecla_space = False

    ventana.bind("<KeyPress>",   key_down)
    ventana.bind("<KeyRelease>", key_up)
    ventana.focus_set()

    # ── Fin de partida ────────────────────────────────────────────────────────
    def game_over():
        activo[0] = False
        messagebox.showinfo("Game Over", f"¡Se acabaron las vidas!\nPuntuación: {jug_score}", parent=ventana)
        reproducir_cancion()
        ventana.destroy()

    def ganar():
        activo[0] = False
        ventana.withdraw()
        ventana_ganar(ventana)



    ventana.protocol("WM_DELETE_WINDOW", al_cerrar)
        
    # ── Bucle ─────────────────────────────────────────────────────────────────
    def loop():
        global jugador_invencible
        if not activo[0]:
            return
        if jugador_invencible > 0:
            jugador_invencible -= 1 
        todas = nivel_platforms + nivel_floor

        now = time.perf_counter()
        if now - last_t[0] >= 1 / FPS:
            last_t[0] = now

            if not jug_alive:
                if jug_lives > 0:
                    respawnear_jugador()
                else:
                    game_over()
                    return

            actualizar_jugador(todas)
            actualizar_enemigos(todas)
            actualizar_enemigos2(todas)
            verificar_colision_enemigos()
            verificar_colision_enemigos2()

            if verificar_meta():
                ganar()
                return

            actualizar_camara(jug_x)
            dibujar_juego(canvas)

        ventana.after(16, loop)

    ventana.protocol("WM_DELETE_WINDOW", lambda: [activo.__setitem__(0, False), ventana.destroy()])
    loop()

#=====================Editor de niveles==================#
#tamaño de vnetana
EDITOR_W = 1825
EDITOR_H = 600
BARRA_H = 100
EDITOR_TOTAL = EDITOR_H + BARRA_H

#herramientas que se van a ocupar
HERRA_PLAT = "plataforma"
HERRA_ESC = "escalera"
HERRA_ENEMIGO = "enemigo"
HERRA_ENEMIGO2 = "enemigo 2"
HERRA_SPAWN = "spawn"
HERRA_META = "meta"
HERRA_BORRAR = "borrar"

#variables de editor
ed_cam_x       = 0          # camara del editor
ed_herramienta = HERRA_PLAT  # herramienta seleccionada
ed_plataformas = []          # lista de tuplas (x, y, ancho, alto)
ed_escaleras   = []          # lista de tuplas (x, y, ancho, alto)
ed_enemigos_x  = []          # posicion x de cada enemigo
ed_enemigos_y  = []          # posicion y de cada enemigo
ed_enemigos2_x = []
ed_enemigos2_y = []
ed_spawn_x     = 100         # posicion spawn
ed_spawn_y     = 440
ed_meta_x      = 5000        # posicion meta
ed_meta_y      = 350
ed_arrastrando = False       # si el mouse esta presionado
ed_inicio_x    = 0           # donde empezo el arrastre
ed_inicio_y    = 0

# Tamaños de elementos
PLAT_W_ED  = 200
PLAT_H_ED  = 20
ESC_W_ED   = 40
ESC_H_ED   = 120
META_W_ED  = 40
META_H_ED  = 80
SPAWN_W_ED = 40
SPAWN_H_ED = 60
EN_W_ED    = 40
EN_H_ED    = 40
EN2_W_ED    = 70
EN2_H_ED    = 40



def abrir_editor(ventana_principal): 
    global ed_cam_x, ed_herramienta, ed_plataformas, ed_escaleras, ed_enemigos_x, ed, ed_enemigos_y, ed_enemigos2_y, ed_spawn_x, ed_spawn_y
    global ed_meta_x, ed_meta_y, ed_arrastrando, ed_inicio_x, ed_inicio_y, nivel_platforms, nivel_ladders, nivel_spawn_x, nivel_spawn_y, nivel_meta
    global datos_enemigos, tecla_space, datos_enemigos2

    ed_cam_x       = 0
    ed_herramienta = HERRA_PLAT
    ed_plataformas = []
    ed_escaleras   = []
    ed_enemigos_x  = []
    ed_enemigos_y  = []
    ed_enemigos2_x  = []
    ed_enemigos2_y  = []
    ed_spawn_x     = 100
    ed_spawn_y     = 440
    ed_meta_x      = 5000
    ed_meta_y      = 350
    ed_arrastrando = False
 
    ventana = tk.Toplevel(ventana_principal)
    ventana.title("Creador de Niveles")
    ventana.geometry(f"{SCREEN_W}x{EDITOR_TOTAL}")
    ventana.resizable(False, False)

    

    #canvas para editor
    canvas = tk.Canvas(ventana, width=SCREEN_W, height=EDITOR_H, bg="#1a1a2e", highlightthickness=0)
    canvas.pack()

    #barra de herramientas
    barra = tk.Frame(ventana, bg="#111122", height=BARRA_H)
    barra.pack(fill=tk.X)
 
    herra_label = tk.Label(barra, text="Herramienta: PLATAFORMA", font=("Perfect DOS VGA 437 Win", 10), bg="#111122", fg="#FFD700")
    herra_label.pack(side=tk.LEFT, padx=10, pady=5)
 
    def seleccionar(h):
        global ed_herramienta
        ed_herramienta = h
        nombres = {
            HERRA_PLAT:    "PLATAFORMA",
            HERRA_ESC:     "ESCALERA",
            HERRA_ENEMIGO: "ENEMIGO",
            HERRA_ENEMIGO2: "ENEMIGO 2",
            HERRA_SPAWN:   "SPAWN",
            HERRA_META:    "META",
            HERRA_BORRAR:  "BORRAR",
        }
        herra_label.config(text=f"Herramienta: {nombres[h]}")

    #botones
    colores_btn = [
        (HERRA_PLAT,    "Plataforma", "#3a7d1e"),
        (HERRA_ESC,     "Escalera",   "#964B00"),
        (HERRA_ENEMIGO, "Enemigo",    "#6a006a"),
        (HERRA_ENEMIGO2, "Enemigo 2", "#6a006a"),
        (HERRA_SPAWN,   "Spawn",      "#0044cc"),
        (HERRA_META,    "Meta",       "#aa8800"),
        (HERRA_BORRAR,  "Borrar",     "#880000"),
    ]
    for herr, texto, color in colores_btn:
        tk.Button(barra, text=texto, font=("Perfect DOS VGA 437 Win", 9),bg=color, fg="black", width=8,
        command=lambda h=herr: seleccionar(h)).pack(side=tk.LEFT, padx=4, pady=8)

    tk.Button(barra, text="◀◀", font=("Courier", 12), bg="#222244", fg="black", command=lambda: mover_camara_editor(-300)).pack(side=tk.LEFT, padx=4)
    tk.Button(barra, text="▶▶", font=("Courier", 12), bg="#222244", fg="black", command=lambda: mover_camara_editor(300)).pack(side=tk.LEFT, padx=4)
 
    # Boton jugar con este nivel
    tk.Button(barra, text="▶ JUGAR", font=("Perfect DOS VGA 437 Win", 11),bg="#004400", fg="black", width=8,
        command=lambda: aplicar_y_jugar(ventana, ventana_principal)).pack(side=tk.RIGHT, padx=10, pady=8)

#==========Funciones para el editor====#
    def mover_camara_editor(dx):
        global ed_cam_x
        ed_cam_x = max(0, min(ed_cam_x + dx, EDITOR_W - SCREEN_W))
        dibujar_editor()
    
    def mundo_x(sx):
        """Pantalla → mundo."""
        return sx + ed_cam_x
 
    def pantalla_x(wx):
        """Mundo → pantalla."""
        return wx - ed_cam_x
 
    def click_editor(event):
        global ed_arrastrando, ed_inicio_x, ed_inicio_y
        ed_arrastrando = True
        ed_inicio_x    = mundo_x(event.x)
        ed_inicio_y    = event.y
        soltar_editor(event)   # colocar al instante
 
    def soltar_editor(event):
        global ed_arrastrando, ed_spawn_x, ed_spawn_y, ed_meta_x, ed_meta_y
        if not ed_arrastrando:
            return
        wx = mundo_x(event.x)
        wy = event.y
 
        if ed_herramienta == HERRA_PLAT:
            ed_plataformas.append((wx, wy, PLAT_W_ED, PLAT_H_ED))
 
        elif ed_herramienta == HERRA_ESC:
            ed_escaleras.append((wx, wy, ESC_W_ED, ESC_H_ED))
 
        elif ed_herramienta == HERRA_ENEMIGO:
            ed_enemigos_x.append(wx)
            ed_enemigos_y.append(wy)
        
        elif ed_herramienta == HERRA_ENEMIGO2:
            ed_enemigos2_x.append(wx)
            ed_enemigos2_y.append(wy)
 
        elif ed_herramienta == HERRA_SPAWN:
            ed_spawn_x = wx
            ed_spawn_y = wy
 
        elif ed_herramienta == HERRA_META:
            ed_meta_x = wx
            ed_meta_y = wy
 
        elif ed_herramienta == HERRA_BORRAR:
            borrar_en(wx, wy) 
            
        dibujar_editor()
 
    def borrar_en(wx, wy):
        # Borrar plataforma
        for i in range(len(ed_plataformas) - 1, -1, -1):
            px, py, pw, ph = ed_plataformas[i]
            if px <= wx <= px + pw and py <= wy <= py + ph:
                ed_plataformas.pop(i)
                return
        # Borrar escalera
        for i in range(len(ed_escaleras) - 1, -1, -1):
            lx, ly, lw, lh = ed_escaleras[i]
            if lx <= wx <= lx + lw and ly <= wy <= ly + lh:
                ed_escaleras.pop(i)
                return
        # Borrar enemigo
        for i in range(len(ed_enemigos_x) - 1, -1, -1):
            if abs(ed_enemigos_x[i] - wx) < EN_W_ED and abs(ed_enemigos_y[i] - wy) < EN_H_ED:
                ed_enemigos_x.pop(i)
                ed_enemigos_y.pop(i)
                return
        # Borrar enemigo
        for i in range(len(ed_enemigos2_x) - 1, -1, -1):
            if abs(ed_enemigos2_x[i] - wx) < EN2_W_ED and abs(ed_enemigos2_y[i] - wy) < EN2_H_ED:
                ed_enemigos2_x.pop(i)
                ed_enemigos2_y.pop(i)
                return
             
    canvas.bind("<Button-1>",  click_editor)
    canvas.bind("<ButtonRelease-1>", lambda e: globals().update(ed_arrastrando=False))
 
    def dibujar_editor():
        canvas.delete("all")
 
        # Fondo
        canvas.create_rectangle(0, 0, SCREEN_W, EDITOR_H, fill="#1a1a2e", outline="")
 
        # Suelo referencia
        canvas.create_rectangle(0, 480, SCREEN_W, EDITOR_H, fill="#5a3010", outline="#3a1a00")
        canvas.create_text(10, 470, anchor="sw", text="SUELO", fill="#888866", font=("Courier", 8))
 
        # Lineas de cuadricula cada 100px
        for wx in range(0, EDITOR_W, 100):
            sx = pantalla_x(wx)
            if 0 <= sx <= SCREEN_W:
                canvas.create_line(sx, 0, sx, EDITOR_H, fill="#222244", width=1)
                canvas.create_text(sx + 2, 4, anchor="nw", text=str(wx),  fill="#333366", font=("Courier", 7))
 
        # Plataformas
        for px, py, pw, ph in ed_plataformas:
            sx = pantalla_x(px)
            if sx + pw < 0 or sx > SCREEN_W:
                continue
            canvas.create_rectangle(sx, py, sx + pw, py + ph, fill="#3a7d1e", outline="#1a5a0a", width=2)
            canvas.create_text(sx + pw // 2, py - 8, text="PLAT",fill="#3a7d1e", font=("Courier", 7))
 
        # Escaleras
        for lx, ly, lw, lh in ed_escaleras:
            sx = pantalla_x(lx)
            if sx + lw < 0 or sx > SCREEN_W:
                continue
            canvas.create_rectangle(sx, ly, sx + lw, ly + lh, fill="#964B00", outline="#6a2a00", width=2)
            canvas.create_text(sx + lw // 2, ly - 8, text="ESC", fill="#964B00", font=("Courier", 7))
 
        # Enemigos
        for i in range(len(ed_enemigos_x)):
            sx = pantalla_x(ed_enemigos_x[i])
            ey = ed_enemigos_y[i]
            canvas.create_oval(sx, ey, sx + EN_W_ED, ey + EN_H_ED, fill="#6a006a", outline="#aa00aa", width=2)
            canvas.create_text(sx + EN_W_ED // 2, ey - 8, text="ENEM", fill="#aa00aa", font=("Courier", 7))

        # Enemigos 2
        for i in range(len(ed_enemigos2_x)):
            sx = pantalla_x(ed_enemigos2_x[i])
            ey = ed_enemigos2_y[i]
            canvas.create_oval(sx, ey, sx + EN2_W_ED, ey + EN2_H_ED, fill="#6a006a", outline="#aa00aa", width=2)
            canvas.create_text(sx + EN2_W_ED // 2, ey - 8, text="ENEM2", fill="#aa00aa", font=("Courier", 7))
 
        # Spawn
        sx = pantalla_x(ed_spawn_x)
        canvas.create_rectangle(sx, ed_spawn_y, sx + SPAWN_W_ED, ed_spawn_y + SPAWN_H_ED, fill="#0044cc", outline="#0088ff", width=2)
        canvas.create_text(sx + SPAWN_W_ED // 2, ed_spawn_y - 10, text="SPAWN", fill="#0088ff", font=("Courier", 8, "bold"))
 
        # Meta
        sx = pantalla_x(ed_meta_x)
        canvas.create_rectangle(sx, ed_meta_y, sx + META_W_ED, ed_meta_y + META_H_ED, fill="#aa8800", outline="#FFD700", width=2)
        canvas.create_text(sx + META_W_ED // 2, ed_meta_y - 10, text="META", fill="#FFD700", font=("Courier", 8, "bold"))
 
        # Posicion de camara
        canvas.create_text(SCREEN_W - 5, 5, anchor="ne", text=f"Cam: {ed_cam_x}  |  ← → para mover la camara",fill="#aaaaaa", font=("Courier", 8))
 
    def aplicar_y_jugar(ventana_editor, ventana_principal):
        global nivel_platforms, nivel_ladders, nivel_spawn_x, nivel_spawn_y
        global nivel_meta, datos_enemigos, datos_enemigos2
 
        # Validar que tenga meta dentro del nivel
        if ed_meta_x < 0 or ed_meta_x > nivel_width - META_W_ED:
            messagebox.showwarning("Editor", "Agrega la meta dentro del nivel.", parent=ventana_editor)
            return
        
        # Aplicar el mapa creado al nivel
        nivel_platforms = ed_plataformas[:]
        nivel_ladders   = ed_escaleras[:]
        nivel_spawn_x   = ed_spawn_x
        nivel_spawn_y   = ed_spawn_y + SPAWN_H_ED
        nivel_meta      = (ed_meta_x, ed_meta_y, META_W_ED, META_H_ED)
        datos_enemigos = []
        datos_enemigos2 = []


        for i in range(len(ed_enemigos_x)):
            x   = ed_enemigos_x[i]
            y   = ed_enemigos_y[i] + EN_H_ED
            izq = max(0, x - 150)
            der = x + 150
            datos_enemigos.append((x, y, izq, der))

        for i in range(len(ed_enemigos2_x)):
            x   = ed_enemigos2_x[i]
            y   = ed_enemigos2_y[i] + EN2_H_ED
            izq = max(0, x - 150)
            der = x + 150
            datos_enemigos2.append((x, y, izq, der))

        ventana_editor.destroy()
        iniciar_juego(ventana_principal)
 
    # Teclado para mover camara con flechas
    def key_editor(event):
        k = event.keysym
        if k == "Left":
            mover_camara_editor(-100)
        if k == "Right":
            mover_camara_editor(100)
 
    ventana.bind("<KeyPress>", key_editor)
    ventana.focus_set()
    dibujar_editor()

# ══════════════════════════════════════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def salir():
    principal.destroy()

def crear_menu():
    ventana = tk.Toplevel(principal)
    ventana.title("Piston Power Adventure")
    ventana.geometry(f"{ANCHO}x{ALTO}")
    ventana.resizable(False, False)


    canvas_menu = tk.Canvas(ventana, width=ANCHO, height=ALTO)
    canvas_menu.pack(fill="both", expand=True)

    imagen = Image.open(os.path.join(carpeta, "menu.png"))
    imagen = imagen.resize((ANCHO, ALTO))
    ventana.fondo = ImageTk.PhotoImage(imagen)
    canvas_menu.create_image(0, 0, anchor="nw", image=ventana.fondo)

    btn_jugar = tk.Label(ventana, text="Jugar Nivel Fijo", font=("Perfect DOS VGA 437 Win", 16), width=15, height=3, bg="#d6bc84", fg="black", cursor="hand2")
    btn_jugar.bind("<Button-1>", lambda e:[cargar_nivel_fijo(), iniciar_juego(ventana)])
    canvas_menu.create_window(351, 256, window=btn_jugar)

    btn_editor = tk.Label(ventana, text="Creador \n de Niveles", font=("Perfect DOS VGA 437 Win", 16), width=13, height=2, bg="#d6bc84", fg="black", cursor="hand2")
    btn_editor.bind("<Button-1>", lambda e: abrir_editor(ventana))
    canvas_menu.create_window(769, 253, window=btn_editor)

    btn_records = tk.Label(ventana, text="Records", font=("Perfect DOS VGA 437 Win", 16), width=13, height=4, bg="#d6bc84", fg="black", cursor="hand2")
    btn_records.bind("<Button-1>", lambda e: ventana_records(principal))
    canvas_menu.create_window(763, 362, window=btn_records)

    btn_salir = tk.Label(ventana, text="Quit", font=("Perfect DOS VGA 437 Win", 16), width=10, height=2, bg="#d6bc84", fg="Black", cursor="hand2")
    btn_salir.bind("<Button-1>", lambda e: salir())
    canvas_menu.create_window(555, 468, window=btn_salir)

    btn_sonido = tk.Label(ventana, text="Sonido", font=("Perfect DOS VGA 437 Win", 16), width=14, height=2, bg="#d6bc84", fg="Black", cursor="hand2")
    btn_sonido.bind("<Button-1>", lambda e: toggle_musica())
    canvas_menu.create_window(351, 357, window=btn_sonido)


    reproducir_cancion()

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRADA
# ══════════════════════════════════════════════════════════════════════════════
principal = tk.Tk()
principal.withdraw()
pygame.mixer.init()
crear_menu()
principal.mainloop()