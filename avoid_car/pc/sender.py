"""
sender.py – PC-side script: chạy DQN simulation và gửi action qua UDP → ESP32.

Workflow:
  1. Load DQN agent từ trained model
  2. Tạo UDP socket → ESP32_IP:8888
  3. Loop:
     - Simulation step → get action từ DQN
     - Send action qua UDP
     - Sleep 100ms (match dt=0.1s)
"""

import socket
import time
import sys
from pathlib import Path

# Add simulation repo to Python path
REPO_ROOT = Path(__file__).parent.parent / "simulation_repo/car"
sys.path.insert(0, str(REPO_ROOT))

try:
    import torch
    from pkg.src.pkg.enums.action import CarAction
    from apps.agent.src.agent.agents.DQN.dqn_agent import DQNAgent
except ImportError as e:
    print(f"ERROR: Cannot import simulation modules: {e}")
    print(f"Make sure simulation_repo is set up correctly at: {REPO_ROOT}")
    sys.exit(1)


# ======================== CONFIGURATION ========================
ESP32_IP = "192.168.1.100"  # TODO: User cần điền IP của ESP32 sau khi connect WiFi
UDP_PORT = 8888
DT = 0.1  # Simulation timestep (seconds)

# Path to trained DQN model
MODEL_PATH = REPO_ROOT / "export/model"  # Adjust if needed


# ======================== MAIN ========================
def load_agent(model_path: Path, state_dim: int, action_dim: int) -> DQNAgent:
    """Load trained DQN agent từ checkpoint.

    Args:
        model_path: Path to model directory
        state_dim: State dimension (phụ thuộc vào env config)
        action_dim: Action dimension (3 cho FORWARD/LEFT/RIGHT)

    Returns:
        DQNAgent instance với trained weights
    """
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        epsilon_start=0.0,  # No exploration during inference
        epsilon_end=0.0,
    )

    # Load checkpoint
    checkpoint_path = model_path / "checkpoint.pth"
    if checkpoint_path.exists():
        agent.load(str(checkpoint_path))
        print(f"✓ Loaded model from: {checkpoint_path}")
    else:
        print(f"WARNING: No checkpoint found at {checkpoint_path}")
        print("Using untrained agent (random actions)")

    return agent


def send_action_loop(esp32_ip: str, udp_port: int, agent: DQNAgent):
    """Main loop: inference + send action qua UDP.

    Args:
        esp32_ip: IP address của ESP32
        udp_port: UDP port (8888)
        agent: DQNAgent instance
    """
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"✓ UDP socket created")
    print(f"Sending actions to {esp32_ip}:{udp_port}\n")

    # TODO: Load environment và get initial state
    # Hiện tại dùng dummy state để demo
    # User cần integrate với simulation environment thực tế

    print("=" * 60)
    print("DEMO MODE: Sending test sequence")
    print("=" * 60)
    print("Sequence: FORWARD → LEFT → RIGHT → FORWARD (loop)")
    print("Press Ctrl+C to stop\n")

    # Demo sequence
    test_sequence = [
        (CarAction.FORWARD, "FORWARD"),
        (CarAction.FORWARD, "FORWARD"),
        (CarAction.FORWARD, "FORWARD"),
        (CarAction.TURN_LEFT, "TURN_LEFT"),
        (CarAction.TURN_LEFT, "TURN_LEFT"),
        (CarAction.FORWARD, "FORWARD"),
        (CarAction.TURN_RIGHT, "TURN_RIGHT"),
        (CarAction.TURN_RIGHT, "TURN_RIGHT"),
        (CarAction.FORWARD, "FORWARD"),
    ]

    step_count = 0

    try:
        while True:
            # Get action (demo: cycle through test sequence)
            action, action_name = test_sequence[step_count % len(test_sequence)]

            # TODO: Replace with actual DQN inference:
            # state_tensor = torch.FloatTensor(state).unsqueeze(0)
            # action = agent.select_action(state_tensor, epsilon=0.0)

            # Send action to ESP32 (1 byte)
            sock.sendto(bytes([action]), (esp32_ip, udp_port))

            # Log
            step_count += 1
            print(f"[{step_count:04d}] Sent: {action_name} ({action})")

            # Sleep to match simulation timestep
            time.sleep(DT)

    except KeyboardInterrupt:
        print("\n\n[STOP] Keyboard interrupt")
    finally:
        sock.close()
        print("UDP socket closed.")


def main():
    """Entry point."""
    print("=" * 60)
    print("Avoid Car — PC Sender")
    print("=" * 60)
    print()

    # Check ESP32 IP
    if ESP32_IP == "192.168.1.100":
        print("⚠ WARNING: ESP32_IP is placeholder!")
        print("Please update ESP32_IP in sender.py with actual IP from ESP32")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    # Load agent (optional for demo)
    # state_dim = 10  # Example: adjust based on your env
    # action_dim = 3  # FORWARD, TURN_LEFT, TURN_RIGHT
    # agent = load_agent(MODEL_PATH, state_dim, action_dim)

    agent = None  # Demo mode không cần agent

    # Start sending loop
    send_action_loop(ESP32_IP, UDP_PORT, agent)


if __name__ == "__main__":
    main()
