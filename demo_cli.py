"""
Maison Hygia — Ritual Intelligence Interactive CLI Demo
Run this script to test the Ritual Intelligence engine directly in your terminal without a browser.

Usage:
    python demo_cli.py
"""
import sys
import os

# Ensure backend package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.conversation import ConversationManager
from backend.engine.recommender import run_margin_experiment, rerank_with_weights
from backend.models import UserProfile
from backend.data.products import get_all_products
import uuid

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title.upper()}")
    print("=" * 60)

def run_interactive_concierge():
    print_header("Maison Hygia — Interactive Concierge")
    print("Type your skincare/wellness goal (or 'exit' to return to menu).\n")
    
    manager = ConversationManager()
    conv_id = str(uuid.uuid4())
    start = manager.start_conversation(conv_id)
    print(f"AI: {start['greeting']}\n")
    
    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ['exit', 'quit', 'q']:
            break
            
        res = manager.process_message(conv_id, user_input)
        print(f"\nAI: {res['response']}\n")
        
        if res.get("follow_up_questions"):
            print("Suggested Options:")
            for q in res["follow_up_questions"]:
                print(f"  • {q['text']}")
                for opt in q.get("options", []):
                    print(f"    - {opt}")
            print()
            
        if res.get("ritual"):
            ritual = res["ritual"]
            print("-" * 50)
            print(f"  YOUR CRAFTED {ritual['moment'].upper()} RITUAL")
            print(f"  Total Investment: ${ritual['total_price']:.2f}")
            print("-" * 50)
            for step in ritual["steps"]:
                p = step["product"]
                print(f"  Step {step['step_number']}: [{step['stage_name'].upper()}] {p['name']} (${p['price']})")
                print(f"    Category: {p['category']} | Concerns: {', '.join(p['skin_concerns'])}")
                print(f"    Description: {p['short_description']}")
            print("-" * 50)
            print("\nYou can now refine this ritual (e.g. 'make it cheaper', 'make it simpler') or type 'exit'.\n")

def run_experiment_demo():
    print_header("Margin-Bias vs. Ritual Intelligence Experiment")
    profile = UserProfile(concerns=["aging", "dry"], budget="premium")
    products = get_all_products()
    exp = run_margin_experiment(profile, products)
    
    print("\n1. NAIVE RANKER (Optimizing pure profit/margin):")
    print("Rank | Product Name                         | Margin | Price | Relevance")
    print("-" * 65)
    for idx, item in enumerate(exp["naive_ranking"][:5], 1):
        p = item["product"]
        print(f" #{idx}  | {p['name']:<36} | {p['margin']:<6} | ${p['price']:<4} | {item['relevance']:.2f}")
        
    print("\n2. RITUAL INTELLIGENCE (Constrained Relevance + Multi-Factor):")
    print("Rank | Product Name                         | Margin | Price | Score")
    print("-" * 65)
    for idx, item in enumerate(exp["intelligent_ranking"][:5], 1):
        p = item["product"]
        print(f" #{idx}  | {p['name']:<36} | {p['margin']:<6} | ${p['price']:<4} | {item['score']['total_score']:.3f}")
    print("\nKey Insight: Business value optimizes among good recommendations; it cannot turn a bad recommendation into a good one.\n")

def list_catalog():
    print_header("Product Catalog (35 Curated Formulations)")
    products = get_all_products()
    for idx, p in enumerate(products, 1):
        print(f"{idx:2d}. {p.name:<34} | ${p.price:5.1f} | {p.category:<18} | Stage: {p.routine_stage.value}")

def main():
    while True:
        print("\n" + "=" * 60)
        print("   MAISON HYGIA — RITUAL INTELLIGENCE CLI")
        print("=" * 60)
        print("  1. Interactive Skincare Concierge (Chat & Ritual Composer)")
        print("  2. Run Margin-Bias vs. AI Experiment")
        print("  3. View Full 35-Product Catalog")
        print("  4. Exit")
        print("=" * 60)
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            run_interactive_concierge()
        elif choice == "2":
            run_experiment_demo()
        elif choice == "3":
            list_catalog()
        elif choice == "4":
            print("\nGoodbye!\n")
            break
        else:
            print("Invalid selection. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
