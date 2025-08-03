"""
Test Strategic Pattern Analysis - Phase 2.4 Implementation

This module tests the strategic pattern analysis functionality:
- Factory control analysis
- Endgame counting analysis
- Risk/reward analysis
- Strategic pattern detection
"""

import unittest
import sys
import os

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.azul_strategic_patterns import StrategicPatternDetector
from core.azul_factory_control import FactoryControlDetector
from core.azul_endgame_counting import EndgameCountingDetector
from core.azul_risk_reward import RiskRewardAnalyzer
from core.azul_strategic_utils import StrategicAnalysisValidator, StrategicAnalysisReporter
from core.azul_model import AzulState


class TestStrategicPatternAnalysis(unittest.TestCase):
    """Test strategic pattern analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategic_detector = StrategicPatternDetector()
        self.factory_detector = FactoryControlDetector()
        self.endgame_detector = EndgameCountingDetector()
        self.risk_analyzer = RiskRewardAnalyzer()
        self.validator = StrategicAnalysisValidator()
        self.reporter = StrategicAnalysisReporter()
        
        # Create a simple test state
        self.test_state = self.create_test_state()
    
    def create_test_state(self) -> AzulState:
        """Create a test game state."""
        # Create a 2-player AzulState
        state = AzulState(2)
        
        # Set up factories with some tiles
        state.factories[0].AddTiles(2, 0)  # 2 blue tiles
        state.factories[0].AddTiles(1, 1)  # 1 yellow tile
        state.factories[1].AddTiles(1, 2)  # 1 red tile
        state.factories[1].AddTiles(1, 3)  # 1 black tile
        state.factories[3].AddTiles(1, 0)  # 1 blue tile
        state.factories[3].AddTiles(1, 4)  # 1 white tile
        
        # Add some tiles to center
        state.centre_pool.AddTiles(1, 0)  # 1 blue tile
        state.centre_pool.AddTiles(1, 1)  # 1 yellow tile
        state.centre_pool.AddTiles(1, 2)  # 1 red tile
        state.centre_pool.AddTiles(1, 3)  # 1 black tile
        state.centre_pool.AddTiles(1, 4)  # 1 white tile
        
        return state
    
    def test_factory_control_detection(self):
        """Test factory control opportunity detection."""
        opportunities = self.factory_detector.detect_opportunities(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(opportunities, list)
        
        # Check that opportunities have required fields
        for opp in opportunities:
            self.assertIsInstance(opp.control_type, str)
            self.assertIn(opp.control_type, ['domination', 'disruption', 'timing', 'color_control'])
            self.assertIsInstance(opp.factory_id, int)
            self.assertIsInstance(opp.strategic_value, float)
            self.assertIsInstance(opp.urgency_score, float)
            self.assertIsInstance(opp.urgency_level, str)
            self.assertIn(opp.urgency_level, ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
            self.assertIsInstance(opp.risk_assessment, str)
            self.assertIn(opp.risk_assessment, ['low', 'medium', 'high'])
            self.assertIsInstance(opp.move_suggestions, list)
            self.assertIsInstance(opp.confidence, float)
            self.assertIsInstance(opp.description, str)
    
    def test_endgame_counting_analysis(self):
        """Test endgame scenario analysis."""
        scenarios = self.endgame_detector.analyze_scenarios(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(scenarios, list)
        
        # Check that scenarios have required fields
        for scenario in scenarios:
            self.assertIsInstance(scenario.scenario_type, str)
            self.assertIn(scenario.scenario_type, ['conservation', 'optimization', 'blocking', 'timing'])
            self.assertIsInstance(scenario.remaining_tiles, dict)
            self.assertIsInstance(scenario.scoring_potential, float)
            self.assertIsInstance(scenario.optimal_sequence, list)
            self.assertIsInstance(scenario.risk_level, str)
            self.assertIn(scenario.risk_level, ['low', 'medium', 'high'])
            self.assertIsInstance(scenario.urgency_score, float)
            self.assertIsInstance(scenario.confidence, float)
            self.assertIsInstance(scenario.description, str)
    
    def test_risk_reward_analysis(self):
        """Test risk/reward scenario analysis."""
        scenarios = self.risk_analyzer.analyze_scenarios(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(scenarios, list)
        
        # Check that scenarios have required fields
        for scenario in scenarios:
            self.assertIsInstance(scenario.scenario_type, str)
            self.assertIn(scenario.scenario_type, ['floor_risk', 'blocking_risk', 'timing_risk', 'scoring_risk'])
            self.assertIsInstance(scenario.expected_value, float)
            self.assertIsInstance(scenario.risk_level, str)
            self.assertIn(scenario.risk_level, ['low', 'medium', 'high'])
            self.assertIsInstance(scenario.urgency_score, float)
            self.assertIsInstance(scenario.confidence, float)
            self.assertIsInstance(scenario.description, str)
            self.assertIsInstance(scenario.move_suggestions, list)
    
    def test_strategic_pattern_detection(self):
        """Test comprehensive strategic pattern detection."""
        patterns = self.strategic_detector.detect_strategic_patterns(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(patterns.factory_control_opportunities, list)
        self.assertIsInstance(patterns.endgame_scenarios, list)
        self.assertIsInstance(patterns.risk_reward_scenarios, list)
        self.assertIsInstance(patterns.total_patterns, int)
        self.assertIsInstance(patterns.total_strategic_value, float)
        self.assertIsInstance(patterns.confidence_score, float)
        
        # Check that total patterns is the sum of individual patterns
        expected_total = (len(patterns.factory_control_opportunities) + 
                         len(patterns.endgame_scenarios) + 
                         len(patterns.risk_reward_scenarios))
        self.assertEqual(patterns.total_patterns, expected_total)
    
    def test_strategic_move_suggestions(self):
        """Test strategic move suggestion generation."""
        suggestions = self.strategic_detector.get_strategic_move_suggestions(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(suggestions, list)
        
        # Check that suggestions are strings
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
    
    def test_strategic_position_analysis(self):
        """Test comprehensive strategic position analysis."""
        analysis = self.strategic_detector.analyze_strategic_position(self.test_state, 0)
        
        # Basic validation
        self.assertIsInstance(analysis, dict)
        self.assertIn('patterns', analysis)
        self.assertIn('strategic_themes', analysis)
        self.assertIn('position_strength', analysis)
        self.assertIn('critical_decisions', analysis)
        self.assertIn('move_suggestions', analysis)
        
        # Check strategic themes
        self.assertIsInstance(analysis['strategic_themes'], list)
        
        # Check position strength
        self.assertIsInstance(analysis['position_strength'], dict)
        required_strength_keys = ['factory_control_strength', 'endgame_strength', 
                                'risk_management_strength', 'overall_strength']
        for key in required_strength_keys:
            self.assertIn(key, analysis['position_strength'])
            self.assertIsInstance(analysis['position_strength'][key], float)
        
        # Check critical decisions
        self.assertIsInstance(analysis['critical_decisions'], list)
    
    def test_result_validation(self):
        """Test result validation functionality."""
        # Test factory control result validation
        factory_result = {
            'opportunities': [],
            'confidence': 0.8
        }
        self.assertTrue(self.validator.validate_factory_control_result(factory_result))
        
        # Test endgame counting result validation
        endgame_result = {
            'scenarios': [],
            'confidence': 0.7
        }
        self.assertTrue(self.validator.validate_endgame_counting_result(endgame_result))
        
        # Test risk/reward result validation
        risk_result = {
            'scenarios': [],
            'confidence': 0.6
        }
        self.assertTrue(self.validator.validate_risk_reward_result(risk_result))
        
        # Test strategic pattern result validation
        strategic_result = {
            'factory_control_opportunities': [],
            'endgame_scenarios': [],
            'risk_reward_scenarios': [],
            'total_patterns': 0,
            'confidence_score': 0.5
        }
        self.assertTrue(self.validator.validate_strategic_pattern_result(strategic_result))
    
    def test_report_generation(self):
        """Test report generation functionality."""
        # Test factory control report
        factory_result = {
            'opportunities': [],
            'confidence': 0.8
        }
        report = self.reporter.generate_analysis_report(factory_result, "factory_control")
        self.assertIsInstance(report, str)
        self.assertIn("Factory Control Analysis", report)
        
        # Test endgame counting report
        endgame_result = {
            'scenarios': [],
            'confidence': 0.7
        }
        report = self.reporter.generate_analysis_report(endgame_result, "endgame_counting")
        self.assertIsInstance(report, str)
        self.assertIn("Endgame Counting Analysis", report)
        
        # Test risk/reward report
        risk_result = {
            'scenarios': [],
            'confidence': 0.6
        }
        report = self.reporter.generate_analysis_report(risk_result, "risk_reward")
        self.assertIsInstance(report, str)
        self.assertIn("Risk/Reward Analysis", report)
        
        # Test strategic patterns report
        strategic_result = {
            'factory_control_opportunities': [],
            'endgame_scenarios': [],
            'risk_reward_scenarios': [],
            'total_patterns': 0,
            'confidence_score': 0.5,
            'total_strategic_value': 0.0
        }
        report = self.reporter.generate_analysis_report(strategic_result, "strategic_patterns")
        self.assertIsInstance(report, str)
        self.assertIn("Strategic Pattern Analysis", report)
    
    def test_performance_basic(self):
        """Test basic performance characteristics."""
        import time
        
        # Test factory control performance
        start_time = time.time()
        opportunities = self.factory_detector.detect_opportunities(self.test_state, 0)
        factory_time = time.time() - start_time
        
        # Test endgame counting performance
        start_time = time.time()
        scenarios = self.endgame_detector.analyze_scenarios(self.test_state, 0)
        endgame_time = time.time() - start_time
        
        # Test risk/reward performance
        start_time = time.time()
        risk_scenarios = self.risk_analyzer.analyze_scenarios(self.test_state, 0)
        risk_time = time.time() - start_time
        
        # Test strategic pattern performance
        start_time = time.time()
        patterns = self.strategic_detector.detect_strategic_patterns(self.test_state, 0)
        strategic_time = time.time() - start_time
        
        # Performance should be reasonable (under 1 second for each)
        self.assertLess(factory_time, 1.0, f"Factory control analysis took {factory_time:.3f}s")
        self.assertLess(endgame_time, 1.0, f"Endgame counting analysis took {endgame_time:.3f}s")
        self.assertLess(risk_time, 1.0, f"Risk/reward analysis took {risk_time:.3f}s")
        self.assertLess(strategic_time, 1.0, f"Strategic pattern analysis took {strategic_time:.3f}s")
        
        print(f"\nPerformance Results:")
        print(f"  Factory Control: {factory_time:.3f}s")
        print(f"  Endgame Counting: {endgame_time:.3f}s")
        print(f"  Risk/Reward: {risk_time:.3f}s")
        print(f"  Strategic Patterns: {strategic_time:.3f}s")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 