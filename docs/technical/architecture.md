# System Architecture

## Overview

The Azul Solver & Analysis Toolkit is a comprehensive system for analyzing Azul game positions and providing strategic insights. The architecture consists of multiple interconnected components that work together to provide analysis, training, and evaluation capabilities.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │   Core Engine   │
│                 │    │                 │    │                 │
│ • React App     │◄──►│ • Flask Server  │◄──►│ • Game Logic    │
│ • Game Board    │    │ • REST API      │    │ • Analysis      │
│ • Analysis UI   │    │ • Authentication │    │ • Neural Models │
│ • Neural UI     │    │ • Rate Limiting │    │ • Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Frontend (React)

#### Structure
```
ui/
├── components/          # React components
│   ├── game/           # Game interface components
│   ├── analysis/       # Analysis display components
│   ├── neural/         # Neural training interface
│   └── positions/      # Position library components
├── api/                # API client modules
├── utils/              # Utility functions
└── styles/             # CSS styling
```

#### Key Components

- **GameBoard**: Main game interface with board, factories, and controls
- **AnalysisResults**: Display analysis results and recommendations
- **NeuralTrainingPage**: Neural model training interface
- **PositionLibrary**: Position management and testing
- **ConfigurationPanel**: System configuration interface

#### State Management

- **useGameState**: Game state management and updates
- **useAnalysis**: Analysis state and API calls
- **useConfiguration**: Configuration state management
- **useNeural**: Neural training state management

### 2. Backend API (Flask)

#### Structure
```
api/
├── app.py              # Main Flask application
├── auth.py             # Authentication middleware
├── routes/             # API route handlers
│   ├── core.py         # Core game endpoints
│   ├── analysis.py     # Analysis endpoints
│   ├── neural.py       # Neural training endpoints
│   └── strategic.py    # Strategic analysis endpoints
├── models/             # Data models
├── middleware/         # Request/response middleware
└── utils/              # API utilities
```

#### Key Features

- **RESTful API**: Standard REST endpoints for all operations
- **Authentication**: JWT-based authentication system
- **Rate Limiting**: Request rate limiting for API protection
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin resource sharing support

#### API Endpoints

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Core** | `/api/v1/game/*` | Game state and move execution |
| **Analysis** | `/api/v1/analysis/*` | Pattern detection and move analysis |
| **Neural** | `/api/v1/neural/*` | Neural training and evaluation |
| **Strategic** | `/api/v1/strategic/*` | Strategic analysis and planning |

### 3. Core Engine (Python)

#### Structure
```
core/
├── azul_model.py       # Game state representation
├── azul_evaluator.py   # Position evaluation
├── azul_patterns.py    # Pattern detection
├── azul_mcts.py        # Monte Carlo Tree Search
├── azul_neural.py      # Neural model integration
├── azul_database.py    # Database management
└── azul_utils.py       # Core utilities
```

#### Key Components

- **AzulState**: Game state representation and management
- **AzulEvaluator**: Position evaluation and scoring
- **AzulPatternDetector**: Pattern detection and analysis
- **AzulMCTS**: Monte Carlo Tree Search implementation
- **AzulNeural**: Neural model integration and inference

## Data Flow

### 1. Game Analysis Flow

```
User Input → Frontend → API → Core Engine → Analysis → Results → Frontend → Display
```

#### Detailed Flow

1. **User Input**: User selects position or makes move
2. **Frontend Processing**: React components update game state
3. **API Request**: Frontend sends request to backend API
4. **Backend Processing**: Flask routes handle request
5. **Core Analysis**: Core engine performs analysis
6. **Result Generation**: Analysis results are generated
7. **Response**: Results sent back to frontend
8. **Display**: Frontend displays results to user

### 2. Neural Training Flow

```
Training Request → API → Neural Engine → Training → Model Save → Status Update → Frontend
```

#### Detailed Flow

1. **Training Request**: User configures and starts training
2. **API Processing**: Backend validates and initiates training
3. **Neural Engine**: PyTorch-based training execution
4. **Model Training**: Neural network training with data
5. **Model Persistence**: Trained model saved to disk
6. **Status Updates**: Real-time status updates to frontend
7. **Completion**: Training results displayed to user

### 3. Pattern Detection Flow

```
Game State → Pattern Detector → Analysis → Opportunities → Move Suggestions → API Response
```

#### Detailed Flow

1. **Game State**: Current game position analyzed
2. **Pattern Detection**: Core engine detects patterns
3. **Opportunity Analysis**: Strategic opportunities identified
4. **Move Generation**: Concrete move suggestions created
5. **Response Formatting**: Results formatted for API response
6. **Frontend Display**: Results displayed in UI

## Database Architecture

### SQLite Database

#### Schema Overview

