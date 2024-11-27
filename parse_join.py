import requests
import pandas as pd
import yaml
import logging


def fetch_character_data(config_path, output_file="output.csv"):
    """
    Fetches character data from the JoinRPG API and writes it to a CSV file.

    Args:
        config_path (str): Path to the YAML configuration file.
        output_file (str, optional): Path to the CSV output file.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load configuration from YAML
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}.")
        return

    auth_url = config["auth_url"]
    login_data = config["login_data"]
    characters_url = config["characters_url"]
    character_details_url = config["character_details_url"]
    project_id = config["project_id"]

    with requests.Session() as session:
        # Authenticate and get the token
        logger.info("Authenticating...")
        try:
            auth_response = session.post(
                auth_url,
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            auth_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Authentication failed: {e}")
            logger.error(f"Status code: {auth_response.status_code if auth_response else 'No response'}")
            logger.error(f"Response content: {auth_response.text if auth_response else 'No response'}")
            return

        try:
            token = auth_response.json().get("access_token")  # Ищем 'access_token'
            if not token:
                logger.error("Authentication failed: No access_token received.")
                logger.error(f"Response content: {auth_response.text}")
                return
        except ValueError:
            logger.error("Failed to decode JSON response.")
            logger.error(f"Response content: {auth_response.text}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # Fetch character IDs
        logger.info("Fetching character IDs...")
        try:
            response = session.get(
                characters_url.format(projectId=project_id),
                headers=headers
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to fetch character IDs: {e}")
            logger.error(f"Response content: {response.text}")
            return

        characters = response.json()
        if not isinstance(characters, list):
            logger.error("Unexpected data format received for characters.")
            return

        if not characters:
            logger.info("No characters found.")
            return

        all_character_data = []

        # Fetch details for each character
        for character in characters:
            character_id = character.get("characterId")
            if not character_id:
                logger.warning("Character ID not found in the character data.")
                continue

            logger.info(f"Fetching details for character ID {character_id}...")
            try:
                details_response = session.get(
                    character_details_url.format(projectId=project_id, characterId=character_id),
                    headers=headers
                )
                details_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(f"Failed to fetch details for character ID {character_id}: {e}")
                logger.error(f"Response content: {details_response.text}")
                continue

            try:
                character_data = details_response.json()
                all_character_data.append(character_data)
            except ValueError:
                logger.error(f"Failed to decode JSON for character ID {character_id}.")
                continue

        # Write data to CSV
        if all_character_data:
            write_to_csv_with_pandas(all_character_data, output_file)
        else:
            logger.info("No character data available to write.")


def write_to_csv_with_pandas(data, output_file):
    """
    Writes a list of dictionaries to a CSV file using pandas.

    Args:
        data (list): List of dictionaries containing data.
        output_file (str): Path to the CSV output file.
    """
    try:
        df = pd.json_normalize(data)
        df.to_csv(output_file, index=False, encoding="utf-8")
        logging.info(f"Data successfully written to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write data to CSV: {e}")


if __name__ == "__main__":
    CONFIG_PATH = "parse_config.yaml"
    OUTPUT_FILE = "output.csv"

    # Fetch data and write to CSV
    fetch_character_data(CONFIG_PATH, output_file=OUTPUT_FILE)
