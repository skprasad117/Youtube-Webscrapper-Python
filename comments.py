import time
from selenium import webdriver
import os

global driver

webpage_len_start = 0
webpage_len_to_scroll = 300


def driver_create(local=False, headless=False):
    try:
        print("creating driver for comments")
        chrome_options = webdriver.ChromeOptions()
        if local:
            if headless is True:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--no-sandbox")
            driver0 = webdriver.Chrome(executable_path=r'chromedriver.exe', options=chrome_options)
            print(driver0)

        else:
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver0 = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        return driver0
    except Exception as e:
        print("error occurred at line 15 of channels :", e)
        return None


def begin_comments(url):
    return_statement = None
    global driver
    global webpage_len_start
    global webpage_len_to_scroll
    driver = driver_create()

    try:
        url = url
        driver.get(url)
        time.sleep(1)
        video_info = fetch_video_info()
        video_info["Video Link"] = url
        comments_bucket = fetch_comments(video_info["Total Comments"])
        print("length of comments bucket", len(comments_bucket))
        if len(comments_bucket) == 0:
            print("no comments found")
            comments = extract_comments(comments_bucket)
            video_info["Fetched comments"] = "0"
        else:
            comments = extract_comments(comments_bucket)
            video_info["Fetched comments"] = str(len(comments))
        return_statement = {"Video Info": video_info, "Comments": comments}
    except Exception as e:
        print("unable to begin, begin comments method,", e)
        return_statement = "error"
    finally:
        if return_statement is None:
            driver.close()
            webpage_len_start = 0
            webpage_len_to_scroll = 300
            return None
        else:
            driver.close()
            webpage_len_start = 0
            webpage_len_to_scroll = 300
            # print(return_statement)
            print(return_statement)
            return return_statement


def scroll():
    global webpage_len_start
    global webpage_len_to_scroll
    global driver

    driver.execute_script("window.scrollTo({a1}, {a2});".format(a1=webpage_len_start,
                                                                a2=webpage_len_to_scroll))
    # document.body.scrollHeight determine total height
    webpage_len_start = webpage_len_to_scroll
    webpage_len_to_scroll = webpage_len_to_scroll + 200
    time.sleep(1.5)


def fetch_video_info():
    scroll()
    scroll()
    scroll()
    temp_likes = None
    temp_total_comments = str()
    temp_dict = dict()
    # fetch likes on video
    time.sleep(2)
    try:

        try:
            try:

                temp_likes = driver.find_elements_by_tag_name("ytd-menu-renderer")[0]. \
                    find_elements_by_tag_name("yt-formatted-string")[0].text

                if type(temp_likes) is None:
                    print("scrolling")
                    scroll()
                    print("scrolling done")
                    temp_likes = driver.find_elements_by_tag_name("ytd-menu-renderer")[0]. \
                        find_elements_by_tag_name("yt-formatted-string")[0].text
                    if type(temp_likes) is None:
                        temp_likes = "error"
            except Exception as e:
                print("problem in fetching likes", e)
            print(type(temp_likes))
            print(temp_likes)
            print("setting some default no to no of comments")

        except Exception as e:
            print("Unable to fetch likes", e)
            temp_likes = "error"
        finally:
            total_video_likes = temp_likes

        try:
            scroll()
            temp_total_comments = driver.find_element_by_id("comments").find_element_by_id("count"). \
                find_elements_by_tag_name("span")[0].text

            if type(temp_total_comments) is None:
                scroll()
                scroll()
                temp_total_comments = driver.find_element_by_id("comments").find_element_by_id("count"). \
                    find_elements_by_tag_name("span")[0].text.replace(",", "")
                if type(temp_total_comments) is None:
                    temp_total_comments = "0"
            temp_total_comments = int(temp_total_comments.replace(",", ""))
            print("Total comments", temp_total_comments)

        except Exception as e:
            print("unable to fetch total comments count,", e)
        finally:
            total_comment_count = int(temp_total_comments)

        temp_dict = {"Total Likes": total_video_likes, "Total Comments": total_comment_count}

    except Exception as e:
        print("unable to fetch likes and total comments", e)
        temp_dict = {"Total Likes": "error", "Total Comments": "error"}

    finally:
        video_info = temp_dict
        return video_info


def fetch_comments(args):
    total_comments = args
    last_fetch = 0
    fetch_list = []
    all_comments = []
    msg = []
    temp_start = None
    try:
        temp_start = len(driver.find_elements_by_tag_name("ytd-comment-thread-renderer"))
        if temp_start is None:
            scroll()
            temp_start = len(driver.find_elements_by_tag_name("ytd-comment-thread-renderer"))
    except Exception as e:
        print("unable to get comment element start value", e)
        temp_start = 15
    finally:
        start = temp_start

    try:
        if total_comments != 0:
            for i in range(start, (total_comments + 5)):
                scroll()
                all_comments = driver.find_elements_by_tag_name("ytd-comment-thread-renderer")
                print("Trying for", i + 1, "/", total_comments + 10, "time", ",total comments", total_comments,
                      ",comments fetched", len(all_comments))

                if last_fetch == len(all_comments):
                    scroll()
                    scroll()
                    time.sleep(1)
                    print("****************** forcefully looking for comment for {a}/10 time ********************".
                          format(a=len(fetch_list) + 1))
                    fetch_list.append(True)
                    if len(fetch_list) == 10:
                        print("fetching limit exceeded")
                        print("******************not able to find new comments for too long********************")
                        break

                else:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!comments found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    last_fetch = len(all_comments)
                    fetch_list.clear()
                    scroll()

                print("Out of total {a} comments able to fetch {b} comments".format(a=total_comments,
                                                                                    b=len(all_comments)))
        else:
            print("no comments found")

        msg = all_comments

    except Exception as e:
        print("Unable to iterate through comments error occurring fetch_comments() method", e)
        msg = []
    finally:

        return msg


def extract_comments(comments_bucket):
    all_comments = comments_bucket
    comments = []
    count = 0
    msg = None
    try:
        if len(all_comments) != 0:
            for i in all_comments:
                count = count + 1
                name = i.find_element_by_id("header-author").text.split("\n")[0]
                comment = i.find_element_by_id("content-text").text.replace("\n", " ")
                # likes
                if i.find_element_by_id("vote-count-middle").text == "":
                    comment_likes = 0
                else:
                    comment_likes = i.find_element_by_id("vote-count-middle").text
                date = i.find_element_by_id("header-author").find_element_by_tag_name("yt-formatted-string").text
                if name == date:
                    date = "Error"
                my_dict = {"count": count, "Name": name, "Date": date, "Likes": comment_likes, "Comment": comment}
                comments.append(my_dict)
        else:
            my_dict = {"count": "0", "Name": "0", "Date": "0", "Likes": "0", "Comment": "0"}
            comments.append(my_dict)
        msg = comments
    except Exception as e:
        print("unable to extract comments data, see method 'extract_comments()'", e)
        msg = None
    finally:
        return msg
