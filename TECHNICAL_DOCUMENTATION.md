# Motu Face Swap - Technical Documentation

### Key Features
- **Interactive User Interface**: Step-by-step guided experience
- **Real-time Camera Capture**: Web-based photo capture with countdown timer
- **Face Swap Processing**: Integration with ComfyUI backend for AI-powered face swapping
- **Template Selection**: Gender-based template categorization
- **Print Integration**: Direct printer connectivity for photo output
- **Hot Folder Monitoring**: Automatic processing of images dropped into monitored folder
- **User Data Management**: SQLite database for user information storage
- **CSV Export**: Export user data for administrative purposes
- **Image Saving**: Configurable automatic image saving to specified directories

### Technology Stack
- **Frontend**: React 19, Vite, TailwindCSS
- **Backend**: Python 3.x, Flask, Flask-CORS
- **Database**: SQLite
- **Image Processing**: OpenCV, PIL/Pillow
- **AI Processing**: ComfyUI integration via WebSocket
- **File Monitoring**: Watchdog
- **Printing**: Windows Print API (win32print)

---

## Architecture

### System Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│  Flask Server   │◄──►│   ComfyUI AI    │
│                 │    │                 │    │   Processing    │
│ - UI Components │    │ - API Endpoints │    │                 │
│ - State Mgmt    │    │ - Business Logic│    │ - Face Swap AI  │
│ - API Client    │    │ - File Handling │    │ - WebSocket API │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼───┐ ┌───▼──────┐
            │  SQLite   │ │ File  │ │ Printer  │
            │ Database  │ │System │ │Integration│
            └───────────┘ └───────┘ └──────────┘
```

### Directory Structure

```
motu_face_swap/
├── clients/                    # Frontend React application
│   ├── public/                # Static assets
│   │   ├── font/              # Custom fonts
│   │   ├── ui/                # UI background images
│   │   └── ...
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── assets/            # Template images (men/women)
│   │   ├── App.jsx            # Main application component
│   │   ├── AppRouter.jsx      # Routing configuration
│   │   └── API.jsx            # Backend API client
│   └── package.json           # Dependencies and scripts
├── server/                    # Backend Python application
│   ├── app.py                 # Main Flask application
│   ├── config.ini             # Configuration file
│   ├── fswap.json             # ComfyUI workflow definition
│   └── requirements.txt       # Python dependencies
├── hot_folder/                # Monitored directory for auto-processing
└── saved_images/              # Default save location for generated images
```

---

## Installation & Setup

### Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (3.8+ required)
- **ComfyUI** running locally on port 8188
- **Windows OS** (for print functionality)

### Frontend Setup

```bash
# Navigate to client directory
cd clients

# Install dependencies
bun install

# Start development server
bun run dev

# Build for production
bun run build
```

### Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

### ComfyUI Setup

Ensure ComfyUI is running and accessible at `http://127.0.0.1:8188`. The application expects ComfyUI to be available for face swap processing.

---

## Configuration

### Server Configuration (`server/config.ini`)

```ini
[HotFolder]
path = C:\path\to\hot_folder
enabled = true

[Printer]
default_printer = Your Default Printer
default_print_size = 4x6

[ImageSaving]
enabled = true
save_folder = C:\path\to\save\folder
save_format = png
include_timestamp = true
```

### Environment Variables

The application uses the following default configurations:
- **Frontend Port**: 5173 (Vite default)
- **Backend Port**: 5000 (Flask default)
- **ComfyUI Address**: 127.0.0.1:8188
- **Database**: `faceswap.db` (auto-created)

### Template Configuration

Place template images in:
- `clients/src/assets/men/` - Male templates
- `clients/src/assets/women/` - Female templates

Supported formats: JPG, JPEG, PNG

---

## Frontend Components

### Core Components

#### 1. **App.jsx** - Main Application
- **Purpose**: Central state management and step coordination
- **Features**: 
  - Multi-step wizard interface
  - Smooth transitions between steps
  - User data collection and submission
- **State Management**: Local state for form data, current step, and animations

#### 2. **UserForm.jsx** - User Information Collection
```jsx
// Key Props
{
  name: string,
  setName: function,
  phone: string,
  setPhone: function,
  onNext: function
}
```

#### 3. **Gender.jsx** - Gender Selection
- Template category selection (men/women)
- Visual gender selection interface

#### 4. **Template.jsx** - Template Selection
- Displays available templates based on gender
- API integration for template fetching
- Image preview functionality

#### 5. **Capture.jsx** - Camera Interface
```jsx
// Key Features
- Real-time camera feed
- Countdown timer (3-2-1)
- Photo capture with canvas manipulation
- Face swap processing integration
```

#### 6. **Result.jsx** - Final Result Display
- Generated image display
- Print functionality
- QR code generation
- Save options

### UI Components (`components/ui/`)

