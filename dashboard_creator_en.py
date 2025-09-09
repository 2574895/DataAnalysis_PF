import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

class DashboardCreator:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.portfolio_dir = "."
        os.makedirs(self.portfolio_dir, exist_ok=True)

    def load_data(self):
        # 이미 로드된 데이터가 있으면 사용
        if hasattr(self, 'df') and self.df is not None:
            return self.df

        # 기본적으로는 CSV 로드 (호환성 유지)
        try:
            self.df = pd.read_csv(self.data_path)
        except:
            print("⚠️ No data path provided, assuming data is already loaded")
            return None
        return self.df

    def create_comprehensive_dashboard(self):
        # 필수 컬럼들이 없으면 계산해서 추가
        if 'complexity_ma' not in self.df.columns:
            # word_count와 question_depth를 기반으로 복잡도 계산
            if 'word_count' in self.df.columns and 'question_depth' in self.df.columns:
                self.df['complexity_ma'] = (self.df['word_count'] / 100) + (self.df['question_depth'] * 10)
            else:
                # 기본값 설정
                self.df['complexity_ma'] = 1.0

        if 'primary_topic' not in self.df.columns:
            # conversation_title을 기반으로 8개 토픽으로 분류
            def classify_topic(title):
                title_lower = str(title).lower()

                # AI/ML 관련
                if any(keyword in title_lower for keyword in ['llm', 'ai', 'ml', 'neural', 'deep learning', 'machine learning', 'langchain', 'langgraph', 'transformer', 'gpt', 'bert']):
                    return 'AI/ML'

                # 개발 관련
                elif any(keyword in title_lower for keyword in ['설치', '오류', '코드', '개발', 'programming', 'python', 'javascript']):
                    return 'Development'

                # 클라우드/인프라 관련
                elif any(keyword in title_lower for keyword in ['aws', '클라우드', '서버리스', 'docker', 'kubernetes']):
                    return 'Cloud/Infra'

                # 디자인 관련
                elif any(keyword in title_lower for keyword in ['디자인', 'ui', 'ux', '그래픽', 'design']):
                    return 'Design'

                # 비즈니스 관련
                elif any(keyword in title_lower for keyword in ['프로젝트', '비즈니스', '네이밍', '마케팅', '사업', 'ott', 'ota']):
                    return 'Business'

                # 교육 관련
                elif any(keyword in title_lower for keyword in ['교육', '학습', 'teaching', 'course', 'tutorial']):
                    return 'Education'

                # 데이터 관련
                elif any(keyword in title_lower for keyword in ['데이터', '분석', 'data', 'analytics', '온톨로지']):
                    return 'Data'

                # 기타 (모든 토픽을 8개로 한정)
                else:
                    return 'General'

            self.df['primary_topic'] = self.df['conversation_title'].apply(classify_topic)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Personalized Learning Analysis Dashboard (Portfolio)", fontsize=16, fontweight="bold")

        # 1. Hourly Efficiency
        # filter by 2025-04-01 ~ 2025-08-31 if 'date' column exists
        df_for_hour = self.df
        if 'date' in self.df.columns:
            df_for_hour = self.df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df_for_hour['date']):
                df_for_hour['date'] = pd.to_datetime(df_for_hour['date'])
            df_for_hour = df_for_hour[(df_for_hour['date'] >= pd.Timestamp('2025-04-01')) & (df_for_hour['date'] <= pd.Timestamp('2025-08-31'))]
        hourly_eff = df_for_hour.groupby("hour")["complexity_ma"].mean()
        ax1.plot(hourly_eff.index, hourly_eff.values, marker="o", linewidth=3, color="#2E86AB")
        ax1.set_title("Hourly Efficiency", fontweight="bold")
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Complexity")
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=15, color="red", linestyle="--", alpha=0.7)

        # 2. Growth Trajectory (Enhanced like learning_growth_trajectory.png)
        # Filter data for April-August period
        df_for_growth = self.df
        if 'date' in self.df.columns:
            df_for_growth = self.df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df_for_growth['date']):
                df_for_growth['date'] = pd.to_datetime(df_for_growth['date'])
            df_for_growth = df_for_growth[(df_for_growth['date'] >= pd.Timestamp('2025-04-01')) &
                                         (df_for_growth['date'] <= pd.Timestamp('2025-08-31'))]

        # Ensure 'date' is datetime and group by date for daily aggregation
        if 'date' in df_for_growth.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_for_growth['date']):
                df_for_growth['date'] = pd.to_datetime(df_for_growth['date'])
            daily_growth = df_for_growth.groupby('date')["complexity_ma"].mean()
        else:
            daily_growth = df_for_growth.groupby(pd.Grouper(key='timestamp', freq='D'))["complexity_ma"].mean()

        # Calculate trend line (7-day moving average)
        trend_line = daily_growth.rolling(window=7).mean()

        # Plot the data
        ax2.fill_between(daily_growth.index, daily_growth.values, alpha=0.3, color="#FFA500")
        ax2.plot(daily_growth.index, trend_line.values, color="#FF6B35", linewidth=4, label="7-day Trend")

        # Add phase markers
        total_days = len(daily_growth)
        if total_days > 0:
            ax2.axvline(x=daily_growth.index[min(int(total_days*0.3), total_days-1)],
                       color="#2E86AB", linestyle="--", linewidth=2, alpha=0.8, label="Initial Phase")
            ax2.axvline(x=daily_growth.index[min(int(total_days*0.7), total_days-1)],
                       color="#F24236", linestyle="--", linewidth=2, alpha=0.8, label="Maturity Phase")

        ax2.set_title("Learning Growth Trajectory (April-August 2025)", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Date", fontsize=10)
        ax2.set_ylabel("Learning Complexity", fontsize=10)
        ax2.legend(fontsize=8)

        # Set robust date formatting on the x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax2.tick_params(axis='x', rotation=45, labelsize=8)
        ax2.grid(True, alpha=0.3)

        # 3. Topic Distribution
        topic_counts = self.df["primary_topic"].value_counts().head(8)
        colors = plt.cm.Set3(np.linspace(0, 1, len(topic_counts)))
        ax3.bar(range(len(topic_counts)), topic_counts.values, color=colors)
        ax3.set_title("Main Topics", fontweight="bold")
        ax3.set_xticks(range(len(topic_counts)))
        ax3.set_xticklabels([t[:10] + "..." if len(t) > 10 else t for t in topic_counts.index],
                           rotation=45, ha="right")
        ax3.set_ylabel("Frequency")

        # 4. Day of Week Patterns (필터링 기간 4월1일 ~ 8월말)
        df_for_day = self.df
        if 'date' in self.df.columns:
            try:
                df_for_day = self.df.copy()
                if not pd.api.types.is_datetime64_any_dtype(df_for_day['date']):
                    df_for_day['date'] = pd.to_datetime(df_for_day['date'])
                df_for_day = df_for_day[(df_for_day['date'] >= pd.Timestamp('2025-04-01')) & (df_for_day['date'] <= pd.Timestamp('2025-08-31'))]
            except Exception:
                pass
        day_stats = df_for_day.groupby("day_of_week")[['complexity_ma', 'question_depth']].mean()
        # Convert numeric day_of_week to day names
        day_mapping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                       4: "Friday", 5: "Saturday", 6: "Sunday"}
        if day_stats.index.dtype.kind in {'i','u','f'}:
            day_stats.index = day_stats.index.map(lambda x: day_mapping.get(int(x), str(x)))
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_stats = day_stats.reindex(day_order).fillna(0)

        x = range(len(day_order))
        width = 0.35
        ax4.bar([i - width/2 for i in x], day_stats["complexity_ma"], width, label="Complexity", color="#4ECDC4")
        ax4.bar([i + width/2 for i in x], day_stats["question_depth"], width, label="Question Depth", color="#45B7D1")
        ax4.set_title("Weekly Patterns", fontweight="bold")
        ax4.set_xticks(x)
        ax4.set_xticklabels([d[:3] for d in day_order])
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        chart_path = os.path.join(self.portfolio_dir, "comprehensive_learning_dashboard.png")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✅ Dashboard created: {chart_path}")

        return len(topic_counts), hourly_eff.max()

if __name__ == "__main__":
    creator = DashboardCreator("../processed_conversations.csv")
    creator.load_data()
    topic_count, max_efficiency = creator.create_comprehensive_dashboard()
    print(f"📊 Dashboard completed: {topic_count} topics")
