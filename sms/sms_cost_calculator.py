"""
SMS Cost Calculator - Compare providers for your specific volume
"""

def calculate_clicksend_cost(volume):
    """Calculate ClickSend cost based on volume tiers"""
    if volume < 5000:
        return volume * 0.0243
    elif volume < 50000:
        return volume * 0.0174
    elif volume < 150000:
        return volume * 0.0118
    else:
        return volume * 0.0087

def calculate_twilio_cost(volume, use_a2p=False):
    """Calculate Twilio cost (with/without A2P)"""
    if use_a2p:
        # A2P rates (volume discounts)
        if volume < 10000:
            return volume * 0.0075
        elif volume < 100000:
            return volume * 0.0055
        else:
            return volume * 0.0040
    else:
        # Standard rates, limited to daily caps
        max_monthly = 6000  # 200/day × 30 days
        if volume > max_monthly:
            return None  # Can't handle this volume without A2P
        return volume * 0.0075

def calculate_optimal_strategy(monthly_volume):
    """Calculate the best SMS strategy for given volume"""
    print(f"\n📊 SMS Cost Analysis for {monthly_volume:,} messages/month")
    print("=" * 60)
    
    strategies = []
    
    # Strategy 1: ClickSend only
    clicksend_cost = calculate_clicksend_cost(monthly_volume)
    strategies.append({
        'name': 'ClickSend Only',
        'cost': clicksend_cost,
        'setup_time': '5 minutes',
        'a2p_required': False,
        'daily_limit': 'Unlimited',
        'pros': ['Instant setup', 'No daily limits', 'No A2P'],
        'cons': ['Higher cost per message']
    })
    
    # Strategy 2: Twilio without A2P
    twilio_cost = calculate_twilio_cost(monthly_volume, use_a2p=False)
    if twilio_cost:
        strategies.append({
            'name': 'Twilio (No A2P)',
            'cost': twilio_cost,
            'setup_time': '5 minutes',
            'a2p_required': False,
            'daily_limit': '6,000/month max',
            'pros': ['Lowest cost per message', 'Instant setup'],
            'cons': ['Volume limited', 'Multiple numbers needed']
        })
    
    # Strategy 3: Twilio with A2P
    twilio_a2p_cost = calculate_twilio_cost(monthly_volume, use_a2p=True)
    strategies.append({
        'name': 'Twilio (A2P)',
        'cost': twilio_a2p_cost,
        'setup_time': '2-6 weeks',
        'a2p_required': True,
        'daily_limit': 'High limits',
        'pros': ['Lowest cost', 'High volume'],
        'cons': ['A2P registration', 'Setup delay', 'Compliance requirements']
    })
    
    # Strategy 4: Hybrid approach
    if monthly_volume > 6000:
        twilio_portion = 6000
        clicksend_portion = monthly_volume - 6000
        hybrid_cost = calculate_twilio_cost(twilio_portion) + calculate_clicksend_cost(clicksend_portion)
        
        strategies.append({
            'name': 'Hybrid (Twilio + ClickSend)',
            'cost': hybrid_cost,
            'setup_time': '10 minutes',
            'a2p_required': False,
            'daily_limit': 'Effectively unlimited',
            'pros': ['Cost optimization', 'Redundancy', 'No A2P'],
            'cons': ['Complexity', 'Two accounts to manage']
        })
    
    # Sort by cost
    strategies.sort(key=lambda x: x['cost'])
    
    # Display results
    for i, strategy in enumerate(strategies):
        icon = "🏆" if i == 0 else "💰" if i == 1 else "⚖️"
        print(f"\n{icon} {strategy['name']}")
        print(f"   Cost: ${strategy['cost']:.2f}/month")
        print(f"   Setup: {strategy['setup_time']}")
        print(f"   A2P: {'Required' if strategy['a2p_required'] else 'Not required'}")
        print(f"   Limit: {strategy['daily_limit']}")
        print(f"   Pros: {', '.join(strategy['pros'])}")
        print(f"   Cons: {', '.join(strategy['cons'])}")
    
    # Recommendation
    best = strategies[0]
    print(f"\n🎯 RECOMMENDATION: {best['name']}")
    print(f"   Monthly Cost: ${best['cost']:.2f}")
    
    if best['name'] == 'ClickSend Only':
        print("   Why: Best for immediate high-volume needs without A2P complexity")
    elif 'Hybrid' in best['name']:
        print("   Why: Optimal cost while avoiding A2P registration")
    else:
        print("   Why: Most cost-effective for your volume")
    
    return strategies

def main():
    """Interactive cost calculator"""
    print("🚀 SMS Provider Cost Calculator")
    print("=" * 40)
    
    # Common volume scenarios
    scenarios = [
        ("Small Business", 1000),
        ("Growing Business", 5000),
        ("Medium Business", 15000),
        ("Large Business", 50000),
        ("Enterprise", 150000)
    ]
    
    print("\nQuick scenarios:")
    for i, (name, volume) in enumerate(scenarios, 1):
        print(f"{i}. {name} ({volume:,} msgs/month)")
    print("6. Custom volume")
    
    try:
        choice = input("\nSelect scenario (1-6): ").strip()
        
        if choice in ['1', '2', '3', '4', '5']:
            volume = scenarios[int(choice) - 1][1]
        elif choice == '6':
            volume = int(input("Enter monthly message volume: "))
        else:
            print("Invalid choice")
            return
        
        # Calculate and display results
        strategies = calculate_optimal_strategy(volume)
        
        # Show annual savings
        if len(strategies) > 1:
            cheapest = strategies[0]['cost']
            most_expensive = max(s['cost'] for s in strategies)
            annual_savings = (most_expensive - cheapest) * 12
            
            print(f"\n💰 Annual Savings: ${annual_savings:.2f}")
            print(f"   (Choosing best vs worst option)")
        
        # ClickSend specific analysis
        clicksend_strategy = next((s for s in strategies if 'ClickSend' in s['name']), None)
        if clicksend_strategy:
            print(f"\n📊 ClickSend Analysis:")
            cost_per_message = clicksend_strategy['cost'] / volume
            print(f"   Your rate: ${cost_per_message:.4f} per message")
            
            # Show tier benefits
            if volume >= 150000:
                print(f"   🎉 You qualify for premium tier (${0.0087:.4f}/msg)")
            elif volume >= 50000:
                print(f"   🎯 You qualify for high-volume tier (${0.0118:.4f}/msg)")
            elif volume >= 5000:
                print(f"   📈 You qualify for volume tier (${0.0174:.4f}/msg)")
            else:
                print(f"   📱 Standard tier (${0.0243:.4f}/msg)")
                print(f"   💡 Tip: At 5,000 msgs, you'd save ${(volume * 0.0243 - volume * 0.0174):.2f}/month")
    
    except (ValueError, KeyboardInterrupt):
        print("\nExiting calculator...")

if __name__ == "__main__":
    main()
