#!/usr/bin/env python3
"""
Face Swap Application Server
===========================

A Flask-based web application for face swapping with printer integration
and hot folder monitoring capabilities.

Version: 2.0.0
"""

import os
import sys
import logging
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from contextlib import contextmanager

# Third-party imports
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3
import configparser
import uuid
import json
import urllib.request
import urllib.parse
import base64
import csv
import websocket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Image processing imports
import cv2
from PIL import Image, ImageWin
import win32print
import win32ui
import win32con

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faceswap_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration data class."""
    base_asset_dir: str
    server_address: str
    client_id: str
    database_path: str
    config_file: str
    hot_folder_path: str
    hot_folder_enabled: bool
    default_printer: str
    default_print_size: str


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


class PrinterError(Exception):
    """Custom exception for printer errors."""
    pass


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create defaults."""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
                logger.info(f"Configuration loaded from {self.config_file}")
                
                # Ensure all required sections exist, add missing ones
                self._ensure_required_sections()
                
                # Ensure hot folder path is absolute and accessible
                if self.config.has_section('HotFolder'):
                    hot_folder_path = self.config['HotFolder']['path']
                    if not os.path.isabs(hot_folder_path):
                        # Convert relative path to absolute based on project root
                        project_root = Path(__file__).parent.parent
                        hot_folder_path = str(project_root / hot_folder_path)
                        self.config['HotFolder']['path'] = hot_folder_path
                        self.save_config()
                    
            else:
                self._create_default_config()
                logger.info("Default configuration created")
            
            self._validate_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration error: {e}")
    
    def _create_default_config(self) -> None:
        """Create default configuration."""
        project_root = Path(__file__).parent.parent
        
        self.config['HotFolder'] = {
            'path': str(project_root / 'hot_folder'),
            'enabled': 'true'
        }
        
        # Add image saving configuration
        self.config['ImageSaving'] = {
            'enabled': 'true',
            'save_folder': r'G:\My Drive\Motu Face Swap',  # modify here
            'save_format': 'png',
            'include_timestamp': 'true'
        }
        
        try:
            default_printer = win32print.GetDefaultPrinter()
        except Exception:
            default_printer = 'Default Printer'
            logger.warning("Could not detect default printer")
        
        self.config['Printer'] = {
            'default_printer': default_printer,
            'default_print_size': '4x6'
        }
        
        self.save_config()
    
    def _ensure_required_sections(self) -> None:
        """Ensure all required configuration sections exist."""
        project_root = Path(__file__).parent.parent
        
        # Ensure HotFolder section exists
        if not self.config.has_section('HotFolder'):
            self.config['HotFolder'] = {
                'path': str(project_root / 'hot_folder'),
                'enabled': 'true'
            }
        
        # Ensure ImageSaving section exists
        if not self.config.has_section('ImageSaving'):
            self.config['ImageSaving'] = {
                'enabled': 'true',
                'save_folder': r'G:\My Drive\Motu Face Swap',  # modify here
                'save_format': 'png',
                'include_timestamp': 'true'
            }
        
        # Ensure Printer section exists
        if not self.config.has_section('Printer'):
            try:
                default_printer = win32print.GetDefaultPrinter()
            except Exception:
                default_printer = 'Default Printer'
                logger.warning("Could not detect default printer")
            
            self.config['Printer'] = {
                'default_printer': default_printer,
                'default_print_size': '4x6'
            }
        
        # Save the config if any sections were added
        self.save_config()
    
    def _validate_config(self) -> None:
        """Validate configuration settings."""
        required_sections = ['HotFolder', 'Printer', 'ImageSaving']
        for section in required_sections:
            if not self.config.has_section(section):
                raise ConfigurationError(f"Missing required section: {section}")
        
        # Ensure hot folder exists
        hot_folder_path = self.get_hot_folder_path()
        try:
            os.makedirs(hot_folder_path, exist_ok=True)
            logger.info(f"Hot folder ready at: {hot_folder_path}")
        except Exception as e:
            logger.warning(f"Could not create hot folder: {e}")
            self.config['HotFolder']['enabled'] = 'false'
            self.save_config()
            
        # Ensure save folder exists if image saving is enabled
        if self.is_image_saving_enabled():
            save_folder_path = self.get_save_folder_path()
            try:
                os.makedirs(save_folder_path, exist_ok=True)
                logger.info(f"Image save folder ready at: {save_folder_path}")
            except Exception as e:
                logger.warning(f"Could not create save folder: {e}")
                self.config['ImageSaving']['enabled'] = 'false'
                self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Could not save configuration: {e}")
    
    def get_hot_folder_path(self) -> str:
        """Get the hot folder path."""
        return self.config['HotFolder']['path']
    
    def is_hot_folder_enabled(self) -> bool:
        """Check if hot folder monitoring is enabled."""
        return self.config['HotFolder'].getboolean('enabled')
    
    def get_printer_config(self) -> Dict[str, str]:
        """Get printer configuration."""
        return {
            'default_printer': self.config['Printer']['default_printer'],
            'default_print_size': self.config['Printer'].get('default_print_size', '4x6')
        }
    
    def update_config(self, section: str, key: str, value: str) -> None:
        """Update a configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][key] = value
        self.save_config()
    
    def get_save_folder_path(self) -> str:
        """Get the image save folder path."""
        if not self.config.has_section('ImageSaving'):
            return str(Path(__file__).parent.parent / 'saved_images')
        return self.config['ImageSaving']['save_folder']
    
    def is_image_saving_enabled(self) -> bool:
        """Check if image saving is enabled."""
        if not self.config.has_section('ImageSaving'):
            return False
        return self.config['ImageSaving'].getboolean('enabled')
    
    def get_image_saving_config(self) -> Dict[str, str]:
        """Get image saving configuration."""
        if not self.config.has_section('ImageSaving'):
            return {
                'enabled': 'false',
                'save_folder': str(Path(__file__).parent.parent / 'saved_images'),
                'save_format': 'jpg',
                'include_timestamp': 'true'
            }
        return {
            'enabled': self.config['ImageSaving'].get('enabled', 'false'),
            'save_folder': self.config['ImageSaving'].get('save_folder', str(Path(__file__).parent.parent / 'saved_images')),
            'save_format': self.config['ImageSaving'].get('save_format', 'jpg'),
            'include_timestamp': self.config['ImageSaving'].get('include_timestamp', 'true')
        }


class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, db_path: str = 'faceswap.db'):
        self.db_path = db_path
        self.table_name = 'user_table'
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the database with required tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_table (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise DatabaseError(f"Database error: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def save_user_data(self, name: str, phone: str) -> bool:
        """Save user data to database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_table (name, phone) VALUES (?, ?)",
                    (name, f"{phone}")
                )
                conn.commit()
            logger.info(f"User data saved: {name}, {phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user data: {e}")
            return False
    
    def export_to_csv(self, output_path: str) -> bool:
        """Export user data to CSV file."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Select only relevant columns and format the date
                cursor.execute(f"""
                    SELECT 
                        id as 'ID',
                        name as 'Name',
                        phone as 'Phone',
                        DATE(created_at) as 'Date',
                        TIME(created_at) as 'Time'
                    FROM {self.table_name}
                    ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(column_names)
                    writer.writerows(rows)
                
            logger.info(f"Data exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False

    def get_csv_data(self) -> Optional[str]:
        """Get user data as CSV string without saving to file."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # First, check what columns exist in the table
                cursor.execute(f"PRAGMA table_info({self.table_name})")
                columns_info = cursor.fetchall()
                available_columns = [col[1] for col in columns_info]  # Column names are at index 1
                
                # Build the SELECT query based on available columns
                select_parts = []
                select_parts.append("id as 'ID'")
                select_parts.append("name as 'Name'")
                select_parts.append("phone as 'Phone'")
                
                # Add date/time columns if they exist
                if 'created_at' in available_columns:
                    select_parts.append("DATE(created_at) as 'Date'")
                    select_parts.append("TIME(created_at) as 'Time'")
                    order_by = "ORDER BY created_at ASC"
                else:
                    order_by = "ORDER BY id ASC"
                
                query = f"SELECT {', '.join(select_parts)} FROM {self.table_name} {order_by}"
                cursor.execute(query)
                
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                # Create CSV in memory with proper phone formatting
                from io import StringIO
                csv_buffer = StringIO()
                writer = csv.writer(csv_buffer)
                writer.writerow(column_names)
                
                # Format phone numbers to preserve leading zeros
                formatted_rows = []
                for row in rows:
                    formatted_row = list(row)
                    # Find the phone column index (should be index 2 based on the SELECT)
                    phone_index = 2
                    if len(formatted_row) > phone_index and formatted_row[phone_index]:
                        # Format phone number to preserve leading zeros in Excel
                        formatted_row[phone_index] = f"{formatted_row[phone_index]}"
                    formatted_rows.append(formatted_row)
                
                writer.writerows(formatted_rows)
                
                csv_data = csv_buffer.getvalue()
                csv_buffer.close()
                
                logger.info("CSV data generated in memory with phone formatting")
                return csv_data
                
        except Exception as e:
            logger.error(f"Failed to generate CSV data: {e}")
            return None


class ImagePrinter:
    """Handles image printing operations."""
    
    PRINT_SIZES = {
        "4x6": (4.0, 6.0),
        "6x4": (6.0, 4.0)
    }
    
    @staticmethod
    def get_available_printers() -> List[str]:
        """Get list of available printers."""
        try:
            return [printer[2] for printer in win32print.EnumPrinters(2)]
        except Exception as e:
            logger.error(f"Failed to get printer list: {e}")
            return []
    
    @staticmethod
    def print_image(image_path: str, printer_name: str, print_size: str = "4x6", 
                   left_offset_percent: int = 10) -> bool:
        """
        Print an image with specified parameters.
        
        Args:
            image_path: Path to the image file
            printer_name: Name of the printer
            print_size: Print size (4x6 or 6x4)
            left_offset_percent: Left offset percentage (0-100)
            
        Returns:
            bool: True if printing succeeded, False otherwise
        """
        try:
            if print_size not in ImagePrinter.PRINT_SIZES:
                raise PrinterError(f"Invalid print size: {print_size}")
            
            # Open and prepare image
            img = Image.open(image_path).convert('RGB')
            
            # Initialize printer
            hprinter = win32print.OpenPrinter(printer_name)
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            
            try:
                # Get printer specifications
                printer_dpi_x = pdc.GetDeviceCaps(win32con.LOGPIXELSX)
                printer_dpi_y = pdc.GetDeviceCaps(win32con.LOGPIXELSY)
                physical_width = pdc.GetDeviceCaps(win32con.PHYSICALWIDTH)
                physical_height = pdc.GetDeviceCaps(win32con.PHYSICALHEIGHT)
                
                # Calculate target dimensions
                target_width_inch, target_height_inch = ImagePrinter.PRINT_SIZES[print_size]
                target_width_px = int(target_width_inch * printer_dpi_x)
                target_height_px = int(target_height_inch * printer_dpi_y)
                
                # Resize image maintaining aspect ratio
                resized_img = ImagePrinter._resize_image_for_print(
                    img, target_width_px, target_height_px
                )
                
                # Create final image with positioning
                final_img = ImagePrinter._position_image(
                    resized_img, target_width_px, target_height_px, left_offset_percent
                )
                
                # Print the image
                ImagePrinter._execute_print(
                    pdc, final_img, physical_width, physical_height, 
                    target_width_px, target_height_px, image_path
                )
                
                logger.info(f"Successfully printed {image_path} on {printer_name}")
                return True
                
            finally:
                pdc.DeleteDC()
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Printing failed: {e}")
            return False
    
    @staticmethod
    def _resize_image_for_print(img: Image.Image, target_width: int, 
                               target_height: int) -> Image.Image:
        """Resize image for printing while maintaining aspect ratio."""
        img_aspect = img.width / img.height
        target_aspect = target_width / target_height
        
        if img_aspect > target_aspect:
            new_width = target_width
            new_height = int(target_width / img_aspect)
        else:
            new_height = target_height
            new_width = int(target_height * img_aspect)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def _position_image(img: Image.Image, target_width: int, target_height: int, 
                       left_offset_percent: int) -> Image.Image:
        """Position image on the target canvas."""
        final_img = Image.new('RGB', (target_width, target_height), 'white')
        
        max_x_offset = target_width - img.width
        base_x_offset = max_x_offset // 2
        additional_offset = int((max_x_offset // 2) * (left_offset_percent / 100))
        x_offset = base_x_offset + additional_offset
        y_offset = (target_height - img.height) // 2
        
        final_img.paste(img, (x_offset, y_offset))
        return final_img
    
    @staticmethod
    def _execute_print(pdc, img: Image.Image, physical_width: int, 
                      physical_height: int, target_width: int, 
                      target_height: int, image_path: str) -> None:
        """Execute the actual printing."""
        dib = ImageWin.Dib(img)
        
        pdc.StartDoc(image_path)
        pdc.StartPage()
        
        margin_x = (physical_width - target_width) // 2
        margin_y = (physical_height - target_height) // 2
        
        dib.draw(pdc.GetHandleOutput(), (
            margin_x, margin_y,
            margin_x + target_width, margin_y + target_height
        ))
        
        pdc.EndPage()
        pdc.EndDoc()


class FaceSwapProcessor:
    """Handles face swap operations."""
    
    def __init__(self, server_address: str, client_id: str):
        self.server_address = server_address
        self.client_id = client_id
        self.workflow_file = "fswap.json"
    
    def process_face_swap(self, template_path: str, source_path: str) -> Optional[bytes]:
        """
        Process face swap operation.
        
        Args:
            template_path: Path to template image
            source_path: Path to source image
            
        Returns:
            bytes: Processed image data or None if failed
        """
        try:
            workflow = self._load_workflow()
            updated_workflow = self._update_workflow(workflow, template_path, source_path)
            
            ws = websocket.WebSocket()
            ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
            
            try:
                images = self._get_images(ws, updated_workflow)
                
                for node_id, image_data_list in images.items():
                    if image_data_list:
                        logger.info(f"Face swap completed successfully")
                        return image_data_list[0]
                
                logger.warning("No images generated from face swap")
                return None
                
            finally:
                ws.close()
                
        except Exception as e:
            logger.error(f"Face swap processing failed: {e}")
            return None
    
    def _load_workflow(self) -> Dict[str, Any]:
        """Load workflow configuration."""
        try:
            with open(self.workflow_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            raise
    
    def _update_workflow(self, workflow: Dict[str, Any], template_path: str, 
                        source_path: str) -> Dict[str, Any]:
        """Update workflow with image paths."""
        workflow["1"]["inputs"]["image"] = template_path
        workflow["3"]["inputs"]["image"] = source_path
        return workflow
    
    def _queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Queue a prompt for processing."""
        data = json.dumps({"prompt": prompt, "client_id": self.client_id}).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    
    def _get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Get processing history."""
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())
    
    def _get_image_data(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Get image data from server."""
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        })
        
        with urllib.request.urlopen(f"http://{self.server_address}/view?{params}") as response:
            return response.read()
    
    def _get_images(self, ws, prompt: Dict[str, Any]) -> Dict[str, List[bytes]]:
        """Get processed images from websocket."""
        prompt_id = self._queue_prompt(prompt)['prompt_id']
        output_images = {}
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break
        
        history = self._get_history(prompt_id)[prompt_id]
        
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = self._get_image_data(
                        image['filename'], image['subfolder'], image['type']
                    )
                    images_output.append(image_data)
                output_images[node_id] = images_output
        
        return output_images

