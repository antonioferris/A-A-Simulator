import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

import pytesseract
from pytesseract import image_to_string
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import numpy as np

"""
TODO: Use alpha channel for masking / weight templates
TODO: Add number recognition
TODO: Extend algorithm to allow searching for all units at once
TODO: Add territory detection
"""

def match_template(img, template_name, do_rgb):
    """

    Args:
        img (opencv Image): Image to match to. Should be grey if do_rgb is false.
        template_name (string): name of the template to match. template_name.png should exist
        do_rgb (bool): whether to match with color or not.

    Returns:
        _type_: _description_
    """
    if do_rgb:
        template = cv.imread(f"{template_name}.png")
        w, h = template.shape[::-1][1:]

        imgR, imgG, imgB = cv.split(img)
        templateR, templateG, templateB = cv.split(template)

        resultB = cv.matchTemplate(imgR, templateR, cv.TM_CCOEFF_NORMED)
        resultG = cv.matchTemplate(imgG, templateG, cv.TM_CCOEFF_NORMED)
        resultR = cv.matchTemplate(imgB, templateB, cv.TM_CCOEFF_NORMED)

        result = resultB + resultG + resultR
    else:
        template = cv.imread(f"{template_name}.png", 0)
        w, h = template.shape[::-1]

        result = cv.matchTemplate(img,template,cv.TM_CCOEFF_NORMED)

    return result

def match_distinct(img_name, template_names, do_rgb, threshold=0.8, spacing=3):
    img = cv.imread("full.png")
    if not do_rgb:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    results = [match_template(img, name, do_rgb) for name in template_names]
    locs = {name : [] for name in template_names}
    skip = set()

    if do_rgb: # triple the channels means triple the threshold.
        threshold = 3 * threshold

    H, W = results[0].shape
    for y in range(H):
        for x in range(W):
            if (x, y) in skip:
                continue
            max_idx = np.argmax([result[y, x] for result in results])
            # make sure that the loc is beyond our threshold
            if results[max_idx][y, x] >= threshold:
                print(f"Adding to locs {template_names[max_idx]} {x}, {y}")
                locs[template_names[max_idx]].append((x, y))
                # now, make sure that we don't look for matches in this area again
                for y2 in range(y, y + spacing + 1):
                    for x2 in range(x - spacing, x + spacing + 1):
                        skip.add((x2, y2))

    return locs

def rectangle_locs(img, locs, color, h, w):
    for pt in locs:
        cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), color, 1)


def main():
    locs = match_distinct("full.png", ["german_inf", "russian_inf"], do_rgb=False)
    print(len(locs["german_inf"]), "german infantry found")
    print(len(locs["russian_inf"]), "russian infantry found")
    print()
    img = cv.imread("full.png")
    rectangle_locs(img, locs["german_inf"], (255, 0, 0), 23, 23)
    rectangle_locs(img, locs["russian_inf"], (0, 0, 255), 23, 23)

    cv.imwrite('res_both_grey.png',img)

    # sz_icon = 23
    # sz_num = 16
    # i = 0
    # for pt in german_inf:
    #     # cv.rectangle(img, pt, (pt[0] + w1, pt[1] + h1), (0,0,255), 2)
    #     offset_w, offset_h = 8, 6
    #     x1, y1 = (pt[0] + sz_icon - offset_w         , pt[1] + sz_icon - offset_h)
    #     x2, y2 = (pt[0] + sz_icon - offset_w + sz_num, pt[1] + sz_icon - offset_h + sz_num)

    #     num = img[y1:y2, x1:x2]
    #     cv.imwrite(f"num_{i}.png", num)
    #     i += 1

    #     cv.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 1)



    # for pt in russian_inf:
    #     cv.rectangle(img, pt, (pt[0] + w2, pt[1] + h2), (255,0,0), 2)

if __name__ == '__main__':
    main()