```sql
-- Neural training sessions
CREATE TABLE neural_training_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    model_size TEXT,
    device TEXT,
    epochs INTEGER,
    status TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata TEXT
);

-- Neural evaluation sessions
CREATE TABLE neural_evaluation_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    model TEXT,
    test_positions INTEGER,
    status TEXT,
    results TEXT,
    created_at TIMESTAMP
);

-- Training configurations
CREATE TABLE neural_configurations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    model_size TEXT,
    device TEXT,
    epochs INTEGER,
    samples INTEGER,
    learning_rate REAL,
    batch_size INTEGER,
    created_at TIMESTAMP
);
```

#### Data Management

- **Session Storage**: Training and evaluation sessions stored persistently
- **Configuration Templates**: Reusable training configurations
- **Model Metadata**: Model performance and training information
- **Historical Data**: Complete training history and results

## Neural Architecture

### Model Architecture

#### Network Structure

```
Input Layer (Game State) → Hidden Layers → Output Layer (Move Probabilities)
```

#### Model Variants

| Model Size | Parameters | Layers | Use Case |
|------------|------------|--------|----------|
| **Small** | ~1M | 3-4 | Quick analysis, testing |
| **Medium** | ~5M | 5-6 | Balanced performance |
| **Large** | ~20M | 7-8 | High accuracy, production |

#### Training Pipeline

1. **Data Generation**: Game positions generated for training
2. **Model Initialization**: Neural network initialized with architecture
3. **Training Loop**: Epoch-based training with loss optimization
4. **Validation**: Regular validation on test positions
5. **Model Saving**: Trained models saved with metadata
6. **Evaluation**: Model performance evaluated on test set

## Security Architecture

### Authentication

- **JWT Tokens**: JSON Web Tokens for API authentication
- **Token Expiration**: Configurable token expiration times
- **Refresh Tokens**: Automatic token refresh mechanism
- **Role-Based Access**: Different access levels for users

### Rate Limiting

- **Request Limits**: Per-endpoint rate limiting
- **User Limits**: Per-user request limits
- **IP Limits**: Per-IP address limiting
- **Graceful Degradation**: Fallback responses when limits exceeded

### Data Protection

- **Input Validation**: Comprehensive input validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Cross-site scripting prevention
- **CORS Configuration**: Proper CORS headers

## Performance Architecture

### Caching Strategy

- **Result Caching**: Analysis results cached for identical positions
- **Model Caching**: Neural models cached in memory
- **Session Caching**: Training session data cached
- **Database Caching**: Database query result caching

### Optimization Techniques

- **Async Processing**: Background processing for long operations
- **Batch Processing**: Multiple operations processed together
- **Memory Management**: Efficient memory usage and cleanup
- **Resource Monitoring**: Real-time resource usage tracking

### Scalability Considerations

- **Horizontal Scaling**: Multiple API instances support
- **Load Balancing**: Request distribution across instances
- **Database Scaling**: Database connection pooling
- **Resource Isolation**: Separate resources for different operations

## Deployment Architecture

### Development Environment

```
Local Development → Flask Development Server → SQLite Database → React Dev Server
```

### Production Environment

```
Nginx → Gunicorn → Flask App → PostgreSQL → Redis Cache
```

#### Components

- **Nginx**: Reverse proxy and static file serving
- **Gunicorn**: WSGI server for Flask application
- **PostgreSQL**: Production database (optional)
- **Redis**: Caching and session storage (optional)

## Monitoring and Logging

### Application Monitoring

- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Error rates and types
- **Resource Usage**: CPU, memory, and disk usage
- **User Activity**: User interaction patterns

### Logging Strategy

- **Request Logging**: All API requests logged
- **Error Logging**: Detailed error information
- **Training Logs**: Neural training progress logs
- **Analysis Logs**: Analysis execution logs

## Integration Points

### External APIs

- **Game Analysis APIs**: Integration with external analysis tools
- **Neural Model APIs**: External model evaluation services
- **Data Storage APIs**: Cloud storage for models and data

### Internal Integrations

- **Core Engine**: All analysis components integrated
- **Database**: Persistent storage for all data
- **Frontend**: Real-time UI updates
- **Neural System**: Training and evaluation integration

## Future Architecture Considerations

### Planned Enhancements

- **Microservices**: Break down into smaller services
- **Message Queues**: Async processing with message queues
- **Containerization**: Docker containerization
- **Cloud Deployment**: Cloud-native deployment options

### Scalability Improvements

- **Horizontal Scaling**: Multiple instance support
- **Database Sharding**: Database scaling strategies
- **CDN Integration**: Content delivery network
- **Load Balancing**: Advanced load balancing

## Related Documentation

- [API Reference](api/endpoints.md) - Complete API documentation
- [Development Setup](development/setup.md) - Development environment setup
- [Neural Training Guide](../../guides/neural/training.md) - Neural system user guide
- [Pattern Detection Guide](../../guides/analysis/pattern-detection.md) - Analysis system user guide 