class HotFolderHandler(FileSystemEventHandler):
    """Handles hot folder file system events."""
    
    def __init__(self, face_swap_processor: FaceSwapProcessor, printer: ImagePrinter, 
                 config_manager: ConfigManager, base_asset_dir: str, app_instance=None):
        self.face_swap_processor = face_swap_processor
        self.printer = printer
        self.config_manager = config_manager
        self.base_asset_dir = base_asset_dir
        self.app_instance = app_instance
        self.processing = set()
        self.supported_formats = ('.jpg', '.jpeg', '.png')
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and event.src_path.lower().endswith(self.supported_formats):
            if event.src_path not in self.processing:
                self.processing.add(event.src_path)
                time.sleep(1)  # Wait for file to be fully written
                threading.Thread(target=self._process_image, args=(event.src_path,)).start()
    
    def _process_image(self, image_path: str) -> None:
        """Process an image from the hot folder."""
        try:
            logger.info(f"Processing hot folder image: {image_path}")
            
            # Use default template
            template_path = os.path.join(self.base_asset_dir, "templates", "default.jpg")
            
            if not os.path.exists(template_path):
                logger.error(f"Template not found: {template_path}")
                return
            
            # Process face swap
            result_data = self.face_swap_processor.process_face_swap(template_path, image_path)
            
            if result_data:
                # Save the generated image (isolated functionality)
                saved_path = None
                if hasattr(self, 'app_instance') and self.app_instance:
                    saved_path = self.app_instance.save_generated_image(result_data, "hotfolder_faceswap")
                    if saved_path:
                        logger.info(f"Hot folder face swap result saved to: {saved_path}")
                
                # Save processed image temporarily
                temp_output = os.path.join(tempfile.gettempdir(), f"processed_{uuid.uuid4()}.jpg")
                with open(temp_output, 'wb') as f:
                    f.write(result_data)
                
                # Print the processed image
                printer_config = self.config_manager.get_printer_config()
                success = self.printer.print_image(
                    temp_output,
                    printer_config['default_printer'],
                    printer_config['default_print_size']
                )
                
                if success:
                    logger.info(f"Successfully processed and printed: {image_path}")
                else:
                    logger.error(f"Failed to print processed image: {image_path}")
                
                # Clean up temporary file
                os.remove(temp_output)
            else:
                logger.error(f"Face swap processing failed for: {image_path}")
                
        except Exception as e:
            logger.error(f"Error processing hot folder image {image_path}: {e}")
        finally:
            self.processing.discard(image_path)


