#!/usr/bin/env python3
"""
Sokoban with ASCII Visualization
A working Sokoban example that displays the game board as text
"""

import sys
import time

try:
    import griddly
    from griddly import gd
    import gymnasium as gym
    from pathlib import Path
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Ensure virtual environment is activated: source venv/bin/activate")
    sys.exit(1)

def create_sokoban_ascii():
    """Create Sokoban environment with ASCII visualization"""
    print("🎮 Creating Sokoban Environment with ASCII Graphics")
    print("=" * 55)
    
    # Get correct path to Sokoban game
    griddly_path = Path(griddly.__file__).parent
    gdy_path = str(griddly_path / 'resources/games/Single-Player/GVGAI/sokoban.yaml')
    
    print(f"📝 Game file: {gdy_path}")
    
    # Register environment with ASCII observer (no GPU needed)
    griddly.GymWrapperFactory().build_gym_from_yaml(
        environment_name="Sokoban-ASCII",
        yaml_file=gdy_path,
        player_observer_type=gd.ObserverType.ASCII,
        global_observer_type=gd.ObserverType.ASCII
    )
    
    print("🏗️  Creating ASCII environment...")
    env = gym.make('GDY-Sokoban-ASCII-v0')
    
    print(f"✅ Sokoban environment created!")
    print(f"   Action space: {env.action_space}")
    print(f"   Observation space: {env.observation_space}")
    
    return env

def display_board(obs):
    """Display the ASCII board state"""
    print("📋 Current Board State:")
    print("─" * 40)
    if isinstance(obs, str):
        print(obs)
    else:
        print("Board state not available as ASCII")
    print("─" * 40)

def explain_sokoban():
    """Explain Sokoban rules"""
    print("🕹️  SOKOBAN GAME RULES")
    print("=" * 30)
    print("🎯 GOAL: Push all boxes (▢) onto target holes (○)")
    print("🚶 CONTROLS:")
    print("   1 = UP ⬆️")
    print("   2 = RIGHT ➡️") 
    print("   3 = DOWN ⬇️")
    print("   4 = LEFT ⬅️")
    print("   0 = NO ACTION")
    print("📦 RULES:")
    print("   • Push boxes by walking into them")
    print("   • Can't pull boxes, only push")
    print("   • Can't push multiple boxes at once")
    print("   • Win when all boxes are on holes")
    print()

def play_sokoban_interactive(env):
    """Play Sokoban interactively"""
    print("🎯 Starting Interactive Sokoban Game")
    print("=" * 40)
    
    obs, info = env.reset()
    print(f"\n🎮 Game initialized!")
    display_board(obs)
    
    total_reward = 0
    step_count = 0
    
    # Action mapping
    actions = {0: 'NONE', 1: 'UP ⬆️', 2: 'RIGHT ➡️', 3: 'DOWN ⬇️', 4: 'LEFT ⬅️'}
    
    # Predefined sequence for demo
    demo_moves = [2, 2, 3, 4, 1, 2, 3, 4, 1, 1, 2, 3, 4, 2, 1, 3, 4, 2]
    
    print(f"🤖 Running automated demo with {len(demo_moves)} moves...")
    print("Press Ctrl+C to stop early\n")
    
    try:
        for i, action in enumerate(demo_moves):
            step_count += 1
            
            print(f"🎯 Step {step_count}: Taking action {action} ({actions[action]})")
            
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            print(f"   💰 Reward: {reward} (Total: {total_reward})")
            
            # Display updated board
            display_board(obs)
            
            if reward > 0:
                print("🎉 Great move! Box placed correctly!")
            
            if terminated:
                print("🏆 LEVEL COMPLETED! All boxes on targets!")
                break
            elif truncated:
                print("⏰ Game truncated (too many steps)")
                break
            
            # Pause for dramatic effect
            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n⚠️  Game interrupted by user")
    
    print(f"\n📊 GAME SUMMARY")
    print("=" * 20)
    print(f"   Steps taken: {step_count}")
    print(f"   Total reward: {total_reward}")
    print(f"   Game completed: {terminated}")
    
    return terminated

def play_sokoban_vector(env_name="Sokoban-Vector"):
    """Also create a vector version for comparison"""
    print("\n🔢 Creating Vector Version for Comparison")
    print("=" * 45)
    
    try:
        griddly_path = Path(griddly.__file__).parent
        gdy_path = str(griddly_path / 'resources/games/Single-Player/GVGAI/sokoban.yaml')
        
        griddly.GymWrapperFactory().build_gym_from_yaml(
            environment_name=env_name,
            yaml_file=gdy_path,
            player_observer_type=gd.ObserverType.VECTOR,
            global_observer_type=gd.ObserverType.VECTOR
        )
        
        env = gym.make(f'GDY-{env_name}-v0')
        obs, info = env.reset()
        
        print(f"✅ Vector environment created")
        print(f"   Observation shape: {obs.shape}")
        print(f"   Observation type: {type(obs)}")
        print(f"   Sample values: {obs.flatten()[:10]}...")
        
        env.close()
        
    except Exception as e:
        print(f"⚠️  Could not create vector version: {e}")

def main():
    """Main function"""
    print("🎮 SOKOBAN ASCII DEMO")
    print("=" * 30)
    
    explain_sokoban()
    
    try:
        # Create ASCII environment
        env = create_sokoban_ascii()
        
        # Play the game
        completed = play_sokoban_interactive(env)
        
        # Show vector version
        play_sokoban_vector()
        
        # Clean up
        env.close()
        
        if completed:
            print("\n🎊 Congratulations! You solved the puzzle!")
        else:
            print("\n🎯 Good attempt! Try different moves to solve it.")
            
        print("\n💡 Next Steps:")
        print("   • Try different Sokoban levels (sokoban2.yaml)")
        print("   • Create an AI solver using reinforcement learning")
        print("   • Build your own Sokoban levels")
        print("   • Try other puzzle games in the collection")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Griddly is properly installed with Python bindings")

if __name__ == "__main__":
    main()