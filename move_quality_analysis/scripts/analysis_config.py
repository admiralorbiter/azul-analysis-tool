#!/usr/bin/env python3
"""
Analysis Configuration System

This module provides a comprehensive configuration system for the move quality analyzer
with support for JSON/YAML configuration files, environment variable overrides, and
validation.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import yaml
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

class AnalysisMode(Enum):
    """Analysis modes for different use cases."""
    QUICK = "quick"           # Fast analysis with limited depth
    STANDARD = "standard"     # Balanced analysis
    COMPREHENSIVE = "comprehensive"  # Full analysis with all features
    RESEARCH = "research"     # Research mode with maximum depth

class ProcessingStrategy(Enum):
    """Processing strategies for different hardware configurations."""
    SINGLE_THREADED = "single_threaded"
    MULTI_THREADED = "multi_threaded"
    MULTI_PROCESS = "multi_process"
    HYBRID = "hybrid"

@dataclass
class ProcessingConfig:
    """Configuration for processing settings."""
    max_workers: int = 8
    batch_size: int = 100
    max_analysis_time: int = 30
    memory_limit_gb: float = 4.0
    enable_caching: bool = True
    cache_size_mb: int = 512
    retry_failed_analyses: bool = True
    max_retries: int = 3
    retry_delay: float = 0.1

@dataclass
class AnalysisComponentsConfig:
    """Configuration for analysis components."""
    enable_pattern_analysis: bool = True
    enable_strategic_analysis: bool = True
    enable_risk_analysis: bool = True
    enable_board_state_analysis: bool = True
    enable_opponent_denial: bool = True
    enable_timing_analysis: bool = True
    enable_neural_evaluation: bool = False
    enable_ml_integration: bool = False

@dataclass
class MoveGenerationConfig:
    """Configuration for move generation."""
    max_moves_per_position: int = 200
    enable_move_filtering: bool = True
    enable_move_prioritization: bool = True
    enable_move_clustering: bool = True
    min_strategic_value: float = 5.0
    min_likelihood: float = 0.05
    min_validation_score: float = 0.1

@dataclass
class DatabaseConfig:
    """Configuration for database settings."""
    results_db_path: str = "../data/comprehensive_analysis_results.db"
    cache_db_path: str = "../data/analysis_cache.db"
    enable_indexing: bool = True
    enable_compression: bool = False
    backup_enabled: bool = True
    backup_interval_hours: int = 24

@dataclass
class ReportingConfig:
    """Configuration for reporting and output."""
    save_intermediate_results: bool = True
    generate_detailed_reports: bool = True
    enable_progress_tracking: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    output_format: str = "json"
    enable_visualization: bool = False
    report_directory: str = "../reports"

@dataclass
class ComprehensiveAnalysisConfig:
    """Complete configuration for comprehensive analysis."""
    # Mode and strategy
    analysis_mode: AnalysisMode = AnalysisMode.STANDARD
    processing_strategy: ProcessingStrategy = ProcessingStrategy.MULTI_PROCESS
    
    # Component configurations
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    analysis_components: AnalysisComponentsConfig = field(default_factory=AnalysisComponentsConfig)
    move_generation: MoveGenerationConfig = field(default_factory=MoveGenerationConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    
    # Advanced settings
    enable_debug_mode: bool = False
    enable_profiling: bool = False
    enable_metrics_collection: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class ConfigurationManager:
    """Manages configuration loading, validation, and overrides."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = None
        self.logger = logging.getLogger(__name__)
    
    def load_configuration(self, config_path: Optional[str] = None) -> ComprehensiveAnalysisConfig:
        """Load configuration from file and environment variables."""
        if config_path:
            self.config_path = config_path
        
        # Start with default configuration
        self.config = ComprehensiveAnalysisConfig()
        
        # Load from file if specified
        if self.config_path and os.path.exists(self.config_path):
            self._load_from_file()
        
        # Apply environment variable overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        return self.config
    
    def _load_from_file(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)
            
            # Apply file configuration
            self._apply_file_config(file_config)
            
        except Exception as e:
            self.logger.warning(f"Failed to load configuration from {self.config_path}: {e}")
    
    def _apply_file_config(self, file_config: Dict[str, Any]):
        """Apply configuration from file."""
        # Apply processing config
        if 'processing' in file_config:
            processing_config = file_config['processing']
            for key, value in processing_config.items():
                if hasattr(self.config.processing, key):
                    setattr(self.config.processing, key, value)
        
        # Apply analysis components config
        if 'analysis_components' in file_config:
            components_config = file_config['analysis_components']
            for key, value in components_config.items():
                if hasattr(self.config.analysis_components, key):
                    setattr(self.config.analysis_components, key, value)
        
        # Apply move generation config
        if 'move_generation' in file_config:
            move_config = file_config['move_generation']
            for key, value in move_config.items():
                if hasattr(self.config.move_generation, key):
                    setattr(self.config.move_generation, key, value)
        
        # Apply database config
        if 'database' in file_config:
            db_config = file_config['database']
            for key, value in db_config.items():
                if hasattr(self.config.database, key):
                    setattr(self.config.database, key, value)
        
        # Apply reporting config
        if 'reporting' in file_config:
            report_config = file_config['reporting']
            for key, value in report_config.items():
                if hasattr(self.config.reporting, key):
                    setattr(self.config.reporting, key, value)
        
        # Apply top-level settings
        for key, value in file_config.items():
            if hasattr(self.config, key) and key not in ['processing', 'analysis_components', 'move_generation', 'database', 'reporting']:
                setattr(self.config, key, value)
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides."""
        # Processing overrides
        if os.environ.get('ANALYSIS_MAX_WORKERS'):
            self.config.processing.max_workers = int(os.environ['ANALYSIS_MAX_WORKERS'])
        
        if os.environ.get('ANALYSIS_BATCH_SIZE'):
            self.config.processing.batch_size = int(os.environ['ANALYSIS_BATCH_SIZE'])
        
        if os.environ.get('ANALYSIS_MAX_TIME'):
            self.config.processing.max_analysis_time = int(os.environ['ANALYSIS_MAX_TIME'])
        
        # Analysis mode override
        if os.environ.get('ANALYSIS_MODE'):
            mode_str = os.environ['ANALYSIS_MODE'].upper()
            if hasattr(AnalysisMode, mode_str):
                self.config.analysis_mode = AnalysisMode[mode_str]
        
        # Processing strategy override
        if os.environ.get('ANALYSIS_STRATEGY'):
            strategy_str = os.environ['ANALYSIS_STRATEGY'].upper()
            if hasattr(ProcessingStrategy, strategy_str):
                self.config.processing_strategy = ProcessingStrategy[strategy_str]
        
        # Database path override
        if os.environ.get('ANALYSIS_DB_PATH'):
            self.config.database.results_db_path = os.environ['ANALYSIS_DB_PATH']
        
        # Log level override
        if os.environ.get('ANALYSIS_LOG_LEVEL'):
            self.config.reporting.log_level = os.environ['ANALYSIS_LOG_LEVEL']
    
    def _validate_configuration(self):
        """Validate the configuration."""
        errors = []
        
        # Validate processing settings
        if self.config.processing.max_workers < 1:
            errors.append("max_workers must be at least 1")
        
        if self.config.processing.batch_size < 1:
            errors.append("batch_size must be at least 1")
        
        if self.config.processing.max_analysis_time < 1:
            errors.append("max_analysis_time must be at least 1 second")
        
        if self.config.processing.memory_limit_gb < 0.1:
            errors.append("memory_limit_gb must be at least 0.1 GB")
        
        # Validate move generation settings
        if self.config.move_generation.max_moves_per_position < 1:
            errors.append("max_moves_per_position must be at least 1")
        
        if not (0 <= self.config.move_generation.min_likelihood <= 1):
            errors.append("min_likelihood must be between 0 and 1")
        
        if not (0 <= self.config.move_generation.min_validation_score <= 1):
            errors.append("min_validation_score must be between 0 and 1")
        
        # Validate database settings
        if self.config.database.backup_interval_hours < 1:
            errors.append("backup_interval_hours must be at least 1")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def save_configuration(self, config: ComprehensiveAnalysisConfig, output_path: str):
        """Save configuration to file."""
        config_dict = asdict(config)
        
        # Convert enums to strings for JSON serialization
        config_dict['analysis_mode'] = config.analysis_mode.value
        config_dict['processing_strategy'] = config.processing_strategy.value
        
        # Save based on file extension
        if output_path.endswith('.yaml') or output_path.endswith('.yml'):
            with open(output_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        else:
            with open(output_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
    
    def create_configuration_template(self, template_path: str, format_type: str = "json"):
        """Create a configuration template file."""
        template_config = ComprehensiveAnalysisConfig()
        
        if format_type.lower() == "yaml":
            template_path = template_path.replace('.json', '.yaml')
            self.save_configuration(template_config, template_path)
        else:
            template_path = template_path.replace('.yaml', '.json')
            self.save_configuration(template_config, template_path)
    
    def get_mode_presets(self) -> Dict[str, ComprehensiveAnalysisConfig]:
        """Get preset configurations for different analysis modes."""
        presets = {}
        
        # Quick mode preset
        quick_config = ComprehensiveAnalysisConfig()
        quick_config.analysis_mode = AnalysisMode.QUICK
        quick_config.processing.max_workers = 2
        quick_config.processing.batch_size = 25
        quick_config.processing.max_analysis_time = 10
        quick_config.move_generation.max_moves_per_position = 50
        quick_config.analysis_components.enable_neural_evaluation = False
        quick_config.analysis_components.enable_ml_integration = False
        presets['quick'] = quick_config
        
        # Standard mode preset
        standard_config = ComprehensiveAnalysisConfig()
        standard_config.analysis_mode = AnalysisMode.STANDARD
        standard_config.processing.max_workers = 4
        standard_config.processing.batch_size = 50
        standard_config.processing.max_analysis_time = 20
        standard_config.move_generation.max_moves_per_position = 100
        presets['standard'] = standard_config
        
        # Comprehensive mode preset
        comprehensive_config = ComprehensiveAnalysisConfig()
        comprehensive_config.analysis_mode = AnalysisMode.COMPREHENSIVE
        comprehensive_config.processing.max_workers = 8
        comprehensive_config.processing.batch_size = 100
        comprehensive_config.processing.max_analysis_time = 30
        comprehensive_config.move_generation.max_moves_per_position = 200
        comprehensive_config.analysis_components.enable_neural_evaluation = True
        comprehensive_config.analysis_components.enable_ml_integration = True
        presets['comprehensive'] = comprehensive_config
        
        # Research mode preset
        research_config = ComprehensiveAnalysisConfig()
        research_config.analysis_mode = AnalysisMode.RESEARCH
        research_config.processing.max_workers = 12
        research_config.processing.batch_size = 200
        research_config.processing.max_analysis_time = 60
        research_config.move_generation.max_moves_per_position = 500
        research_config.analysis_components.enable_neural_evaluation = True
        research_config.analysis_components.enable_ml_integration = True
        research_config.enable_profiling = True
        research_config.enable_metrics_collection = True
        presets['research'] = research_config
        
        return presets

def main():
    """Main function for configuration management."""
    # Create configuration manager
    manager = ConfigurationManager()
    
    # Create configuration templates
    os.makedirs("../config", exist_ok=True)
    
    # Create JSON template
    manager.create_configuration_template("../config/analysis_config.json", "json")
    print("Created JSON configuration template: ../config/analysis_config.json")
    
    # Create YAML template
    manager.create_configuration_template("../config/analysis_config.yaml", "yaml")
    print("Created YAML configuration template: ../config/analysis_config.yaml")
    
    # Create mode-specific templates
    presets = manager.get_mode_presets()
    for mode, config in presets.items():
        template_path = f"../config/analysis_config_{mode}.json"
        manager.save_configuration(config, template_path)
        print(f"Created {mode} mode template: {template_path}")
    
    # Test configuration loading
    test_config = manager.load_configuration()
    print(f"Loaded default configuration with {test_config.processing.max_workers} workers")

if __name__ == "__main__":
    main() 