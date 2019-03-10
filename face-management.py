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
        types = {0: "Base", 1: "Roll", 2: "Yaw", 3: "Video to detect open mouth", 4: "Video to detect closed eyes"}
        multiprocessing.set_start_method('spawn')
        for num, v in enumerate(args):
            cap = cv2.VideoCapture(v)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            starts = [[] for _ in range(7)]
            for ind, i in enumerate(range(0, length, length // 6)):
                starts[ind] = i
            if not starts[6]:
                starts[6] = length - 1
            params = []
            for i in range(7):
                params.append([v, num + 1, starts[i]])
            res = False
            with multiprocessing.Pool(7) as p:
                res = list(p.map(create_frames_hard, params))
            p.terminate()
            clear_files(list(map(lambda x: "test" + str(x) + ".jpg", starts)))
            if False in res:
                print(types[num], "video does not follow requirements")
                exit()
        exist_group(True)
        res = check_all_right(cf.person.create, person_group_id=g_id, name="anonymous")
        face_ids = set()
        if res:
            person_id = res["personId"]
            face_ids = set()
            for path in ["normal" + str(i) + ".jpg" for i in range(1, 6)]:
                res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id, image=path)
                if res:
                    face_ids.add(res["persistedFaceId"])
                else:
                    print("Base video does not follow requirements")
                    clear_files(["normal" + str(i) + ".jpg" for i in range(1, 6)])
                    return
            clear_files(["normal" + str(i) + ".jpg" for i in range(1, 6)])
            if len(args) > 1:
                paths = ["roll" + str(i) + ".jpg" for i in range(-30, 45, 15)]
                for path in paths:
                    res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id, image=path)
                    if res:
                        face_ids.add(res["persistedFaceId"])
                    else:
                        print("Roll video does not follow requirements")
                        return
                clear_files(paths)
            if len(args) > 2:
                paths = ["yaw" + str(i) + ".jpg" for i in range(-20, 30, 10)]
                for path in paths:
                    res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id, image=path)
                    if res:
                        face_ids.add(res["persistedFaceId"])
                    else:
                        print("hren")
                        clear_files(paths)
                        print("Yaw video does not follow requirements")
                        return
                clear_files(paths)
            if len(args) > 3:
                paths = ["mouth.jpg"]
                for path in paths:
                    res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id, image=path)
                    if res:
                        face_ids.add(res["persistedFaceId"])
                    else:
                        print("Video to detect open mouth video does not follow requirements")
                        return
                clear_files(paths)
            if len(args) > 4:
                paths = ["right_eye.jpg", "left_eye.jpg"]
                for path in paths:
                    res = check_all_right(cf.person.add_face, person_id=person_id, person_group_id=g_id, image=path)
                    if res:
                        face_ids.add(res["persistedFaceId"])
                    else:
                        print("Video to detect closed eyes video does not follow requirements")
                        return
                clear_files(paths)
            cf.person_group.update(g_id, user_data="not trained")
            print(len(face_ids), "frames extracted\nPersonId:", person_id + "\nFaceIds\n=======" + "\n" +
                  "\n".join(face_ids))


def create_frames_hard(args):
    video = args[0]
    type = args[1]
    start = args[2]
    types = {1: "normal", 2: "roll", 3: "yaw"}
    steps = {2: 15, 3: 10}
    face_ids = []
    if (type == 2) | (type == 3):
        rotations = [i for i in range(-steps[type] * 2, steps[type] * 3, steps[type])]
    if os.path.exists(video):
        face_ids = []
        cap = cv2.VideoCapture(video)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if length < 5:
            return False
        cap.release()
        for i in range(start, start + length // 6):
            cap = cv2.VideoCapture(video)
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            im_frame = cap.read()[1]
            cv2.imwrite("test" + str(start) + ".jpg", im_frame)
            cap.release()
            if type == 1:
                file = "test" + str(start) + ".jpg"
                cv2.imwrite(file, im_frame)
                rot = check_right_rotation(file, [0], 5)
                good = [0, 1][rot == "0"] + (not get_open_mouth(im_frame)) + sum([g ^ 1 for g in get_open_eyes(im_frame)])
                if good == 4:
                    for path in ["normal" + str(g) + ".jpg" for g in range(1, 6)]:
                        if not os.path.exists(path):
                            cv2.imwrite(path, im_frame)
                            break
                fin = True
                for path in ["normal" + str(g) + ".jpg" for g in range(1, 6)]:
                    if not os.path.exists(path):
                        fin = False
                if fin:
                    return True
            elif type == 2:
                now_rotations = []
                for g in rotations:
                    if not os.path.exists("roll" + str(g) + ".jpg"):
                        now_rotations.append(g)
                file = "test" + str(start) + ".jpg"
                cv2.imwrite(file, im_frame)
                res = check_right_rotation(file, now_rotations, 3, 1)
                if res:
                    now_rotations.remove(int(res))
                    cv2.imwrite("roll" + str(res) + ".jpg", cv2.imread(file))
                fin = True
                for path in ["roll" + str(g) + ".jpg" for g in rotations]:
                    if not os.path.exists(path):
                        fin = False
                if fin:
                    return True
            elif type == 3:
                now_rotations = []
                for g in rotations:
                    if not os.path.exists("yaw" + str(g) + ".jpg"):
                        now_rotations.append(g)
                file = "test" + str(start) + ".jpg"
                cv2.imwrite(file, im_frame)
                res = check_right_rotation(file, now_rotations, 3, 2)
                if res:
                    now_rotations.remove(int(res))
                    cv2.imwrite("yaw" + str(res) + ".jpg", cv2.imread(file))
                fin = True
                for path in ["yaw" + str(g) + ".jpg" for g in rotations]:
                    if not os.path.exists(path):
                        fin = False
                if fin:
                    return True
            elif type == 4:
                res = get_open_mouth(im_frame)
                if res:
                    cv2.imwrite("mouth.jpg", im_frame)
                if os.path.exists("mouth.jpg"):
                    return True
            elif type == 5:
                res = get_open_eyes(im_frame)
                if res[1]:
                    cv2.imwrite("right_eye.jpg", im_frame)
                if res[0]:
                    cv2.imwrite("left_eye.jpg", im_frame)
                if os.path.exists("left_eye.jpg") & os.path.exists("right_eye.jpg"):
                    return True
            else:
                return False
        return True
    else:
        return False


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
        create_person(*sys.argv[2:], simple=False)
    elif sys.argv[1] == "--del":
        delete_person(sys.argv[2])
    elif sys.argv[1] == "--list":
        get_persons()
    elif sys.argv[1] == "--train":
        train_group()
