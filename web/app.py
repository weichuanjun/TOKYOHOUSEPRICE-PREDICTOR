from flask import Flask, request, render_template
import pandas as pd
import joblib

app = Flask(__name__)

# 加载模型和预处理器
loaded_preprocessor = joblib.load('xgboost_preprocessor.pkl')
loaded_model = joblib.load('xgboost_model.pkl')

# 加载数据集
data = pd.read_csv('./exported_data11.csv', dtype={
    '最寄駅：距離（分）': int,
    '面積（㎡）': float,
    '建物の構造': str,
    '建ぺい率（％）': float,
    '容積率（％）': float,
    '建築年数': int,
    '地区名': str
})

# 加载地区数据并创建市区町村名到地区名的映射
districts_data = pd.read_csv('./city_district_mapping.csv')
city_to_districts = districts_data.groupby('市区町村名')['地区名'].apply(list).to_dict()

@app.route('/', methods=['GET', 'POST'])
def home():
    selected_city = None
    selected_district = None

    if request.method == 'POST':
        # 获取表单数据
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

        return render_template('index.html', prediction_text=prediction_text, result=result, city_to_districts=city_to_districts, cities=list(city_to_districts.keys()), selected_city=selected_city, selected_district=selected_district)

    return render_template('index.html', city_to_districts=city_to_districts, cities=list(city_to_districts.keys()), selected_city=selected_city, selected_district=selected_district)

if __name__ == '__main__':
    app.run(debug=True, port=8070)