- **StartButton.jsx**: Animated start button
- **SaveButton.jsx**: Primary action button with disabled state
- **SmallButtons.jsx**: Navigation button pair (back/next)

### Pages

#### 1. **CSV.jsx** - Data Export Page
- User data table display
- CSV export functionality
- Administrative interface

#### 2. **Print.jsx** - Print Configuration Page
- Printer selection and configuration
- Print size options
- Hot folder settings

### API Client (`API.jsx`)

```javascript
// Key Functions
fetchTemplates(gender)          // Get template list
swapFace(templateUrl, sourceImage) // Process face swap
saveUserData(userData)          // Save user information
exportTableToCSV()              // Export data
fetchPrinters()                 // Get available printers
printImage(imageBlob)           // Send to printer
```

---

## Backend API

### Application Classes

#### 1. **ConfigManager**
- Handles application configuration
- Auto-creates default settings
- Validates paths and permissions

#### 2. **DatabaseManager**
- SQLite database operations
- User data CRUD operations
- CSV export functionality

#### 3. **FaceSwapProcessor**
- ComfyUI integration
- WebSocket communication
- Workflow management

#### 4. **ImagePrinter**
- Windows print API integration
- Image resizing and positioning
- Print size management

#### 5. **HotFolderMonitor**
- File system event handling
- Automatic image processing
- Background monitoring

### API Endpoints

#### Templates
```
GET /api/templates?folder={gender}
GET /api/template?filepath={path}
```

#### Face Swap
```
POST /api/swap
Content-Type: multipart/form-data
Body: template (file), source (file)
```

#### User Data
```
POST /api/save-user-data
Content-Type: application/json
Body: {name: string, phone: string}

GET /api/export
Returns: CSV file download
```

#### Printer Configuration
```
GET /api/printer/config
PUT /api/printer/config
POST /api/printer/print
```

#### Image Saving
```
GET /api/image-saving/config
PUT /api/image-saving/config
POST /api/image-saving/test
```

---

## Features

### 1. Interactive User Flow

```
Start Screen → User Form → Gender Selection → Template Selection → Camera Capture → Result Display
```

### 2. Face Swap Processing
- Integration with ComfyUI for AI-powered face swapping
- Configurable workflow via `fswap.json`
- Real-time processing feedback

### 3. Hot Folder Monitoring
- Automatic detection of new images
- Background processing with default templates
- Auto-print functionality

### 4. Print System
- Direct Windows printer integration
- Multiple print sizes (4x6, 6x4)
- Image positioning and scaling

### 5. Data Management
- SQLite database for user information
- Automatic timestamp tracking
- CSV export with proper formatting

### 6. Image Saving
- Configurable save locations
- Multiple format support (JPG, PNG)
- Incremental file naming
- Timestamp inclusion options

---

### System Requirements

#### Minimum Hardware
- **RAM**: 8GB (16GB recommended for AI processing)
- **Storage**: 10GB free space
- **CPU**: Quad-core processor
- **GPU**: CUDA-compatible GPU (recommended for ComfyUI)

#### Software Dependencies
- **Windows 10/11** (for print functionality)
- **Python 3.8+**
- **Node.js 18+**
- **ComfyUI** with required models

---

## Troubleshooting

### Common Issues

#### 1. **ComfyUI Connection Failed**
```
Error: Face swap processing failed
Solution: Ensure ComfyUI is running on 127.0.0.1:8188
```

#### 2. **Camera Access Denied**
```
Error: Camera stream not available
Solution: Grant browser camera permissions
```

#### 3. **Print Functionality Not Working**
```
Error: Printer not found
Solution: Check Windows printer drivers and permissions
```

#### 4. **Hot Folder Not Monitoring**
```
Error: Hot folder monitoring disabled
Solution: Check folder permissions and path in config.ini
```

### Debug Mode

Enable debug logging by setting:
```python
app.run(debug=True)
```

### Log Files

- **Server Logs**: `faceswap_server.log`
- **Browser Console**: Check for JavaScript errors
- **ComfyUI Logs**: Check ComfyUI terminal output

---

## Development Guide

### Adding New Templates

1. Place images in appropriate gender folders:
   ```
   clients/src/assets/men/new_template.jpg
   clients/src/assets/women/new_template.jpg
   ```

2. Templates are automatically detected by the API

### Customizing UI

1. **Colors**: Modify TailwindCSS classes
2. **Backgrounds**: Replace images in `clients/public/ui/`
3. **Fonts**: Update font files in `clients/public/font/`

### Extending API

```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    # Implementation
    return jsonify({'result': 'success'})
```

### Modifying Face Swap Workflow

Edit `server/fswap.json` to customize ComfyUI processing pipeline.

### Database Schema

```sql
CREATE TABLE user_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

*Last Updated: Juli 2025*
*Version: 1.0.0* 