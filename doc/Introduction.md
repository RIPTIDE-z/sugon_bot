# Sugon_Bot 介绍

- Sugon_Bot是一个打卡记录与积分计算的QQ机器人，使用Nonebot2架构
  - 可以记录打卡信息
  - 可以设定打卡时间段
  - 可以计算积分并展示

---

## 项目结构

以下为 `sugon_bot/plugins/sugon_mark/` 内文件作用概览：

### .env

- ENVIRONMENT指定使用哪个环境文件
- 若ENVIRONMENT=prod，需要自行根据example建立env.prod并填入相关信息

### \_\_init\_\_.py

插件入口与命令注册，包含打卡、命名、积分榜、权限校验与积分更新的核心逻辑

### access_token_get.py

获取 QQ Bot 的 access token，并生成调用官方 API 的鉴权请求头

### api_datapack.py

封装频道 API 调用所需的路径与请求体，集中管理基础请求结构

### config.py

Nonebot 插件配置模型（占位），用于读取全局配置

### group_image_check.py

校验群聊图片下载链接是否符合指定的 QQ 媒体域名格式

### guild_api.py

调用 QQ 频道 API 获取身份组与成员信息，并提供角色/成员校验方法

### link_check.py

检查链接可用性并判断链接是否指向图片资源

### load_data.py

负责积分、打卡记录与配置的 JSON 读写和持久化

### logger.py

- Nonebot 日志封装
  - 将日志输出重定向到txt文件并按小时切片
  - 更改ENABLE_FILE_REDIRECT调整是否重定向到文件

### mark_caculate.py

- 积分计算逻辑
- TODO:
  - 处理节假日加成与打卡次数限制

### super_user_group.py

管理员（超级用户）列表的初始化、持久化与权限校验

### time_check.py

打卡时间段校验与跨午夜的“有效日期”计算