class HotFolderMonitor:
    """Monitors hot folder for new images."""
    
    def __init__(self, config_manager: ConfigManager, face_swap_processor: FaceSwapProcessor, 
                 printer: ImagePrinter, base_asset_dir: str, app_instance=None):
        self.config_manager = config_manager
        self.face_swap_processor = face_swap_processor
        self.printer = printer
        self.base_asset_dir = base_asset_dir
        self.app_instance = app_instance
        self.observer = None
    
    def start(self) -> bool:
        """Start hot folder monitoring."""
        try:
            if not self.config_manager.is_hot_folder_enabled():
                logger.info("Hot folder monitoring is disabled")
                return False
            
            hot_folder_path = self.config_manager.get_hot_folder_path()
            
            if not os.path.exists(hot_folder_path):
                logger.error(f"Hot folder does not exist: {hot_folder_path}")
                return False
            
            event_handler = HotFolderHandler(
                self.face_swap_processor, self.printer, self.config_manager, self.base_asset_dir, self.app_instance
            )
            
            self.observer = Observer()
            self.observer.schedule(event_handler, hot_folder_path, recursive=False)
            self.observer.start()
            
            logger.info(f"Hot folder monitoring started: {hot_folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hot folder monitoring: {e}")
            return False
    
    def stop(self) -> None:
        """Stop hot folder monitoring."""
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join()
                logger.info("Hot folder monitoring stopped")
            except Exception as e:
                logger.error(f"Error stopping hot folder monitor: {e}")


