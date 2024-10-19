from utils.config import setup_logging
from agents.assistant import assistant_agent


def main():
    setup_logging()

    assistant_agent.run()


if __name__ == "__main__":
    main()
