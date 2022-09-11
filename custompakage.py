import os
import datetime
import snowflake.connector
import pymongo
import comments
import base64
from urllib.request import urlopen

global client
global cursor


def create_connection():
    global cursor
    conn = snowflake.connector.connect(user=os.environ.get("snowuser"), password=os.environ.get("snowpass"),
                                       account=os.environ.get("snowacc"),
                                       warehouse="TEMP", database="youtubescrapper")

    return conn


def create_mongo_conn():
    global client
    client = pymongo.MongoClient(os.environ.get("mongo"))
    return client


def push_channel_info(args):
    global cursor
    bucket = args
    try:
        conn = create_connection()
        # time.sleep(2)
        try:
            uid = bucket["Channel Details"]["Channel Link"].split("/")[-2].replace("-", "")
            name = bucket["Channel Details"]["Channel Name"]
            link = bucket["Channel Details"]["Channel Link"]
            thum = bucket["Channel Details"]["Channel Thumbnail"]
            subs = bucket["Channel Details"]["Total Subscriber"]
            channel_thum = thum
        except Exception as e:
            print("Error occurred in getting data from bucket", e)
            raise Exception("Error occurred in getting data from bucket. Exception:", e)
        try:
            date = datetime.datetime.now().strftime("%d%B%Y %X")
        except Exception as e:
            print("unable to grab data", e)
            date = "Not available"

        cursor = conn.cursor()
        print("cursor created successfully")
        cursor.execute("use warehouse temp")
        print("warehouse selected")

        create_table_youtubers(cursor)
        create_youtuber_videos_table(cursor, uid)
        exists = check_if_exists(cursor, column="channel_uid", value=uid, table="youtubers")
        if exists:
            print("record already present")
            drop_record(cursor, col="channel_uid", val=uid)
        else:
            print("record not present")
        try:
            q1 = "INSERT INTO youtubescrapper.public.youtubers values('{a}','{b}','{c}','{d}','{e}','{f}')" \
                .format(a=uid, b=name, c=link, d=thum, e=subs, f=date)
            print(q1)
            cursor.execute(q1)
            print("success")
        except Exception as e:
            print("oops", e)
            raise Exception("problem in creating database youtubers, Exception :", e)
        try:
            push_video_list(cursor, uid, bucket["Video Details"], channel_thum)
            print("inserted successfully")
        except Exception as e:
            print("went wrong", e)
            raise Exception(" error in pushing videos,", e)

        # pushing videos list

        return "pushed info successfully"
    except Exception as e:
        print(e)
        return "unable to push info"
    finally:
        cursor.close()


def create_table_youtubers(args):
    global cursor
    cursor = args
    q0 = str()
    try:
        q0 = '''create table if not exists youtubescrapper.public.youtubers(
                               channel_uid varchar(50),
                               channel_name varchar(50),
                               channel_link varchar(254),
                               channel_thumbnail varchar(254),
                               total_subscriber varchar(50),
                               date_fetched_on varchar(50))'''
        cursor.execute(q0)
        print(q0)
        print("table youtubers created successfully or present already")
    except Exception as e:
        print("Unable to create youtubers table", e)
        print(q0)
        raise Exception("Error occurred in creating table youtubers", e)
    finally:
        return None


