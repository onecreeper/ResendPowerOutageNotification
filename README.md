# 断电自动发送邮件使用RESEND
## 简介
断电自动发送邮件使用RESEND，通过定时任务，检测服务器是否断电，断电后自动发送邮件通知。

## 项目起源
发现resend的api可以发送邮件，而且免费，不用白不用，没有需求就创造需求。然后~~自己~~AI写了一个脚本。

## 使用方法
1. 克隆本仓库
2. cd 到仓库目录
3. 修改docker-compose.yml文件，根据自己需求设置环境变量
4. docker-compose up -d 或者 docker compose up -d