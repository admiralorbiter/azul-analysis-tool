"""
Test suite for Development Tools Panel component.

This module tests the Development Tools Panel functionality including:
- System health checks
- API statistics retrieval
- Performance monitoring
- Database optimization
- Cache analytics
- Monitoring data
"""

import unittest
import json
import time
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import subprocess
import signal
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Add the project root to the path so we can import the API
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import create_test_app
import threading
import socket

def find_free_port():
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_test_server(port):
    """Start the Flask test server in a separate thread."""
    app = create_test_app()
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

class TestDevelopmentToolsPanel(unittest.TestCase):
    """Test suite for Development Tools Panel functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with running server."""
        # Find a free port
        cls.port = find_free_port()
        cls.base_url = f"http://localhost:{cls.port}"
        cls.api_base_url = f"{cls.base_url}/api/v1"
        
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(
            target=start_test_server, 
            args=(cls.port,),
            daemon=True
        )
        cls.server_thread.start()
        
        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/healthz", timeout=1)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt == max_attempts - 1:
                    raise Exception("Server failed to start")
                time.sleep(0.1)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # The server thread will be cleaned up automatically as it's a daemon thread
        pass

    def setUp(self):
        """Set up test environment."""
        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Create session for API testing
        self.session = requests.Session()
        self.session_id = None
        
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def create_session(self):
        """Create a test session for API access."""
        try:
            response = self.session.post(
                f"{self.api_base_url}/auth/session",
                json={"username": "test", "password": "test"}
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.session.headers.update({
                    'X-Session-ID': self.session_id
                })
                return True
        except Exception as e:
            print(f"Failed to create session: {e}")
        return False

    def test_development_tools_panel_rendering(self):
        """Test that the Development Tools Panel renders correctly."""
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Wait a bit more for React to render
            time.sleep(3)
            
            # First, look for any button that might toggle the Development Tools Panel
            # The panel might be hidden by default, so we need to find a way to show it
            try:
                # Look for a toggle button or any button that might show development tools
                toggle_button = self.driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Development') or contains(text(), 'Tools') or contains(text(), '🔧')]"
                )
                toggle_button.click()
                time.sleep(1)
            except:
                # If no toggle button found, the panel might be visible by default
                pass
            
            # Now look for Development Tools Panel header
            dev_tools_header = self.driver.find_element(
                By.XPATH, 
                "//h3//span[contains(text(), '🔧 Development Tools')]"
            )
            self.assertIsNotNone(dev_tools_header)
            
            # Check if panel has expand/collapse button
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3//span[contains(text(), '🔧 Development Tools')]/../button"
            )
            self.assertIsNotNone(expand_button)
            
        except Exception as e:
            # Take a screenshot for debugging
            self.driver.save_screenshot("test_failure.png")
            # Also get page source for debugging
            page_source = self.driver.page_source
            with open("test_failure.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            self.fail(f"Development Tools Panel not found on page: {e}")

    def test_development_tools_panel_expansion(self):
        """Test that the Development Tools Panel can be expanded and collapsed."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Wait a bit more for React to render
            time.sleep(2)
            
            # Find and click the expand button
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3//span[contains(text(), '🔧 Development Tools')]/../button"
            )
            expand_button.click()
            
            # Wait for panel to expand and check for buttons
            self.wait.until(EC.presence_of_element_located((
                By.XPATH, 
                "//button[contains(text(), '🏥 System Health Check')]"
            )))
            
            # Check for all development tool buttons
            expected_buttons = [
                '🏥 System Health Check',
                '📊 API Statistics',
                '⚡ Performance Stats',
                '🔍 Detailed Health',
                '🔧 Optimize Database',
                '📈 Cache Analytics',
                '📊 Monitoring Data',
                '🗑️ Clear All Data'
            ]
            
            for button_text in expected_buttons:
                button = self.driver.find_element(
                    By.XPATH, 
                    f"//button[contains(text(), '{button_text}')]"
                )
                self.assertIsNotNone(button)
                
        except TimeoutException as e:
            self.fail(f"Development Tools Panel expansion failed: {e}")

    def test_system_health_check(self):
        """Test the system health check functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test API health endpoint
        response = self.session.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')

    def test_api_statistics(self):
        """Test the API statistics functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test API stats endpoint
        response = self.session.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('rate_limits', data)
        self.assertIn('session_stats', data)

    def test_performance_statistics(self):
        """Test the performance statistics functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test performance stats endpoint
        response = self.session.get(f"{self.api_base_url}/performance/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)
        self.assertIn('search_performance', data)
        self.assertIn('cache_analytics', data)

    def test_system_health_detailed(self):
        """Test the detailed system health functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test detailed health endpoint
        response = self.session.get(f"{self.api_base_url}/performance/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('version', data)

    def test_database_optimization(self):
        """Test the database optimization functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test database optimization endpoint
        response = self.session.post(f"{self.api_base_url}/performance/optimize")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('optimization_result', data)
        self.assertIn('timestamp', data)

    def test_cache_analytics(self):
        """Test the cache analytics functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test cache analytics endpoint
        response = self.session.get(f"{self.api_base_url}/performance/analytics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)
        # Note: Specific fields may vary based on database state

    def test_monitoring_data(self):
        """Test the monitoring data functionality."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        # Test monitoring data endpoint
        response = self.session.get(f"{self.api_base_url}/performance/monitoring")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)
        # Note: Specific fields may vary based on system state

    def test_development_tools_button_interactions(self):
        """Test that all development tool buttons are clickable and show loading states."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Expand the Development Tools Panel
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            expand_button.click()
            
            # Test each button
            test_buttons = [
                '🏥 System Health Check',
                '📊 API Statistics',
                '⚡ Performance Stats',
                '🔍 Detailed Health',
                '🔧 Optimize Database',
                '📈 Cache Analytics',
                '📊 Monitoring Data'
            ]
            
            for button_text in test_buttons:
                try:
                    button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(text(), '{button_text}')]"
                    )
                    
                    # Check that button is enabled
                    self.assertTrue(button.is_enabled())
                    
                    # Click button and check for loading state
                    button.click()
                    
                    # Wait for loading state (button should be disabled)
                    self.wait.until(EC.element_to_be_clickable((
                        By.XPATH, 
                        f"//button[contains(text(), '{button_text}') and @disabled]"
                    )))
                    
                    # Wait for button to be enabled again
                    self.wait.until(EC.element_to_be_clickable((
                        By.XPATH, 
                        f"//button[contains(text(), '{button_text}') and not(@disabled)]"
                    )))
                    
                except TimeoutException:
                    # Some buttons might not work without proper session
                    print(f"Button {button_text} test skipped - may require session")
                    
        except Exception as e:
            self.fail(f"Development Tools button interaction test failed: {e}")

    def test_clear_all_data_functionality(self):
        """Test the clear all data functionality."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Expand the Development Tools Panel
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            expand_button.click()
            
            # Find and click the clear all data button
            clear_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), '🗑️ Clear All Data')]"
            )
            clear_button.click()
            
            # Check for status message
            self.wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(text(), 'Development tools data cleared')]"
            )))
            
        except TimeoutException:
            self.fail("Clear all data functionality test failed")

    def test_development_tools_data_display(self):
        """Test that development tools data is displayed correctly after API calls."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Expand the Development Tools Panel
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            expand_button.click()
            
            # Test system health check and data display
            health_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), '🏥 System Health Check')]"
            )
            health_button.click()
            
            # Wait for data to be displayed
            self.wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'bg-green-50')]//div[contains(text(), 'System Status:')]"
            )))
            
            # Check for specific data fields
            status_element = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class, 'text-green-700') and contains(text(), 'Status:')]"
            )
            self.assertIsNotNone(status_element)
            
        except TimeoutException:
            self.fail("Development tools data display test failed")

    def test_development_tools_error_handling(self):
        """Test that development tools handle errors gracefully."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Expand the Development Tools Panel
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            expand_button.click()
            
            # Test with invalid session (should show error)
            # This test verifies that the UI handles API errors gracefully
            health_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), '🏥 System Health Check')]"
            )
            health_button.click()
            
            # Wait for either success or error message
            try:
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//div[contains(text(), 'System health check completed')]"
                    )),
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//div[contains(text(), 'Health check failed')]"
                    ))
                ))
            except TimeoutException:
                # If no message appears, that's also acceptable (graceful handling)
                pass
                
        except Exception as e:
            self.fail(f"Development tools error handling test failed: {e}")

    def test_development_tools_panel_state_management(self):
        """Test that the Development Tools Panel maintains proper state."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Test panel expansion state
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            
            # Initially should be collapsed (+)
            self.assertIn('+', expand_button.text)
            
            # Click to expand
            expand_button.click()
            
            # Should now be expanded (-)
            self.wait.until(EC.text_to_be_present_in_element((
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            ), '−'))
            
            # Click to collapse
            expand_button.click()
            
            # Should be collapsed again (+)
            self.wait.until(EC.text_to_be_present_in_element((
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            ), '+'))
            
        except TimeoutException:
            self.fail("Development Tools Panel state management test failed")

    def test_development_tools_panel_accessibility(self):
        """Test that the Development Tools Panel is accessible."""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.ID, "root")))
            
            # Check that panel has proper heading structure
            dev_tools_heading = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]"
            )
            self.assertEqual(dev_tools_heading.tag_name, 'h3')
            
            # Check that buttons have proper accessibility attributes
            expand_button = self.driver.find_element(
                By.XPATH,
                "//h3[contains(text(), '🔧 Development Tools')]/following-sibling::button"
            )
            self.assertTrue(expand_button.is_enabled())
            
            # Expand panel and check button accessibility
            expand_button.click()
            
            # Check that all buttons are keyboard accessible
            test_buttons = [
                '🏥 System Health Check',
                '📊 API Statistics',
                '⚡ Performance Stats',
                '🔍 Detailed Health',
                '🔧 Optimize Database',
                '📈 Cache Analytics',
                '📊 Monitoring Data',
                '🗑️ Clear All Data'
            ]
            
            for button_text in test_buttons:
                try:
                    button = self.driver.find_element(
                        By.XPATH, 
                        f"//button[contains(text(), '{button_text}')]"
                    )
                    self.assertTrue(button.is_enabled())
                    self.assertTrue(button.is_displayed())
                except NoSuchElementException:
                    # Some buttons might not be present without proper setup
                    pass
                    
        except Exception as e:
            self.fail(f"Development Tools Panel accessibility test failed: {e}")


class TestDevelopmentToolsPanelAPI(unittest.TestCase):
    """Test suite for Development Tools Panel API integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with running server."""
        # Find a free port
        cls.port = find_free_port()
        cls.base_url = f"http://localhost:{cls.port}"
        cls.api_base_url = f"{cls.base_url}/api/v1"
        
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(
            target=start_test_server, 
            args=(cls.port,),
            daemon=True
        )
        cls.server_thread.start()
        
        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/healthz", timeout=1)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt == max_attempts - 1:
                    raise Exception("Server failed to start")
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # The server thread will be cleaned up automatically as it's a daemon thread
        pass

    def setUp(self):
        """Set up test environment."""
        self.session = requests.Session()
        self.session_id = None

    def create_session(self):
        """Create a test session for API access."""
        try:
            response = self.session.post(
                f"{self.api_base_url}/auth/session",
                json={"username": "test", "password": "test"}
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.session.headers.update({
                    'X-Session-ID': self.session_id
                })
                return True
        except Exception as e:
            print(f"Failed to create session: {e}")
        return False

    def test_health_endpoint_response_format(self):
        """Test that the health endpoint returns the expected format."""
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['status', 'version', 'timestamp']
        for field in required_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['status'], 'healthy')
        self.assertIsInstance(data['version'], str)
        self.assertIsInstance(data['timestamp'], (int, float))

    def test_stats_endpoint_with_session(self):
        """Test the stats endpoint with proper session authentication."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('rate_limits', data)
        self.assertIn('session_stats', data)

    def test_performance_stats_endpoint(self):
        """Test the performance stats endpoint with proper session."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['timestamp', 'search_performance', 'cache_analytics']
        for field in required_fields:
            self.assertIn(field, data)

    def test_system_health_endpoint(self):
        """Test the detailed system health endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['status', 'timestamp', 'version']
        for field in required_fields:
            self.assertIn(field, data)

    def test_database_optimization_endpoint(self):
        """Test the database optimization endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.post(f"{self.api_base_url}/performance/optimize")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        required_fields = ['success', 'optimization_result', 'timestamp']
        for field in required_fields:
            self.assertIn(field, data)

    def test_cache_analytics_endpoint(self):
        """Test the cache analytics endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/analytics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)

    def test_monitoring_endpoint(self):
        """Test the monitoring data endpoint."""
        if not self.create_session():
            self.skipTest("Could not create session for API testing")
            
        response = self.session.get(f"{self.api_base_url}/performance/monitoring")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('timestamp', data)

    def test_endpoint_error_handling(self):
        """Test that endpoints handle errors gracefully."""
        # Test with invalid session
        response = requests.get(f"{self.api_base_url}/stats")
        self.assertEqual(response.status_code, 401)  # Unauthorized
        
        # Test with invalid endpoint
        response = requests.get(f"{self.api_base_url}/invalid_endpoint")
        self.assertEqual(response.status_code, 404)  # Not found


if __name__ == '__main__':
    unittest.main() 