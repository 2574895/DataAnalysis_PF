# advanced_correlation_analyzer.py
# 상관관계 분석 모듈 - 변수 간 관계성 도출

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

class AdvancedCorrelationAnalyzer:
    """상관관계 기반 고급 분석 모듈"""

    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.portfolio_dir = "."
        os.makedirs(self.portfolio_dir, exist_ok=True)

    def load_data(self):
        """데이터 로드"""
        try:
            from data_loader_en import DataLoader
            loader = DataLoader(self.data_path)
            if loader.load_data():
                self.df = loader.data.copy()
                print("✅ 데이터 로드 성공")
                return True
            else:
                print("❌ 데이터 로드 실패")
                return False
        except Exception as e:
            print(f"❌ 데이터 로드 오류: {e}")
            return False

    def calculate_correlations(self):
        """다양한 상관관계 분석"""
        if self.df is None:
            return None

        # 분석할 주요 변수들
        numeric_cols = ['complexity_ma', 'word_count', 'question_depth', 'hour']

        # 사용할 수 있는 컬럼만 필터링
        available_cols = [col for col in numeric_cols if col in self.df.columns]

        if len(available_cols) < 2:
            print("❌ 상관관계 분석에 충분한 수치 데이터가 없습니다.")
            return None

        # 상관관계 행렬 계산
        correlation_matrix = self.df[available_cols].corr()

        # 시간대별 상관관계 분석
        hourly_correlations = {}
        for hour in range(24):
            hour_data = self.df[self.df['hour'] == hour]
            if len(hour_data) > 10:  # 충분한 데이터가 있는 경우만
                if len(available_cols) >= 2:
                    hourly_correlations[hour] = hour_data[available_cols].corr()

        print("✅ 상관관계 분석 완료")
        return {
            'overall': correlation_matrix,
            'hourly': hourly_correlations
        }

    def create_correlation_dashboard(self):
        """상관관계 기반 개인화 학습 패턴 분석 대시보드 생성"""
        correlations = self.calculate_correlations()
        if correlations is None:
            return False

        # Figure 1: 학습 패턴 상관관계 분석
        fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig1.suptitle("Learning Pattern Correlation Deep Analysis (April-August 2025)", fontsize=16, fontweight="bold")

        # 1. 학습 변수 간 상관관계 히트맵
        corr_matrix = correlations['overall']
        if not corr_matrix.empty:
            # Column name mapping for better readability
            display_names = {
                'complexity_ma': 'Learning Complexity',
                'word_count': 'Expression Length',
                'question_depth': 'Question Depth',
                'hour': 'Hour'
            }
            display_matrix = corr_matrix.rename(columns=display_names, index=display_names)

            sns.heatmap(display_matrix, annot=True, cmap='RdYlBu_r', center=0,
                       square=True, ax=ax1, cbar_kws={'shrink': 0.8})
            ax1.set_title("Learning Variables Correlation Matrix", fontweight="bold", fontsize=12)

        # 2. 시간대별 학습 패턴 상관관계 변화
        if correlations['hourly']:
            hours = []
            complexity_word_corr = []
            complexity_question_corr = []

            for hour, corr_df in correlations['hourly'].items():
                if 'word_count' in corr_df.columns and 'question_depth' in corr_df.columns:
                    corr_value = corr_df.loc['word_count', 'question_depth']
                    if not pd.isna(corr_value):
                        hours.append(hour)
                        complexity_word_corr.append(corr_value)
                        complexity_question_corr.append(corr_value)

            if hours and complexity_word_corr:
                ax2.plot(hours, complexity_word_corr, 'o-', linewidth=3, markersize=8,
                        color="#2E86AB", markerfacecolor='white', markeredgewidth=2,
                        label='Expression ↔ Question Depth')

                ax2.axhline(y=0, color='black', linestyle='--', linewidth=2, alpha=0.5)
                ax2.fill_between(hours, complexity_word_corr, 0,
                               where=(np.array(complexity_word_corr) >= 0),
                               color="#2E86AB", alpha=0.2)
                ax2.fill_between(hours, complexity_word_corr, 0,
                               where=(np.array(complexity_word_corr) < 0),
                               color="#F24236", alpha=0.2)

                ax2.set_title("Hourly Learning Pattern Correlation Changes", fontweight="bold", fontsize=12)
                ax2.set_xlabel("Hour")
                ax2.set_ylabel("Correlation Coefficient")
                ax2.set_xticks(range(0, 24, 2))
                ax2.legend()
                ax2.grid(True, alpha=0.3)

        # 3. 요일별 학습 스타일 상관관계
        if 'day_of_week' in self.df.columns:
            day_correlations = {}
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            for day in days_order:
                day_data = self.df[self.df['day_of_week'] == day]
                if len(day_data) > 10:
                    available_cols = [col for col in ['word_count', 'question_depth']
                                    if col in day_data.columns]
                    if len(available_cols) >= 2:
                        day_corr = day_data[available_cols].corr()
                        if 'word_count' in day_corr.columns and 'question_depth' in day_corr.columns:
                            day_correlations[day] = day_corr.loc['word_count', 'question_depth']

            if day_correlations:
                days = list(day_correlations.keys())
                day_corr_values = list(day_correlations.values())

                colors = ['#FF6B6B' if v >= 0.3 else '#FFD93D' if v >= 0 else '#6BCF7F' if v >= -0.3 else '#4ECDC4' for v in day_corr_values]
                bars = ax3.bar(range(len(days)), day_corr_values, color=colors, alpha=0.8, edgecolor='black')

                ax3.axhline(y=0.3, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Strong Positive Correlation')
                ax3.axhline(y=-0.3, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Strong Negative Correlation')
                ax3.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5, label='No Correlation')

                ax3.set_title("Daily Learning Style Correlation", fontweight="bold", fontsize=12)
                ax3.set_xlabel("Day of Week")
                ax3.set_ylabel("Correlation Coefficient")
                ax3.set_xticks(range(len(days)))
                ax3.set_xticklabels([day[:3] for day in days], rotation=45, ha='right')
                ax3.legend()
                ax3.grid(True, alpha=0.3)

                # 각 바 위에 값 표시
                for i, v in enumerate(day_corr_values):
                    ax3.text(i, v + 0.02 if v >= 0 else v - 0.08, f'{v:.2f}', ha='center',
                           va='bottom' if v >= 0 else 'top', fontweight='bold')

        # 4. 상관관계 강도 및 의미 분석
        corr_matrix = correlations['overall']
        if not corr_matrix.empty:
            # 상관관계 계수의 절대값 분포
            abs_corr_values = corr_matrix.abs().values
            abs_corr_values = abs_corr_values[abs_corr_values != 1.0]  # 자기상관 제외

            if len(abs_corr_values) > 0:
                # 상관관계 강도별 분포
                weak_corr = len(abs_corr_values[(abs_corr_values >= 0) & (abs_corr_values < 0.3)])
                moderate_corr = len(abs_corr_values[(abs_corr_values >= 0.3) & (abs_corr_values < 0.7)])
                strong_corr = len(abs_corr_values[abs_corr_values >= 0.7])

                categories = ['Weak Correlation\n(0-0.3)', 'Moderate Correlation\n(0.3-0.7)', 'Strong Correlation\n(0.7+)']
                counts = [weak_corr, moderate_corr, strong_corr]
                colors = ['#90EE90', '#FFD700', '#FF6347']

                bars = ax4.bar(categories, counts, color=colors, alpha=0.8, edgecolor='black')
                ax4.set_title("Correlation Strength Distribution & Learning Pattern Analysis", fontweight="bold", fontsize=12)
                ax4.set_ylabel("Number of Correlation Pairs")
                ax4.grid(True, alpha=0.3)

                # 각 바 위에 값 표시
                for i, v in enumerate(counts):
                    ax4.text(i, v + max(counts) * 0.02, str(v), ha='center', va='bottom', fontweight='bold')


        plt.tight_layout()
        plt.savefig(os.path.join(self.portfolio_dir, "correlation_learning_patterns.png"), dpi=300, bbox_inches='tight')
        plt.close()


        print("✅ 개인화된 상관관계 분석 대시보드 생성 완료")
        print(f"   📊 저장 위치: {os.path.join(self.portfolio_dir, 'correlation_learning_patterns.png')}")

        return True

    def get_correlation_insights(self):
        """상관관계 기반 인사이트 추출"""
        correlations = self.calculate_correlations()
        if correlations is None:
            return {}

        insights = {}

        # 전체 상관관계 분석
        corr_matrix = correlations['overall']
        if not corr_matrix.empty:
            # 가장 강한 상관관계 찾기
            abs_corr = corr_matrix.abs()
            np.fill_diagonal(abs_corr.values, 0)  # 대각선 0으로 설정

            max_corr_idx = abs_corr.stack().idxmax()
            max_corr_value = abs_corr.stack().max()

            insights['strongest_correlation'] = {
                'variables': max_corr_idx,
                'correlation': max_corr_value,
                'strength': 'Strong' if max_corr_value >= 0.7 else ('Moderate' if max_corr_value >= 0.3 else 'Weak')
            }

            # 변수별 평균 상관관계
            insights['average_correlations'] = {}
            for col in corr_matrix.columns:
                avg_corr = corr_matrix[col].drop(col).abs().mean()
                insights['average_correlations'][col] = avg_corr

        return insights
