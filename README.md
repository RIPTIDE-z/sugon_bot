# Sugon-Bot

- 对瑞翼工坊打卡机器人的重构项目
  - 项目改用uv作为环境管理工具
  - 优化部分指令的逻辑并修复bug

## 项目说明

- 项目基础依赖为Nonebot2框架以及QQ适配器
- 可直接在终端`uv run nb run --reload`或使用`sugonbot.service`注册为systemd服务

## 项目部署

1. `uv sync`拉取依赖
2. 根据`env.example`新建`env.prod`并填写相关token、secret和appid
3. 启动服务，systemd服务注册略，需要根据服务器操作系统自行调整，默认使用的是centos

## 文档

- 更详细说明请见 [Introduction](doc/Introduction.md)