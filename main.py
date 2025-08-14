import cv2
import mediapipe as mp
import time
import math
import pygame

class DistractionDetector:
    def __init__(self, buzzer_file="buzzer.mp3"):
        # Initialize pygame mixer for buzzer
        pygame.mixer.init()
        self.buzzer_file = buzzer_file

        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=5)

        # Thresholds
        self.EYE_AR_THRESH = 0.25
        self.EYE_CLOSED_TIME = 5   # seconds
        self.LOOK_AWAY_TIME = 10   # seconds

        # Timers
        self.eye_close_start = None
        self.look_away_start = None
        self.look_direction = "Forward"
        self.normal_start_time = None
        self.BUZZER_STOP_DELAY = 2  # seconds after normal

        # Alert flags
        self.eye_alert_on = False
        self.look_away_alert_on = False

    def _play_buzzer(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(self.buzzer_file)
            pygame.mixer.music.play(-1)

    def _stop_buzzer(self):
        pygame.mixer.music.stop()

    @staticmethod
    def eye_aspect_ratio(eye_points):
        A = math.dist(eye_points[1], eye_points[5])
        B = math.dist(eye_points[2], eye_points[4])
        C = math.dist(eye_points[0], eye_points[3])
        return (A + B) / (2.0 * C)

    def detect(self, frame):
        eye_timer_display = 0
        away_timer_display = 0
        direction_text = "Forward"

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            # Select the largest face (closest to camera)
            h, w, _ = frame.shape
            largest_area = 0
            main_face = None
            for face_landmarks in results.multi_face_landmarks:
                xs = [landmark.x * w for landmark in face_landmarks.landmark]
                ys = [landmark.y * h for landmark in face_landmarks.landmark]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                area = (max_x - min_x) * (max_y - min_y)
                if area > largest_area:
                    largest_area = area
                    main_face = face_landmarks

            face_landmarks = main_face

            # Eyes
            left_eye_idx = [33, 160, 158, 133, 153, 144]
            right_eye_idx = [362, 385, 387, 263, 373, 380]

            left_eye = [(int(face_landmarks.landmark[i].x * w),
                         int(face_landmarks.landmark[i].y * h)) for i in left_eye_idx]
            right_eye = [(int(face_landmarks.landmark[i].x * w),
                          int(face_landmarks.landmark[i].y * h)) for i in right_eye_idx]

            # Nose tip
            nose_tip = face_landmarks.landmark[1]
            nose_x = nose_tip.x * w
            frame_center_x = w / 2

            # EAR
            ear = (self.eye_aspect_ratio(left_eye) + self.eye_aspect_ratio(right_eye)) / 2.0

            # Eye closure detection
            if ear < self.EYE_AR_THRESH:
                if self.eye_close_start is None:
                    self.eye_close_start = time.time()
                eye_timer_display = round(time.time() - self.eye_close_start, 1)
                if eye_timer_display >= self.EYE_CLOSED_TIME:
                    cv2.putText(frame, "ALERT: Eyes Closed!", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    if not self.eye_alert_on:
                        self._play_buzzer()
                        self.eye_alert_on = True
            else:
                self.eye_close_start = None
                eye_timer_display = 0
                if self.eye_alert_on:
                    self.normal_start_time = time.time()

            # Looking away detection with direction
            if nose_x < frame_center_x - 50:
                direction_text = "Looking Left"
            elif nose_x > frame_center_x + 50:
                direction_text = "Looking Right"
            else:
                direction_text = "Forward"

            if direction_text != "Forward":
                if self.look_away_start is None:
                    self.look_away_start = time.time()
                away_timer_display = round(time.time() - self.look_away_start, 1)
                if away_timer_display >= self.LOOK_AWAY_TIME:
                    cv2.putText(frame, f"ALERT: {direction_text}!", (50, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    if not self.look_away_alert_on:
                        self._play_buzzer()
                        self.look_away_alert_on = True
            else:
                self.look_away_start = None
                away_timer_display = 0
                if self.look_away_alert_on or self.eye_alert_on:
                    self.normal_start_time = time.time()

            self.look_direction = direction_text

            # Draw eyes
            for (x, y) in left_eye + right_eye:
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        else:
            # No face detected
            self.eye_close_start = None
            self.look_away_start = None
            eye_timer_display = 0
            away_timer_display = 0
            direction_text = "No Face Detected"
            if self.eye_alert_on or self.look_away_alert_on:
                self.normal_start_time = time.time()

        # Stop buzzer 2s after normal
        if self.normal_start_time is not None:
            if time.time() - self.normal_start_time >= self.BUZZER_STOP_DELAY:
                self._stop_buzzer()
                self.eye_alert_on = False
                self.look_away_alert_on = False
                self.normal_start_time = None

        # Display info
        cv2.putText(frame, f"Eye Closed Timer: {eye_timer_display:.1f}s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"Looking Away Timer: {away_timer_display:.1f}s", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"Direction: {direction_text}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        return frame

    def cleanup(self):
        self._stop_buzzer()
        pygame.mixer.quit()
        self.face_mesh.close()


def main():
    cap = cv2.VideoCapture(0)
    detector = DistractionDetector(buzzer_file="buzzer.mp3")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detector.detect(frame)
        cv2.imshow("Driver Distraction Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.cleanup()


if __name__ == "__main__":
    main()
