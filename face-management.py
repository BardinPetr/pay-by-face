#!/usr/bin/env python

from json import load
import cognitive_face as cf
import cv2
import sys
import os


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


def create_frames(file_name):
    cap = cv2.VideoCapture(file_name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = length // 4
    cap.release()
    for i in range(1, 6):
        if i == 1:
            frame = -1
        elif i == 5:
            frame = length - 1
        else:
            frame = step * i - 1
        cap.set(2, frame)
        cap = cv2.VideoCapture(file_name)
        try:
            cv2.imwrite(str(i) + ".jpg", cap.read()[1])
        except:
            f = open(str(i) + ".jpg", "w")
            f.close()
        res = cf.face.detect(str(i) + ".jpg")
        print(res)
        if not res:
            clear(i)
            return False
        cap.release()
    return True


def update_person(video):
    if create_frames(video):
        exist_group()
        res = cf.person.create(person_group_id=g_id, name="anonymous")
        if res:
            person_id = res["personId"]
        face_ids = set()
        for i in range(1, 6):
            res = check_all_right(cf.person.add_face(person_id=person_id, person_group_id=g_id, image=(str(i) + ".jpg")))
            if res:
                face_ids.add(res["persistedFaceId"])
            else:
                break
        print("5 frames extracted\nPersonId:", person_id + "\nFaceIds\n=======" + "\n" + "\n".join(face_ids))
        clear(5)
    else:
        print("Video does not contain any face")


def clear(to):
    for i in range(1, to + 1):
        os.remove(str(i) + ".jpg")


def exist_group():
    try:
        cf.person_group.get(g_id)
    except:
        cf.person_group.create(g_id)


def delete_person(name):
    exist_group()
    flag = False
    res = check_all_right(cf.person.lists(g_id))
    if res:
        for req in res:
            if req["name"] == name:
                flag = True
                person_id = req["personId"]
                break
        if flag:
            check_all_right(cf.person.delete(person_group_id=g_id, person_id=person_id))
            print("Person with id", person_id, "deleted")
        else:
            print('No person with name "' + name + '"')


def train_group():
    exist_group()
    check_all_right(cf.person_group.train(g_id))
    res = check_all_right(cf.person.lists(g_id))
    if res:
        print("Training task for", len(res), "persons started")


def identify_person(video):
    exist_group()
    create_frames(video)
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
        except:
            print("The system is not ready yet")
            return
    res = check_all_right(cf.person.get(person_group_id=g_id, person_id=candidate))
    if res:
        print('The person is "' + res['name'] + '"')


def check_all_right(func=cf.person_group.lists()):
    try:
        return func
    except ConnectionError:
        print("No connection to MS Face API provider")
        exit(5)
    except Exception as e:
        if hasattr(e, 'status_code'):
            if e.status_code == 401:
                print("Incorrect subscription key")
                exit()
        elif hasattr(e, 'code'):
            if e.code == 5:
                exit()


if __name__ == "__main__":
    check_all_right()
    if sys.argv[1] == "--simple-add":
        update_person(sys.argv[2])
    elif sys.argv[1] == "--del":
        delete_person(sys.argv[2])
    elif sys.argv[1] == "--train":
        train_group()
    elif sys.argv[1] == "--identify":
        identify_person(sys.argv[2])
