import pandas as pd
import numpy as np
import os

def load_and_clean_data(filename):
    """读取并清洗数据"""
    try:
        # 检查文件是否存在
        if not os.path.exists(filename):
            print("File not found")
            return None
        
        # 读取CSV文件
        df = pd.read_csv(filename)
        
        print("原始数据列名:", list(df.columns))
        print("原始数据形状:", df.shape)
        
        # 处理每列的数据
        score_columns = ['math', 'english', 'chinese']
        
        for col in score_columns:
            if col in df.columns:
                for idx, value in enumerate(df[col]):
                    # 检查是否为异常值
                    if pd.isna(value) or value == '' or str(value).strip().lower() in ['na', 'null', 'none', 'not_available', 'not_availa', 'nan']:
                        # 替换为'unknown'并打印警告
                        df.at[idx, col] = 'unknown'
                        print(f"Warning: '{value}' in row {idx+2}, column '{col}' replaced with 'unknown'")
                    else:
                        try:
                            # 尝试转换为数值
                            df.at[idx, col] = float(value)
                        except (ValueError, TypeError):
                            # 如果转换失败，替换为'unknown'并打印警告
                            df.at[idx, col] = 'unknown'
                            print(f"Warning: '{value}' in row {idx+2}, column '{col}' replaced with 'unknown'")
        
        return df
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def calculate_student_stats(df):
    """计算学生统计信息"""
    score_columns = ['math', 'english', 'chinese']
    
    # 创建一个副本用于计算，将'unknown'替换为NaN
    df_calc = df.copy()
    for col in score_columns:
        if col in df_calc.columns:
            df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce')
    
    # 计算每个学生的平均分（保留1位小数），忽略NaN值
    df['avg'] = df_calc[score_columns].mean(axis=1, skipna=True).round(1)
    
    # 如果所有科目都是unknown，平均分设为NaN
    for idx in df.index:
        if all(df.loc[idx, col] == 'unknown' for col in score_columns):
            df.at[idx, 'avg'] = 'unknown'
    
    return df

def calculate_subject_stats(df):
    """计算科目统计信息"""
    score_columns = ['math', 'english', 'chinese']
    subject_stats = []
    
    for subject in score_columns:
        if subject in df.columns:
            # 提取数值成绩，忽略'unknown'
            scores = []
            for value in df[subject]:
                if value != 'unknown' and not pd.isna(value):
                    try:
                        scores.append(float(value))
                    except (ValueError, TypeError):
                        pass
            
            if scores:  # 如果有有效成绩
                # 使用numpy计算统计指标
                max_score = np.max(scores)
                min_score = np.min(scores)
                avg_score = np.mean(scores).round(1)
                
                subject_stats.append({
                    'subject': subject,
                    'max': max_score,
                    'min': min_score,
                    'avg': avg_score
                })
            else:  # 如果没有有效成绩
                subject_stats.append({
                    'subject': subject,
                    'max': 'unknown',
                    'min': 'unknown',
                    'avg': 'unknown'
                })
    
    return pd.DataFrame(subject_stats)

def calculate_overall_stats(df):
    """计算全班成绩统计"""
    score_columns = ['math', 'english', 'chinese']
    all_scores = []
    
    for subject in score_columns:
        if subject in df.columns:
            # 提取数值成绩，忽略'unknown'
            for value in df[subject]:
                if value != 'unknown' and not pd.isna(value):
                    try:
                        all_scores.append(float(value))
                    except (ValueError, TypeError):
                        pass
    
    if all_scores:
        # 使用numpy计算方差和标准差
        variance = np.var(all_scores).round(2)
        std_dev = np.std(all_scores).round(2)
        
        print(f"\n全班成绩统计 (排除'unknown'值):")
        print(f"方差: {variance}")
        print(f"标准差: {std_dev}")
        
        return variance, std_dev
    else:
        print("\n全班成绩统计: 没有有效成绩数据")
        return 'unknown', 'unknown'

def main():
    # 读取并清洗数据
    df = load_and_clean_data('students.csv')
    
    if df is None:
        return
    
    print("\n数据读取成功！")
    print(f"共读取 {len(df)} 条学生记录")
    
    # 计算学生统计信息
    df_clean = calculate_student_stats(df)
    
    # 计算科目统计信息
    report_df = calculate_subject_stats(df_clean)
    
    # 计算全班统计信息
    calculate_overall_stats(df_clean)
    
    # 保存清洗后的数据
    df_clean.to_csv('students_clean.csv', index=False)
    print(f"\n已保存清洗后的数据到: students_clean.csv")
    
    # 保存统计报告
    report_df.to_csv('report.csv', index=False)
    print(f"已保存统计报告到: report.csv")
    
    # 显示结果预览
    print("\n清洗后的数据预览:")
    print(df_clean.head(15))  # 显示前15行
    
    print("\n统计报告预览 (排除'unknown'值):")
    print(report_df)

if __name__ == "__main__":
    main()