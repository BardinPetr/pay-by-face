#!/usr/bin/env python
import dlib
import sys

from imutils import face_utils

from tools import *
import multiprocessing


api_data = parceJson("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]


def create_person(*args, simple=True):
    global video
    global type
    if simple:
        if create_frames_simple(args[0]):
            exist_group(True)
            res = check_all_right(cf.person.create, person_group_id=g_id, name="anonymous")
            if res:
                person_id = res["personId"]
                face_ids = set()
                for i in range(1, 6):
                    res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id,
                                          image=(str(i) + ".jpg"))
                    if res:
                        face_ids.add(res["persistedFaceId"])
                    else:
                        break
                cf.person_group.update(g_id, user_data="not trained")
                print("5 frames extracted\nPersonId:", person_id + "\nFaceIds\n=======" + "\n" + "\n".join(face_ids))
                clear(5)
        else:
            print("Video does not contain any face")
    else:
        cap = cv2.VideoCapture(args[3])
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video = args[3]
        cap.release()
        type = 3
        with multiprocessing.Pool(5) as p:
            print(p.map(create_frames_hard, list(range(0, length, length // 4))))
        p.terminate()
        # create_frames_hard(args[3], type=3)


def create_frames_hard(start):
    global video
    global type
    types = {1: "roll", 2: "yaw"}
    steps = {1: 15, 2: 20}
    all_nice = []
    if os.path.exists(video):
        face_ids = []
        cap = cv2.VideoCapture(video)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if length < 5:
            return False
        cap.release()
        for i in range(start, start + length // 4):
            cap = cv2.VideoCapture(video)
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            im_frame = cap.read()[1]
            if (type == 1) or (type == 2):
                cv2.imwrite("test.jpg", im_frame)
                res = check_all_right(cf.face.detect, "test.jpg")
                if res:
                    face_ids.append(res[0]["faceId"])
                else:
                    clear(i)
                    return False
                cap.release()
            elif type == 3:
                all_nice += [0, 0]
                gray = cv2.cvtColor(im_frame, cv2.COLOR_BGR2GRAY)
                detector = dlib.get_frontal_face_detector()
                predictor = dlib.shape_predictor("./opt/shape_predictor_68_face_landmarks.dat")
                rects = detector(gray, 0)
                eye_ar_thresh = 0.3
                for ind, rect in enumerate(rects):
                    print(6)
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
                    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
                    left_eye = shape[lStart:lEnd]
                    right_eye = shape[rStart:rEnd]
                    left_ear = eye_aspect_ratio(left_eye)
                    right_ear = eye_aspect_ratio(right_eye)
                    if (left_ear > eye_ar_thresh) & (right_ear < eye_ar_thresh) & (not all_nice[0]):
                        cv2.imwrite("left_eye.jpg", gray)
                        all_nice[0] = 1
                    elif (left_ear < eye_ar_thresh) & (right_ear > eye_ar_thresh) & (not all_nice[1]):
                        cv2.imwrite("right_eye.jpg", gray)
                        all_nice[1] = 1
                    if sum(all_nice) == 2:
                        return True
            else:
                print("asdasd")
        return face_ids
    else:
        return False


def euclidean(p, q):
    sum_sq = 0.0
    # Суммируем квадраты разностей
    for i in range(len(p)):
        sum_sq += (p[i]-q[i])**2
    # Извлекаем квадратный корень
    return sum_sq ** 0.5


def eye_aspect_ratio(eye):
    a = euclidean(eye[1], eye[5])
    b = euclidean(eye[2], eye[4])
    c = euclidean(eye[0], eye[3])

    ear = (a + b) / (2.0 * c)

    return ear


def delete_person(person_id):
    if exist_group():
        res = check_all_right(cf.person.lists, g_id)
        if res:
            if person_id in [i["personId"] for i in res]:
                check_all_right(cf.person.delete, person_group_id=g_id, person_id=person_id)
                check_all_right(cf.person_group.update, g_id, user_data="not trained")
                print("Person deleted")
            else:
                print("The person does not exist")
        else:
            print("The person does not exist")
    else:
        print("The group does not exist")


def train_group():
    if exist_group():
        res = check_all_right(cf.person_group.get, g_id)
        if res.setdefault("userData") == "trained":
            print("Already trained")
        elif res.setdefault("userData") == "not trained":
            check_all_right(cf.person_group.train, g_id)
            check_all_right(cf.person_group.update, g_id, user_data="trained")
            print("Training successfully started")
        else:
            print("There is nothing to train")

    else:
        print("There is nothing to train")


def is_trained():
    res = check_all_right(cf.person_group.get_status, g_id)
    if res:
        if res["status"] == "failed":
            return False
        else:
            return True
    else:
        return False


def get_persons():
    if exist_group():
        res = check_all_right(cf.person.lists, g_id)
        if res:
            print("Persons IDs:")
            for i in res:
                print(i["personId"])
        else:
            print("No persons found")
    else:
        print("The group does not exist")


if __name__ == "__main__":
    check_all_right()
    if sys.argv[1] == "--simple-add":
        create_person(sys.argv[2])
    elif sys.argv[1] == "--add":
        create_person(*sys.argv[2::2], simple=False)
    elif sys.argv[1] == "--del":
        delete_person(sys.argv[2])
    elif sys.argv[1] == "--list":
        get_persons()
    elif sys.argv[1] == "--train":
        train_group()
