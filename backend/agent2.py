from utils.config import setup_logging
from agents.user import user_agent


def main():
    setup_logging()

    user_agent.run()


if __name__ == "__main__":
    main()
