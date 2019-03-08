#!/usr/bin/env python

from json import load
import cognitive_face as cf
import cv2
import sys
import os
import time


def parse_json(file_path):
    try:
        with open(file_path) as f:
            content = load(f)
        return content
    except FileNotFoundError:
        return None


api_data = parse_json("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]


def create_frames(video):
    cap = cv2.VideoCapture(video)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if length < 5:
        return False
    step = length // 4
    cap.release()
    for i in range(1, 6):
        if i == 1:
            frame = -1
        elif i == 5:
            frame = length - 1
        else:
            frame = step * (i - 1)
        cap.set(2, frame)
        cap = cv2.VideoCapture(video)
        try:
            cv2.imwrite(str(i) + ".jpg", cap.read()[1])
        except:
            f = open(str(i) + ".jpg", "w")
            f.close()
        res = check_all_right(cf.face.detect, str(i) + ".jpg")
        if not res:
            clear(i)
            return False
        cap.release()
    return True


def create_person(video, simple=True):
    if simple:
        if create_frames(video):
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
        pass


def clear(to):
    for i in range(1, to + 1):
        os.remove(str(i) + ".jpg")


def exist_group(create=False):
    if check_all_right(cf.person_group.get, g_id):
        return True
    else:
        if create:
            check_all_right(cf.person_group.create, g_id, user_data="null")
        return False


def delete_person(person_id):
    if exist_group():
        res = check_all_right(cf.person.lists, g_id)
        if res:
            if person_id in res:
                check_all_right(cf.person.delete, person_group_id=g_id, person_id=person_id)
                check_all_right(cf.person_group.update, g_id, user_data="not trained")
                print("Person with id deleted")
            else:
                print("The person does not exist")
    else:
        print("The group does not exist")


def train_group():
    if exist_group():
        res = check_all_right(cf.person_group.get, g_id)
        if res.setdefault("userData") == "trained":
            print("Already trained")
        elif res.setdefault("userData") == "null":
            print("There is nothing to train")
        elif res.setdefault("userData") == "not trained":
            check_all_right(cf.person_group.train, g_id)
            while not check_all_right(cf.person_group.update, g_id, user_data="trained"):
                pass
            print("Training successfully started")
    else:
        print("There is nothing to train")


def get_predict(imgs):
    exist_group(True)
    faces = []
    for img in imgs:

        faces.append()
    # new_candidate = list(filter(lambda x: x["confidence"] >= 0.5,
    #                             cf.face.identify(face_ids=[cf.face.detect(str(i) + ".jpg")[0]["faceId"]],
    #                                              person_group_id=g_id)[0]["candidates"]))


def idetify_person(video, simple=True):
    if exist_group():
        res = check_all_right(cf.person_group.get, g_id)
    else:
        print("The service is not ready")


def find_person(video, simple=True):
    exist_group()
    if simple:
        if is_trained():
            if create_frames(video):
                for i in range(1, 6):
                    try:
                        new_candidate = list(filter(lambda x: x["confidence"] >= 0.5,
                                                    cf.face.identify(face_ids=[cf.face.detect(str(i) + ".jpg")[0]["faceId"]],
                                                                     person_group_id=g_id)[0]["candidates"]))
                        if new_candidate:
                            if i == 1:
                                candidate = new_candidate[0]["personId"]
                            else:
                                if candidate != new_candidate[0]["personId"]:
                                    print("The person cannot be identified")
                                    return
                        else:
                            print("The person cannot be identified")
                            return
                    except IndexError:
                        print("The person cannot be identified")
                        return
                res = check_all_right(cf.person.get, person_group_id=g_id, person_id=candidate)
                if res:
                    open("actions.json", "w").write(str({"id": res["personId"]}))
            else:
                print("The person cannot be identified")
        else:
            print("The system is not ready yet")
    else:
        pass


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
        res = check_all_right(cf.person.lists, person_group_id=g_id)
        if res:
            print("Persons IDs:")
            for i in res:
                print(i["personId"])
        else:
            print("No persons found")
    else:
        print("The group does not exist")
        cf.person_group.update()


def check_all_right(func=cf.person_group.lists, *args, **kwargs):
    try:
        if args:
            if kwargs:
                return func(args, kwargs)
            else:
                return func(args)
        elif kwargs:
            return func(kwargs)
        else:
            return func()
    except ConnectionError:
        print("No connection to MS Face API provider")
        exit(5)
    except Exception as e:
        if hasattr(e, 'status_code'):
            if e.status_code == 401:
                print("Incorrect subscription key")
                exit()
            elif e.status_code == 404:
                return False
            elif e.status_code == 409:
                pass
            elif e.status_code == 429:
                if hasattr(e, 'message'):
                    time.sleep(int(e.message.split("Try again in ")[1].split()[0]))
        elif hasattr(e, 'code'):
            if e.code == 5:
                exit()
            elif e.code == "PersonGroupNotFound":
                return False
            elif e.code == "LargePersonGroupTrainingNotFinished":
                return False


if __name__ == "__main__":
    check_all_right()
    if sys.argv[1] == "--simple-add":
        create_person(sys.argv[2])
    elif sys.argv[1] == "--del":
        delete_person(sys.argv[2])
    elif sys.argv[1] == "--list":
        get_persons()
    elif sys.argv[1] == "--train":
        train_group()
    elif sys.argv[1] == "--find":
        find_person(sys.argv[2], os.path.exists("actions.json"))
