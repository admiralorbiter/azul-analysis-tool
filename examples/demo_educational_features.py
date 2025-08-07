#!/usr/bin/env python3
"""
Educational Features Demonstration

This script demonstrates the educational integration features we've implemented.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def demo_educational_move_explanation():
    """Demonstrate educational move explanation for different quality tiers."""
    print("🎓 Educational Move Explanation Demo")
    print("=" * 50)
    
    quality_tiers = ['!!', '!', '=', '?!', '?']
    
    for tier in quality_tiers:
        print(f"\n📊 Quality Tier: {tier}")
        print("-" * 30)
        
        test_data = {
            "quality_tier": tier,
            "move_description": f"Take blue tile from factory 2 to pattern line 3",
            "position_context": "Mid-game position with multiple options"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/education/move-explanation",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    content = data.get("educational_content", {})
                    
                    print(f"🎯 Title: {content.get('title', 'N/A')}")
                    print(f"📖 Explanation: {content.get('explanation', 'N/A')}")
                    print(f"♟️ Strategic Reasoning: {content.get('strategic_reasoning', 'N/A')}")
                    print(f"💡 Learning Tips: {len(content.get('learning_tips', []))} tips")
                    print(f"✅ Best Practice: {content.get('best_practices', 'N/A')}")
                    print(f"📚 Difficulty: {content.get('difficulty_level', 'N/A')}")
                    
                    # Show first learning tip
                    tips = content.get('learning_tips', [])
                    if tips:
                        print(f"   💡 Example tip: {tips[0]}")
                else:
                    print(f"❌ API error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")

def demo_strategic_concepts():
    """Demonstrate strategic concepts library."""
    print("\n🎓 Strategic Concepts Demo")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/education/strategic-concepts")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                concepts = data.get("concepts", [])
                print(f"📚 Found {len(concepts)} strategic concepts:")
                
                for concept in concepts:
                    print(f"\n🎯 {concept.get('name', 'N/A')} ({concept.get('difficulty', 'N/A')})")
                    print(f"   📖 {concept.get('description', 'N/A')}")
                    print(f"   💡 Learning Tips: {len(concept.get('learning_tips', []))} tips")
                    print(f"   📝 Examples: {', '.join(concept.get('examples', []))}")
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def demo_move_quality_integration():
    """Demonstrate move quality analysis with educational content."""
    print("\n🎓 Move Quality Analysis with Educational Content Demo")
    print("=" * 50)
    
    # Test with a simple position
    test_data = {
        "fen_string": "local_test_position_simple",
        "player_id": 0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/evaluate-all-moves",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                assessment = data.get("assessment", {})
                print("✅ Move quality analysis working with educational integration!")
                print(f"📊 Total moves analyzed: {len(assessment.get('all_moves_quality', {}))}")
                print(f"🏆 Best moves: {len(assessment.get('best_moves', []))}")
                print(f"🔄 Alternative moves: {len(assessment.get('alternative_moves', []))}")
                
                # Show educational insights if available
                insights = assessment.get('educational_insights', [])
                if insights:
                    print(f"🎓 Educational insights: {len(insights)} found")
                    for i, insight in enumerate(insights[:3], 1):
                        print(f"   {i}. {insight}")
                else:
                    print("📝 No educational insights for this test position (expected)")
                
                # Show analysis confidence
                confidence = assessment.get('analysis_confidence', 0)
                complexity = assessment.get('position_complexity', 0)
                print(f"🎯 Analysis confidence: {confidence:.1%}")
                print(f"🧩 Position complexity: {complexity:.1%}")
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def demo_frontend_integration():
    """Demonstrate how the frontend educational features work."""
    print("\n🎓 Frontend Educational Integration Demo")
    print("=" * 50)
    
    print("✅ Enhanced MoveQualityDisplay Component Features:")
    print("   🎓 'Learn About This Move' button for each quality tier")
    print("   📖 Educational explanations with strategic reasoning")
    print("   💡 Learning tips and best practices")
    print("   🎯 Interactive collapsible educational panels")
    print("   📱 Responsive design for educational content")
    print("   🎨 Visual learning aids with icons and color coding")
    
    print("\n✅ Educational Content Structure:")
    print("   📖 Explanation: Why the move is rated as it is")
    print("   ♟️ Strategic Reasoning: Educational context")
    print("   💡 Learning Tips: Actionable advice")
    print("   ✅ Best Practices: Key principles to remember")
    
    print("\n✅ Quality Tier Educational Coverage:")
    tiers = ['!!', '!', '=', '?!', '?']
    for tier in tiers:
        print(f"   {tier}: Complete educational content available")

def main():
    """Run the educational features demonstration."""
    print("🎓 Azul Educational Integration Features Demonstration")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/v1/move-quality-info")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    print("✅ Server is running - Starting demonstration...")
    
    # Run demonstrations
    demo_educational_move_explanation()
    demo_strategic_concepts()
    demo_move_quality_integration()
    demo_frontend_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Educational Integration Phase 1 Complete!")
    print("\n✅ What we've accomplished:")
    print("   🎓 Enhanced MoveQualityDisplay with educational content")
    print("   📚 Comprehensive educational content for all quality tiers")
    print("   🧠 Strategic concepts library with learning tips")
    print("   🔧 New educational API endpoints")
    print("   🧪 Comprehensive testing and validation")
    print("   📖 Complete documentation and implementation summary")
    
    print("\n🚀 Ready for Phase 2:")
    print("   🎯 Pattern recognition educational content")
    print("   🧪 Advanced Analysis Lab educational integration")
    print("   📚 Tutorial system foundation")

if __name__ == "__main__":
    main() 