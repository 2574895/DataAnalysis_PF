import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

class QuestionLevelAnalyzer:
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
            # Convert timestamp to datetime for time-based analysis
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                # Filter for April 1st to August 31st 2025
                start_date = pd.Timestamp('2025-04-01')
                end_date = pd.Timestamp('2025-08-31')
                self.df = self.df[(self.df['timestamp'] >= start_date) & (self.df['timestamp'] <= end_date)]
        except:
            print("⚠️ No data path provided, assuming data is already loaded")

        return self.df

    def filter_learning_related_conversations(self):
        """Filter only learning-related conversations"""
        learning_keywords = [
            'learn', 'study', 'understand', 'explain', 'how', 'what', 'why', 'teach',
            'concept', 'algorithm', 'model', 'data', 'analysis', 'programming', 'code',
            'python', 'machine learning', 'ai', 'deep learning', 'neural', 'network',
            'statistics', 'probability', 'math', 'calculus', 'linear algebra',
            'optimization', 'gradient', 'loss', 'accuracy', 'training', 'validation'
        ]

        # Filter conversations containing learning keywords
        learning_mask = self.df['content'].str.lower().apply(
            lambda x: any(keyword in str(x) for keyword in learning_keywords)
        )

        # Conversations with questions (has_question 컬럼이 없으면 계산)
        if 'has_question' not in self.df.columns:
            self.df['has_question'] = self.df['content'].str.contains(r'\?|what|how|why|when|where', case=False, na=False)

        question_mask = self.df['has_question'] == True

        # Conversations with high technical term density
        if 'tech_term_density' not in self.df.columns:
            # 간단한 기술 용어 밀도 계산
            tech_terms = ['python', 'ai', 'machine learning', 'data', 'algorithm', 'neural', 'network', 'model', 'training']
            self.df['tech_term_density'] = self.df['content'].str.lower().apply(
                lambda x: sum(1 for term in tech_terms if term in str(x)) / len(tech_terms) if x else 0
            )

        tech_mask = self.df['tech_term_density'] > 0.1

        # Learning-related = (keywords) OR (questions) OR (high tech density)
        learning_related = self.df[learning_mask | question_mask | tech_mask].copy()

        # Ensure date column exists for time-based analysis
        if 'date' not in learning_related.columns and 'timestamp' in learning_related.columns:
            learning_related['date'] = pd.to_datetime(learning_related['timestamp'].dt.date)

        print(f"📚 Total conversations: {len(self.df)}")
        print(f"🎓 Learning-related conversations: {len(learning_related)}")
        print(f"📊 Learning ratio: {len(learning_related)/len(self.df)*100:.1f}%")

        return learning_related

    def analyze_question_level_trends(self, learning_data):
        """Analyze question level evolution trends"""
        # Ensure timestamp is datetime for proper grouping
        if 'timestamp' in learning_data.columns:
            learning_data = learning_data.copy()
            if not pd.api.types.is_datetime64_any_dtype(learning_data['timestamp']):
                learning_data['timestamp'] = pd.to_datetime(learning_data['timestamp'])

        # Daily question depth average - use timestamp for consistent grouping
        if 'date' in learning_data.columns:
            # Ensure date column is datetime type
            if not pd.api.types.is_datetime64_any_dtype(learning_data['date']):
                learning_data = learning_data.copy()
                learning_data['date'] = pd.to_datetime(learning_data['date'])
            daily_question_depth = learning_data.groupby('date')['question_depth'].mean()
        else:
            # Fallback to daily grouping by timestamp
            daily_question_depth = learning_data.groupby(pd.Grouper(key='timestamp', freq='D'))['question_depth'].mean()

        # Weekly question depth changes
        weekly_question_depth = learning_data.groupby(pd.Grouper(key='timestamp', freq='W'))['question_depth'].mean()

        # Monthly question depth changes - use 'ME' instead of deprecated 'M'
        monthly_question_depth = learning_data.groupby(pd.Grouper(key='timestamp', freq='ME'))['question_depth'].mean()

        # Apply topic refinement for better categorization (same as topic_analyzer_en.py)
        df = learning_data.copy()

        # Refine General topics based on content analysis
        general_mask = df["primary_topic"] == "General"

        if general_mask.sum() > 0:
            general_data = df[general_mask].copy()

            # More comprehensive keywords with lower threshold for better classification
            topic_keywords = {
                'Programming': ['code', 'python', 'javascript', 'java', 'c++', 'php', 'ruby', 'swift', 'kotlin',
                              'function', 'class', 'method', 'variable', 'loop', 'algorithm', 'debug', 'error',
                              'compile', 'syntax', 'programming', 'script', 'library', 'framework', 'api',
                              'database', 'sql', 'query', 'server', 'backend', 'frontend'],
                'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'network',
                         'deep learning', 'model', 'training', 'predict', 'classification', 'regression',
                         'tensor', 'pytorch', 'tensorflow', 'keras', 'scikit', 'nlp', 'vision', 'gpt',
                         'bert', 'transformer', 'embedding', 'token', 'fine-tune', 'inference'],
                'Data Science': ['data', 'dataset', 'dataframe', 'pandas', 'numpy', 'matplotlib', 'seaborn',
                               'analysis', 'analytics', 'statistics', 'probability', 'correlation', 'plot',
                               'visualization', 'chart', 'graph', 'csv', 'json', 'excel', 'table', 'pivot'],
                'Web Development': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'node', 'express',
                                   'jquery', 'bootstrap', 'sass', 'webpack', 'babel', 'npm', 'yarn', 'web',
                                   'website', 'browser', 'dom', 'http', 'ajax', 'json', 'api', 'rest'],
                'Mathematics': ['math', 'calculus', 'algebra', 'geometry', 'statistics', 'probability',
                              'equation', 'formula', 'theorem', 'matrix', 'vector', 'integral', 'derivative',
                              'function', 'graph', 'plot', 'linear', 'quadratic', 'differential'],
                'Development Tools': ['vscode', 'cursor', 'git', 'github', 'terminal', 'cli', 'command',
                                    'shell', 'bash', 'docker', 'kubernetes', 'linux', 'mac', 'windows',
                                    'editor', 'ide', 'debug', 'compile', 'build', 'deploy'],
                'Design Tools': ['figma', 'sketch', 'photoshop', 'illustrator', 'ui', 'ux', 'design',
                               'wireframe', 'prototype', 'mockup', 'color', 'font', 'layout', 'responsive',
                               'mobile', 'web', 'app', 'interface', 'user experience'],
                'Research/Education': ['learn', 'study', 'understand', 'explain', 'research', 'paper',
                                     'experiment', 'methodology', 'analysis', 'theory', 'concept', 'principle',
                                     'education', 'teaching', 'course', 'tutorial', 'guide', 'documentation']
            }

            # Create a mapping for reclassification with priorities
            topic_mapping = {}
            for idx in general_data.index:
                content = str(general_data.loc[idx, 'content']).lower()

                # Find best matching topic based on keyword count
                best_topic = None
                max_matches = 0

                for topic, keywords in topic_keywords.items():
                    matches = sum(1 for keyword in keywords if keyword in content)
                    if matches > max_matches:
                        max_matches = matches
                        best_topic = topic

                # More flexible threshold: reclassify if we have at least 1 keyword match
                if best_topic and max_matches >= 1:
                    topic_mapping[idx] = best_topic

            # Apply reclassification
            for idx, new_topic in topic_mapping.items():
                df.loc[idx, "primary_topic"] = new_topic

        # Question category distribution changes over time (using refined topics)
        # More balanced bins: only 0 is Basic, rest distributed
        df['question_category'] = pd.cut(
            df['question_depth'],
            bins=[-0.1, 0.5, 2.5, 16.1],  # Basic: 0, Intermediate: 1-2, Advanced: 3+
            labels=['Basic', 'Intermediate', 'Advanced']
        )

        question_categories_over_time = df.groupby(
            [pd.Grouper(key='timestamp', freq='W'), 'question_category'],
            observed=False
        ).size().unstack().fillna(0)

        return daily_question_depth, weekly_question_depth, monthly_question_depth, question_categories_over_time

    def create_question_level_chart(self):
        """Create question level evolution chart"""
        learning_data = self.filter_learning_related_conversations()
        daily_depth, weekly_depth, monthly_depth, category_trends = self.analyze_question_level_trends(learning_data)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Question Level Evolution Analysis (April-August 2025, Learning Conversations Only)", fontsize=16, fontweight="bold")

        # 1. Daily question depth trend
        # Convert index to datetime for proper plotting
        if not pd.api.types.is_datetime64_any_dtype(daily_depth.index):
            daily_depth.index = pd.to_datetime(daily_depth.index)

        ax1.plot(daily_depth.index, daily_depth.values, linewidth=2, color="#2E86AB", alpha=0.7)
        ax1.fill_between(daily_depth.index, daily_depth.values, alpha=0.3, color="#2E86AB")
        ax1.set_title("Daily Question Depth Trend (April-August 2025)", fontweight="bold")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Average Question Depth")

        # Set date format for x-axis - ensure proper datetime handling
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Weekly ticks
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(True, alpha=0.3)

        # 2. Weekly question depth evolution
        ax2.plot(weekly_depth.index, weekly_depth.values, marker="o", linewidth=3,
                markersize=6, color="#FF6B35", markerfacecolor="#F24236")
        ax2.set_title("Weekly Question Depth Evolution (April-August 2025)", fontweight="bold")
        ax2.set_xlabel("Week")
        ax2.set_ylabel("Average Question Depth")

        # Set date format for x-axis - more robust approach
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(True, alpha=0.3)

        # 3. Question categories over time
        if not category_trends.empty:
            category_trends.plot(kind='area', stacked=True, ax=ax3,
                               color=['#4ECDC4', '#45B7D1', '#96CEB4'])
            ax3.set_title("Question Categories Over Time (April-August 2025)", fontweight="bold")
            ax3.set_xlabel("Week")
            ax3.set_ylabel("Number of Questions")
            ax3.legend(title="Question Level")
            ax3.tick_params(axis="x", rotation=45)

        # 4. Monthly progression
        ax4.plot(monthly_depth.index, monthly_depth.values, linewidth=4,
                marker="s", markersize=8, color="#F24236", markerfacecolor="#FF6B35")
        ax4.set_title("Monthly Question Level Progression (April-August 2025)", fontweight="bold")
        ax4.set_xlabel("Month")
        ax4.set_ylabel("Average Question Depth")
        ax4.tick_params(axis="x", rotation=45)
        ax4.grid(True, alpha=0.3)

        # Add trend line
        if len(monthly_depth) > 1:
            z = np.polyfit(range(len(monthly_depth)), monthly_depth.values, 1)
            p = np.poly1d(z)
            ax4.plot(monthly_depth.index, p(range(len(monthly_depth))),
                    "--", color="red", linewidth=2, alpha=0.8, label="Trend")
            ax4.legend()

        plt.tight_layout()
        chart_path = os.path.join(self.portfolio_dir, "question_level_evolution.png")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✅ Question level evolution chart created: {chart_path}")

        return len(learning_data), daily_depth.mean(), weekly_depth.mean()

if __name__ == "__main__":
    analyzer = QuestionLevelAnalyzer("../processed_conversations.csv")
    analyzer.load_data()
    learning_count, daily_avg, weekly_avg = analyzer.create_question_level_chart()
    print(f"📊 Learning conversations analyzed: {learning_count}")
    print(f"📈 Daily average question depth: {daily_avg:.2f}")
    print(f"📈 Weekly average question depth: {weekly_avg:.2f}")
