import cv2

ref_path = "reference/chara_n_flat_alpha/chara_ncharaequipmente0676texturev02_c0101e0676_top_n.png"
img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)

# todo: values in the bad ranges need to be adjusted to the nearest acceptable value, so good ranges work.

# these are the bad ranges
mask_1_2 = cv2.inRange(img, 0x12, 0x21)
mask_3_4 = cv2.inRange(img, 0x34, 0x43)
mask_5_6 = cv2.inRange(img, 0x56, 0x65)
mask_7_8 = cv2.inRange(img, 0x78, 0x87)
mask_9_10 = cv2.inRange(img, 0x9A, 0xA9)
mask_11_12 = cv2.inRange(img, 0xBC, 0xCB)
mask_13_14 = cv2.inRange(img, 0xDE, 0xED)

# these are the good ranges.
mask_14_15 = cv2.inRange(img, 0xEE, 0xFF)
mask_12_13 = cv2.inRange(img, 0xCC, 0xDD)
mask_10_11 = cv2.inRange(img, 0xAA, 0xBB)
mask_8_9 = cv2.inRange(img, 0x88, 0x99)
mask_6_7 = cv2.inRange(img, 0x66, 0x77)
mask_4_5 = cv2.inRange(img, 0x44, 0x55)
mask_2_3 = cv2.inRange(img, 0x22, 0x33)
mask_0_1 = cv2.inRange(img, 0x00, 0x11)
masks = [mask_0_1, mask_1_2, mask_2_3, mask_3_4, mask_4_5, mask_5_6, mask_6_7, mask_7_8, mask_8_9, mask_9_10,
         mask_10_11, mask_11_12, mask_12_13, mask_13_14, mask_14_15]
suffix = 0
for mask in masks:
    filename = "output/mask_var_" + str(suffix) + ".png"
    # DO NOT CONVERT COLOR AS IT WILL DAMAGE THE VALUES
    bgra = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    bgra[:, :, 3] = mask
    result = cv2.bitwise_and(img, img, mask=mask)
    cv2.imwrite(filename, bgra)
    suffix += 1
