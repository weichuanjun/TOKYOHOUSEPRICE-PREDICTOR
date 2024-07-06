# 东京房价预测 Web 应用

这是一个使用 Flask 构建的东京房价预测 Web 应用。用户可以输入房产的特征信息，预测房产的价格，并查看相关的历史交易数据和趋势图表。

## 目录

- [安装](#安装)
- [使用](#使用)
- [文件结构](#文件结构)
- [功能](#功能)
- [注意事项](#注意事项)

## 安装

- 1. 克隆此仓库到本地：
   ```bash
   git clone <仓库URL>
- 2.进入项目目录：
   ```bash
   cd <项目目录>
- 3.创建虚拟环境并激活：
     ```bash
   python -m venv venv
   source venv/bin/activate  # 对于 Windows 系统：venv\Scripts\activate
- 4.安装依赖项：
  ```bash
  pip install -r requirements.txt

## 使用
- 1.	启动 Flask 应用：
     ```bash
     python app.py
- 2.	打开浏览器，访问 http://127.0.0.1:8070。
- 3.	在主页上输入房产的特征信息并点击“PREDICT”按钮以获取预测价格和相关的历史交易数据。
