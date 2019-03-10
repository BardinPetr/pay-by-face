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
        for num, v in enumerate(args):
            cap = cv2.VideoCapture(v)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            starts = [[] for _ in range(5)]
            for ind, i in enumerate(range(0, length, length // 4)):
                starts[ind] = i
            starts[4] = length - 1
            params = []
            for i in range(5):
                params.append([v, num + 1, starts[i]])
            multiprocessing.set_start_method('spawn')
            res = False
            with multiprocessing.Pool(5) as p:
                res = p.map(create_frames_hard, params)
            p.terminate()
            cleat_tests(list(map(str, starts)))
            if not res:
                print("Base video does not follow requirements")
                exit()


def create_frames_hard(args):
    video = args[0]
    type = args[1]
    start = args[2]
    types = {1: "normal", 2: "roll", 3: "yaw"}
    steps = {1: 15, 2: 20}
    if os.path.exists(video):
        face_ids = []
        cap = cv2.VideoCapture(video)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if length < 5:
            return False
        cap.release()
        for i in range(start, start + length // 4):
            print(i)
            cap = cv2.VideoCapture(video)
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            im_frame = cap.read()[1]
            cv2.imwrite("test" + str(start) + ".jpg", im_frame)
            cap.release()
            if type == 1:
                file = "test" + str(start) + ".jpg"
                cv2.imwrite(file, im_frame)
                res = check_all_right(cf.face.detect, file, )
                if res:
                    face_ids.append(res[0]["faceId"])
                else:
                    clear(i)
                    return False
                fin = True
                for path in ["normal" + str(i) + ".jpg" for i in range(1, 6)]:
                    if not os.path.exists(path):
                        fin = False
                if fin:
                    return True
            elif (type == 2) or (type == 3):
                cv2.imwrite("test.jpg", im_frame)
                res = check_all_right(cf.face.detect, "test.jpg")
                if res:
                    face_ids.append(res[0]["faceId"])
                else:
                    clear(i)
                    return False
            elif type == 4:
                res = get_open_eyes(im_frame)
                if res[1]:
                    cv2.imwrite("right_eye.jpg", im_frame)
                if res[0]:
                    cv2.imwrite("left_eye.jpg", im_frame)
                if os.path.exists("left_eye.jpg") & os.path.exists("right_eye.jpg"):
                    return True
            else:
                print("asdasd")
        return face_ids
    else:
        return False


def cleat_tests(names):
    for name in names:
        if os.path.exists("test" + name + ".jpg"):
            os.remove("test" + name + ".jpg")


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
