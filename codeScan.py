import pandas as pd
import json

def parseCodeScan():
    #codeScan.xls各部门git汇总
    code_scan_projects_df = pd.read_excel(r'.\data\CodeScan\code_scan_projects.v3.xls', sheet_name='code_scan_projects.v3')
    git_url = code_scan_projects_df['git_url']

    with open(r'.\data\git.n.*.com\projects.json', "r", encoding="utf-8") as f:
        projects_gitn = json.load(f)
    projects_gitn_web_url = []
    for i in range(len(projects_gitn)):
        projects_gitn_web_url.append(projects_gitn[i]['web_url'])

    with open(r'.\data\micode.be.*.com\projects.json', "r", encoding="utf-8") as f:
        projects_micode = json.load(f)
    projects_micode_web_url = []
    for i in range(len(projects_micode)):
        projects_micode_web_url.append(projects_micode[i]['web_url'])

    projects_gitn_success = pd.DataFrame(columns=['project_name','git_url','created_at','department','jira_id'])
    projects_micode_success = pd.DataFrame(columns=['project_name','git_url','created_at','department','jira_id'])

    for i in range(len(git_url)):
        if str(git_url[i])[8:14] == 'git.n.':
            if git_url[i] in projects_gitn_web_url:
                projects_gitn_success = projects_gitn_success.append(code_scan_projects_df.iloc[i])
        elif str(git_url[i])[8:14] == 'micode':
            if git_url[i] in projects_micode_web_url:
                projects_micode_success = projects_micode_success.append(code_scan_projects_df.iloc[i])

    projects_success = pd.concat([projects_gitn_success, projects_micode_success])
    dept_project_codescan = projects_success.groupby(by=['department'])['project_name']
    dept_project_codescan_count = dept_project_codescan.count()
    dept_project_codescan_count = pd.DataFrame(dept_project_codescan_count)
    dept_project_codescan_count.columns = pd.Series(['dept_project_codescan_count'])

    #deptList各部门git汇总(git.n.*.com)
    FileName = r'.\data\git.n.*.com\deptList.json'
    with open(FileName, 'r', encoding='utf-8') as file_obj:
        dept_list_gitn = json.load(file_obj)

    for oneDept in dept_list_gitn:
        if oneDept['dept_level'] == 2:
            oneDept['department'] = oneDept['dept_parent_id']
        else:
            oneDept['department'] = oneDept['dept_id']

    dept_list_gitn_df = pd.DataFrame(dept_list_gitn)
    dept_project_gitn_count = dept_list_gitn_df.groupby('department').agg({'dept_project_count':'sum'})

    #deptList各部门git汇总(micode.be.xiaomi.com)
    FileName = r'.\data\micode.be.*.com\deptList.json'
    with open(FileName, 'r', encoding='utf-8') as file_obj:
        dept_list_micode = json.load(file_obj)

    for oneDept in dept_list_micode:
        if oneDept['dept_level'] == 2:
            oneDept['department'] = oneDept['dept_parent_id']
        else:
            oneDept['department'] = oneDept['dept_id']

    dept_list_micode_df = pd.DataFrame(dept_list_micode)
    dept_project_micode_count = dept_list_micode_df.groupby('department').agg({'dept_project_count':'sum'})

    #加总两个gitlab各部门的git数量以及接入CodeScan的git数量
    dept_project_count = pd.merge(dept_project_gitn_count, dept_project_micode_count, on=['department'], how='outer').sum(axis=1)
    dept_project_count = pd.DataFrame(dept_project_count)
    dept_project_count.columns = pd.Series(['dept_project_count'])
    dept_codescan = dept_project_count.merge(dept_project_codescan_count, on=['department'], how='left')
    dept_codescan['dept_project_codescan_count'].fillna(0, inplace=True)
    dept_codescan.to_excel('.\data\CodeScan.xls')