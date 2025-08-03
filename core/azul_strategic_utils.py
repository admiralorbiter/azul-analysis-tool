"""
Azul Strategic Analysis Utilities - Phase 2.4 Implementation

This module provides utilities for strategic pattern analysis:
- Caching for analysis results
- Timeout handling for complex analysis
- Performance optimization utilities
- Strategic analysis helpers

Integrates with existing pattern detection system for comprehensive analysis.
"""

import time
import hashlib
import json
import threading
from contextlib import contextmanager
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from .azul_model import AzulState


@dataclass
class CacheEntry:
    """Represents a cached analysis result."""
    result: Dict[str, Any]
    timestamp: float
    analysis_type: str
    state_hash: str


class StrategicAnalysisCache:
    """Cache for strategic analysis results."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get_cached_result(self, state_hash: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        key = f"{state_hash}_{analysis_type}"
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if entry has expired
        if time.time() - entry.timestamp > self.ttl_seconds:
            del self.cache[key]
            return None
        
        return entry.result
    
    def cache_result(self, state_hash: str, analysis_type: str, result: Dict[str, Any]):
        """Cache analysis result."""
        key = f"{state_hash}_{analysis_type}"
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
        
        self.cache[key] = CacheEntry(
            result=result,
            timestamp=time.time(),
            analysis_type=analysis_type,
            state_hash=state_hash
        )
    
    def clear_expired_entries(self):
        """Clear expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry.timestamp > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for entry in self.cache.values():
            if current_time - entry.timestamp <= self.ttl_seconds:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }


class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


@contextmanager
def timeout(seconds: int):
    """Timeout context manager for analysis functions (Windows compatible)."""
    # For now, just yield without timeout to avoid Windows signal issues
    # TODO: Implement proper timeout for Windows
    yield


