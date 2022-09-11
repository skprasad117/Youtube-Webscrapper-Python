import time
import os
from selenium import webdriver

# **********************-global variables-***************************


webpage_len_start = 0
webpage_len_to_scroll = 300
global driver


# ********************************************************************
def driver_create(local=False, headless=True):
    try:
        print("creating driver for channels")
        chrome_options = webdriver.ChromeOptions()
        if local:
            if headless is True:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")
            driver0 = webdriver.Chrome(executable_path=r'chromedriver.exe', options=chrome_options)

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


# **********************************************************************


# *********************************************************************


def begin(url, length):
    ''' begin(url , length)
       url : url must be of videos section
       for eg: www.youtube.com/xyz/ChannelName/videos '''
    global webpage_len_start
    global webpage_len_to_scroll
    global driver
    print("successfully created driver")
    msg = dict()
    try:
        driver = driver_create()
        url = url
        driver.get(url)
        time.sleep(5)
        print("fetching details")

        channel_details = get_channel_details(driver, url)
        print("grabbing videos container")
        videos = videos_fetch(driver, length)
        print("fetching videos details")
        video_details = fetch_video_details(driver, videos, length)

        msg["Channel Details"] = channel_details
        msg["Video Details"] = video_details

        print(channel_details)
        print(len(videos))

        for i in range(len(video_details)):
            print(i + 1, video_details[i])

    except Exception as e:
        print("error in begin", e)
        msg["Channel Details"] = "error"
        msg["Video Details"] = "error"
    finally:
        driver.close()
        webpage_len_start = 0
        webpage_len_to_scroll = 300
        # return msg
        return msg


def scroll():
    global webpage_len_start
    global webpage_len_to_scroll
    global driver
    driver.execute_script("window.scrollTo({a1}, {a2});".format(a1=webpage_len_start, a2=webpage_len_to_scroll))
    webpage_len_start = webpage_len_to_scroll
    webpage_len_to_scroll = webpage_len_to_scroll + 200
    time.sleep(1)
    return None


def get_channel_details(driver1, url):
    global driver
    driver = driver1
    channel_name = str()
    subscriber_count = str()
    channel_thumbnail = str()
    channel_link = url
    scroll()
    scroll()
    try:
        print("Trying to fetch channel basic details")
        time.sleep(1)
        try:
            print("Fetching Channel Name")
            channel_name = driver.find_element_by_id('channel-name').text

        except Exception as e:
            print("unable to fetch Channel Name", e)
            channel_name = "error"

        try:
            print("Fetching Subscriber Count")
            subscriber_count = driver.find_element_by_id('subscriber-count').text.replace(" subscribers", "")
        except Exception as e:
            print("unable to fetch total subscriber count", e)
            subscriber_count = "error"
        try:
            print("Fetching Channel Thumbnail")
            channel_thumbnail = driver.find_element_by_id('avatar').find_elements_by_tag_name("img")[0]. \
                get_attribute("src")
        except Exception as e:
            print("unable to fetch channel thumbnail", e)
            channel_thumbnail = "error"

    except Exception as e:
        print("unable to fetch channel basic details", e)
    finally:
        channel_dict = {"Channel Name": channel_name, "Channel Link": channel_link,
                        "Total Subscriber": subscriber_count,
                        "Channel Thumbnail": channel_thumbnail}
        return channel_dict


def videos_fetch(driver1, length):
    global driver
    global webpage_len_start
    global webpage_len_to_scroll
    driver = driver1
    msg = []
    if type(length) != int:
        length = int(length)
    try:
        last_fetch = 0
        print("trying to fetch all videos containers")
        while True:
            videos = driver.find_elements_by_tag_name('ytd-grid-video-renderer')
            l = []

            if len(videos) <= (length + 10):
                print("videos fetched", len(videos))
                scroll()
                last_fetch = len(videos)
                if last_fetch == len(videos):
                    print("stopping fetching videos container in {a}/8".format(a=len(l)))
                    l.append(True)
                    if len(l) == 8:
                        break
                if len(videos) > length:
                    break



            else:
                break
        msg = videos[:length]
    except Exception as e:
        print("problem in fetching videos containers", e)
        msg = []
    finally:
        return msg


def fetch_video_details(driver0, container_of_all_videos, length_of_the_container):
    global driver
    driver = driver0
    container = container_of_all_videos
    length = length_of_the_container
    temp_video_thumbnail = str()
    temp_link = str()
    temp_video_detail = list()
    final_videos_list = list()
    if type(length) != int:
        length = int(length)
    try:
        for video_count in range(length):

            try:
                temp_video_thumbnail = container[video_count].find_elements_by_tag_name("img")[0].get_attribute("src")
            except Exception as e:
                print("unable to fetch {a} video thumbnail, {e}".format(a=(video_count + 1), e=e))
                temp_video_thumbnail = "error"
            finally:
                video_thumbnail = temp_video_thumbnail

            try:
                temp_link = container[video_count].find_elements_by_tag_name("a")[0].get_attribute("href")
            except Exception as e:
                print("unable to fetch {a} video link, {e}".format(a=(video_count + 1), e=e))
            finally:
                link = temp_link

            try:
                temp_video_detail = container[video_count].text.replace("\n", "$%@%$").split("$%@%$")
                if len(temp_video_detail) != 4:
                    temp_video_detail.insert(0, "unable to fetch Video Length")
                elif len(temp_video_detail) > 4:
                    temp_video_detail = ["error", "error", "error", "error"]

            except Exception as e:
                print("error occurred in fetching video detail at line 139, {e}".format(e=e))
                temp_video_detail = ["error", "error", "error", "error"]

            finally:
                video_detail = temp_video_detail
                video = {"Video ID": (video_count + 1), "Video Title": video_detail[1],
                         "Video Duration": video_detail[0],
                         "Video Views": video_detail[2], "Upload Date": video_detail[3], "Video Link": link,
                         "Video Thumbnail": video_thumbnail}
                final_videos_list.append(video)

    except Exception as e:
        print("problem occurred at somewhere between line 125 - 161", e)
        return ["error"]
    finally:
        return final_videos_list

# begin("https://www.youtube.com/user/krishnaik06/videos", 2)
