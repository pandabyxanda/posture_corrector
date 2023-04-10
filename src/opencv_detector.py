import math

import cv2
import mediapipe as mp
import time




# cap = cv2.VideoCapture(0)

pTime = 0

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Detector():
    def __init__(self, camera=0):
        self.cap = cv2.VideoCapture(camera)
        self.set_angle()

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=False)

    def set_angle(self, angle_max=10):
        self.angle_max = angle_max

    def check_posture(self, angle_max=10):
        self.angle_max = angle_max
        success, img = self.cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(imgRGB)
        # print(f"{results.pose_landmarks = }")
        alpha = None
        if results.pose_landmarks:
            # self.mpDraw.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            h, w, c = img.shape

            # ears and nose drawing circles
            lm_7 = results.pose_landmarks.landmark[7]
            lm_8 = results.pose_landmarks.landmark[8]
            cv2.circle(img, (int(lm_7.x * w), int(lm_7.y * h)), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (int(lm_8.x * w), int(lm_8.y * h)), 5, (255, 0, 0), cv2.FILLED)

            # ears center draw
            ears_cp = Point((lm_7.x + lm_8.x) / 2, (lm_7.y + lm_8.y) / 2, (lm_7.z + lm_8.z) / 2)
            cv2.circle(img, (int(ears_cp.x * w), int(ears_cp.y * h)), 5, (0, 255, 0), cv2.FILLED)
            lm_0 = results.pose_landmarks.landmark[0]
            cv2.circle(img, (int((lm_0.x) * w), int((lm_0.y) * h)), 5, (0, 255, 255), cv2.FILLED)
            nose_project_p = Point(lm_0.x, ears_cp.y, lm_0.z)
            cv2.circle(img, (int((nose_project_p.x) * w), int((nose_project_p.y) * h)), 5, (0, 255, 255), cv2.FILLED)




            # ears and nose meter coordination
            lmw_7 = results.pose_world_landmarks.landmark[7]
            lmw_8 = results.pose_world_landmarks.landmark[8]
            ears_cpw = Point((lmw_7.x + lmw_8.x) / 2, (lmw_7.y + lmw_8.y) / 2, (lmw_7.z + lmw_8.z) / 2)

            lmw_0 = results.pose_world_landmarks.landmark[0]
            cv2.circle(img, (int(lmw_0.x * w), int(lmw_0.y * h)), 5, (255, 0, 0), cv2.FILLED)
            nose_project_p = Point(lmw_0.x, ears_cpw.y, lmw_0.z)
            length_ears_cp_nose_pr = (((ears_cpw.x - nose_project_p.x) ** 2 + (ears_cpw.y - nose_project_p.y) ** 2 +
                                       (ears_cpw.z - nose_project_p.z) ** 2) ** 0.5) * 1000
            length_ears_cp_nose = (((ears_cpw.x - lmw_0.x) ** 2 + (ears_cpw.y - lmw_0.y) ** 2 +
                                    (ears_cpw.z - lmw_0.z) ** 2) ** 0.5) * 1000

            if length_ears_cp_nose != 0 and abs(length_ears_cp_nose_pr/length_ears_cp_nose) < 1:
                alpha = abs(round(math.acos(length_ears_cp_nose_pr/length_ears_cp_nose) * 180 / 3.1415, 2))
                if nose_project_p.y > lmw_0.y:
                    alpha = -alpha
                # if alpha > self.angle_max:
                #     print(f"Sit in the correct posture (angle max = {angle_max}), {alpha = }")

                    # pass




            # shoulders center draw
            lm_11 = results.pose_landmarks.landmark[11]
            lm_12 = results.pose_landmarks.landmark[12]
            lm_0 = results.pose_landmarks.landmark[0]
            cv2.circle(img, (int(lm_11.x * w), int(lm_11.y * h)), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (int(lm_12.x * w), int(lm_12.y * h)), 5, (255, 0, 0), cv2.FILLED)
            shoulders_cp = Point((lm_11.x + lm_12.x) / 2, (lm_11.y + lm_12.y) / 2, (lm_11.z + lm_12.z) / 2)
            cv2.circle(img, (int(shoulders_cp.x * w), int(shoulders_cp.y * h)), 5, (0, 255, 0), cv2.FILLED)
            shoulders_cp_pr = Point(shoulders_cp.x, ears_cp.y, shoulders_cp.z)
            cv2.circle(img, (int(shoulders_cp_pr.x * w), int(shoulders_cp_pr.y * h)), 5, (0, 255, 255), cv2.FILLED)




            # shoulders and nose meter coordination
            lmw_11 = results.pose_world_landmarks.landmark[11]
            lmw_12 = results.pose_world_landmarks.landmark[12]
            shoulders_cp = Point((lmw_11.x + lmw_12.x) / 2, (lmw_11.y + lmw_12.y) / 2, (lmw_11.z + lmw_12.z) / 2)

            lmw_0 = results.pose_world_landmarks.landmark[0]

            shoulders_cp_pr = Point(shoulders_cp.x, ears_cpw.y, shoulders_cp.z)

            length_sh_cp_ears = (((shoulders_cp.x - ears_cpw.x) ** 2 + (shoulders_cp.y - ears_cpw.y) ** 2 +
                                       (shoulders_cp.z - ears_cpw.z) ** 2) ** 0.5) * 1000
            length_sh_sh_cp_pr = (((shoulders_cp.x - shoulders_cp_pr.x) ** 2 + (shoulders_cp.y - shoulders_cp_pr.y) ** 2 +
                                    (shoulders_cp.z - shoulders_cp_pr.z) ** 2) ** 0.5) * 1000

            # if length_ears_cp_nose != 0 and abs(length_ears_cp_nose_pr/length_ears_cp_nose) < 1:
            alpha = abs(round(math.acos(length_sh_sh_cp_pr/length_sh_cp_ears) * 180 / 3.1415, 2))
            # if nose_project_p.y > lmw_0.y:
            #     alpha = -alpha
            # if alpha > 10:
            # print(f"Sit in the correct posture, {alpha = }")
            #     # pass

        # cv2.imshow("Image", img)
        return alpha



if __name__ == "__main__":
    dt = Detector(0)
    while True:
        dt.check_posture()

        # cTime = time.time()
        # fps = 1 / (cTime - pTime)
        # pTime = cTime

        # cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)
        cv2.waitKey(1)