class StrategicAnalysisProfiler:
    """Profiler for strategic analysis performance."""
    
    def __init__(self):
        self.analysis_times: Dict[str, List[float]] = {}
        self.analysis_counts: Dict[str, int] = {}
    
    def start_analysis(self, analysis_type: str):
        """Start timing an analysis."""
        if analysis_type not in self.analysis_times:
            self.analysis_times[analysis_type] = []
            self.analysis_counts[analysis_type] = 0
        
        return time.time()
    
    def end_analysis(self, analysis_type: str, start_time: float):
        """End timing an analysis."""
        duration = time.time() - start_time
        self.analysis_times[analysis_type].append(duration)
        self.analysis_counts[analysis_type] += 1
    
    def get_analysis_stats(self, analysis_type: str) -> Dict[str, Any]:
        """Get statistics for a specific analysis type."""
        if analysis_type not in self.analysis_times:
            return {}
        
        times = self.analysis_times[analysis_type]
        count = self.analysis_counts[analysis_type]
        
        if not times:
            return {}
        
        return {
            'count': count,
            'total_time': sum(times),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'recent_times': times[-10:]  # Last 10 times
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all analysis types."""
        return {
            analysis_type: self.get_analysis_stats(analysis_type)
            for analysis_type in self.analysis_times.keys()
        }


class StateHasher:
    """Utility for creating consistent state hashes."""
    
    @staticmethod
    def hash_state(state: AzulState) -> str:
        """Create a hash of the game state for caching."""
        # Create a simplified representation of the state
        state_dict = {
            'factories': [sorted(factory) for factory in state.factories],
            'center': sorted(state.center),
            'player_states': []
        }
        
        for player_state in state.agents:
            player_dict = {
                'pattern_lines': player_state.lines_number,
                'wall': [list(row) for row in player_state.grid_state],
                'floor_line': sorted(player_state.floor_tiles),
                'score': player_state.score
            }
            state_dict['player_states'].append(player_dict)
        
        # Convert to JSON string and hash
        state_json = json.dumps(state_dict, sort_keys=True)
        return hashlib.md5(state_json.encode()).hexdigest()


class ProgressiveAnalysis:
    """Progressive analysis with early termination."""
    
    def __init__(self, max_time_per_analysis: float = 0.5):
        self.max_time_per_analysis = max_time_per_analysis
        self.profiler = StrategicAnalysisProfiler()
    
    def analyze_with_progressive_timeout(self, analysis_func, state: AzulState, player_id: int, 
                                       analysis_type: str) -> Dict[str, Any]:
        """Run analysis with progressive timeout."""
        start_time = self.profiler.start_analysis(analysis_type)
        
        try:
            with timeout(self.max_time_per_analysis):
                result = analysis_func(state, player_id)
        except TimeoutError:
            # Return partial results if analysis times out
            result = self._get_partial_result(analysis_type)
        
        self.profiler.end_analysis(analysis_type, start_time)
        return result
    
    def _get_partial_result(self, analysis_type: str) -> Dict[str, Any]:
        """Get partial results when analysis times out."""
        if analysis_type == "factory_control":
            return {
                'opportunities': [],
                'confidence': 0.3,
                'partial': True,
                'timeout': True
            }
        elif analysis_type == "endgame_counting":
            return {
                'scenarios': [],
                'confidence': 0.3,
                'partial': True,
                'timeout': True
            }
        elif analysis_type == "risk_reward":
            return {
                'scenarios': [],
                'confidence': 0.3,
                'partial': True,
                'timeout': True
            }
        else:
            return {
                'results': [],
                'confidence': 0.3,
                'partial': True,
                'timeout': True
            }


class StrategicAnalysisOptimizer:
    """Optimizer for strategic analysis performance."""
    
    def __init__(self):
        self.cache = StrategicAnalysisCache()
        self.profiler = StrategicAnalysisProfiler()
        self.progressive_analyzer = ProgressiveAnalysis()
        self.state_hasher = StateHasher()
    
    def optimize_analysis(self, analysis_func, state: AzulState, player_id: int, 
                         analysis_type: str) -> Dict[str, Any]:
        """Run optimized analysis with caching and timeout."""
        # Generate state hash for caching
        state_hash = self.state_hasher.hash_state(state)
        
        # Check cache first
        cached_result = self.cache.get_cached_result(state_hash, analysis_type)
        if cached_result is not None:
            return cached_result
        
        # Run analysis with progressive timeout
        result = self.progressive_analyzer.analyze_with_progressive_timeout(
            analysis_func, state, player_id, analysis_type
        )
        
        # Cache the result
        self.cache.cache_result(state_hash, analysis_type, result)
        
        return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            'cache_stats': self.cache.get_cache_stats(),
            'analysis_stats': self.profiler.get_all_stats()
        }
    
    def clear_cache(self):
        """Clear the analysis cache."""
        self.cache.cache.clear()
    
    def optimize_cache(self):
        """Optimize cache by removing expired entries."""
        self.cache.clear_expired_entries()


class StrategicAnalysisValidator:
    """Validator for strategic analysis results."""
    
    @staticmethod
    def validate_factory_control_result(result: Dict[str, Any]) -> bool:
        """Validate factory control analysis result."""
        if not isinstance(result, dict):
            return False
        
        required_keys = ['opportunities', 'confidence']
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result['opportunities'], list):
            return False
        
        if not isinstance(result['confidence'], (int, float)):
            return False
        
        return True
    
    @staticmethod
    def validate_endgame_counting_result(result: Dict[str, Any]) -> bool:
        """Validate endgame counting analysis result."""
        if not isinstance(result, dict):
            return False
        
        required_keys = ['scenarios', 'confidence']
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result['scenarios'], list):
            return False
        
        if not isinstance(result['confidence'], (int, float)):
            return False
        
        return True
    
    @staticmethod
    def validate_risk_reward_result(result: Dict[str, Any]) -> bool:
        """Validate risk/reward analysis result."""
        if not isinstance(result, dict):
            return False
        
        required_keys = ['scenarios', 'confidence']
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result['scenarios'], list):
            return False
        
        if not isinstance(result['confidence'], (int, float)):
            return False
        
        return True
    
    @staticmethod
    def validate_strategic_pattern_result(result: Dict[str, Any]) -> bool:
        """Validate strategic pattern analysis result."""
        if not isinstance(result, dict):
            return False
        
        required_keys = ['factory_control_opportunities', 'endgame_scenarios', 
                        'risk_reward_scenarios', 'total_patterns', 'confidence_score']
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result['factory_control_opportunities'], list):
            return False
        
        if not isinstance(result['endgame_scenarios'], list):
            return False
        
        if not isinstance(result['risk_reward_scenarios'], list):
            return False
        
        if not isinstance(result['total_patterns'], int):
            return False
        
        if not isinstance(result['confidence_score'], (int, float)):
            return False
        
        return True


class StrategicAnalysisReporter:
    """Reporter for strategic analysis results."""
    
    @staticmethod
    def generate_analysis_report(analysis_result: Dict[str, Any], analysis_type: str) -> str:
        """Generate a human-readable analysis report."""
        if analysis_type == "factory_control":
            return StrategicAnalysisReporter._format_factory_control_report(analysis_result)
        elif analysis_type == "endgame_counting":
            return StrategicAnalysisReporter._format_endgame_counting_report(analysis_result)
        elif analysis_type == "risk_reward":
            return StrategicAnalysisReporter._format_risk_reward_report(analysis_result)
        elif analysis_type == "strategic_patterns":
            return StrategicAnalysisReporter._format_strategic_patterns_report(analysis_result)
        else:
            return f"Analysis report for {analysis_type}: {str(analysis_result)}"
    
    @staticmethod
    def _format_factory_control_report(result: Dict[str, Any]) -> str:
        """Format factory control analysis report."""
        opportunities = result.get('opportunities', [])
        confidence = result.get('confidence', 0.0)
        
        report = f"Factory Control Analysis (Confidence: {confidence:.2f})\n"
        report += "=" * 50 + "\n"
        
        if not opportunities:
            report += "No factory control opportunities detected.\n"
        else:
            for i, opp in enumerate(opportunities, 1):
                report += f"\n{i}. {opp.get('control_type', 'Unknown')} Opportunity\n"
                report += f"   Factory: {opp.get('factory_id', 'Unknown')}\n"
                report += f"   Strategic Value: {opp.get('strategic_value', 0.0):.2f}\n"
                report += f"   Urgency: {opp.get('urgency_level', 'Unknown')}\n"
                report += f"   Risk: {opp.get('risk_assessment', 'Unknown')}\n"
                report += f"   Description: {opp.get('description', 'No description')}\n"
        
        return report
    
    @staticmethod
    def _format_endgame_counting_report(result: Dict[str, Any]) -> str:
        """Format endgame counting analysis report."""
        scenarios = result.get('scenarios', [])
        confidence = result.get('confidence', 0.0)
        
        report = f"Endgame Counting Analysis (Confidence: {confidence:.2f})\n"
        report += "=" * 50 + "\n"
        
        if not scenarios:
            report += "No endgame scenarios detected.\n"
        else:
            for i, scenario in enumerate(scenarios, 1):
                report += f"\n{i}. {scenario.get('scenario_type', 'Unknown')} Scenario\n"
                report += f"   Scoring Potential: {scenario.get('scoring_potential', 0.0):.2f}\n"
                report += f"   Risk Level: {scenario.get('risk_level', 'Unknown')}\n"
                report += f"   Urgency: {scenario.get('urgency_score', 0.0):.2f}\n"
                report += f"   Description: {scenario.get('description', 'No description')}\n"
        
        return report
    
    @staticmethod
    def _format_risk_reward_report(result: Dict[str, Any]) -> str:
        """Format risk/reward analysis report."""
        scenarios = result.get('scenarios', [])
        confidence = result.get('confidence', 0.0)
        
        report = f"Risk/Reward Analysis (Confidence: {confidence:.2f})\n"
        report += "=" * 50 + "\n"
        
        if not scenarios:
            report += "No risk/reward scenarios detected.\n"
        else:
            for i, scenario in enumerate(scenarios, 1):
                report += f"\n{i}. {scenario.get('scenario_type', 'Unknown')} Scenario\n"
                report += f"   Expected Value: {scenario.get('expected_value', 0.0):.2f}\n"
                report += f"   Risk Level: {scenario.get('risk_level', 'Unknown')}\n"
                report += f"   Urgency: {scenario.get('urgency_score', 0.0):.2f}\n"
                report += f"   Description: {scenario.get('description', 'No description')}\n"
        
        return report
    
    @staticmethod
    def _format_strategic_patterns_report(result: Dict[str, Any]) -> str:
        """Format strategic patterns analysis report."""
        total_patterns = result.get('total_patterns', 0)
        confidence = result.get('confidence_score', 0.0)
        strategic_value = result.get('total_strategic_value', 0.0)
        
        report = f"Strategic Pattern Analysis (Confidence: {confidence:.2f})\n"
        report += "=" * 50 + "\n"
        report += f"Total Patterns: {total_patterns}\n"
        report += f"Strategic Value: {strategic_value:.2f}\n"
        
        factory_control = result.get('factory_control_opportunities', [])
        endgame_scenarios = result.get('endgame_scenarios', [])
        risk_reward_scenarios = result.get('risk_reward_scenarios', [])
        
        report += f"\nFactory Control Opportunities: {len(factory_control)}\n"
        report += f"Endgame Scenarios: {len(endgame_scenarios)}\n"
        report += f"Risk/Reward Scenarios: {len(risk_reward_scenarios)}\n"
        
        return report 