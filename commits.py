import urllib.error, urllib.request, urllib.parse
import json
import datetime
from requests import exceptions
import tools

def crawlOneCommitInfo(project_id, commit_id):
    handler = urllib.request.BaseHandler()
    opener = urllib.request.build_opener(handler)
    commitInfo = []

    url = r"https://git.n.*.com/api/v4/projects/" + str(project_id) + "/repository/commits/" + commit_id + "?private_token=" + tools.getGitToken()
    get_request = urllib.request.Request(url)
    try:
        get_response = opener.open(get_request, timeout=5)
    except urllib.error.URLError as e:
        print("ignore error: continue.")
        print(e)
        return None

    ret = get_response.read().decode()
    ret_dict = json.loads(ret)
    commitInfo.append(ret_dict)
    return commitInfo

def crawlCommit(minProjectId, maxProjectId):
    projects_list = []
    with open(r'./data/projects.json', "r", encoding="utf-8") as f:
        projects = json.load(f)
    for i in range(len(projects)):
        projects_list.append(projects[i]['id'])
    baseUrl = r"https://git.n.*.com/api/v4"
    handler = urllib.request.BaseHandler()
    opener = urllib.request.build_opener(handler)
    commits = []
    commitInfoList = []

    def preWrite():
        try:
            print("preWrite: 1")

            get_request = urllib.request.Request(url)
            print("preWrite: 1.1")
            ret_dict = dict()
            try:
                get_response = opener.open(get_request, timeout = 5)
                print("preWrite: 1.2")
                ret = get_response.read().decode()
                print("preWrite: 1.3")
                ret_dict = json.loads(ret)
                committed_date_mod_sec = datetime.datetime.now()
            except urllib.error.URLError as e:
                print("ignore error: continue.")
                print(e)
            except exceptions.Timeout as e:
                print("抛出异常: timeout")

            print("preWrite: 2")
            if len(ret_dict) != 0:

                print("preWrite: 3")
                committed_date_str0 = ret_dict[0]['committed_date'][0:10] + ' ' + ret_dict[0]['committed_date'][11:19]
                committed_date_date0 = datetime.datetime.strptime(committed_date_str0, "%Y-%m-%d %H:%M:%S")
                gmt_hour0 = int(ret_dict[0]['committed_date'][24:26])
                gmt_minute0 = int(ret_dict[0]['committed_date'][27:29])
                delta0 = datetime.timedelta(hours=gmt_hour0, minutes=gmt_minute0)
                if ret_dict[0]['committed_date'][23] == '+':
                    committed_date_date0_mod = committed_date_date0 - delta0
                else:
                    committed_date_date0_mod = committed_date_date0 + delta0

                print("preWrite: 4")
                committed_date_str1 = ret_dict[-1]['committed_date'][0:10] + ' ' + ret_dict[-1]['committed_date'][11:19]
                committed_date_date1 = datetime.datetime.strptime(committed_date_str1, "%Y-%m-%d %H:%M:%S")
                gmt_hour1 = int(ret_dict[-1]['committed_date'][24:26])
                gmt_minute1 = int(ret_dict[-1]['committed_date'][27:29])
                delta1 = datetime.timedelta(hours=gmt_hour1, minutes=gmt_minute1)
                if ret_dict[-1]['committed_date'][23] == '+':
                    committed_date_date1_mod = committed_date_date1 - delta1
                else:
                    committed_date_date1_mod = committed_date_date1 + delta1

                if committed_date_date1_mod > committed_date_date0_mod:
                    committed_date_last = "none"
                else:
                    print("preWrite: 5")
                    if committed_date_date0 <= committed_date_mod_sec:
                        print("preWrite: 6")
                        for i in range(len(ret_dict)):
                            ret_dict[i]['project_id'] = projects_id
                            commits.append(ret_dict[i])
                            commit_id = str(ret_dict[i]['id'])
                            print('id = ' + commit_id + ' done')

                            onecommitInfo = crawlOneCommitInfo(projects_id, commit_id)
                            if (onecommitInfo != None):
                                commitInfoList.append(onecommitInfo)

                        print("preWrite: 7")
                        committed_date_str = commits[-1]['committed_date'][0:10] + ' ' + commits[-1]['committed_date'][11:19]
                        committed_date_date = datetime.datetime.strptime(committed_date_str, "%Y-%m-%d %H:%M:%S")
                        gmt_hour = int(commits[-1]['committed_date'][24:26])
                        gmt_minute = int(commits[-1]['committed_date'][27:29])
                        delta_pre = datetime.timedelta(hours=gmt_hour, minutes=gmt_minute)
                        delta_re = datetime.timedelta(seconds=1)
                        print("preWrite: 8")
                        if commits[-1]['committed_date'][23] == '+':
                            committed_date_mod = committed_date_date - delta_pre
                            committed_date_mod_sec = committed_date_mod - delta_re
                        else:
                            committed_date_mod = committed_date_date + delta_pre
                            committed_date_mod_sec = committed_date_mod - delta_re
                        committed_date_mod_sec_str = committed_date_mod_sec.strftime("%Y-%m-%d %H:%M:%S")
                        committed_date_last = committed_date_mod_sec_str[0:10] + 'T' + committed_date_mod_sec_str[11:19]
                        print("preWrite: 9")
                    else:
                        print("preWrite: 9.2")
                        committed_date_last = "none"
            else:
                committed_date_last = "none"

            print("preWrite: 10: " + committed_date_last)
            return committed_date_last

        except urllib.error.URLError as e:
            print("URLError: ")
            print(e)
            if hasattr(e, "code"):
                print(e.code)
                if hasattr(e, "reason"):
                    print(e.reason)
            committed_date_last = "none"

            return committed_date_last
        except Exception as e:
            print(e)
            committed_date_last = "none"

            return committed_date_last

    for i in range(len(projects_list)):
        projects_id = projects_list[i]
        if not ((minProjectId <= projects_id) and (projects_id <= maxProjectId)):
            continue

        url = baseUrl + "/projects/" + str(projects_list[i]) + "/repository/commits?private_token=" + tools.getGitToken()
        print("start: " + url)
        print("done: urlopen")
        committed_date = preWrite()

        while committed_date != "none":
            url = baseUrl + "/projects/" + str(projects_list[i]) + "/repository/commits?private_token={0}&until=".format(tools.getGitToken()) + committed_date
            print('url = ' + url)
            committed_date = preWrite()

    print("Writing Json...")

    fileNameCommitList = r"./data/commits_{0}_{1}.json".format(minProjectId, maxProjectId)
    tools.writeJson(fileNameCommitList, commits)

    # filename = r"D:/crawler/data/commits2.json"
    # with open(filename, 'w', encoding='utf-8') as file_obj:
    #     json.dump(commits, file_obj, ensure_ascii=False)

    fileNameCommitInfoList = r"./data/commitInfo_{0}_{1}.json".format(minProjectId, maxProjectId)
    tools.writeJson(fileNameCommitInfoList, commitInfoList)
    print("Finish Writing!")

import sys
minProjectId = 0
maxProjectId = 100000
if (len(sys.argv) >= 3):
    print('sys.argv: ' + sys.argv[1] + " : " + sys.argv[2])
    minProjectId = int(sys.argv[1])
    maxProjectId = int(sys.argv[2])

crawlCommit(minProjectId, maxProjectId)

