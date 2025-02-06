import os
import pytesseract
from PIL import Image
import json
import logging

_logger = logging.getLogger(__name__)

class PixelTextCore:
    def __init__(self, config):
        """
        Initializes the PixelTextCore with the given configuration.

        Args:
            config (dict): A dictionary containing the configuration parameters.
        """
        self.config = config
        self.index = {}  # In-memory index: {image_path: text_content}
        self.data_dir = config.get('data_dir')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.index_file = os.path.join(self.data_dir, 'index.json')
        self.load_index()

    def load_index(self):
         """Loads the index from file, if it exists."""
         try:
             with open(self.index_file, 'r') as f:
                 self.index = json.load(f)
             _logger.info(f"Index loaded from {self.index_file}")
         except FileNotFoundError:
             _logger.info("No existing index found. Starting with an empty index.")
             self.index = {}
         except json.JSONDecodeError:
             _logger.error(f"Error decoding JSON from {self.index_file}. Starting with an empty index.")
             self.index = {}

    def save_index(self):
        """Saves the index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=4)
        _logger.info(f"Index saved to {self.index_file}")

    def extract_text_from_image(self, image_path):
        """
        Extracts text from the given image using Tesseract OCR.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The extracted text, or None if an error occurred.
        """
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception as e:
            _logger.error(f"Error extracting text from {image_path}: {e}")
            return None

    def index_image(self, image_path):
        """
        Indexes the given image by extracting text and adding it to the index.

        Args:
            image_path (str): The path to the image file.
        """
        text = self.extract_text_from_image(image_path)
        if text:
            self.index[image_path] = text
            self.save_index()
            _logger.info(f"Indexed {image_path}")
        else:
            _logger.warning(f"No text extracted from {image_path}")

    def remove_image_from_index(self, image_path):
        """Removes an image from the index."""
        if image_path in self.index:
            del self.index[image_path]
            self.save_index()
            _logger.info(f"Removed {image_path} from index.")

    def search_index(self, query):
        """
        Searches the index for the given query.

        Args:
            query (str): The search query.

        Returns:
            list: A list of image paths that contain the query, sorted by relevance.
        """
        results = []
        for image_path, text in self.index.items():
            if query.lower() in text.lower():
                results.append(image_path)
        return results
