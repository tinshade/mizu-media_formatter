from lib2to3.fixes import fix_dict
import os
import pika
import json


def queue_upload(file_id, channel, access):
    message = {
        "video_file_id": str(file_id),
        "mp3_file_id": None,
        "username": access.get("username", "Anonymous"),
    }
    try:
        channel.basic_publish(
            exchange="",
        )
    except Exception as e:
        print(e)
        return "Internal Server Error", 500


def upload(file, fs, channel, access):
    """ """
    try:
        file_id = fs.put(file)

    except Exception as e:
        print(e)
        return "Internal Server Error", 500
