from __future__ import (
    absolute_import,
    division,
    print_function,
)


from collections import namedtuple
import time

import requests


Post = namedtuple('Post', ['message', 'comments'])


def _read_all_messages(feed):
    posts = []
    for post_object in feed['data']:
        message = post_object.get('message')

        comments = None
        if post_object.get('comments'):
            # Extract only the "message" fields from each comment's "data" object
            comments = map(lambda comment: comment['message'],
                           post_object['comments']['data'])

        posts.append(Post(message=message, comments=comments))

    return posts


def _next_feed_page(feed, access_token):
    next_url = feed['paging']['next']
    next_url = next_url + '&access_token=' + access_token

    response = requests.get(next_url)
    if response.status_code != requests.codes.ok:
        raise response.raise_for_status()

    return response.json()


def _crawl_feed_from(feed, access_token, page_limit=20, throttle=1):
    # TODO: Unicode <-> ASCII bugs? :/
    posts = []
    for _ in xrange(page_limit):
        feed = _next_feed_page(feed, access_token)
        posts.extend(_read_all_messages(feed))
        time.sleep(throttle)

    return posts


def _fetch_feed(graph, object_id, fields=None, limit=50):
    fields = fields or ['message', 'comments.fields(message)']
    args = {
        "fields": ','.join(fields),
        "limit": limit,
        }
    return graph.get_connections(object_id, 'feed', **args)


def crawl_feed(graph, object_id, fields=None, item_limit=50, page_limit=21, throttle=1):
    feed = _fetch_feed(graph, object_id, fields=fields, limit=item_limit)
    posts = _read_all_messages(feed)

    if page_limit and page_limit > 1:
        time.sleep(throttle)
        posts.extend(_crawl_feed_from(
            feed,
            graph.access_token,
            page_limit=20,
            throttle=throttle,
        ))
    return posts


