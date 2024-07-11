import pandas as pd
from collections import defaultdict
from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import joblib
import os
from matplotlib.font_manager import FontProperties

app = Flask(__name__)

# Ensure the static directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# Load city to district mapping
districts_data = pd.read_csv('../DataSet/city_map_all.csv')
prefecture_city_district = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for _, row in districts_data.iterrows():
    prefecture = row['都道府県名']
    city = row['市区町村名']
    district = row['地区名']
    station = row['最寄駅：名称']
    prefecture_city_district[prefecture][city][district].append(station)

# 设置支持CJK字符的字体
font_path = "/System/Library/Fonts/STHeiti Light.ttc"  # 适用于MacOS系统
font_prop = FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False


def calculate_and_plot_stats(df, district_name, station_name, output_dir='./static/'):
    # Filter data for the specified district
    df_filtered_district = df[df['地区名'] == district_name].copy()  # 使用 .copy() 避免 SettingWithCopyWarning

    # Filter data for the specified station
    df_filtered_station = df[df['最寄駅：名称'] == station_name].copy()  # 使用 .copy() 避免 SettingWithCopyWarning

    def plot_stats(df_filtered, name, output_suffix):
        # Group by '取引時期' and calculate statistics for '取引価格（総額）'
        grouped_price = df_filtered.groupby('取引時期')['取引価格（総額）']
        average_prices = grouped_price.mean() / 10000  # Convert to ten thousand units
        median_prices = grouped_price.median() / 10000  # Convert to ten thousand units
        transaction_counts = grouped_price.size()  # Transaction count

        # Calculate price per square meter
        df_filtered['price_per_sqm'] = df_filtered['取引価格（総額）'] / df_filtered['面積（㎡）']
        grouped_price_per_sqm = df_filtered.groupby('取引時期')['price_per_sqm']
        average_price_per_sqm = grouped_price_per_sqm.mean() / 10000  # Convert to ten thousand units
        median_price_per_sqm = grouped_price_per_sqm.median() / 10000  # Convert to ten thousand units

        # Plot average price and median price
        plt.figure(figsize=(10, 4))
        plt.plot(average_prices.index, average_prices, marker='o', linestyle='-', label='平均価格')
        plt.plot(median_prices.index, median_prices, marker='x', linestyle='--', label='中位価格')
        plt.xticks(rotation=45)
        plt.ylabel('価格 (万)')
        plt.title(f'{name} - 価格トレンド')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{output_dir}{output_suffix}_price_trend.png')
        plt.close()

        # Plot transaction volume
        plt.figure(figsize=(10, 4))
        plt.bar(transaction_counts.index, transaction_counts, color='skyblue', label='取引量')
        plt.xticks(rotation=45)
        plt.ylabel('取引量')
        plt.title(f'{name} - 取引量')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{output_dir}{output_suffix}_transaction_volume.png')
        plt.close()

        # Transaction prices by year
        df_filtered['年'] = pd.to_datetime(df_filtered['取引時期']).dt.year
        df_filtered['取引価格（総額）'] /= 10000
        plt.figure(figsize=(15, 10))
        df_filtered.boxplot(column='取引価格（総額）', by='年', grid=True)
        plt.xticks(rotation=45)
        plt.ylabel('価格（万円）')
        plt.title(f'{name} - 年間取引価格の分布')
        plt.suptitle('')
        plt.tight_layout()
        plt.savefig(f'{output_dir}{output_suffix}_price_distribution.png')
        plt.close()

        # Plot price per square meter trend
        plt.figure(figsize=(10, 4))
        plt.plot(average_price_per_sqm.index, average_price_per_sqm, marker='o', linestyle='-', label='平均平方メートル単価')
        plt.plot(median_price_per_sqm.index, median_price_per_sqm, marker='x', linestyle='--', label='中位平方メートル単価')
        plt.xticks(rotation=45)
        plt.ylabel('平方メートル単価 (万)')
        plt.title(f'{name} - 平方メートル単価トレンド')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{output_dir}{output_suffix}_price_per_sqm_trend.png')
        plt.close()
        
        # Pie chart for price ranges in the past five years
        last_five_years = df_filtered[df_filtered['年'] >= (pd.to_datetime('today').year - 5)].copy()
        
        # Define price ranges (in ten thousand units)
        bins = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, float('inf')]
        labels = ['0-1000万', '1000万-2000万', '2000万-3000万', '3000万-4000万', '4000万-5000万', '5000万-6000万', '6000万-7000万', '7000万-8000万', '8000万以上']
        
        last_five_years['price_range'] = pd.cut(last_five_years['取引価格（総額）'], bins=bins, labels=labels, right=False)
        price_range_counts = last_five_years['price_range'].value_counts().sort_index()
        
        # Define lighter colors
        colors = ['#d0e7ff', '#b3d9ff', '#99ccff', '#80bfff', '#66b3ff', '#4da6ff', '#3399ff', '#1a8cff', '#007fff']

        plt.figure(figsize=(8, 6))
        plt.pie(price_range_counts, labels=price_range_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
        plt.title('過去五年間の各価格帯の割合')
        plt.tight_layout()
        plt.savefig(f'{output_dir}{output_suffix}_price_distribution_pie.png')
        plt.close()

    # Generate plots for the district
    plot_stats(df_filtered_district, district_name, 'district')

    # Generate plots for the station
    plot_stats(df_filtered_station, station_name, 'station')

@app.route('/', methods=['GET', 'POST'])
def home():
    selected_prefecture = ""
    selected_city = ""
    selected_district = ""
    selected_station = ""
    prediction_text = ""
    result = ""
    chart_exists = False
    error_message = ""
    property_type = ""
    analysis_type = ""

    if request.method == 'POST':
        try:
            selected_prefecture = request.form.get('prefecture', "")
            selected_city = request.form.get('city', "")
            selected_district = request.form.get('district', "")
            selected_station = request.form.get('station', "")
            analysis_type = request.form.get('analysis_type', "")
            property_type = request.form.get('property_type', "")

            if property_type == 'house':
                query = {
                    '最寄駅：距離（分）': int(request.form['distance']),
                    '面積（㎡）': int(request.form['house_land_area']),
                    '延床面積（㎡）': float(request.form['house_building_area']),
                    '建物の構造': request.form['house_structure'],
                    '建築年数': int(request.form['house_age']),
                    '地区名': selected_district
                }
                preprocessor_file = "../models/xgboost_preprocessor_house.pkl"
                model_file = "../models/xgboost_model_house.pkl"
                data = pd.read_csv('../DataSet/exported_data_web.csv', dtype={
                    '取引時期': str,
                    '取引価格（総額）': int,
                    '最寄駅：名称': str,
                    '最寄駅：距離（分）': int,
                    '面積（㎡）': int,
                    '延床面積（㎡）': int,
                    '建築年': int,
                    '建物の構造': str,
                    '地区名': str,
                    '延床面積（㎡）': int,
                    '建築年数': int
                })
            else:
                query = {
                    '最寄駅：距離（分）': int(request.form['distance']),
                    '面積（㎡）': int(request.form['apartment_area']),
                    '建物の構造': request.form['apartment_structure'],
                    '建築年数': int(request.form['apartment_age']),
                    '間取り': request.form['apartment_layout'],
                    '地区名': selected_district,
                    '最寄駅：名称': selected_station
                }
                preprocessor_file = "../models/xgboost_preprocessor_masion.pkl"
                model_file = "../models/xgboost_model_masion.pkl"
                data = pd.read_csv('../DataSet/exported_data_masion.csv', dtype={
                    '取引時期': str,
                    '取引価格（総額）': int,
                    '最寄駅：名称': str,
                    '最寄駅：距離（分）': int,
                    '面積（㎡）': int,
                    '建物の構造': str,
                    '間取り': str,
                    '建築年': int,
                    '改装': str,
                    '建築年数': int
                }, na_values=['', ' ', 'NA'])
            # Sort by transaction period
            data = data.sort_values(by='取引時期', ascending=False)
            loaded_preprocessor = joblib.load(preprocessor_file)
            loaded_model = joblib.load(model_file)

            new_data = pd.DataFrame([query])
            X_test_transformed = loaded_preprocessor.transform(new_data)
            predicted_price = loaded_model.predict(X_test_transformed)
            predicted_price = predicted_price[0]
            rounded_price = round(predicted_price, -5)
            prediction_text = f"予測価格：{int(rounded_price // 10000)}万"

            if property_type == 'house':
                conditions = (
                    # (data['面積（㎡）'].between(query['面積（㎡）'] * 0.8, query['面積（㎡）'] * 1.2)) &
                    (data['延床面積（㎡）'].between(query['延床面積（㎡）'] * 0.8, query['延床面積（㎡）'] * 1.2)) &
                    (data['建築年数'].between(query['建築年数'] - 5, query['建築年数'] + 5)) &
                    (data['地区名'] == selected_district)
                )
            else:
                conditions = (
                    (data['地区名'] == selected_district)
                )
            filtered_data = data[conditions]
            filtered_data.loc[:, '取引価格（総額）'] = filtered_data['取引価格（総額）'] / 10000
            result = "NO DATA" if filtered_data.empty else filtered_data.to_html(classes='data', index=False, border=0)

            calculate_and_plot_stats(data, selected_district, selected_station)
            chart_exists = True

        except ValueError as e:
            error_message = f"输入错误: {e}"
        except Exception as e:
            error_message = f"错误: {e}"

    return render_template('index.html',
                           prediction_text=prediction_text, 
                           result=result, 
                           prefectures=list(prefecture_city_district.keys()), 
                           city_to_districts=prefecture_city_district,
                           selected_prefecture=selected_prefecture, 
                           selected_city=selected_city, 
                           selected_district=selected_district, 
                           chart_exists=chart_exists, 
                           error_message=error_message,
                           property_type=property_type,
                           analysis_type=analysis_type,
                           district_price_trend_path='/static/district_price_trend.png' if chart_exists else '',
                           district_transaction_volume_path='/static/district_transaction_volume.png' if chart_exists else '',
                           district_price_distribution_path='/static/district_price_distribution.png' if chart_exists else '',
                           district_price_per_sqm_trend_path='/static/district_price_per_sqm_trend.png' if chart_exists else '',
                           
                           station_price_trend_path='/static/station_price_trend.png' if chart_exists else '',
                           station_transaction_volume_path='/static/station_transaction_volume.png' if chart_exists else '',
                           station_price_distribution_path='/static/station_price_distribution.png' if chart_exists else '',
                           station_price_per_sqm_trend_path='/static/station_price_per_sqm_trend.png' if chart_exists else '',
                           station_price_distribution_pie_path ='/static/station_price_distribution_pie.png' if chart_exists else '',
                           district_price_distribution_pie_path ='/static/district_price_distribution_pie.png' if chart_exists else '',
                           selected_station=selected_station)

if __name__ == '__main__':
    app.run(debug=True, port=8070)