def push_video_list(args, unique_id, video_list, channel_thum):
    global cursor
    cursor = args
    uid = unique_id
    bucket = video_list
    channel_thum = channel_thum

    try:
        print("pushing videos list in db")
        for i in bucket:
            a = i["Video ID"]
            b = i["Video Title"].replace("'", "")
            c = i["Video Link"]
            d = i["Video Thumbnail"]
            e = i["Upload Date"]
            f = i["Video Duration"]
            g = i["Video Views"]
            h = "not updated yet"
            i_ = "not updated yet"
            j = "not updated yet"

            q = '''INSERT INTO {uid} values({a},'{b}','{c}','{d}','{e}','{f}','{g}','{h}','{i}','{j}')'''. \
                format(uid=uid, a=a, b=b, c=c, d=d, e=e, f=f, g=g, h=h, i=i_, j=j)
            print(q)
            cursor.execute(q)
            print("success pushed video {a} into db")
            try:
                print("attempting  fetch comments")
                video_data = comments.begin_comments(c)
                print(a, "video comments", video_data)
                v1 = video_data["Video Info"]["Total Likes"]
                v2 = str(video_data["Video Info"]["Total Comments"])
                v3 = video_data["Video Info"]["Fetched comments"]
                try:
                    q3 = '''UPDATE {uid} SET total_likes = '{a}', total_comments = '{b}', fetched_comments = '{c}' WHERE
                    video_id = {d}''' \
                        .format(uid=uid, a=v1, b=v2, c=v3, d=a)
                    print(q3)
                    cursor.execute(q3)
                    print("successfully inserted likes and comment count")
                    try:
                        print("trying to push comments")
                        comments_push(video_data, uid, a, d, channel_thum)
                    except Exception as e:
                        print("problem occurred during pushing comment", e)

                except Exception as e:
                    print("error in inserting extra data", e)

            except Exception as e:
                print("line 137", e)

    except Exception as e:
        print("error in pushing into videos db", e)
    return None


def create_youtuber_videos_table(args, youtuber_uid):
    global cursor
    cursor = args
    table_name = youtuber_uid
    try:
        q = '''create table if not exists youtubescrapper.public.{a}(
                        video_id         int,
                        video_title      varchar(110),
                        video_link       varchar(150),
                        video_thumbnail  varchar(150),
                        uploade_date     varchar(50),
                        duration         varchar(50),
                        total_views      varchar(50),
                        total_likes      varchar(50),
                        total_comments   varchar(50),
                        fetched_comments varchar(50))'''.format(a=table_name)
        print(q)
        cursor.execute(q)
        cursor.execute("TRUNCATE TABLE youtubescrapper.public.{a}".format(a=youtuber_uid))
    except Exception as e:
        print("error create youtubers video", e)
        raise Exception("problem in creating table {a}. error : {e}".format(a=table_name, e=e))
    finally:
        pass
    return None


def check_if_exists(cursor_args, column=str(), value=str(), table=str()):
    global cursor
    cursor = cursor_args
    col = column
    value = value
    table = table
    print("i am here", col, value)
    try:

        l = []
        cursor.execute("select {col} from youtubescrapper.public.{table}".format(col=col, table=table))
        for i in cursor.fetchall():
            l.append(i[0])
        print("method check if exists", l)
        if value in l:
            return True
        else:
            return False
    except Exception as e:
        print("Problem occurred in checking '{value}' in column '{column}' in Table '{table}' ", e)


def drop_record(args, col="abc", val="def"):
    global cursor
    cursor = args
    try:
        q = "delete from youtubers where {col} = '{val}'".format(col=col, val=val)
        print(q)
        cursor.execute(q)
        print("deleted successfully")
    except Exception as e:
        print("unable to delete {col} = '{val}, {e}'".format(col=col, val=val, e=e))
    finally:
        return None


# *******************************************************************************

def comments_push(list_of_comments, userid, vid_id, thum, channel_thum):
    ''' comments list, user uid, video id, thumbnail, video thum'''
    global client
    list_comm = list_of_comments["Comments"]
    for i in list_comm:
        i["youtuber"] = userid
        i["video_id"] = vid_id
    print(list_comm)
    try:
        client = create_mongo_conn()
        try:
            data0 = {"youtuber": userid, "video_id": vid_id,
                     "video_thumbnail": base64.encodebytes(urlopen(thum).read())}
            database = client["youtubescrapper"]
            collection0 = database["youtubers_thumbnail"]
            collection0.delete_many({"youtuber": userid, "video_id": vid_id})
            collection0.insert_one(data0)

        except Exception as e:
            print("at line 255", e)
        try:
            print("trying to push comments")
            data = {
                "name": userid,
                "thumbnail": base64.encodebytes(urlopen(channel_thum).read())}
            database = client["youtubescrapper"]
            collection = database["youtubers"]
            collection.delete_many({"name": userid})
            collection.insert_one(data)
            try:
                data1 = list_comm
                print(data1)
                # database = client["youtubescrapper"]
                collection1 = database["comments"]
                if vid_id == 1:
                    print("true, deleting all data")
                    type(vid_id)
                    mq = {"youtuber": userid}
                    collection1.delete_many(mq)
                    print(mq)
                collection1.insert_many(data1)
            except Exception as e:
                print("unable to push comment", e)
        except Exception as e:
            print("error in pushing thum to mongo db", e)
            client.close()
    except Exception as e:
        print("error in connecting with mongodb server", e)
    return None


