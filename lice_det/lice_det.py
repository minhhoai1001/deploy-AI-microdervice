import os
import sys
import cv2
import numpy as np
from yolov8 import YOLOv8
import collections

Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])

def tiles_location_gen(img_size, tile_size, overlap=60):
    """Generates location of tiles after splitting the given image according the tile_size and overlap.

    Args:
        img_size (int, int): size of original image as width x height.
        tile_size (int, int): size of the returned tiles as width x height.
        overlap (int): The number of pixels to overlap the tiles.

    Yields:
        A list of points representing the coordinates of the tile in xmin, ymin,
        xmax, ymax.
    """
    tile_width, tile_height = tile_size, tile_size
    img_height, img_width = img_size
    h_stride = tile_height - overlap
    w_stride = tile_width - overlap
    for h in range(0, img_height, h_stride):
        for w in range(0, img_width, w_stride):
            xmin = w
            ymin = h
            xmax = min(img_width, w + tile_width)
            ymax = min(img_height, h + tile_height)
            yield [xmin, ymin, xmax, ymax]

def reposition_bounding_box(bbox, tile_location):
    """Relocates bbox to the relative location to the original image.

    Args:
        bbox (int, int, int, int): bounding box relative to tile_location as xmin,
        ymin, xmax, ymax.
        tile_location (int, int, int, int): tile_location in the original image as
        xmin, ymin, xmax, ymax.

    Returns:
        A list of points representing the location of the bounding box relative to
        the original image as xmin, ymin, xmax, ymax.
    """
    bbox[0] = bbox[0] + tile_location[0]
    bbox[1] = bbox[1] + tile_location[1]
    bbox[2] = bbox[2] + tile_location[0]
    bbox[3] = bbox[3] + tile_location[1]
    return bbox

def non_max_suppression(objects, threshold):
    """Returns a list of indexes of objects passing the NMS.

    Args:
        objects: result candidates.
        threshold: the threshold of overlapping IoU to merge the boxes.

    Returns:
        A list of indexes containings the objects that pass the NMS.
    """
    if len(objects) == 1:
        return [0]

    boxes = np.array([o.bbox for o in objects])
    xmins = boxes[:, 0]
    ymins = boxes[:, 1]
    xmaxs = boxes[:, 2]
    ymaxs = boxes[:, 3]

    areas = (xmaxs - xmins) * (ymaxs - ymins)
    scores = [o.score for o in objects]
    idxs = np.argsort(scores)

    selected_idxs = []
    while idxs.size != 0:

        selected_idx = idxs[-1]
        selected_idxs.append(selected_idx)

        overlapped_xmins = np.maximum(xmins[selected_idx], xmins[idxs[:-1]])
        overlapped_ymins = np.maximum(ymins[selected_idx], ymins[idxs[:-1]])
        overlapped_xmaxs = np.minimum(xmaxs[selected_idx], xmaxs[idxs[:-1]])
        overlapped_ymaxs = np.minimum(ymaxs[selected_idx], ymaxs[idxs[:-1]])

        w = np.maximum(0, overlapped_xmaxs - overlapped_xmins)
        h = np.maximum(0, overlapped_ymaxs - overlapped_ymins)

        intersections = w * h
        unions = areas[idxs[:-1]] + areas[selected_idx] - intersections
        ious = intersections / unions

        idxs = np.delete(
            idxs, np.concatenate(([len(idxs) - 1], np.where(ious > threshold)[0])))

    return selected_idxs

def draw_object(img, obj):
    x1, y1, x2, y2 = obj.bbox
    return cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
def main(image_folder):
    model_path = "models/yolov8m-lice-det.onnx"
    yolov8_det = YOLOv8(model_path, conf_thres=0.2, iou_thres=0.3)

    for filename in (os.listdir(image_folder)):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            objects = []
            image_path = os.path.join(image_folder, filename)
            img = cv2.imread(image_path)

            img_size = img.shape[:2]
            h, w = img_size

            for tile_location in tiles_location_gen(img_size, tile_size=640, overlap=100):
                x1, y1, x2, y2 = tile_location
                tile = img[y1:y2, x1:x2]
                h_tile, w_tile = tile.shape[:2]
                if(h_tile < 640 or w_tile<640 ):
                    blank_img = np.zeros((640, 640, 3), dtype = np.uint8)
                    blank_img[0:h_tile, 0:w_tile] = tile
                    tile = blank_img

                boxes, scores, class_ids = yolov8_det(tile)
                for class_id, box, score in zip(class_ids, boxes, scores):
                    bbox = reposition_bounding_box(box, tile_location)
                    bbox = bbox.astype(int)
                    objects.append(Object(class_id, score, bbox))

            if len(objects) == 0: continue
            idxs = non_max_suppression(objects, 0.3)
            for id in idxs:
                img = draw_object(img, objects[id])
            
            cv2.imwrite(f"../imgs/lice_detect/{filename.replace('png', 'jpg')}", img)

if __name__ == "__main__":
    image_folder = sys.argv[1]
    main(image_folder)
