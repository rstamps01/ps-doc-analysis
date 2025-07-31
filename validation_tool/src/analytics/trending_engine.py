"""
Trending Analytics Engine for Information Validation Tool

Provides comprehensive trending analytics including:
- Pass/fail rates over time by category
- Most common failure types
- Document quality improvement trends
- Time-to-completion metrics
- Accuracy confidence trends
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics

class TrendingEngine:
    """Advanced trending analytics engine for validation metrics"""
    
    def __init__(self, db_path: str = "validation_results.db"):
        self.db_path = db_path
        self.init_analytics_tables()
    
    def init_analytics_tables(self):
        """Initialize analytics-specific database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analytics summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_validations INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0.0,
                avg_processing_time REAL DEFAULT 0.0,
                most_common_failure TEXT,
                improvement_trend REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create category trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                pass_rate REAL DEFAULT 0.0,
                avg_score REAL DEFAULT 0.0,
                failure_count INTEGER DEFAULT 0,
                improvement_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create failure patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                failure_type TEXT NOT NULL,
                category TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_occurrence TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity TEXT DEFAULT 'medium',
                recommendation TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_validation_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze validation trends over specified time period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get validation results within date range
        cursor.execute('''
            SELECT * FROM validation_results 
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return self._empty_trends_response()
        
        # Analyze trends
        trends = {
            'overview': self._analyze_overview_trends(results),
            'category_trends': self._analyze_category_trends(results),
            'failure_patterns': self._analyze_failure_patterns(results),
            'performance_metrics': self._analyze_performance_metrics(results),
            'improvement_trends': self._analyze_improvement_trends(results),
            'recommendations': self._generate_trend_recommendations(results)
        }
        
        return trends
    
    def _analyze_overview_trends(self, results: List) -> Dict[str, Any]:
        """Analyze overall validation trends"""
        if not results:
            return {}
        
        scores = []
        processing_times = []
        daily_counts = defaultdict(int)
        
        for result in results:
            # Parse result data
            result_data = json.loads(result[3]) if result[3] else {}
            
            # Extract metrics
            if 'overall_score' in result_data:
                scores.append(result_data['overall_score'])
            
            if 'processing_time' in result_data:
                processing_times.append(result_data['processing_time'])
            
            # Count daily validations
            date_str = result[5][:10]  # Extract date part
            daily_counts[date_str] += 1
        
        return {
            'total_validations': len(results),
            'average_score': statistics.mean(scores) if scores else 0,
            'score_trend': self._calculate_trend(scores),
            'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'daily_validation_counts': dict(daily_counts),
            'score_distribution': self._calculate_score_distribution(scores)
        }
    
    def _analyze_category_trends(self, results: List) -> Dict[str, Any]:
        """Analyze trends by validation category"""
        category_data = defaultdict(lambda: {
            'scores': [],
            'pass_counts': 0,
            'total_counts': 0,
            'failures': []
        })
        
        for result in results:
            result_data = json.loads(result[3]) if result[3] else {}
            
            if 'category_results' in result_data:
                for category, cat_data in result_data['category_results'].items():
                    category_data[category]['scores'].append(cat_data.get('score', 0))
                    category_data[category]['total_counts'] += 1
                    
                    if cat_data.get('status') == 'pass':
                        category_data[category]['pass_counts'] += 1
                    else:
                        category_data[category]['failures'].append(cat_data.get('issues', []))
        
        # Calculate trends for each category
        trends = {}
        for category, data in category_data.items():
            trends[category] = {
                'pass_rate': (data['pass_counts'] / data['total_counts']) * 100 if data['total_counts'] > 0 else 0,
                'average_score': statistics.mean(data['scores']) if data['scores'] else 0,
                'score_trend': self._calculate_trend(data['scores']),
                'total_validations': data['total_counts'],
                'common_failures': self._extract_common_failures(data['failures'])
            }
        
        return trends
    
    def _analyze_failure_patterns(self, results: List) -> Dict[str, Any]:
        """Analyze common failure patterns and their frequency"""
        failure_counts = defaultdict(int)
        failure_categories = defaultdict(lambda: defaultdict(int))
        
        for result in results:
            result_data = json.loads(result[3]) if result[3] else {}
            
            if 'category_results' in result_data:
                for category, cat_data in result_data['category_results'].items():
                    if cat_data.get('status') != 'pass':
                        issues = cat_data.get('issues', [])
                        for issue in issues:
                            failure_type = issue.get('type', 'unknown')
                            failure_counts[failure_type] += 1
                            failure_categories[category][failure_type] += 1
        
        # Sort failures by frequency
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_common_failures': sorted_failures[:10],
            'failure_by_category': dict(failure_categories),
            'total_unique_failures': len(failure_counts),
            'failure_frequency_distribution': self._calculate_failure_distribution(failure_counts)
        }
    
    def _analyze_performance_metrics(self, results: List) -> Dict[str, Any]:
        """Analyze system performance metrics"""
        processing_times = []
        document_sizes = []
        success_rates = []
        
        for result in results:
            result_data = json.loads(result[3]) if result[3] else {}
            
            if 'processing_time' in result_data:
                processing_times.append(result_data['processing_time'])
            
            if 'document_size' in result_data:
                document_sizes.append(result_data['document_size'])
            
            if 'overall_score' in result_data:
                success_rates.append(1 if result_data['overall_score'] >= 80 else 0)
        
        return {
            'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'processing_time_trend': self._calculate_trend(processing_times),
            'success_rate': (sum(success_rates) / len(success_rates)) * 100 if success_rates else 0,
            'performance_stability': statistics.stdev(processing_times) if len(processing_times) > 1 else 0,
            'throughput_metrics': self._calculate_throughput_metrics(results)
        }
    
    def _analyze_improvement_trends(self, results: List) -> Dict[str, Any]:
        """Analyze document quality improvement trends over time"""
        # Sort results by date
        sorted_results = sorted(results, key=lambda x: x[5])
        
        # Group by document type or project
        project_trends = defaultdict(list)
        
        for result in sorted_results:
            result_data = json.loads(result[3]) if result[3] else {}
            project_id = result_data.get('project_id', 'default')
            
            if 'overall_score' in result_data:
                project_trends[project_id].append({
                    'date': result[5],
                    'score': result_data['overall_score']
                })
        
        # Calculate improvement trends
        improvement_analysis = {}
        for project_id, scores_data in project_trends.items():
            if len(scores_data) >= 2:
                scores = [item['score'] for item in scores_data]
                improvement_analysis[project_id] = {
                    'initial_score': scores[0],
                    'latest_score': scores[-1],
                    'improvement': scores[-1] - scores[0],
                    'trend_slope': self._calculate_trend_slope(scores),
                    'consistency': self._calculate_consistency(scores)
                }
        
        return improvement_analysis
    
    def _generate_trend_recommendations(self, results: List) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on trend analysis"""
        recommendations = []
        
        # Analyze recent performance
        recent_results = results[-10:] if len(results) >= 10 else results
        
        if recent_results:
            recent_scores = []
            for result in recent_results:
                result_data = json.loads(result[3]) if result[3] else {}
                if 'overall_score' in result_data:
                    recent_scores.append(result_data['overall_score'])
            
            if recent_scores:
                avg_recent_score = statistics.mean(recent_scores)
                
                if avg_recent_score < 70:
                    recommendations.append({
                        'type': 'quality_improvement',
                        'priority': 'high',
                        'title': 'Document Quality Below Threshold',
                        'description': f'Recent average score is {avg_recent_score:.1f}%. Focus on improving document completeness and accuracy.',
                        'action': 'Review validation criteria and provide additional training on document preparation.'
                    })
                
                elif avg_recent_score > 90:
                    recommendations.append({
                        'type': 'optimization',
                        'priority': 'low',
                        'title': 'Excellent Document Quality',
                        'description': f'Recent average score is {avg_recent_score:.1f}%. Consider optimizing validation criteria for efficiency.',
                        'action': 'Review validation criteria to ensure they remain challenging and relevant.'
                    })
        
        # Add more recommendations based on patterns
        recommendations.extend([
            {
                'type': 'process_improvement',
                'priority': 'medium',
                'title': 'Implement Regular Quality Reviews',
                'description': 'Schedule weekly reviews of validation results to identify improvement opportunities.',
                'action': 'Set up automated weekly reports and review meetings.'
            },
            {
                'type': 'training',
                'priority': 'medium',
                'title': 'Document Preparation Training',
                'description': 'Provide training on common validation failures to improve initial document quality.',
                'action': 'Create training materials based on most common failure patterns.'
            }
        ])
        
        return recommendations
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction (increasing, decreasing, stable)"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate numerical trend slope"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score (lower standard deviation = higher consistency)"""
        if len(values) < 2:
            return 100.0
        
        std_dev = statistics.stdev(values)
        mean_val = statistics.mean(values)
        
        # Coefficient of variation (inverted for consistency score)
        if mean_val != 0:
            cv = std_dev / mean_val
            return max(0, 100 - (cv * 100))
        
        return 100.0
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of scores by ranges"""
        distribution = {
            'excellent': 0,  # 90-100
            'good': 0,       # 80-89
            'fair': 0,       # 70-79
            'poor': 0        # <70
        }
        
        for score in scores:
            if score >= 90:
                distribution['excellent'] += 1
            elif score >= 80:
                distribution['good'] += 1
            elif score >= 70:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _calculate_failure_distribution(self, failure_counts: Dict) -> Dict[str, int]:
        """Calculate distribution of failure frequencies"""
        frequencies = list(failure_counts.values())
        
        if not frequencies:
            return {}
        
        max_freq = max(frequencies)
        
        distribution = {
            'very_common': 0,  # >75% of max
            'common': 0,       # 50-75% of max
            'occasional': 0,   # 25-50% of max
            'rare': 0          # <25% of max
        }
        
        for freq in frequencies:
            percentage = (freq / max_freq) * 100
            
            if percentage > 75:
                distribution['very_common'] += 1
            elif percentage > 50:
                distribution['common'] += 1
            elif percentage > 25:
                distribution['occasional'] += 1
            else:
                distribution['rare'] += 1
        
        return distribution
    
    def _extract_common_failures(self, failures_list: List) -> List[str]:
        """Extract most common failure types from nested failure data"""
        failure_counts = defaultdict(int)
        
        for failures in failures_list:
            for failure in failures:
                if isinstance(failure, dict):
                    failure_type = failure.get('type', 'unknown')
                    failure_counts[failure_type] += 1
        
        # Return top 5 most common failures
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        return [failure[0] for failure in sorted_failures[:5]]
    
    def _calculate_throughput_metrics(self, results: List) -> Dict[str, float]:
        """Calculate system throughput metrics"""
        if not results:
            return {}
        
        # Group by day
        daily_counts = defaultdict(int)
        for result in results:
            date_str = result[5][:10]
            daily_counts[date_str] += 1
        
        daily_values = list(daily_counts.values())
        
        return {
            'average_daily_validations': statistics.mean(daily_values) if daily_values else 0,
            'peak_daily_validations': max(daily_values) if daily_values else 0,
            'throughput_consistency': self._calculate_consistency(daily_values)
        }
    
    def _empty_trends_response(self) -> Dict[str, Any]:
        """Return empty trends response when no data available"""
        return {
            'overview': {
                'total_validations': 0,
                'average_score': 0,
                'message': 'No validation data available for trend analysis'
            },
            'category_trends': {},
            'failure_patterns': {
                'most_common_failures': [],
                'total_unique_failures': 0
            },
            'performance_metrics': {
                'average_processing_time': 0,
                'success_rate': 0
            },
            'improvement_trends': {},
            'recommendations': [
                {
                    'type': 'data_collection',
                    'priority': 'high',
                    'title': 'Start Collecting Validation Data',
                    'description': 'No historical data available for trend analysis.',
                    'action': 'Run validation processes to begin collecting trend data.'
                }
            ]
        }

    def generate_analytics_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        trends = self.analyze_validation_trends(days)
        
        # Add metadata
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': days,
                'report_version': '1.0'
            },
            'executive_summary': self._generate_executive_summary(trends),
            'detailed_analysis': trends
        }
        
        return report
    
    def _generate_executive_summary(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from trends data"""
        overview = trends.get('overview', {})
        
        summary = {
            'total_validations': overview.get('total_validations', 0),
            'average_score': overview.get('average_score', 0),
            'key_insights': [],
            'action_items': []
        }
        
        # Generate key insights
        if overview.get('average_score', 0) >= 85:
            summary['key_insights'].append('Document quality is consistently high')
        elif overview.get('average_score', 0) < 70:
            summary['key_insights'].append('Document quality needs improvement')
        
        # Extract action items from recommendations
        recommendations = trends.get('recommendations', [])
        high_priority_actions = [rec for rec in recommendations if rec.get('priority') == 'high']
        summary['action_items'] = [action['title'] for action in high_priority_actions[:3]]
        
        return summary

