"""
Trend analysis utilities for Tech Extractor.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """Data class for trend analysis results."""
    technology: str
    trend_type: str
    growth_rate: float
    mentions: int
    sentiment: float
    sources: List[str]
    related_keywords: List[str]
    market_impact: str
    prediction: str


class TrendAnalyzer:
    """Trend analysis utilities for technology trends."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Trend Analyzer.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.trend_sources = self._load_trend_sources()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.prediction_engine = PredictionEngine()
    
    def _load_trend_sources(self) -> Dict[str, Dict[str, Any]]:
        """Load trend source configurations."""
        return {
            'github': {
                'enabled': True,
                'weight': 0.3,
                'apis': ['repositories', 'stars', 'forks', 'issues'],
                'time_windows': ['1m', '3m', '6m', '1y']
            },
            'stackoverflow': {
                'enabled': True,
                'weight': 0.25,
                'apis': ['questions', 'answers', 'views'],
                'time_windows': ['1m', '3m', '6m', '1y']
            },
            'reddit': {
                'enabled': True,
                'weight': 0.2,
                'apis': ['posts', 'comments', 'upvotes'],
                'time_windows': ['1m', '3m', '6m', '1y']
            },
            'news': {
                'enabled': True,
                'weight': 0.15,
                'apis': ['articles', 'mentions'],
                'time_windows': ['1w', '1m', '3m', '6m']
            },
            'npm': {
                'enabled': True,
                'weight': 0.1,
                'apis': ['downloads', 'packages'],
                'time_windows': ['1w', '1m', '3m', '6m']
            }
        }
    
    def analyze_trend(self, 
                     technology: str, 
                     time_period: str = "1y",
                     sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze trend for a specific technology.
        
        Args:
            technology: Technology name to analyze.
            time_period: Time period for analysis.
            sources: List of sources to use.
            
        Returns:
            Dictionary containing trend analysis.
        """
        if sources is None:
            sources = ['github', 'stackoverflow', 'reddit', 'news']
        
        # Collect data from sources
        source_data = {}
        total_mentions = 0
        weighted_growth = 0.0
        total_weight = 0.0
        
        for source in sources:
            if source in self.trend_sources and self.trend_sources[source]['enabled']:
                data = self._fetch_source_data(technology, source, time_period)
                if data:
                    source_data[source] = data
                    total_mentions += data.get('mentions', 0)
                    weight = self.trend_sources[source]['weight']
                    weighted_growth += data.get('growth_rate', 0) * weight
                    total_weight += weight
        
        # Calculate overall metrics
        overall_growth_rate = weighted_growth / total_weight if total_weight > 0 else 0.0
        
        # Determine trend type
        trend_type = self._classify_trend_type(overall_growth_rate)
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(technology, source_data)
        
        # Extract related keywords
        related_keywords = self._extract_related_keywords(technology, source_data)
        
        # Assess market impact
        market_impact = self._assess_market_impact(technology, overall_growth_rate, total_mentions)
        
        # Generate prediction
        prediction = self.prediction_engine.predict_trend(
            technology, overall_growth_rate, trend_type, time_period
        )
        
        return {
            'technology': technology,
            'trend_type': trend_type,
            'growth_rate': round(overall_growth_rate, 2),
            'mentions': total_mentions,
            'sentiment': round(sentiment, 2),
            'sources': list(source_data.keys()),
            'related_keywords': related_keywords,
            'market_impact': market_impact,
            'prediction': prediction,
            'source_data': source_data
        }
    
    def _fetch_source_data(self, technology: str, source: str, time_period: str) -> Optional[Dict[str, Any]]:
        """Fetch trend data from a specific source."""
        try:
            if source == 'github':
                return self._fetch_github_data(technology, time_period)
            elif source == 'stackoverflow':
                return self._fetch_stackoverflow_data(technology, time_period)
            elif source == 'reddit':
                return self._fetch_reddit_data(technology, time_period)
            elif source == 'news':
                return self._fetch_news_data(technology, time_period)
            elif source == 'npm':
                return self._fetch_npm_data(technology, time_period)
        except Exception as e:
            logger.warning(f"Failed to fetch data from {source}: {e}")
        
        return None
    
    def _fetch_github_data(self, technology: str, time_period: str) -> Dict[str, Any]:
        """Simulate fetching GitHub trend data."""
        # In a real implementation, this would call GitHub API
        # For simulation, generate realistic-looking data
        import random
        
        base_count = random.randint(100, 10000)
        growth_rate = random.uniform(-20, 50)
        
        return {
            'mentions': base_count,
            'growth_rate': growth_rate,
            'stars': base_count * random.uniform(0.5, 2.0),
            'forks': base_count * random.uniform(0.2, 0.8),
            'issues': base_count * random.uniform(0.1, 0.5),
            'pull_requests': base_count * random.uniform(0.05, 0.3)
        }
    
    def _fetch_stackoverflow_data(self, technology: str, time_period: str) -> Dict[str, Any]:
        """Simulate fetching Stack Overflow trend data."""
        import random
        
        base_count = random.randint(50, 2000)
        growth_rate = random.uniform(-15, 30)
        
        return {
            'mentions': base_count,
            'growth_rate': growth_rate,
            'questions': base_count,
            'answers': base_count * random.uniform(1.5, 3.0),
            'views': base_count * random.uniform(10, 100),
            'score': base_count * random.uniform(0.5, 2.0)
        }
    
    def _fetch_reddit_data(self, technology: str, time_period: str) -> Dict[str, Any]:
        """Simulate fetching Reddit trend data."""
        import random
        
        base_count = random.randint(20, 1000)
        growth_rate = random.uniform(-25, 40)
        
        return {
            'mentions': base_count,
            'growth_rate': growth_rate,
            'posts': base_count,
            'comments': base_count * random.uniform(2, 10),
            'upvotes': base_count * random.uniform(5, 50),
            'subreddits': random.randint(1, 10)
        }
    
    def _fetch_news_data(self, technology: str, time_period: str) -> Dict[str, Any]:
        """Simulate fetching news trend data."""
        import random
        
        base_count = random.randint(10, 500)
        growth_rate = random.uniform(-30, 60)
        
        return {
            'mentions': base_count,
            'growth_rate': growth_rate,
            'articles': base_count,
            'mentions_in_articles': base_count * random.uniform(2, 5),
            'sentiment_score': random.uniform(-0.5, 0.8)
        }
    
    def _fetch_npm_data(self, technology: str, time_period: str) -> Dict[str, Any]:
        """Simulate fetching NPM trend data."""
        import random
        
        base_count = random.randint(1000, 1000000)
        growth_rate = random.uniform(-10, 100)
        
        return {
            'mentions': base_count,
            'growth_rate': growth_rate,
            'downloads': base_count,
            'weekly_downloads': base_count // 4,
            'daily_downloads': base_count // 28
        }
    
    def _classify_trend_type(self, growth_rate: float) -> str:
        """Classify trend type based on growth rate."""
        if growth_rate > 20:
            return 'rising'
        elif growth_rate > 5:
            return 'growing'
        elif growth_rate > -5:
            return 'stable'
        elif growth_rate > -15:
            return 'declining'
        else:
            return 'falling'
    
    def _extract_related_keywords(self, technology: str, source_data: Dict[str, Any]) -> List[str]:
        """Extract related keywords from source data."""
        # In a real implementation, this would analyze the actual content
        # For simulation, generate relevant keywords based on technology
        keyword_map = {
            'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy', 'machine learning'],
            'javascript': ['react', 'vue', 'angular', 'nodejs', 'typescript', 'webpack'],
            'typescript': ['react', 'vue', 'angular', 'nodejs', 'javascript', 'type safety'],
            'react': ['javascript', 'typescript', 'next.js', 'redux', 'hooks', 'frontend'],
            'vue': ['javascript', 'typescript', 'nuxt', 'vuex', 'frontend', 'progressive'],
            'docker': ['kubernetes', 'containers', 'devops', 'microservices', 'cloud'],
            'kubernetes': ['docker', 'containers', 'orchestration', 'microservices', 'cloud'],
            'aws': ['cloud', 'ec2', 's3', 'lambda', 'serverless', 'infrastructure'],
            'tensorflow': ['machine learning', 'deep learning', 'ai', 'neural networks', 'python'],
            'pytorch': ['machine learning', 'deep learning', 'ai', 'neural networks', 'python']
        }
        
        tech_lower = technology.lower()
        if tech_lower in keyword_map:
            return keyword_map[tech_lower]
        
        # Generate generic keywords
        generic_keywords = [
            f'{technology} tutorial', f'{technology} examples', f'{technology} best practices',
            f'{technology} alternatives', f'{technology} vs', f'{technology} performance'
        ]
        
        return generic_keywords[:6]
    
    def _assess_market_impact(self, technology: str, growth_rate: float, mentions: int) -> str:
        """Assess market impact based on metrics."""
        impact_score = growth_rate * 0.6 + (mentions / 1000) * 0.4
        
        if impact_score > 30:
            return 'High'
        elif impact_score > 15:
            return 'Medium-High'
        elif impact_score > 5:
            return 'Medium'
        elif impact_score > 0:
            return 'Low-Medium'
        else:
            return 'Low'
    
    def compare_trends(self, technologies: List[str], time_period: str = "1y") -> Dict[str, Any]:
        """
        Compare trends across multiple technologies.
        
        Args:
            technologies: List of technology names to compare.
            time_period: Time period for analysis.
            
        Returns:
            Dictionary containing comparison results.
        """
        trend_data = {}
        
        for tech in technologies:
            trend_data[tech] = self.analyze_trend(tech, time_period)
        
        # Sort technologies by growth rate
        sorted_by_growth = sorted(
            trend_data.items(), 
            key=lambda x: x[1]['growth_rate'], 
            reverse=True
        )
        
        # Generate insights
        insights = self._generate_comparison_insights(trend_data)
        
        return {
            'technologies': trend_data,
            'ranking_by_growth': [(tech, data['growth_rate']) for tech, data in sorted_by_growth],
            'insights': insights,
            'analysis_period': time_period
        }
    
    def _generate_comparison_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights from trend comparison."""
        insights = []
        
        if not trend_data:
            return insights
        
        # Find top performer
        top_tech = max(trend_data.items(), key=lambda x: x[1]['growth_rate'])
        insights.append(f"{top_tech[0]} shows the strongest growth at {top_tech[1]['growth_rate']:+.1f}%")
        
        # Find declining technologies
        declining = [tech for tech, data in trend_data.items() if data['growth_rate'] < -5]
        if declining:
            insights.append(f"Declining technologies: {', '.join(declining)}")
        
        # Sentiment analysis
        positive_sentiment = [tech for tech, data in trend_data.items() if data['sentiment'] > 0.3]
        if positive_sentiment:
            insights.append(f"Technologies with positive sentiment: {', '.join(positive_sentiment)}")
        
        # High impact technologies
        high_impact = [tech for tech, data in trend_data.items() if data['market_impact'] in ['High', 'Medium-High']]
        if high_impact:
            insights.append(f"High market impact technologies: {', '.join(high_impact)}")
        
        return insights


class SentimentAnalyzer:
    """Sentiment analysis utilities for trend data."""
    
    def analyze_sentiment(self, technology: str, source_data: Dict[str, Any]) -> float:
        """
        Analyze sentiment for a technology across sources.
        
        Args:
            technology: Technology name.
            source_data: Data from various sources.
            
        Returns:
            Sentiment score between -1 (negative) and 1 (positive).
        """
        total_sentiment = 0.0
        total_weight = 0.0
        
        source_weights = {
            'github': 0.3,
            'stackoverflow': 0.25,
            'reddit': 0.2,
            'news': 0.15,
            'npm': 0.1
        }
        
        for source, data in source_data.items():
            weight = source_weights.get(source, 0.1)
            sentiment = self._analyze_source_sentiment(data)
            total_sentiment += sentiment * weight
            total_weight += weight
        
        return total_sentiment / total_weight if total_weight > 0 else 0.0
    
    def _analyze_source_sentiment(self, data: Dict[str, Any]) -> float:
        """Analyze sentiment for a specific source."""
        # Simulate sentiment analysis based on data patterns
        # In a real implementation, this would use NLP on actual text content
        
        # Higher growth rates generally correlate with positive sentiment
        growth_sentiment = min(1.0, max(-1.0, data.get('growth_rate', 0) / 50))
        
        # Higher activity levels generally indicate positive sentiment
        mentions = data.get('mentions', 0)
        activity_sentiment = min(1.0, mentions / 1000)
        
        # Weighted average
        return growth_sentiment * 0.7 + activity_sentiment * 0.3


class PredictionEngine:
    """Prediction engine for future trends."""
    
    def predict_trend(self, 
                     technology: str, 
                     current_growth: float, 
                     trend_type: str, 
                     time_period: str) -> str:
        """
        Predict future trend for a technology.
        
        Args:
            technology: Technology name.
            current_growth: Current growth rate.
            trend_type: Current trend type.
            time_period: Analysis time period.
            
        Returns:
            Prediction string.
        """
        # Simulate prediction logic
        if trend_type == 'rising':
            if current_growth > 40:
                return "Likely to continue strong growth, potentially becoming mainstream"
            else:
                return "Expected to maintain positive growth trajectory"
        elif trend_type == 'growing':
            return "Steady growth expected, may reach mainstream adoption"
        elif trend_type == 'stable':
            return "Likely to remain stable with minor fluctuations"
        elif trend_type == 'declining':
            return "May continue to decline unless major updates occur"
        elif trend_type == 'falling':
            return "Risk of becoming obsolete, consider alternatives"
        else:
            return "Insufficient data for reliable prediction"