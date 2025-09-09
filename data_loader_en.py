import pandas as pd
import os
import json

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def _get_file_format(self):
        """파일 확장자에 따라 포맷 결정"""
        _, ext = os.path.splitext(self.file_path)
        return ext.lower()

    def _load_csv(self):
        """CSV 파일 로드"""
        return pd.read_csv(self.file_path)

    def _load_json(self):
        """JSON 파일 로드"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # JSON이 배열인 경우
        if isinstance(data, list):
            return pd.DataFrame(data)
        # JSON이 단일 객체인 경우
        else:
            return pd.DataFrame([data])

    def _load_jsonl(self):
        """JSONL 파일 로드"""
        data_list = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 빈 줄 스킵
                    data_list.append(json.loads(line.strip()))
        return pd.DataFrame(data_list)

    def load_data(self):
        if not os.path.exists(self.file_path):
            print(f"❌ Error: File not found at {self.file_path}")
            return False

        try:
            # 파일 포맷에 따라 로더 선택
            file_format = self._get_file_format()

            if file_format == '.csv':
                print("📄 Loading CSV file...")
                self.data = self._load_csv()
            elif file_format == '.json':
                print("📋 Loading JSON file...")
                self.data = self._load_json()
            elif file_format == '.jsonl':
                print("📝 Loading JSONL file...")
                self.data = self._load_jsonl()
            else:
                print(f"❌ Unsupported file format: {file_format}")
                print("📄 Supported formats: .csv, .json, .jsonl")
                return False

            # timestamp 컬럼 처리 (JSONL의 create_time을 사용)
            if 'create_time' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['create_time'], unit='s')
            elif 'timestamp' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            else:
                print("⚠️ Warning: No timestamp column found, skipping date filtering")
                return False

            # Filter data for April 1st to August 31st 2025
            start_date = pd.Timestamp('2025-04-01')
            end_date = pd.Timestamp('2025-08-31')
            self.data = self.data[(self.data['timestamp'] >= start_date) & (self.data['timestamp'] <= end_date)]

            # 필수 컬럼들 추가 (없으면 계산)
            if 'word_count' not in self.data.columns:
                self.data['word_count'] = self.data['content'].str.len()

            if 'question_depth' not in self.data.columns:
                # 간단한 질문 감지 로직
                self.data['question_depth'] = self.data['content'].str.contains(r'\?|what|how|why|when|where', case=False).astype(int)

            # 추가 컬럼 생성
            self.data['date'] = self.data['timestamp'].dt.date
            self.data['hour'] = self.data['timestamp'].dt.hour
            self.data['day_of_week'] = self.data['timestamp'].dt.day_name()

            print(f"✅ {len(self.data)} messages loaded successfully from {file_format.upper()} file")
            if 'timestamp' in self.data.columns:
                print(f"   📅 Filtered: 2025-04-01 ~ 2025-08-31")
            return True

        except Exception as e:
            print(f"❌ Data loading error: {e}")
            print(f"   File: {self.file_path}")
            print(f"   Format: {self._get_file_format()}")
            return False

    def get_data(self):
        return self.data

    def get_basic_stats(self):
        if self.data is not None and not self.data.empty:
            return {
                'total_messages': len(self.data),
                'start_date': self.data['timestamp'].min().strftime('%Y-%m-%d'),
                'end_date': self.data['timestamp'].max().strftime('%Y-%m-%d'),
                'avg_word_count': float(self.data['word_count'].mean()),
                'avg_question_depth': float(self.data['question_depth'].mean())
            }
        return {}

if __name__ == "__main__":
    loader = DataLoader("../processed_conversations.csv")
    if loader.load_data():
        stats = loader.get_basic_stats()
        print("✅ Data loader test completed")
        print(f"📊 Basic stats: {stats}")
