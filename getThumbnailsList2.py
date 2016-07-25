import json
import os
import numpy as np
import math


with open("facebook_video_1.json") as json_file:
    fb_videos = json.load(json_file)

with open("facebook_pages.json") as json_file:
    fb_pages = json.load(json_file)

channels = {}

for channel in fb_pages:
    channels.update({channel["id"]: channel["likes"]})

# for k, v in channels.iteritems():
#     if v == "0":
#         pr/media/andrusza2/Nowy/Workspace/facebook_database/getFeatureVectorDump.pyint k, v

# print channels

for video in fb_videos:
    folderpath = os.path.join("/media/andrusza2/Nowy/Workspace/thumbnails/thumbnails_old/fb", video["id"])
    if os.path.isdir(folderpath):
        if "thumbnails" not in video:
            continue
        thumbnail = video["thumbnails"][0]
        imgpath = os.path.join(folderpath, thumbnail["id"] + ".jpg")
        if os.path.exists(imgpath):
            for thumb in video["thumbnails"]:
                if (thumb["is_preferred"]):
                    imgpath2 = os.path.join(folderpath, thumb["id"] + ".jpg")
                    if os.path.exists(imgpath2):

                        if (float(channels[video["from"]["id"]]) != 0 and float(video["viewCount"] + 1) != 0):
                            print imgpath, imgpath2, np.log2((float(video["viewCount"]) + 1) / float(channels[video["from"]["id"]]))


                    # with np.errstate(divide='raise'):
                    #     try:
                    #         np.log2(float(video["viewCount"] + 1) / float(channels[video["from"]["id"]]))
                    #     except FloatingPointError:
                    #         print 'Error - viewsC: ', video["viewCount"], ' channels: ', channels[video["from"]["id"]]

                    # print np.log2((video["viewCount"]+1)/3911998.0)