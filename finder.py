import sys
import urllib.request
import json
import time
#from playsound import playsound
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import *
from multiprocessing import Pool

streamer_link='https://tmi.twitch.tv/group/user/{}/chatters'
homepage_link='https://www.twitch.tv/directory/all'

sound_name='strilliamo.wav'

#usage py finder.py <username> <pages>
#<username> is the user you want to check if is watching most popular italian streams
#<pages> is proportional to the number of popular streams to check. normally 1 page = 10 streamers

#example1 py finder.py ranoblinoidepensante 10
#example2 py finder.py ranoblinoidepensante,enkfull 15

if(len(sys.argv)>2):
    usernames=sys.argv[1].lower()
    pages=int(sys.argv[2])
else:
	
    print("Username to search pls")
    exit()

def get_page(website):
    resp=""
    try:
        with urllib.request.urlopen(website) as url:
            #resp = json.loads(url.read().decode())
            return url.read()
    except:
        resp=""

url = 'https://twitchtracker.com/channels/live/italian'
url_paged = 'https://twitchtracker.com/channels/live/italian?page={}'
start='<div class="ri-name">\\n<a href="/'
end='">'
def get_streamers_online():
    streamers_=[]
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')]
    urllib.request.install_opener(opener)
    page=str(get_page(url))
    if(page is None):
        page=""
    splits=page.split(start)
    for i in range(1,pages+1):
        print("Getting most popular online streamers from page "+str(i)+"..")
        time.sleep(1)
        page=str(get_page(url_paged.format(i)))
        splits=page.split(start)
        for split in splits:
            candidate=split.split(end)[0]
            if(' ' not in candidate):
                streamers_.append(candidate)
        #print(streamers_,len(streamers_))
    return streamers_


#streamers=get_streamers_online() da twitch
streamers=get_streamers_online() #alcune volte non ritorna tutti gli elementi. bug
print("got "+str(len(streamers))+" streamers")

#streamers={'imviolet_','paoloidolo',}

#valuta pro e contro di avere streamers della prima pag e poi checkarli per poi seconda pag e poi checkarli e non mass download streamer list per poi check tutti

#utilizzando timing.py cronometro il tempo di risposta e il max è stato 130 quindi se si volesse periodicamente 
# fare cose con la risposta di $streamerlink, si imposti il delta t di 3 minuti e si """"dovrebbe""""" star tranquilli

i=1
finds=[]
def search_in_streams(streamer):
    global i
    
    chatters=[]
    page=get_page(streamer_link.format(streamer))
    if(page is None):
        return ""

    chatter_list=json.loads(page.decode())['chatters']

    broadcasters=chatter_list['broadcaster']
    for broadcaster in broadcasters:
        chatters.append(broadcaster)

    vips=chatter_list['vips']
    for vip in vips:
        chatters.append(vip)

    moderators=chatter_list['moderators']
    for moderator in moderators:
        chatters.append(moderator)

    staff=chatter_list['staff']
    for staff_ in staff:
        chatters.append(staff_)

    admins=chatter_list['admins']
    for admin in admins:
        chatters.append(admin)

    viewers=chatter_list['viewers']
    for viewer in viewers:
        chatters.append(viewer)

    print("checked "+streamer+"... "+str(i)+"/"+str(len(streamers)))
    #print("checked "+streamer)
    if(',' in usernames):
        usernames_=usernames.split(',')
        for username in usernames_:
            if(username in chatters):
                finds.append([username,streamer])
                print("    ",username,"è presente in",streamer)
                #playsound(sound_name,block=True)
    else:
        username=usernames
        if(username in chatters):
            finds.append([username,streamer])
            print("    ",username,"è presente in",streamer)
            #playsound(sound_name,block=True)
    i+=1

pool = ThreadPool(10)  
results = pool.map(search_in_streams, streamers)
pool.close()
pool.join()

print("")
for find in finds:
    print("c'è "+find[0]+" da "+find[1])
