try:
    import dlib
except:
    pass

from eth_account import Account
from math import ceil
from json import load

try:
    from imutils import face_utils
except:
    pass
from web3 import Web3, HTTPProvider
import uuid
import sha3
import cognitive_face as cf
import os
import time
import cv2


from random import choice, randint



def parceJson(file_path):
    try:
        with open(file_path) as f:
            content = load(f)
        return content
    except FileNotFoundError:
        return None


def toAddress(priv_key):
    prefix = '' if priv_key.startswith('0x') else '0x'
    return Account.privateKeyToAccount(prefix + priv_key).address


def keccak256(data):
    k = sha3.keccak_256()
    k.update(data)
    return k


def get_private_key(uid, pin):
    pin = map(int, str(pin))
    u = uuid.UUID(uid)
    a = keccak256("".encode())
    for _ in range(4):
        a = keccak256(a.digest() + u.bytes + pin.__next__().to_bytes(1, "little"))
    return a.hexdigest()


nominal = ['wei', 'kwei', 'mwei', 'gwei', 'szabo', 'finney', 'poa']


def weighing(val):
    k = min(ceil(len(str(val)) / 3) - 1, 6)
    val = round(int(val) / 10 ** (k * 3), 6)
    return str(val).rstrip('0').rstrip('.'), nominal[k] if val != 0 else "poa"


def get_balance(web3, addr):
    return web3.eth.getBalance(addr)


def get_balance_by_priv(web3, priv):
    return web3.eth.getBalance(toAddress(priv))


def clear(to):
    for i in range(1, to + 1):
        if os.path.exists(str(i) + ".jpg"):
            os.remove(str(i) + ".jpg")


def clear_files(names):
    for name in names:
        if os.path.exists(name):
            os.remove(name)


def exist_group(create=False):
    g_id = parceJson("faceapi.json")["groupId"]
    if check_all_right(cf.person_group.get, g_id):
        return True
    else:
        if create:
            check_all_right(cf.person_group.create, g_id, user_data="null")
        return False


def check_all_right(func=cf.person_group.lists, *args, **kwargs):
    try:
        return func(*args, **kwargs)
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
                    return check_all_right(func, *args, **kwargs)
        elif hasattr(e, 'code'):
            if e.code == 5:
                exit()
            elif e.code == "PersonGroupNotFound":
                return False
            elif e.code == "LargePersonGroupTrainingNotFinished":
                return False


def create_frames_simple(video):
    try:
        video = (video + [])[0]
    except:
        pass
    if os.path.exists(video):
        face_ids = []
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
            cap = cv2.VideoCapture(video)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            try:
                cv2.imwrite(str(i) + ".jpg", cap.read()[1])
            except:
                f = open(str(i) + ".jpg", "w")
                f.close()
            res = check_all_right(cf.face.detect, str(i) + ".jpg")
            if res:
                face_ids.append(res[0]["faceId"])
            else:
                clear(i)
                return False
            cap.release()
        return face_ids
    else:
        return False


def get_open_eyes(frame):
    eyes = [False, False]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./opt/shape_predictor_68_face_landmarks.dat")
    rects = detector(gray, 0)
    eye_ar_thresh = 0.2
    for ind, rect in enumerate(rects):
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        left_eye = shape[lStart:lEnd]
        right_eye = shape[rStart:rEnd]
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        if right_ear < eye_ar_thresh:
            eyes[1] = True
        if left_ear < eye_ar_thresh:
            eyes[0] = True
    return eyes


def get_open_mouth(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./opt/shape_predictor_68_face_landmarks.dat")
    rects = detector(gray, 0)
    eye_ar_thresh = 0.4
    for ind, rect in enumerate(rects):
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        lStart += 12
        mouth_dots = shape[lStart:lEnd]
        mar = mouth_aspect_ratio(mouth_dots)
        if mar > eye_ar_thresh:
            return True
    return False


def mouth_aspect_ratio(mouth):
    a = euclidean(mouth[1], mouth[7])
    b = euclidean(mouth[2], mouth[6])
    c = euclidean(mouth[3], mouth[5])
    d = euclidean(mouth[0], mouth[4])

    mar = (a + b + c) / (2.0 * d)

    return mar


def eye_aspect_ratio(eye):
    a = euclidean(eye[1], eye[5])
    b = euclidean(eye[2], eye[4])
    c = euclidean(eye[0], eye[3])

    ear = (a + b) / (2.0 * c)

    return ear


def check_right_rotation(image, right_rotation, max_error, type=0):
    check = {0: ["roll", "yaw"], 1: ["roll"], 2: ["yaw"]}
    res = check_all_right(cf.face.detect, image, attributes="headPose")
    rig = 0
    if res:
        rot = res[0]["faceAttributes"]["headPose"]
        for ch in check[type]:
            for right in right_rotation:
                if type == 0:
                    if (right - max_error) <= rot[ch] <= (right + max_error):
                        pass
                    else:
                        return False
                else:
                    if (right - max_error) <= rot[ch] <= (right + max_error):
                        rig = right
                        return str(rig)
        if type == 0:
            return str(rig)
        else:
            return False
    else:
        return False


def euclidean(p, q):
    sum_sq = 0.0
    for i in range(len(p)):
        sum_sq += (p[i] - q[i])**2
    return sum_sq ** 0.5


def get_predict(faces):
    g_id = parceJson("faceapi.json")["groupId"]
    exist_group(True)
    res = check_all_right(cf.face.identify, face_ids=faces, person_group_id=g_id)
    if res:
        if any(list(map(lambda x: len(x["candidates"]) == 0, res))):
            return False
        candidates = set(map(lambda x: x["personId"], list(
            map(lambda can: list(filter(lambda x: x["confidence"] >= 0.5, can["candidates"]))[0],
                res))))
        if len(candidates) == 1:
            return candidates.pop()
        else:
            return False