class FaceSwapApp:
    """Main application class."""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize configuration
        self.config_manager = ConfigManager()
        
        # Initialize components
        self.database = DatabaseManager()
        self.printer = ImagePrinter()
        
        # Initialize face swap processor
        self.face_swap_processor = FaceSwapProcessor(
            server_address="127.0.0.1:8188",
            client_id=str(uuid.uuid4())
        )
        
        # Application configuration
        # Use relative path from the server directory to the assets directory
        project_root = Path(__file__).parent.parent
        self.base_asset_dir = str(project_root / 'clients/src/assets')
        
        # Overlay directory setup
        self.overlay_dir = os.path.join(Path(__file__).parent, 'overlays')
        os.makedirs(self.overlay_dir, exist_ok=True)
        
        # Initialize hot folder monitor
        self.hot_folder_monitor = HotFolderMonitor(
            self.config_manager, self.face_swap_processor, self.printer, self.base_asset_dir, self
        )
        
        # Set up routes
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Set up Flask routes."""
        
        @self.app.route('/api/templates', methods=['GET'])
        def get_templates():
            """Get list of template images."""
            try:
                folder = request.args.get('folder', '').strip()
                if not folder:
                    return jsonify({"error": "Folder parameter is required"}), 400
                
                full_path = os.path.join(self.base_asset_dir, *folder.split('/'))
                images = self._list_images(full_path)
                
                if images is None:
                    return jsonify({"error": "Folder not found"}), 404
                
                return jsonify(images)
                
            except Exception as e:
                logger.error(f"Error getting templates: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/api/template', methods=['GET'])
        def get_template():
            """Get a specific template image."""
            try:
                filepath = request.args.get('filepath', '').strip()
                if not filepath:
                    return jsonify({"error": "Filepath parameter is required"}), 400
                
                full_path = os.path.join(self.base_asset_dir, *filepath.split('/'))
                
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    return send_file(full_path, mimetype='image/jpeg')
                
                return jsonify({"error": "Image not found"}), 404
                
            except Exception as e:
                logger.error(f"Error getting template: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/api/swap', methods=['POST'])
        def swap_face():
            """Perform face swap operation."""
            try:
                template = request.files.get('template')
                source = request.files.get('source')
                
                if not template or not source:
                    return jsonify({'error': 'Missing template or source image'}), 400
                
                # Save template temporarily
                template_path = os.path.join(tempfile.gettempdir(), f"template_{uuid.uuid4()}.jpg")
                template.save(template_path)
                
                # Save source temporarily
                source_path = os.path.join(tempfile.gettempdir(), f"source_{uuid.uuid4()}.jpg")
                source.save(source_path)
                
                try:
                    # Process face swap
                    result_data = self.face_swap_processor.process_face_swap(template_path, source_path)
                    
                    if result_data:
                        # Save the generated image (isolated functionality)
                        saved_path = self.save_generated_image(result_data, "api_faceswap")
                        if saved_path:
                            logger.info(f"Face swap result saved to: {saved_path}")
                        
                        return jsonify({'image': base64.b64encode(result_data).decode('utf-8')})
                    else:
                        return jsonify({'error': 'Face swap processing failed'}), 500
                        
                finally:
                    # Clean up temporary files
                    for temp_file in [template_path, source_path]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                
            except Exception as e:
                logger.error(f"Error in face swap: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/printer/config', methods=['GET', 'PUT'])
        def printer_config():
            """Get or update printer configuration."""
            try:
                if request.method == 'GET':
                    printers = self.printer.get_available_printers()
                    printer_config = self.config_manager.get_printer_config()
                    
                    return jsonify({
                        'printers': printers,
                        'default_printer': printer_config['default_printer'],
                        'default_print_size': printer_config['default_print_size'],
                        'available_sizes': list(self.printer.PRINT_SIZES.keys()),
                        'hot_folder': {
                            'path': self.config_manager.get_hot_folder_path(),
                            'enabled': self.config_manager.is_hot_folder_enabled()
                        }
                    })
                
                elif request.method == 'PUT':
                    data = request.json
                    
                    if 'default_printer' in data:
                        self.config_manager.update_config('Printer', 'default_printer', data['default_printer'])
                    
                    if 'default_print_size' in data:
                        if data['default_print_size'] in self.printer.PRINT_SIZES:
                            self.config_manager.update_config('Printer', 'default_print_size', data['default_print_size'])
                    
                    if 'hot_folder' in data:
                        hot_folder_data = data['hot_folder']
                        if 'enabled' in hot_folder_data:
                            self.config_manager.update_config('HotFolder', 'enabled', str(hot_folder_data['enabled']).lower())
                    
                    return jsonify({'message': 'Configuration updated successfully'})
                
            except Exception as e:
                logger.error(f"Error in printer config: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/printer/print', methods=['POST'])
        def print_image():
            """Print an image."""
            try:
                if 'image' not in request.files:
                    return jsonify({'error': 'No image provided'}), 400
                
                image = request.files['image']
                printer_name = request.form.get('printer')
                print_size = request.form.get('print_size', '4x6')
                
                if not printer_name:
                    printer_config = self.config_manager.get_printer_config()
                    printer_name = printer_config['default_printer']
                
                if print_size not in self.printer.PRINT_SIZES:
                    return jsonify({'error': 'Invalid print size'}), 400
                
                # Save image temporarily
                temp_path = os.path.join(tempfile.gettempdir(), f"print_{uuid.uuid4()}.jpg")
                image.save(temp_path)
                
                try:
                    success = self.printer.print_image(temp_path, printer_name, print_size)
                    
                    if success:
                        return jsonify({'message': 'Image printed successfully'})
                    else:
                        return jsonify({'error': 'Failed to print image'}), 500
                        
                finally:
                    os.remove(temp_path)
                
            except Exception as e:
                logger.error(f"Error printing image: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/save-user-data', methods=['POST'])
        def save_user_data():
            """Save user data to database."""
            try:
                user_data = request.json
                name = user_data.get('name')
                phone = user_data.get('phone')
                
                if not name or not phone:
                    return jsonify({"error": "Missing name or phone"}), 400
                
                success = self.database.save_user_data(name, str(phone))
                
                if success:
                    return jsonify({"message": "User data saved successfully"}), 200
                else:
                    return jsonify({"error": "Failed to save user data"}), 500
                
            except Exception as e:
                logger.error(f"Error saving user data: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/api/export', methods=['GET'])
        def export_to_csv():
            """Export user data to CSV."""
            try:
                # Generate CSV data in memory
                csv_data = self.database.get_csv_data()
                
                if csv_data:
                    # Create response with CSV data
                    from flask import Response
                    from datetime import datetime
                    
                    # Generate filename with current timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"user_data_export_{timestamp}.csv"
                    
                    response = Response(
                        csv_data,
                        mimetype='text/csv',
                        headers={
                            'Content-Disposition': f'attachment; filename="{filename}"'
                        }
                    )
                    return response
                else:
                    return jsonify({"error": "Export failed"}), 500
                    
            except Exception as e:
                logger.error(f"Error exporting data: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/api/image-saving/config', methods=['GET', 'PUT'])
        def image_saving_config():
            """Get or update image saving configuration."""
            try:
                if request.method == 'GET':
                    save_config = self.config_manager.get_image_saving_config()
                    
                    return jsonify({
                        'enabled': save_config['enabled'].lower() == 'true',
                        'save_folder': save_config['save_folder'],
                        'save_format': save_config['save_format'],
                        'include_timestamp': save_config['include_timestamp'].lower() == 'true'
                    })
                
                elif request.method == 'PUT':
                    data = request.json
                    
                    if 'enabled' in data:
                        self.config_manager.update_config('ImageSaving', 'enabled', str(data['enabled']).lower())
                    
                    if 'save_folder' in data:
                        save_folder = data['save_folder'].strip()
                        if save_folder:
                            # Validate that the folder can be created
                            try:
                                os.makedirs(save_folder, exist_ok=True)
                                self.config_manager.update_config('ImageSaving', 'save_folder', save_folder)
                            except Exception as e:
                                return jsonify({'error': f'Invalid save folder path: {e}'}), 400
                    
                    if 'save_format' in data:
                        save_format = data['save_format'].lower()
                        if save_format in ['jpg', 'jpeg', 'png']:
                            self.config_manager.update_config('ImageSaving', 'save_format', save_format)
                    
                    if 'include_timestamp' in data:
                        self.config_manager.update_config('ImageSaving', 'include_timestamp', str(data['include_timestamp']).lower())
                    
                    return jsonify({'message': 'Image saving configuration updated successfully'})
                
            except Exception as e:
                logger.error(f"Error in image saving config: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/image-saving/test', methods=['POST'])
        def test_image_saving():
            """Test endpoint to verify image saving functionality."""
            try:
                if not self.config_manager.is_image_saving_enabled():
                    return jsonify({'error': 'Image saving is disabled'}), 400
                
                # Create a simple test image
                test_image = Image.new('RGB', (100, 100), color='red')
                
                # Convert to bytes
                from io import BytesIO
                img_bytes = BytesIO()
                test_image.save(img_bytes, format='JPEG')
                img_data = img_bytes.getvalue()
                
                # Save the test image
                saved_path = self.save_generated_image(img_data, "test_image")
                
                if saved_path:
                    return jsonify({
                        'message': 'Image saving test successful',
                        'saved_path': saved_path
                    })
                else:
                    return jsonify({'error': 'Image saving test failed'}), 500
                
            except Exception as e:
                logger.error(f"Error in image saving test: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/overlay', methods=['POST'])
        def upload_overlay():
            """Upload and configure overlay image for face swap workflow."""
            try:
                overlay = request.files.get('overlay')
                if not overlay:
                    return jsonify({'error': 'Overlay image is required'}), 400

                # Generate unique filename for overlay
                overlay_filename = f"overlay_{uuid.uuid4()}.png"
                overlay_path = os.path.join(self.overlay_dir, overlay_filename)
                overlay.save(overlay_path)

                try:
                    # Load and update workflow configuration
                    with open(self.face_swap_processor.workflow_file, 'r', encoding='utf-8') as f:
                        workflow = json.load(f)

                    # Update node 10 with overlay image path
                    if "10" in workflow and "inputs" in workflow["10"]:
                        workflow["10"]["inputs"]["image"] = overlay_path
                    else:
                        logger.warning("Node 10 not found in workflow or missing inputs")

                    # Save updated workflow
                    with open(self.face_swap_processor.workflow_file, 'w', encoding='utf-8') as f:
                        json.dump(workflow, f, indent=2)

                    logger.info(f"Overlay uploaded and workflow updated: {overlay_path}")
                    return jsonify({
                        "message": "Overlay uploaded and configured successfully", 
                        "path": overlay_path,
                        "filename": overlay_filename
                    })

                except Exception as e:
                    logger.error(f"Error updating workflow with overlay: {e}")
                    # Clean up uploaded file if workflow update fails
                    if os.path.exists(overlay_path):
                        os.remove(overlay_path)
                    return jsonify({"error": f"Failed to update workflow: {str(e)}"}), 500

            except Exception as e:
                logger.error(f"Error in overlay upload: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({"error": "Internal server error"}), 500
    
    def _list_images(self, folder_path: str) -> Optional[List[str]]:
        """List image files in a folder."""
        try:
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                return None
            
            supported_formats = ('.jpg', '.jpeg', '.png')
            return [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and 
                f.lower().endswith(supported_formats)
            ]
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return None
    
    def save_generated_image(self, image_data: bytes, prefix: str = "faceswap") -> Optional[str]:
        """
        Save generated image to the configured save folder.
        
        Args:
            image_data: The image data to save
            prefix: Prefix for the filename (kept for compatibility but not used)
            
        Returns:
            str: Path to saved file or None if saving failed/disabled
        """
        try:
            # Check if image saving is enabled
            if not self.config_manager.is_image_saving_enabled():
                logger.debug("Image saving is disabled")
                return None
            
            # Get save configuration
            save_config = self.config_manager.get_image_saving_config()
            save_folder = save_config['save_folder']
            save_format = save_config['save_format'].lower()
            
            # Ensure save folder exists
            os.makedirs(save_folder, exist_ok=True)
            
            # Find the next available number
            next_number = self._get_next_file_number(save_folder, save_format)
            
            # Generate simple filename with just the number
            filename = f"{next_number}.{save_format}"
            
            # Full path for the saved file
            save_path = os.path.join(save_folder, filename)
            
            # Save the image
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Generated image saved to: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to save generated image: {e}")
            return None
    
    def _get_next_file_number(self, save_folder: str, save_format: str) -> int:
        """
        Get the next available file number for incremental naming.
        
        Args:
            save_folder: The folder to check for existing files
            save_format: The file format extension
            
        Returns:
            int: The next available number
        """
        try:
            import re
            
            if not os.path.exists(save_folder):
                return 1
            
            # Get all files in the save folder
            files = os.listdir(save_folder)
            
            # Filter files that match our pattern and extract numbers
            numbers = []
            
            for file in files:
                if file.lower().endswith(f'.{save_format}'):
                    # Pattern: number.extension (e.g., 1.png, 2.png, etc.)
                    pattern = rf'^(\d+)\.{re.escape(save_format)}$'
                    
                    match = re.match(pattern, file)
                    if match:
                        numbers.append(int(match.group(1)))
            
            # Return the next available number
            if numbers:
                return max(numbers) + 1
            else:
                return 1
                
        except Exception as e:
            logger.error(f"Error getting next file number: {e}")
            return 1
    
    def start_hot_folder_monitoring(self) -> None:
        """Start hot folder monitoring."""
        self.hot_folder_monitor.start()
    
    def stop_hot_folder_monitoring(self) -> None:
        """Stop hot folder monitoring."""
        self.hot_folder_monitor.stop()
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
        """Run the Flask application."""
        try:
            logger.info("Starting Face Swap Application Server")
            
            # Start hot folder monitoring
            self.start_hot_folder_monitoring()
            
            # Run Flask app
            self.app.run(host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"Error starting application: {e}")
            raise
        finally:
            self.stop_hot_folder_monitoring()


def main():
    """Main entry point."""
    try:
        app = FaceSwapApp()
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 