import pandas as pd

def classify_threshold(row):
    pH, tds, temp = row['pH'], row['NTU'], row['Temperature(C)']
    violations = 0

    if not (6.5 <= pH <= 9.0):
        violations += 1
    if not (200 <= tds <= 400):
        violations += 1
    if not (20 <= temp <= 40):
        violations += 1

    if violations == 0:
        return 'Safe'
    elif violations == 1:
        return 'Sign Of Water Pollution'
    else:
        return 'Pollution'

def classify_combined(df, window_minutes=5, threshold=2.0):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Phân loại theo ngưỡng kỹ thuật
    df['ThresholdLabel'] = df.apply(classify_threshold, axis=1)

    # Đánh giá độ lệch so với trung bình thời gian gần nhất
    for col in ['pH', 'NTU', 'Temperature(C)']:
        rolling_mean = df[col].rolling(f'{window_minutes}min').mean()
        deviation = (df[col] - rolling_mean).abs()
        df[f'{col}_dev'] = deviation

    df['violation_count'] = (df[[f'{col}_dev' for col in ['pH', 'NTU', 'Temperature(C)']] ] > threshold).sum(axis=1)

    def classify_deviation(row):
        if row['violation_count'] == 0:
            return 'Stable'
        elif row['violation_count'] == 1:
            return 'Slight Drift'
        else:
            return 'Unstable'

    df['DeviationLabel'] = df.apply(classify_deviation, axis=1)

    # Kết hợp hai nhãn thành 1 nhãn tổng quát
    def combine_labels(threshold_label, deviation_label):
        if threshold_label == 'Pollution' or deviation_label == 'Unstable':
            return 'Critical'
        elif threshold_label == 'Sign Of Water Pollution' or deviation_label == 'Slight Drift':
            return 'Warning'
        else:
            return 'Normal'

    df['FinalLabel'] = df.apply(lambda row: combine_labels(row['ThresholdLabel'], row['DeviationLabel']), axis=1)
    
    df.reset_index(inplace=True)
    return df
