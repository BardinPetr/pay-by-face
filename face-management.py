#!/usr/bin/env python

from json import load
import cognitive_face as cf
import cv2
import sys
import os
import time
from tools import *


api_data = parceJson("faceapi.json")
key = api_data["key"]
base_url = api_data["serviceUrl"]
cf.Key.set(key)
cf.BaseUrl.set(base_url)
g_id = api_data["groupId"]


def create_person(*args, simple=True):
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
        if create_frames_simple(args[0]):
            exist_group(True)



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
