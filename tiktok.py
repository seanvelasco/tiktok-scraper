import requests
import base64

def get_comment(post_id, count, cursor):
    response = requests.get(f"https://www.tiktok.com/api/comment/list/?aweme_id={post_id}&count={count}&cursor={cursor}&os=mac&region=US&screen_height=900&screen_width=1440&X-Bogus=DFSzsIVOxrhAN9fbtfB5EX16ZwHH", headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0"
})
    response.raise_for_status()
    return response.json()

def get_replies(post_id, comment_id, count):
    response = requests.get(f"https://www.tiktok.com/api/comment/list/reply/?comment_id={comment_id}&count={count}&item_id={post_id}")
    response.raise_for_status()
    return response.json()

def get_and_process_avatar(url):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

def process_user(user):
    processed_user = {
        "id": user["uid"],
        "username": user["unique_id"],
        "nickname": user["nickname"],
        "bio": user["signature"],
        "region": user["region"],
        "avatar_uri": user["avatar_uri"],
        "avatar": user["avatar_thumb"]["url_list"][0]
    }
    return processed_user

def process_comment(comment):
    return {
    "user": process_user(comment["user"]),
    "id": comment["cid"],
    "created": comment["create_time"],
    "likes": comment["digg_count"],
    "reply_count": comment["reply_comment_total"],
    "text": comment["text"],
    "liked_by_creator": comment["is_author_digged"]
    }

def process_reply(reply):
    processed_reply =  {
    "user": process_user(reply["user"]),
    "id": reply["cid"],
    "created": reply["create_time"],
    "likes": reply["digg_count"],
    "text": reply["text"],
    "liked_by_creator": reply["is_author_digged"],
    "parent_comment": reply["reply_id"]
    }

    if "reply_to_userid" in reply and "reply_to_reply_id" in reply:
        processed_reply["parent_user"] = reply["reply_to_userid"],
        processed_reply["parent_comment"] = reply["reply_to_reply_id"]
    return processed_reply

def format_processed_post(comments):
    for comment in comments:
        if "replies" in comment:
            for reply in comment["replies"]:
                if "parent_comment" in reply:
                    parent = next((p for p in comment["replies"] if p.get("id") == reply["parent_comment"]), None)
                    if parent:
                        if "replies" not in parent:
                            parent["replies"] = []
                        parent["replies"].append(reply)
                        comment["replies"].remove(reply)
    return comments

def process_post(post_id):

    comments = []

    has_more = True
    offset = 0
    limit = 50

    while(has_more):
        post = get_comment(post_id, limit, offset)
        comments.extend(post["comments"])
        if post["has_more"] == 1:
             offset += limit
        else:
            has_more = False

    comments = [process_comment(comment) for comment in comments]

    for comment in comments:
        if comment["reply_count"] > 0:
            replies = get_replies(post_id, comment["id"], comment["reply_count"])
            replies = [process_reply(reply) for reply in replies["comments"]]
            comment["replies"] = replies

    return comments