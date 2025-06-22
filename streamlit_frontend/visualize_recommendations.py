#!/usr/bin/env python
"""
Map visualization for booth recommendations based on resume analysis.
This script demonstrates how booth recommendations can be displayed on a job fair map.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

# Add the current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the analyzer transition module
from lib.analyzer import analyze_resume_file

def visualize_recommendations(pdf_path, map_path=None, output_path="booth_recommendations.png"):
    """
    Analyze a resume and visualize the booth recommendations on a job fair map.
    
    Args:
        pdf_path: Path to the resume PDF file
        map_path: Path to the job fair map image (optional, uses a blank canvas if not provided)
        output_path: Path where to save the visualization image
    """
    print(f"Analyzing resume: {pdf_path}")
    
    # Analyze the resume
    result = analyze_resume_file(pdf_path)
    
    if "error" in result:
        print(f"Error analyzing resume: {result.get('error', 'Unknown error')}")
        return
    
    # Get booth recommendations
    booth_recommendations = result.get("booth_recommendations", [])
    if not booth_recommendations:
        # Try to match resume to booths if available (assuming the function exists somewhere)
        from lib.analyzer import match_resume_to_booths
        try:
            # Get sample booths or actual booths from API
            from lib.api import get_job_fair_booths
            booths = get_job_fair_booths()
            if booths:
                booth_recommendations = match_resume_to_booths(result, booths)
            else:
                print("No booths available for recommendations.")
                return
        except Exception as e:
            print(f"Error getting booth recommendations: {str(e)}")
            return
    
    # Get top job recommendations
    job_recommendations = result.get("recommendations", {}).get("job_roles", [])
    top_jobs = [job["role"] for job in job_recommendations[:3]] if job_recommendations else []
    
    # Create a figure for visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # If map image provided, use it as background
    if map_path and os.path.exists(map_path):
        try:
            img = np.array(Image.open(map_path))
            ax.imshow(img)
            print(f"Using map image: {map_path}")
        except Exception as e:
            print(f"Error loading map image: {str(e)}")
            # Create a blank canvas with grid as fallback
            ax.set_xlim(0, 800)
            ax.set_ylim(0, 600)
            ax.grid(True, linestyle='--', alpha=0.7)
    else:
        # Create a blank canvas with grid
        ax.set_xlim(0, 800)
        ax.set_ylim(0, 600)
        ax.grid(True, linestyle='--', alpha=0.7)
        print("Using blank canvas (no map provided)")
    
    # Add booth recommendations to the map
    legend_handles = []
    legend_labels = []
    
    # Define color map for match scores
    def get_color(score):
        # Red to green color gradient based on score
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellowgreen'
        elif score >= 40:
            return 'gold'
        else:
            return 'orange'
    
    # Plot each booth recommendation
    for i, booth in enumerate(booth_recommendations[:5]):  # Show top 5 booths
        match_score = booth.get("match_score", 0)
        booth_name = booth.get("name", f"Booth {i+1}")
        booth_number = booth.get("booth_number", "")
        
        # Get booth position
        pos = booth.get("map_position", {})
        x = pos.get("x", 100 + i * 150)  # Default positions if not provided
        y = pos.get("y", 200)
        width = pos.get("width", 80)
        height = pos.get("height", 80)
        
        # Draw booth rectangle
        color = get_color(match_score)
        rect = patches.Rectangle((x, y), width, height, linewidth=2, 
                                edgecolor=color, facecolor=color, alpha=0.5)
        ax.add_patch(rect)
        
        # Add booth label
        label_text = f"{booth_number}\n{match_score}%"
        ax.text(x + width/2, y + height/2, label_text, 
                horizontalalignment='center', verticalalignment='center',
                fontweight='bold', color='black')
        
        # Add to legend
        legend_handles.append(patches.Patch(color=color, alpha=0.5))
        legend_labels.append(f"{booth_name} ({booth_number}) - {match_score}% match")
        
        print(f"Added booth: {booth_name} ({booth_number}) - Match score: {match_score}%")
    
    # Add legend
    ax.legend(legend_handles, legend_labels, loc='upper right', bbox_to_anchor=(1, 1))
    
    # Add title and labels
    if top_jobs:
        title = f"Job Fair Booth Recommendations\nTop Jobs: {', '.join(top_jobs)}"
    else:
        title = "Job Fair Booth Recommendations"
    
    ax.set_title(title)
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    
    # Show resume information
    contact_info = result.get("contact_info", {})
    name = contact_info.get("name", "Job Seeker")
    
    # Get skills
    skills_data = result.get("skills", {})
    if isinstance(skills_data, dict):
        skills = skills_data.get("all_skills", [])
    else:
        skills = []
    top_skills = ", ".join(skills[:5]) if skills else "No skills extracted"
    
    info_text = f"Name: {name}\nTop Skills: {top_skills}"
    fig.text(0.02, 0.02, info_text, fontsize=10)
    
    # Save the visualization
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Visualize booth recommendations for a resume")
    parser.add_argument("pdf_path", help="Path to the resume PDF file")
    parser.add_argument("--map", help="Path to the job fair map image (optional)")
    parser.add_argument("--output", default="booth_recommendations.png", help="Output image file path")
    args = parser.parse_args()
    
    # Call the visualization function
    visualize_recommendations(args.pdf_path, args.map, args.output) 