import os
import sys

# Mock settings and imports before importing app components
os.environ["GOOGLE_API_KEY"] = "dummy"
os.environ["TWILIO_ACCOUNT_SID"] = "dummy"
os.environ["TWILIO_API_KEY"] = "dummy"
os.environ["TWILIO_API_SECRET"] = "dummy"

from app.services.ai_agent import SalesAgent

def test_sales_agent_config():
    agent = SalesAgent()
    print(f"Initial config: {agent.config}")

    agent.update_config(dialect="المصرية", instructions="Be very funny")
    print(f"Updated config: {agent.config}")

    if agent.config["dialect"] == "المصرية" and agent.config["instructions"] == "Be very funny":
        print("✅ Config update test passed!")
    else:
        print("❌ Config update test failed!")
        sys.exit(1)

if __name__ == "__main__":
    test_sales_agent_config()
