import sqlite3
import json
import glob

sql = sqlite3.connect("reddit.db")

def parse(n, f, level):
    if "kind" in n and n["kind"] != "Listing" and n["kind"] != "more":
        # insert data
        d = n["data"]
        link_id = d["link_id"] if "link_id" in d else None
        parent_id = d["parent_id"] if "parent_id" in d else None
        body =  d["body"] if "body" in d else None
        title =  d["title"] if "title" in d else None
        num_comments =  d["num_comments"] if "num_comments" in d else None
        url = d["url"] if "url" in d else None
        permalink = d["permalink"] if "permalink" in d else None
        selftext = d["selftext"] if "selftext" in d else None
        sql.execute("INSERT INTO posts (id, created_utc, kind, title, link_id, parent_id, name, \
                                    ups, downs, score, author, num_comments, permalink, url, \
                                    selftext, body, level) \
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (n["kind"] + "_" + d["id"], d["created_utc"], n["kind"], 
                  title, link_id, parent_id, d["name"],
                  d["ups"], d["downs"], d["score"], d["author"], 
                  num_comments, url, permalink, selftext, 
                  body, level))
    # and parse children if available
    try:
        if "kind" in n and n["kind"] != "more":
            if "data" in n and "children" in n["data"]:
                for c in n["data"]["children"]:
                    parse(c, f, level+1)
    except:
        print(n)
        pass
    if "data" in n and "replies" in n["data"] and "data" in n["data"]["replies"]:
        parse(n["data"]["replies"], f, level+1) 

files = glob.glob("comments/??????.json")

from tqdm.auto import tqdm
for i, f in tqdm(enumerate(files), total=len(files)):
    if i % 100 == 0:
        sql.commit()
    with open(f) as fp:
        j = json.load(fp)
    for n in j:
        parse(n, f.replace("comments/", "").replace(".json", ""), 0)

sql.commit()
