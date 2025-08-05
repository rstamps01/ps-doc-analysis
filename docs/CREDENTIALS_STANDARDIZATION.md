# Google Credentials Path Standardization

## Overview
This update standardizes all Google API credentials to use a single, consistent path: `/app/credentials/google-service-account.json`

## Changes Made

### 1. Dockerfile Updates
- **File**: `validation_tool/Dockerfile`
- **Change**: Create `/app/credentials` directory with proper permissions (777)
- **Before**: Created `/app/src/credentials`
- **After**: Creates `/app/credentials` with write permissions

### 2. Credentials Manager Updates
- **File**: `validation_tool/src/config/credentials_manager.py`
- **Change**: Updated all 3 path lists to prioritize `/app/credentials/`
- **Locations**: `__init__`, `reload_credentials`, `get_preferred_save_path`
- **Impact**: All credential loading now checks `/app/credentials/` first

### 3. Google Integration Updates
- **File**: `validation_tool/src/routes/google_integration.py`
- **Changes**:
  - Status check function: `/app/credentials/google-service-account.json`
  - Upload function: `/app/credentials` directory
- **Impact**: Upload and status check now use same path

### 4. Environment Variable Updates
- **File**: `.env`
- **Change**: `GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-service-account.json`
- **Impact**: Environment variable matches actual file location

### 5. Cleanup
- **Removed**: `validation_tool/src/routes/google_integration copy.py`
- **Reason**: Contained old path references

## Benefits

1. **Consistency**: All components use the same path
2. **Reliability**: No more path mismatches between upload and status check
3. **Maintainability**: Single source of truth for credentials location
4. **Container Compatibility**: Proper permissions for containerized deployment

## Path Priority Order

1. `/app/credentials/google-service-account.json` (preferred for containers)
2. `../credentials/google-service-account.json` (local development)
3. `/home/ubuntu/ps-doc-analysis/validation_tool/src/credentials/google-service-account.json` (absolute local)
4. `/src/credentials/google-service-account.json` (legacy container)
5. `/tmp/google_credentials.json` (fallback)

## Testing

After deployment:
1. Upload credentials via Settings tab
2. Check that status shows "Configured"
3. Test Google API connections
4. Verify validation processes work correctly

## Deployment Notes

- Container must be rebuilt to get new Dockerfile changes
- Environment variables must be updated in deployment configuration
- No data migration needed - system will find existing credentials in legacy locations