# *********************************************************************
#
def fetch_content_db(url):
    global cursor
    conn = create_connection()
    cursor = conn.cursor()
    try:
        if check_if_exists(cursor, column="channel_uid", value=url.split("/")[-2], table="youtubers"):
            cursor.close()
            return True
        else:
            cursor.close()
            return False
    except Exception as e:
        print(e)
        cursor.close()
        return False


def fetch_db(url):
    global cursor
    global client
    client = create_mongo_conn()
    conn = create_connection()
    details = dict()
    video_list = []
    cursor = conn.cursor()

    print("trying to fetch")
    cursor.execute("use warehouse temp")
    print("url", url)
    cursor.execute("select * from youtubescrapper.public.youtubers where channel_uid = '{youtuber}'".format(
        youtuber=url.split("/")[-2]))
    for i in cursor.fetchall():
        print(i)
        database = client["youtubescrapper"]
        collection0 = database["youtubers"]
        temp = dict()
        temp["thumbnail"] = "error"
        try:
            print("grabbing youtubers from mongo")
            print(collection0.find({"name": i[0]}))
            print(type(collection0.find({"name": i[0]})))
            for j in collection0.find({"name": i[0]}):
                print("inside loop")
                print("content :", j)
                temp = j
            print("sucess")
        except Exception as e:
            print("at line 331", e)
            temp["thumbnail"] = "error"
        print("i am here")
        print(temp)
        details["youtuber_info"] = {"uid": i[0], "name": i[1], "channel_link": i[2], "channel_thum_link": i[3],
                                    "subs": i[4], "fetchon": i[5], "thum_base": temp["thumbnail"]}
        print(details)
        print("123")
        print(details)
        print("select *  from youtubescrapper.public.{a}".format(a=i[0]))
        cursor.execute("select *  from youtubescrapper.public.{a}".format(a=i[0]))
        for k in cursor.fetchall():
            print(k)
            try:
                temp_dict0 = {"count": k[0], "title": k[1], "link": k[2], "video_thum_link": k[3], "date": k[4],
                              "duration": k[5], "views": k[6], "likes": k[7], "total_comments": k[8],
                              "fetched_comments": k[9]}
            except Exception as e:
                print("at line 363 in custompackage", e)
                temp_dict0 = {"count": "error", "title": "error", "link": "error", "video_thum_link": "error",
                              "date": "error",
                              "duration": "error", "views": "error", "likes": "error", "total_comments": "error",
                              "fetched_comments": "error"}
            print("dict is ", temp_dict0)
            # print(temp_dict0)
            video_list.append(temp_dict0)
        details["video"] = video_list
        print(details)

    cursor.close()
    client.close()
    return details


def comments_fetch_db(video_id, channel):
    global cursor
    global client
    print("i am running")
    client = create_mongo_conn()
    print(video_id, channel)
    print(type(video_id), type(channel))
    database = client["youtubescrapper"]
    collection = database["comments"]
    temp_list = list()
    temp = None
    for i in collection.find({"youtuber": channel, "video_id": int(video_id)}):
        temp_list.append(i)
    cursor = create_connection().cursor()
    cursor.execute("select video_title,video_thumbnail from youtubescrapper.public.{name} where video_id = {id}".
                   format(name=channel, id=int(video_id)))
    for j in cursor.fetchall():
        print(j)
        temp = j
    mydict = {"info": temp, "comments": temp_list}
    # print(temp_list)
    client.close()
    cursor.close()
    print("success")
    return mydict
