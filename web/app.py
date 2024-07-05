from flask import Flask, request, render_template
import pandas as pd
import joblib

app = Flask(__name__)

# 加载模型和预处理器
loaded_preprocessor = joblib.load('xgboost_preprocessor.pkl')
loaded_model = joblib.load('xgboost_model.pkl')

# 加载数据集
data = pd.read_csv('./exported_data11.csv')  # 确保路径正确

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 获取表单数据
        query = {
            '最寄駅：距離（分）': int(request.form['distance']),
            '面積（㎡）': float(request.form['area']),
            '建物の構造': request.form['structure'],
            '建ぺい率（％）': float(request.form['coverage']),
            '容積率（％）': float(request.form['volume_rate']),
            '建築年数': int(request.form['age']),
            '地区名': request.form['district']
        }
        new_data = pd.DataFrame([query])

        # 预处理和预测
        X_test_transformed = loaded_preprocessor.transform(new_data)
        predicted_price = loaded_model.predict(X_test_transformed)
        predicted_price_in_ten_thousands = round(predicted_price[0]*1.02 / 10000)
        prediction_text = f"预测价格：{predicted_price_in_ten_thousands}万"

        # 根据表单数据筛选匹配的历史记录
        conditions = (
            # (data['最寄駅：距離（分）'] == query['最寄駅：距離（分）']) &
            (data['面積（㎡）'].between(query['面積（㎡）'] * 0.90, query['面積（㎡）'] * 1.1)) &
            (data['建物の構造'] == query['建物の構造']) &
            # (data['建ぺい率（％）'].between(query['建ぺい率（％）'] * 0.95, query['建ぺい率（％）'] * 1.05)) &
            # (data['容積率（％）'].between(query['容積率（％）'] * 0.95, query['容積率（％）'] * 1.05)) &
            (data['建築年数'] == query['建築年数']) &
            (data['地区名'] == query['地区名'])
        )
        filtered_data = data[conditions]
        if not filtered_data.empty:
            result = filtered_data.to_html(classes='data', index=False, border=0)
        else:
            result = "没有找到匹配的数据。"

        return render_template('index.html', prediction_text=prediction_text, result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8070)