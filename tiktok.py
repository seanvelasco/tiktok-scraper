import asyncio
import aiohttp

async def get_comment(session, post_id, count, cursor):
    url = "https://www.tiktok.com/api/comment/list/"
    params = {
        "aweme_id": post_id,
        "count": count,
        "cursor": cursor,
        "os": "mac",
        "region": "US",
        "screen_height": "900",
        "screen_width": "1440",
        "X-Bogus": "DFSzsIVOxrhAN9fbtfB5EX16ZwHH"
    }
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0"
    }
    async with session.get(url, params=params, headers=headers) as response:
        response.raise_for_status()
        body =  await response.json()
        print(body)
        return body

async def get_replies(session, post_id, comment_id, count):
    url = "https://www.tiktok.com/api/comment/list/reply"
    params = {
        "comment_id": comment_id,
        "count": count,
        "item_id": post_id
    }
    async with session.get(url, params=params) as response:
        response.raise_for_status()
        body =  await response.json()
        print(body)
        return body

# def get_and_process_avatar(url):
#     response = requests.get(url)
#     response.raise_for_status()
#     return base64.b64encode(response.content).decode('utf-8')

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
        processed_reply["parent_user"] = reply["reply_to_userid"]
        processed_reply["parent_comment"] = reply["reply_to_reply_id"]

    return processed_reply

def format_processed_post(comments):
    for comment in comments:
        if "replies" in comment:
            for reply in comment["replies"]:
                if "parent_comment" in reply:
                    # Make this a dict for more efficient lookups
                    parent = next((p for p in comment["replies"] if p.get("id") == reply["parent_comment"]), None)
                    if parent:
                        if "replies" not in parent:
                            parent["replies"] = []
                        parent["replies"].append(reply)
                        comment["replies"].remove(reply)
    return comments

async def process_post(post_id):
    async with aiohttp.ClientSession() as session:
        comments = []
        offset = 0
        limit = 50

        while True:
            post = await get_comment(session, post_id, limit, offset)
            if not post or "comments" not in post:
                break
            comments.extend(post["comments"])
            if post["has_more"] != 1:
                break
            offset += limit

        comments = [process_comment(comment) for comment in comments]

        # for comment in comments:
        #     if comment["reply_count"] > 0:
        #         replies = get_replies(post_id, comment["id"], comment["reply_count"])
        #         replies = [process_reply(reply) for reply in replies["comments"]]
        #         comment["replies"] = replies

        tasks = []

        for comment in comments:
            if comment["reply_count"] > 0:
                task = asyncio.create_task(get_replies(session, post_id, comment["id"], comment["reply_count"]))
                tasks.append((comment, task))

        for comment, task in tasks:
            replies = await task
            comment["replies"] = [process_reply(reply) for reply in replies["comments"]]

        return format_processed_post(comments)