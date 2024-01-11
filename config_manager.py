import yaml
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('config_manager')

class SingletonType(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonType):
    def __init__(self, config_file="config.yaml"):
        self.config_values = self.load_config(config_file)
        self.api_key = self.config_values.get("OPENAI_API_KEY")
        self.note_directory = self.config_values.get("NOTE_DIRECTORY")
        self.task_header = self.config_values.get("TASK_HEADER", "# Tasks")
        self.gpt_model = self.config_values.get("GPT_MODEL", "gpt-4-1106-preview")
        self.language = self.config_values.get("LANGUAGE", "en")
        self.validate()

    def load_config(self, config_file):
        """
        Load the configuration from a YAML file.
        """
        try:
            with open(config_file, 'r') as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(f"Error loading YAML config: {exc}")
            raise
        except FileNotFoundError:
            logger.error(f"Config file {config_file} not found.")
            raise

    def validate(self):
        """
        Validate the loaded configuration.
        """
        if not self.api_key or not self.note_directory:
            logger.error("Required configuration parameters are missing")
            raise ValueError("Required environment variables are not set")

        logger.info("Configuration loaded and validated successfully")
