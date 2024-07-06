from flask import Flask, request, render_template
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib
matplotlib.use('Agg')
import joblib
import os


app = Flask(__name__)

# 确保 static 目录存在
if not os.path.exists('static'):
    os.makedirs('static')

# 加载模型和预处理器
loaded_preprocessor = joblib.load('../models/xgboost_preprocessor.pkl')
loaded_model = joblib.load('../models/xgboost_model.pkl')

# 加载数据集
data = pd.read_csv('../DataSet/exported_data11.csv', dtype={
    '最寄駅：距離（分）': int,
    '面積（㎡）': float,
    '建物の構造': str,
    '建ぺい率（％）': float,
    '容積率（％）': float,
    '建築年数': int,
    '地区名': str,
    '四半期': str
})

# 加载地区数据并创建市区町村名到地区名的映射
districts_data = pd.read_csv('../DataSet/city_district_mapping.csv')
city_to_districts = districts_data.groupby('市区町村名')['地区名'].apply(list).to_dict()

def calculate_and_plot_stats(df, district_name):
    df_filtered = df[(df['地区名'] == district_name) &
                     (df['取引時期'].str.match('20(1[3-9]|2[0-3])年第[1-4]四半期'))]
    
    grouped = df_filtered.groupby('取引時期')['取引価格（総額）']
    average_prices = grouped.mean() / 10000  # 转换为万单位
    median_prices = grouped.median() / 10000  # 转换为万单位
    transaction_counts = grouped.size()  # 交易数量

    # 绘制平均价格和中位数价格
    plt.figure(figsize=(14, 7))
    plt.subplot(2, 1, 1)
    plt.plot(average_prices.index, average_prices, marker='o', linestyle='-', label='Average Price')
    plt.plot(median_prices.index, median_prices, marker='x', linestyle='--', label='Middle Price')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.title('Price Trend')
    plt.legend()
    plt.grid(True)

    # 绘制交易量
    plt.subplot(2, 1, 2)
    plt.bar(transaction_counts.index, transaction_counts, color='skyblue', label='Trading Volume')
    plt.xticks(rotation=45)
    plt.ylabel('Trading Volume')
    plt.title('Trading Volume')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('./static/price_stats.png')
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    selected_city = None
    selected_district = None
    prediction_text = ""
    result = ""
    chart_exists = False

    if request.method == 'POST':
        selected_city = request.form['city']
        selected_district = request.form['district']
        query = {
            '最寄駅：距離（分）': int(request.form['distance']),
            '面積（㎡）': float(request.form['area']),
            '建物の構造': request.form['structure'],
            '建ぺい率（％）': float(request.form['coverage']),
            '容積率（％）': float(request.form['volume_rate']),
            '建築年数': int(request.form['age']),
            '地区名': selected_district
        }

        # 预处理和预测
        new_data = pd.DataFrame([query])
        X_test_transformed = loaded_preprocessor.transform(new_data)
        predicted_price = loaded_model.predict(X_test_transformed)
        predicted_price_in_ten_thousands = round(predicted_price[0] * 1.01 / 10000)
        prediction_text = f"预测价格：{predicted_price_in_ten_thousands}万"

        # 根据表单数据筛选匹配的历史记录
        conditions = (
            (data['面積（㎡）'].between(query['面積（㎡）'] * 0.5, query['面積（㎡）'] * 1.5)) &
            (data['建築年数'].between(query['建築年数'] - 5, query['建築年数'] + 5)) &
            (data['地区名'] == selected_district)
        )
        
        filtered_data = data[conditions]
        result = "没有找到匹配的数据。" if filtered_data.empty else filtered_data.to_html(classes='data', index=False, border=0)
        # 计算并生成统计图
        calculate_and_plot_stats(data, selected_district)
        chart_exists = True

        return render_template('index.html', prediction_text=prediction_text, result=result, city_to_districts=city_to_districts, cities=list(city_to_districts.keys()), selected_city=selected_city, selected_district=selected_district, chart_exists=chart_exists)

    return render_template('index.html', prediction_text=prediction_text, result=result,
                           city_to_districts=city_to_districts, cities=list(city_to_districts.keys()),
                           selected_city=selected_city, selected_district=selected_district,
                           chart_exists=chart_exists)

if __name__ == '__main__':
    app.run(debug=True, port=8070)