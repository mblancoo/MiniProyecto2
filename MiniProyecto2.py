import cv2
import mediapipe as mp
import serial
import time

# Configura el puerto serial (ajusta el puerto COM según tu equipo)
arduino = serial.Serial('COM5', 9600)
time.sleep(2)  # Espera para establecer conexión

# Inicializa MediaPipe y OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
prev_finger_count = -1

def contar_dedos(mano):
    dedos = [mp_hands.HandLandmark.THUMB_TIP,
             mp_hands.HandLandmark.INDEX_FINGER_TIP,
             mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
             mp_hands.HandLandmark.RING_FINGER_TIP,
             mp_hands.HandLandmark.PINKY_TIP]

    count = 0
    for i in range(1, 5):
        if mano.landmark[dedos[i]].y < mano.landmark[dedos[i] - 2].y:
            count += 1
    # Verifica el pulgar (movimiento horizontal)
    if mano.landmark[mp_hands.HandLandmark.THUMB_TIP].x < mano.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        count += 1
    return count

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    dedos_lev = 0  # Por defecto, sin manos detectadas

    if resultado.multi_hand_landmarks:
        for mano in resultado.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, mano, mp_hands.HAND_CONNECTIONS)
            dedos_lev = contar_dedos(mano)
            break  # Solo consideramos una mano

    # Enviar solo si cambia la cantidad de dedos
    if dedos_lev != prev_finger_count:
        print("Dedos levantados:", dedos_lev)
        arduino.write(f"{dedos_lev}\n".encode())
        prev_finger_count = dedos_lev

    cv2.imshow("Contador de Dedos", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()
arduino.close()
