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
    
    def __init__(self, db_path: str = "src/validation_results.db"):
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
        """Analyze validation trends over specified time period using actual database structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get validation runs within date range (using actual table structure)
        cursor.execute('''
            SELECT id, timestamp, overall_score, status, execution_time
            FROM validation_runs 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        runs = cursor.fetchall()
        
        if not runs:
            conn.close()
            return self._empty_trends_response()
        
        # Get detailed validation results for these runs
        run_ids = [run[0] for run in runs]
        placeholders = ','.join(['?' for _ in run_ids])
        cursor.execute(f'''
            SELECT run_id, category, status, score, message
            FROM validation_results 
            WHERE run_id IN ({placeholders})
        ''', run_ids)
        
        detailed_results = cursor.fetchall()
        conn.close()
        
        # Analyze trends using actual data
        trends = {
            'overview': self._analyze_overview_trends_real(runs),
            'category_trends': self._analyze_category_trends_real(detailed_results),
            'failure_patterns': self._analyze_failure_patterns_real(detailed_results),
            'performance_metrics': self._analyze_performance_metrics_real(runs),
            'improvement_trends': self._analyze_improvement_trends_real(runs),
            'recommendations': self._generate_trend_recommendations_real(runs, detailed_results)
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


    def _analyze_overview_trends_real(self, runs: List) -> Dict[str, Any]:
        """Analyze overall validation trends using real data"""
        if not runs:
            return {}
        
        scores = [run[2] for run in runs if run[2] is not None]
        processing_times = [run[4] for run in runs if run[4] is not None]
        
        # Calculate daily counts
        daily_counts = defaultdict(int)
        for run in runs:
            date_str = run[1][:10] if run[1] else datetime.now().strftime('%Y-%m-%d')
            daily_counts[date_str] += 1
        
        # Calculate score distribution
        score_distribution = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
        for score in scores:
            if score <= 20:
                score_distribution['0-20'] += 1
            elif score <= 40:
                score_distribution['21-40'] += 1
            elif score <= 60:
                score_distribution['41-60'] += 1
            elif score <= 80:
                score_distribution['61-80'] += 1
            else:
                score_distribution['81-100'] += 1
        
        # Determine score trend
        if len(scores) >= 4:
            mid_point = len(scores) // 2
            first_half = scores[:mid_point]
            second_half = scores[mid_point:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 5:
                score_trend = 'increasing'
            elif second_avg < first_avg - 5:
                score_trend = 'decreasing'
            else:
                score_trend = 'stable'
        else:
            score_trend = 'insufficient_data'
        
        return {
            'total_validations': len(runs),
            'average_score': round(sum(scores) / len(scores), 1) if scores else 0.0,
            'score_distribution': score_distribution,
            'daily_validation_counts': dict(daily_counts),
            'score_trend': score_trend,
            'average_processing_time': round(sum(processing_times) / len(processing_times), 2) if processing_times else 0.0
        }
    
    def _analyze_category_trends_real(self, detailed_results: List) -> Dict[str, Any]:
        """Analyze category trends using real data"""
        category_data = defaultdict(lambda: {'scores': [], 'statuses': []})
        
        for result in detailed_results:
            run_id, category, status, score, message = result
            if category and score is not None:
                category_data[category]['scores'].append(score)
                category_data[category]['statuses'].append(status)
        
        category_trends = {}
        for category, data in category_data.items():
            scores = data['scores']
            statuses = data['statuses']
            
            if scores:
                avg_score = sum(scores) / len(scores)
                pass_count = sum(1 for s in statuses if s == 'pass')
                pass_rate = (pass_count / len(statuses)) * 100 if statuses else 0
                
                # Determine trend
                if len(scores) >= 2:
                    recent_avg = sum(scores[-2:]) / 2
                    older_avg = sum(scores[:-2]) / max(1, len(scores) - 2)
                    trend = 'increasing' if recent_avg > older_avg + 2 else ('decreasing' if recent_avg < older_avg - 2 else 'stable')
                else:
                    trend = 'insufficient_data'
                
                category_trends[category] = {
                    'average_score': round(avg_score, 1),
                    'pass_rate': round(pass_rate, 1),
                    'score_trend': trend,
                    'total_checks': len(scores)
                }
        
        return category_trends
    
    def _analyze_failure_patterns_real(self, detailed_results: List) -> Dict[str, Any]:
        """Analyze failure patterns using real data"""
        failure_counts = defaultdict(int)
        failure_messages = defaultdict(list)
        
        for result in detailed_results:
            run_id, category, status, score, message = result
            if status in ['fail', 'warning'] and message:
                failure_counts[message] += 1
                failure_messages[category].append(message)
        
        # Get most common failures
        most_common_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get failure rate by category
        category_failure_rates = {}
        for category, messages in failure_messages.items():
            total_for_category = len([r for r in detailed_results if r[1] == category])
            failure_rate = (len(messages) / total_for_category) * 100 if total_for_category > 0 else 0
            category_failure_rates[category] = round(failure_rate, 1)
        
        return {
            'most_common_failures': [{'failure': f[0], 'count': f[1]} for f in most_common_failures],
            'category_failure_rates': category_failure_rates,
            'total_failures': sum(failure_counts.values())
        }
    
    def _analyze_performance_metrics_real(self, runs: List) -> Dict[str, Any]:
        """Analyze performance metrics using real data"""
        if not runs:
            return {}
        
        scores = [run[2] for run in runs if run[2] is not None]
        processing_times = [run[4] for run in runs if run[4] is not None]
        statuses = [run[3] for run in runs if run[3]]
        
        success_count = sum(1 for s in statuses if s == 'completed')
        success_rate = (success_count / len(statuses)) * 100 if statuses else 0
        
        # Calculate processing time trend
        if len(processing_times) >= 4:
            mid_point = len(processing_times) // 2
            first_half_avg = sum(processing_times[:mid_point]) / mid_point
            second_half_avg = sum(processing_times[mid_point:]) / (len(processing_times) - mid_point)
            
            if second_half_avg > first_half_avg + 0.5:
                time_trend = 'increasing'
            elif second_half_avg < first_half_avg - 0.5:
                time_trend = 'decreasing'
            else:
                time_trend = 'stable'
        else:
            time_trend = 'insufficient_data'
        
        return {
            'success_rate': round(success_rate, 1),
            'average_processing_time': round(sum(processing_times) / len(processing_times), 2) if processing_times else 0.0,
            'processing_time_trend': time_trend,
            'total_runs': len(runs)
        }
    
    def _analyze_improvement_trends_real(self, runs: List) -> Dict[str, Any]:
        """Analyze improvement trends using real data"""
        if len(runs) < 2:
            return {'trend': 'insufficient_data', 'improvement_rate': 0.0}
        
        scores = [run[2] for run in runs if run[2] is not None]
        
        if len(scores) < 2:
            return {'trend': 'insufficient_data', 'improvement_rate': 0.0}
        
        # Calculate improvement rate (change from first to last)
        first_score = scores[0]
        last_score = scores[-1]
        improvement_rate = ((last_score - first_score) / first_score) * 100 if first_score > 0 else 0
        
        # Determine overall trend
        if improvement_rate > 5:
            trend = 'improving'
        elif improvement_rate < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'improvement_rate': round(improvement_rate, 1),
            'first_score': round(first_score, 1),
            'last_score': round(last_score, 1)
        }
    
    def _generate_trend_recommendations_real(self, runs: List, detailed_results: List) -> List[Dict[str, Any]]:
        """Generate recommendations based on real data analysis"""
        recommendations = []
        
        if not runs:
            return [{'title': 'No Data Available', 'priority': 'info', 'description': 'No validation data to analyze'}]
        
        scores = [run[2] for run in runs if run[2] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Score-based recommendations
        if avg_score < 70:
            recommendations.append({
                'title': 'Improve Overall Validation Scores',
                'priority': 'high',
                'description': f'Average score is {avg_score:.1f}%. Focus on addressing common validation failures.'
            })
        elif avg_score < 85:
            recommendations.append({
                'title': 'Good Performance - Minor Improvements Needed',
                'priority': 'medium',
                'description': f'Average score is {avg_score:.1f}%. Address remaining issues for excellence.'
            })
        
        # Category-specific recommendations
        category_data = defaultdict(list)
        for result in detailed_results:
            if result[3] and result[3] in ['fail', 'warning']:
                category_data[result[1]].append(result)
        
        for category, failures in category_data.items():
            if len(failures) > 2:  # More than 2 failures in this category
                recommendations.append({
                    'title': f'Focus on {category.replace("_", " ").title()}',
                    'priority': 'medium',
                    'description': f'{len(failures)} issues found in {category}. Review and improve this area.'
                })
        
        # Processing time recommendations
        processing_times = [run[4] for run in runs if run[4] is not None]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            if avg_time > 10:  # More than 10 seconds average
                recommendations.append({
                    'title': 'Optimize Processing Performance',
                    'priority': 'low',
                    'description': f'Average processing time is {avg_time:.1f}s. Consider optimization.'
                })
        
        if not recommendations:
            recommendations.append({
                'title': 'Excellent Performance',
                'priority': 'low',
                'description': 'Validation performance is excellent. Continue current practices.'
            })
        
        return recommendations[:5]  # Return top 5 recommendations

