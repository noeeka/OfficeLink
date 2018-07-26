# Git学习笔记(Windows)

1. 安装
    * [Git下载](https://git-scm.com/download/)，安装
    * [下载TortoiseGit](https://tortoisegit.org/download/)，安装

2. 克隆
    * 右键单击，选择Git Clone...
    * 填写URL，Directory，点击确定。
    
        ```
        URL：http://192.168.1.254:80/homelink/homeserver.git，
        Directory：F:\tcs\homeserver
        ```

3. 提交
    * 修改一些文档：添加、删除、修改
    * F:\tcs\homeserver目录下右键单击，选择Git Commit -> "master"...
    * 选择要提交的修改，填写日志，点击Commit
    * Push，可以立即Push到Git服务器，也可以稍后再Push

4. 日志
    * F:\tcs\homeserver目录下右键单击，选择TortoiseGit -> Show log

5. 推送，将本地修改同步到服务器
    * F:\tcs\homeserver目录下右键单击，选择TortoiseGit -> Push

6. 拉取，把服务器上的内容更新到本地
    * F:\tcs\homeserver目录下右键单击，选择TortoiseGit -> Pull