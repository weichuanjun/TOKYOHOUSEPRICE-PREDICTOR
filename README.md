# 东京房价预测应用

这是一个使用 Flask 构建的东京房价预测 Web 应用。使用东京30年真实房产成交数据训练的机器学习模型。用户可以输入房产的特征信息，预测房产的价格，并查看相关的历史交易数据和趋势图表。
![My Image](https://user-images.githubusercontent.com/your-username/issue-number/image.png)
## 目录

- [安装](#安装)
- [使用](#使用)
- [文件结构](#文件结构)
- [功能](#功能)
- [RELEASE](#RELEASE)

## 安装

- 克隆此仓库到本地：
   ```bash
   git clone https://github.com/weichuanjun/TOKYOHOUSEPRICE-PREDICTOR.git
- 进入项目目录：
   ```bash
   cd web
- 创建虚拟环境并激活：
     ```bash
   python -m venv venv
   source venv/bin/activate  # 对于 Windows 系统：venv\Scripts\activate
- 安装依赖项：
  ```bash
  pip install -r requirements.txt

## 使用
- 启动 Flask 应用：
     ```bash
     python app.py
- 打开浏览器，访问 http://127.0.0.1:8070
- 在主页上输入房产的特征信息并点击“PREDICT”按钮以获取预测价格和相关的历史交易数据。

## 文件结构
- app.py: Flask 应用的主文件，处理路由和主要逻辑。
- templates/index.html: 网页的 HTML 模板。
- static/price_stats.png: 生成的价格趋势图表。
- Train_Project/:里面有模型的训练方法
- models/：里面存储着训练好的模型
- DataSet/：里面存储着需要用到的数据
  
## 功能
- 预测房价: 用户输入房产特征，应用使用预训练的 XGBoost 模型进行预测。
- 显示历史数据: 根据用户输入的特征，筛选并显示匹配的历史交易记录。
- 生成统计图表: 生成并显示选定地区的房价趋势和交易量图表。

## RELEASE
- V3.0: 增加新的训练模型，并且支持多模型间切换预测
- V2.1：fix some bugs
- V2.0：加上了价格平均数和中位数走势图，加上了成交量走势图
- V1.1：地区内容加上了下拉菜单
