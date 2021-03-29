import requests
import urllib
import time
import sys
import os
import json

TempFile_BVInfo='bvinfo.json'
TempFile_BVList='bvlist.json'
Dir_Download='download'
BVList=[
'BV1QK4y1T7to','BV1zf4y1x7kt','BV1Li4y1P7bL','BV1BZ4y1w72X','BV1Xp4y1h7TU'
]

def getBVList(bv=TempFile_BVList):
	global BVList
	if not os.path.exists(bv):
		# The object is serialized to the file
		json.dump(BVList,open(bv, 'w'))
	else:
		# Deserialize to object 
		BVList=json.load(open(bv, 'r'))
	
def getCidAndTitle(bvid,p=1):
    url='https://api.bilibili.com/x/web-interface/view?bvid='+bvid
    data=requests.get(url).json()['data']
    title=data['title']
    cid=data['pages'][p-1]['cid']
    return str(cid),title

def getInformation(bvList):
    infoDict={}
    if os.path.exists(TempFile_BVInfo):
    	# Deserialize to object 
    	infoDict=json.load(open(TempFile_BVInfo, 'r'))
    	
    if not os.path.exists(TempFile_BVInfo) or len(bvList)!=len(infoDict):
    	for bvid in bvList:
    		if bvid in infoDict.keys():
    			continue
    		
    		item=[]
    		if len(bvid) == 12:
    			cid,title=getCidAndTitle(bvid)
    			item.append(bvid)
    			item.append(cid)
    			item.append(title)
    			infoDict[bvid]=item
    		else:
    			# 分P
    			cid,title=getCidAndTitle(bvid[:12],int(bvid[13:]))
    			item.append(bvid[:12])
    			item.append(cid)
    			item.append(title)
    			infoDict[bvid[:12]]=item
    		#item.append(cid)
    		#item.append(title)
    		# infoDict.append(item)
		# The object is serialized to the file
    	json.dump(infoDict,open(TempFile_BVInfo, 'w'))
    #else:
    	# Deserialize to object 
    	# infoDict=json.load(open(TempFile_BVInfo, 'r'))
		
    return infoDict

def getAudio(infoDict):
    baseUrl='https://api.bilibili.com/x/player/playurl?fnval=16&'
    
    len_infoDict=str(len(infoDict))
    count=0
    
    for item in infoDict.values():
        st=time.time()
        bvid,cid,title=item[0],item[1],item[2]
        
        count=count+1
        print('No. '+str(count)+'/'+len_infoDict)
        
        str_FileName=Dir_Download+'/'+title+'.m4a'
        if os.path.isfile(str_FileName) == True:
        	print('exist '+str_FileName)
        	continue
        url=baseUrl+'bvid='+bvid+'&cid='+cid

        audioUrl=requests.get(url).json()['data']['dash']['audio'][0]['baseUrl']
        # print(audioUrl)
        
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),
            ('Referer', 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid),  # 注意修改referer,必须要加的!
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),
        ]
        print('download start:',title)
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url=audioUrl, filename=str_FileName,reporthook=callbackfunc)
        ed=time.time()
        print('\r'+str(round(ed-st,2))+' seconds download complete:',title)
        time.sleep(1)

def callbackfunc(blocknum, blocksize, totalsize):
    '''回调函数
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100 
    print("\r{:^.2f}%".format(percent),end="",flush=True)

if __name__ == '__main__':
    print('The downloader starts:')
    print('Maybe 3-6 times will report errors, the problem is unknown! Space?')
    getBVList()
    if not os.path.exists(Dir_Download):
    	os.makedirs(Dir_Download)
    st=time.time()
    getAudio(getInformation(BVList))
    ed=time.time()
    print('Download complete, total time:',str(round(ed-st,2))+' seconds')
