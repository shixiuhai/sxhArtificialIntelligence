import cv2
import base64
def cv2img_to_base64(cv2imgNp):
    # img = cv2.imread('test.jpg')
    # _, im_arr = cv2.imencode('.jpg', img)  # im_arr: image in Numpy one-dim array format.
    # im_bytes = im_arr.tobytes()
    # return base64.b64encode(im_bytes)
    image = cv2.imencode('.jpg',cv2imgNp)[1]
    return str(base64.b64encode(image))[2:-1]

imgBase64=cv2img_to_base64(cv2.imread("2.png"))
print(base64.b64decode(imgBase64))
with open("4.png","wb+") as f:
    f.write(base64.b64decode(imgBase64))