import React, { useState, useEffect } from 'react';

const ProgressMonitor = ({ runId, onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Initializing...');
  const [status, setStatus] = useState('RUNNING');
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(Date.now());
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(null);
  const [detailedProgress, setDetailedProgress] = useState(null);

  useEffect(() => {
    if (!runId) return;

    const pollProgress = async () => {
      try {
        const response = await fetch(`/api/workflow/progress/${runId}`);
        const data = await response.json();

        if (data.status === 'success') {
          const progressData = data.data;
          const statusInfo = progressData.status;

          setProgress(statusInfo.progress || 0);
          setCurrentStep(statusInfo.current_step || 'Processing...');
          setStatus(statusInfo.status || 'RUNNING');
          setDetailedProgress(statusInfo);

          if (statusInfo.error) {
            setError(statusInfo.error);
          }

          // Calculate estimated time remaining
          if (statusInfo.progress > 0 && statusInfo.progress < 100) {
            const elapsed = Date.now() - startTime;
            const estimated = (elapsed / statusInfo.progress) * (100 - statusInfo.progress);
            setEstimatedTimeRemaining(Math.round(estimated / 1000));
          }

          // Check if completed
          if (statusInfo.status === 'COMPLETED' || statusInfo.status === 'FAILED' || statusInfo.status === 'ERROR') {
            if (onComplete) {
              onComplete(progressData);
            }
            return; // Stop polling
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
        setError('Failed to fetch progress');
      }
    };

    // Initial poll
    pollProgress();

    // Set up polling interval
    const interval = setInterval(pollProgress, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [runId, startTime, onComplete]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'RUNNING': return 'text-blue-600 bg-blue-100';
      case 'COMPLETED': return 'text-green-600 bg-green-100';
      case 'FAILED': return 'text-red-600 bg-red-100';
      case 'ERROR': return 'text-red-600 bg-red-200';
      case 'CANCELLED': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 100) return 'bg-green-500';
    if (progress >= 75) return 'bg-blue-500';
    if (progress >= 50) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  if (!runId) {
    return (
      <div className="text-center py-4 text-gray-500">
        No validation run in progress
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 max-w-2xl mx-auto">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-900">Validation Progress</h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
            {status}
          </span>
        </div>
        <p className="text-sm text-gray-600">Run ID: {runId.substring(0, 8)}...</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-gray-700">{progress.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ease-out ${getProgressColor(progress)}`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Current Step */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          {status === 'RUNNING' && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          <span className="text-sm font-medium text-gray-700">Current Step:</span>
        </div>
        <p className="text-gray-900 mt-1">{currentStep}</p>
      </div>

      {/* Detailed Progress Information */}
      {detailedProgress && (
        <div className="space-y-3 mb-4">
          {detailedProgress.current_check && detailedProgress.total_checks && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Validation Checks:</span>
              <span className="font-medium">
                {detailedProgress.current_check} / {detailedProgress.total_checks}
              </span>
            </div>
          )}

          {estimatedTimeRemaining && status === 'RUNNING' && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Estimated Time Remaining:</span>
              <span className="font-medium text-blue-600">
                {formatTime(estimatedTimeRemaining)}
              </span>
            </div>
          )}

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Elapsed Time:</span>
            <span className="font-medium">
              {formatTime(Math.floor((Date.now() - startTime) / 1000))}
            </span>
          </div>

          {detailedProgress.overall_score !== undefined && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Current Score:</span>
              <span className="font-medium text-green-600">
                {detailedProgress.overall_score.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-red-600 mr-2">⚠️</span>
            <span className="text-sm font-medium text-red-800">Error:</span>
          </div>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      )}

      {/* Progress Steps Visualization */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Validation Steps</h4>
        <div className="space-y-2">
          {[
            { step: 'Document Access Verification', threshold: 10 },
            { step: 'Data Extraction', threshold: 30 },
            { step: 'Validation Criteria Loading', threshold: 40 },
            { step: 'Running Validation Checks', threshold: 70 },
            { step: 'Calculating Scores', threshold: 90 },
            { step: 'Storing Results', threshold: 100 }
          ].map((item, index) => {
            const isCompleted = progress >= item.threshold;
            const isCurrent = progress >= (index > 0 ? [10, 30, 40, 70, 90][index - 1] : 0) && progress < item.threshold;
            
            return (
              <div key={index} className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  isCompleted ? 'bg-green-500' : 
                  isCurrent ? 'bg-blue-500 animate-pulse' : 
                  'bg-gray-300'
                }`}></div>
                <span className={`text-sm ${
                  isCompleted ? 'text-green-700 font-medium' :
                  isCurrent ? 'text-blue-700 font-medium' :
                  'text-gray-500'
                }`}>
                  {item.step}
                </span>
                {isCompleted && <span className="text-green-600 text-xs">✓</span>}
                {isCurrent && <span className="text-blue-600 text-xs">⏳</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      {status === 'RUNNING' && (
        <div className="mt-6 flex justify-center">
          <button
            onClick={async () => {
              try {
                const response = await fetch(`/api/workflow/cancel/${runId}`, {
                  method: 'POST'
                });
                const data = await response.json();
                if (data.status === 'success') {
                  setStatus('CANCELLED');
                  setCurrentStep('Validation cancelled');
                }
              } catch (error) {
                console.error('Error cancelling validation:', error);
              }
            }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Cancel Validation
          </button>
        </div>
      )}

      {/* Completion Message */}
      {status === 'COMPLETED' && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-green-600 mr-2">✅</span>
            <span className="text-sm font-medium text-green-800">Validation Completed Successfully!</span>
          </div>
          {detailedProgress && detailedProgress.overall_score !== undefined && (
            <p className="text-sm text-green-700 mt-1">
              Final Score: {detailedProgress.overall_score.toFixed(1)}% 
              ({detailedProgress.final_status})
            </p>
          )}
        </div>
      )}

      {(status === 'FAILED' || status === 'ERROR') && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-red-600 mr-2">❌</span>
            <span className="text-sm font-medium text-red-800">Validation Failed</span>
          </div>
          <p className="text-sm text-red-700 mt-1">
            Please check the error details above and try again.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProgressMonitor;

