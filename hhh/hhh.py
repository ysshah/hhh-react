#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import os
import sqlite3

import praw


DATE_FORMAT = '%m/%d/%y'
RED, GREEN, RESET = '\u001b[31m', '\u001b[32m', '\u001b[0m'


def getDB():
    return sqlite3.connect('/Users/yash/Documents/hhh/fresh.db')


def getSubreddit():
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent=os.environ['REDDIT_USER_AGENT']
    )
    sub = reddit.subreddit('hiphopheads')
    return sub


def makeDB():
    db = getDB()
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY, title TEXT, url TEXT, create_time INT, score INT)')
    db.commit()
    db.close()


def deleteDuplicatePosts():
    db = getDB()
    c = db.cursor()
    c.execute('DELETE FROM posts WHERE rowid NOT IN (SELECT MAX(rowid) FROM posts GROUP BY id)')
    db.commit()
    db.close()


def backfill(sub):
    db = getDB()
    c = db.cursor()
    duration = timedelta(days=10)

    date = datetime(2015, 1, 10)
    for _ in range(100):
        fetchAndInsertPosts(sub, db, c, date, duration)
        date -= duration

    db.close()


def update(sub):
    db = getDB()
    c = db.cursor()
    duration = timedelta(days=10)

    now = datetime.now()
    timestamp = c.execute('SELECT MAX(create_time) FROM posts').fetchone()[0]
    latest = datetime.fromtimestamp(timestamp)
    print('Latest post in fresh.db on', latest.date())

    date = latest - 3 * duration
    while date < now:
        fetchAndInsertPosts(sub, db, c, date, duration)
        date += duration

    db.close()


def fetchAndInsertPosts(sub, db, c, date, duration):
    posts = fetchTopPostsFromDate(sub, date, duration)
    values = [(p.id, p.title, p.url, int(p.created_utc), p.score) for p in posts]
    print('Retrieved {} posts between {} and {}'.format(
        len(values), date.date(), (date + duration).date()))
    c.executemany('REPLACE INTO posts VALUES (?, ?, ?, ?, ?)', values)
    db.commit()


def fetchTopPostsFromDate(sub, start, duration):
    end = start + duration
    query = "(and timestamp:{:.0f}..{:.0f} title:'[fresh')".format(start.timestamp(), end.timestamp())
    return sub.search(query, sort='top', syntax='cloudsearch', limit=None)


def listTopPostsInRange(start, end):
    db = getDB()
    c = db.cursor()

    result = c.execute(
        'SELECT * FROM posts WHERE ? < create_time AND create_time < ? ORDER BY score',
        (start.timestamp(), end.timestamp()))

    for row in result:
        post_id, title, url, timestamp, score = row
        printPost(post_id, title, url, score)

    db.close()


def fetchTopPosts(sub, time_filter):
    posts = sub.search('title:[fresh', sort='top', time_filter=time_filter)
    for p in reversed(list(posts)):
        printPost(p.id, p.title, p.url, p.score)


def printPost(post_id, title, url, score):
    if 'video' in title.lower():
        color = RED
    elif 'album' in title.lower():
        color = GREEN
    else:
        color = ''

    print('{}{:5d} | {} | https://redd.it/{}'.format(color, score, title, post_id))
    print('      | {}{}'.format(url, RESET))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dates', nargs='*')
    parser.add_argument('-t', '--time_filter', default='week')
    parser.add_argument('-u', '--update', action='store_true')

    args = parser.parse_args()
    if args.dates:
        start = datetime.strptime(args.dates[0], DATE_FORMAT)
        if len(args.dates) == 1:
            end = start + timedelta(days=1)
        elif len(args.dates) == 2:
            try:
                end = datetime.strptime(args.dates[1], DATE_FORMAT)
            except ValueError:
                end = start + timedelta(days=int(args.dates[1]))
        listTopPostsInRange(start, end)
        print('\nTop FRESH posts between {} and {}'.format(start.date(), end.date()))
    elif args.update:
        update(getSubreddit())
    else:
        print('Retrieving top FRESH posts this {}...'.format(args.time_filter))
        fetchTopPosts(getSubreddit(), args.time_filter)


if __name__ == '__main__':
    main()
