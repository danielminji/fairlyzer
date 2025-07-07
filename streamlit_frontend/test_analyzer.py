#!/usr/bin/env python
"""
Test script for the enhanced resume analyzer system.
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the new analyzer module
from lib.analyzer import analyze_resume_file

def test_analyzer():
    """Test the enhanced resume analyzer with a PDF file."""
    
    # Check if a PDF file was provided as argument
    if len(sys.argv) < 2:
        print("Usage: python test_analyzer.py <path_to_resume.pdf>")
        return
    
    pdf_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return
    
    print(f"Testing resume analyzer with: {pdf_path}")
    print("="*50)
    
    # Test with the unified analyzer
    print("Using unified analyzer:")
    try:
        result = analyze_resume_file(pdf_path)
        
        if "error" not in result:
            print("✅ Analysis successful!")
            
            # Print key data points
            if "contact_info" in result:
                print("\nContact Information:")
                contact = result["contact_info"]
                for key, value in contact.items():
                    if value:
                        print(f"  {key.capitalize()}: {value}")
            
            if "skills" in result:
                skills_data = result["skills"]
                print("\nSkills:")
                all_skills = []
                
                if isinstance(skills_data, dict):
                    if "all_skills" in skills_data:
                        all_skills = skills_data["all_skills"]
                    elif "categorized" in skills_data:
                        for category, skills in skills_data["categorized"].items():
                            all_skills.extend(skills)
                
                for skill in all_skills[:10]:  # Show top 10 skills
                    print(f"  • {skill}")
                    
                if len(all_skills) > 10:
                    print(f"  • ... and {len(all_skills) - 10} more")
            
            if "job_recommendations" in result:
                print("\nJob Recommendations:")
                for job in result["job_recommendations"][:3]:  # Show top 3 jobs
                    print(f"  • {job['role']} (Match: {job['match_score']}%)")
            
            if "recommendations" in result:
                recommendations = result["recommendations"]
                
                if "job_roles" in recommendations and recommendations["job_roles"]:
                    print("\nRecommended Job Roles:")
                    for job in recommendations["job_roles"][:3]:  # Show top 3 jobs
                        print(f"  • {job['role']} (Match: {job['match_score']}%)")
                
                if "skills_to_add" in recommendations and recommendations["skills_to_add"]:
                    print("\nSkills to Add:")
                    for skill in recommendations["skills_to_add"][:5]:  # Show top 5 skills
                        print(f"  • {skill}")
                        
                if "industry_matches" in recommendations and recommendations["industry_matches"]:
                    print("\nIndustry Matches:")
                    for industry in recommendations["industry_matches"]:
                        print(f"  • {industry}")
        else:
            print("❌ Analysis failed:", result.get("error", "Unknown error"))
    
    except Exception as e:
        print(f"❌ Error testing unified analyzer: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyzer() 