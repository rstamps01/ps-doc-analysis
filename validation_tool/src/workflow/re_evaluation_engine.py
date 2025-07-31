"""
Re-evaluation engine for managing validation workflow and version tracking
"""
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.results_manager import ValidationResultsManager
from validation.comprehensive_engine import ComprehensiveValidationEngine
from integrations.api_key_google_sheets import APIKeyGoogleSheetsIntegration

class ReEvaluationEngine:
    def __init__(self):
        """Initialize the re-evaluation engine"""
        self.results_manager = ValidationResultsManager()
        self.validation_engine = ComprehensiveValidationEngine()
        self.google_integration = APIKeyGoogleSheetsIntegration()
        self.active_evaluations = {}  # Track running evaluations
        self.progress_callbacks = {}  # Store progress callback functions
    
    def register_progress_callback(self, run_id: str, callback: Callable[[Dict], None]):
        """Register a callback function for progress updates"""
        self.progress_callbacks[run_id] = callback
    
    def _update_progress(self, run_id: str, progress_data: Dict[str, Any]):
        """Update progress and call registered callback if available"""
        if run_id in self.progress_callbacks:
            try:
                self.progress_callbacks[run_id](progress_data)
            except Exception as e:
                print(f"Error calling progress callback: {e}")
    
    async def start_comprehensive_validation(self,
                                           document_urls: Dict[str, str],
                                           validation_config: Dict[str, Any],
                                           user_id: str = "default",
                                           project_name: str = "Unknown",
                                           is_re_evaluation: bool = False,
                                           original_run_id: str = None,
                                           change_reason: str = None,
                                           changed_by: str = None) -> str:
        """Start a comprehensive validation run with progress tracking"""
        
        # Start the validation run in the database
        run_id = self.results_manager.start_validation_run(
            document_urls=document_urls,
            validation_config=validation_config,
            user_id=user_id,
            project_name=project_name
        )
        
        # Track as active evaluation
        self.active_evaluations[run_id] = {
            'status': 'RUNNING',
            'start_time': time.time(),
            'progress': 0,
            'current_step': 'Initializing',
            'is_re_evaluation': is_re_evaluation,
            'original_run_id': original_run_id
        }
        
        # If this is a re-evaluation, store the relationship
        if is_re_evaluation and original_run_id:
            comparison_data = {
                'trigger_reason': change_reason,
                'triggered_by': changed_by,
                'start_timestamp': datetime.now().isoformat()
            }
            
            self.results_manager.db.store_re_evaluation(
                original_run_id=original_run_id,
                new_run_id=run_id,
                change_reason=change_reason or "Manual re-evaluation",
                changed_by=changed_by or "Unknown",
                comparison_data=comparison_data
            )
        
        # Start the validation process asynchronously
        asyncio.create_task(self._run_validation_process(run_id, document_urls, validation_config))
        
        return run_id
    
    async def _run_validation_process(self, run_id: str, document_urls: Dict[str, str], validation_config: Dict[str, Any]):
        """Run the actual validation process with progress tracking"""
        try:
            # Step 1: Document Access Verification (10%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 10,
                'current_step': 'Verifying document access',
                'status': 'RUNNING'
            })
            
            self.active_evaluations[run_id]['progress'] = 10
            self.active_evaluations[run_id]['current_step'] = 'Verifying document access'
            
            # Verify document access
            access_results = await self._verify_document_access(document_urls)
            
            if not access_results['all_accessible']:
                # Complete with error
                error_message = f"Document access failed: {access_results['errors']}"
                self.results_manager.complete_validation_run(
                    run_id=run_id,
                    overall_score=0.0,
                    status="FAILED",
                    results=[],
                    error_message=error_message
                )
                
                self.active_evaluations[run_id]['status'] = 'FAILED'
                self._update_progress(run_id, {
                    'run_id': run_id,
                    'progress': 100,
                    'current_step': 'Failed - Document access error',
                    'status': 'FAILED',
                    'error': error_message
                })
                return
            
            # Step 2: Data Extraction (30%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 30,
                'current_step': 'Extracting document data',
                'status': 'RUNNING'
            })
            
            self.active_evaluations[run_id]['progress'] = 30
            self.active_evaluations[run_id]['current_step'] = 'Extracting document data'
            
            # Extract data from documents
            extracted_data = await self._extract_document_data(document_urls)
            
            # Step 3: Validation Criteria Loading (40%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 40,
                'current_step': 'Loading validation criteria',
                'status': 'RUNNING'
            })
            
            self.active_evaluations[run_id]['progress'] = 40
            self.active_evaluations[run_id]['current_step'] = 'Loading validation criteria'
            
            # Load validation criteria
            validation_criteria = self.validation_engine.get_validation_criteria()
            
            # Step 4: Running Validation Checks (70%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 70,
                'current_step': 'Running validation checks',
                'status': 'RUNNING'
            })
            
            self.active_evaluations[run_id]['progress'] = 70
            self.active_evaluations[run_id]['current_step'] = 'Running validation checks'
            
            # Run comprehensive validation
            validation_results = await self._run_comprehensive_checks(
                extracted_data, validation_criteria, validation_config, run_id
            )
            
            # Step 5: Calculating Scores (90%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 90,
                'current_step': 'Calculating final scores',
                'status': 'RUNNING'
            })
            
            self.active_evaluations[run_id]['progress'] = 90
            self.active_evaluations[run_id]['current_step'] = 'Calculating final scores'
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(validation_results, validation_config)
            
            # Determine status
            pass_threshold = validation_config.get('pass_threshold', 80)
            status = "PASS" if overall_score >= pass_threshold else "FAIL"
            
            # Step 6: Storing Results (100%)
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 100,
                'current_step': 'Storing results',
                'status': 'COMPLETING'
            })
            
            # Complete the validation run
            self.results_manager.complete_validation_run(
                run_id=run_id,
                overall_score=overall_score,
                status=status,
                results=validation_results
            )
            
            # Final progress update
            self.active_evaluations[run_id]['status'] = 'COMPLETED'
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 100,
                'current_step': 'Validation completed',
                'status': 'COMPLETED',
                'overall_score': overall_score,
                'final_status': status
            })
            
            # Clean up
            if run_id in self.active_evaluations:
                del self.active_evaluations[run_id]
            if run_id in self.progress_callbacks:
                del self.progress_callbacks[run_id]
        
        except Exception as e:
            # Handle errors
            error_message = str(e)
            
            self.results_manager.complete_validation_run(
                run_id=run_id,
                overall_score=0.0,
                status="ERROR",
                results=[],
                error_message=error_message
            )
            
            self.active_evaluations[run_id]['status'] = 'ERROR'
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': 100,
                'current_step': 'Error occurred',
                'status': 'ERROR',
                'error': error_message
            })
            
            # Clean up
            if run_id in self.active_evaluations:
                del self.active_evaluations[run_id]
            if run_id in self.progress_callbacks:
                del self.progress_callbacks[run_id]
    
    async def _verify_document_access(self, document_urls: Dict[str, str]) -> Dict[str, Any]:
        """Verify that all documents are accessible"""
        results = {
            'all_accessible': True,
            'accessible_docs': [],
            'inaccessible_docs': [],
            'errors': []
        }
        
        for doc_type, url in document_urls.items():
            try:
                if 'docs.google.com/spreadsheets' in url:
                    # Test Google Sheets access
                    test_result = self.google_integration.test_connection()
                    if test_result.get('status') == 'success':
                        results['accessible_docs'].append(doc_type)
                    else:
                        results['inaccessible_docs'].append(doc_type)
                        results['errors'].append(f"{doc_type}: {test_result.get('message', 'Unknown error')}")
                        results['all_accessible'] = False
                elif 'drive.google.com' in url:
                    # Test Google Drive access (simplified)
                    results['accessible_docs'].append(doc_type)
                else:
                    results['inaccessible_docs'].append(doc_type)
                    results['errors'].append(f"{doc_type}: Unsupported URL format")
                    results['all_accessible'] = False
            
            except Exception as e:
                results['inaccessible_docs'].append(doc_type)
                results['errors'].append(f"{doc_type}: {str(e)}")
                results['all_accessible'] = False
        
        return results
    
    async def _extract_document_data(self, document_urls: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from all documents"""
        extracted_data = {}
        
        for doc_type, url in document_urls.items():
            try:
                if 'docs.google.com/spreadsheets' in url:
                    # Extract from Google Sheets
                    sheet_data = self.google_integration.extract_comprehensive_data(url)
                    extracted_data[doc_type] = sheet_data
                elif 'drive.google.com' in url:
                    # For Google Drive documents, we'll simulate extraction
                    extracted_data[doc_type] = {
                        'type': 'pdf',
                        'url': url,
                        'status': 'accessible',
                        'content': 'PDF content would be extracted here'
                    }
                else:
                    extracted_data[doc_type] = {
                        'type': 'unknown',
                        'url': url,
                        'status': 'unsupported',
                        'error': 'Unsupported document type'
                    }
            
            except Exception as e:
                extracted_data[doc_type] = {
                    'type': 'error',
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                }
        
        return extracted_data
    
    async def _run_comprehensive_checks(self, 
                                      extracted_data: Dict[str, Any], 
                                      validation_criteria: List[Dict], 
                                      validation_config: Dict[str, Any],
                                      run_id: str) -> List[Dict[str, Any]]:
        """Run comprehensive validation checks with progress updates"""
        results = []
        total_checks = len(validation_criteria)
        
        for i, criterion in enumerate(validation_criteria):
            # Update progress for individual checks
            check_progress = 70 + (i / total_checks) * 15  # 70% to 85%
            self._update_progress(run_id, {
                'run_id': run_id,
                'progress': check_progress,
                'current_step': f'Running check: {criterion.get("name", "Unknown")}',
                'status': 'RUNNING',
                'current_check': i + 1,
                'total_checks': total_checks
            })
            
            # Run individual validation check
            check_result = self._run_individual_check(criterion, extracted_data, validation_config)
            results.append(check_result)
            
            # Small delay to make progress visible
            await asyncio.sleep(0.1)
        
        return results
    
    def _run_individual_check(self, 
                            criterion: Dict[str, Any], 
                            extracted_data: Dict[str, Any], 
                            validation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run an individual validation check"""
        try:
            # Use the comprehensive validation engine
            result = self.validation_engine.run_single_validation(criterion, extracted_data)
            
            # Apply configuration weights if specified
            category_weights = validation_config.get('category_weights', {})
            category = criterion.get('category', 'Unknown')
            weight = category_weights.get(category, 1.0)
            
            # Adjust score based on weight
            if 'score' in result:
                result['weighted_score'] = result['score'] * weight
                result['weight_applied'] = weight
            
            return result
        
        except Exception as e:
            return {
                'check_id': criterion.get('id', 'unknown'),
                'check_name': criterion.get('name', 'Unknown Check'),
                'category': criterion.get('category', 'Unknown'),
                'status': 'ERROR',
                'score': 0.0,
                'message': f'Check failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _calculate_overall_score(self, 
                               validation_results: List[Dict[str, Any]], 
                               validation_config: Dict[str, Any]) -> float:
        """Calculate the overall validation score"""
        if not validation_results:
            return 0.0
        
        # Use weighted scores if available, otherwise use regular scores
        scores = []
        for result in validation_results:
            if 'weighted_score' in result:
                scores.append(result['weighted_score'])
            elif 'score' in result:
                scores.append(result['score'])
            else:
                scores.append(0.0)
        
        # Calculate weighted average
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.0
    
    def get_evaluation_status(self, run_id: str) -> Dict[str, Any]:
        """Get the current status of a running evaluation"""
        if run_id in self.active_evaluations:
            return self.active_evaluations[run_id]
        else:
            # Check if it's a completed run
            run_details = self.results_manager.get_validation_run_details(run_id)
            if run_details:
                return {
                    'status': run_details['run']['status'],
                    'progress': 100,
                    'current_step': 'Completed',
                    'overall_score': run_details['run']['overall_score']
                }
            else:
                return {
                    'status': 'NOT_FOUND',
                    'progress': 0,
                    'current_step': 'Run not found'
                }
    
    def trigger_re_evaluation(self,
                            original_run_id: str,
                            change_reason: str,
                            changed_by: str,
                            user_id: str = "default",
                            updated_config: Dict[str, Any] = None) -> str:
        """Trigger a re-evaluation based on an original run"""
        
        # Get the original run details
        original_run = self.results_manager.get_validation_run_details(original_run_id)
        if not original_run:
            raise ValueError(f"Original run {original_run_id} not found")
        
        # Use original document URLs and config, with any updates
        document_urls = original_run['run']['document_urls']
        validation_config = original_run['run']['validation_config']
        
        if updated_config:
            validation_config.update(updated_config)
        
        project_name = original_run['run']['project_name']
        
        # Start the re-evaluation
        new_run_id = asyncio.run(self.start_comprehensive_validation(
            document_urls=document_urls,
            validation_config=validation_config,
            user_id=user_id,
            project_name=project_name,
            is_re_evaluation=True,
            original_run_id=original_run_id,
            change_reason=change_reason,
            changed_by=changed_by
        ))
        
        return new_run_id
    
    def get_active_evaluations(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active evaluations"""
        return self.active_evaluations.copy()
    
    def cancel_evaluation(self, run_id: str) -> bool:
        """Cancel a running evaluation"""
        if run_id in self.active_evaluations:
            self.active_evaluations[run_id]['status'] = 'CANCELLED'
            
            # Complete the run with cancelled status
            self.results_manager.complete_validation_run(
                run_id=run_id,
                overall_score=0.0,
                status="CANCELLED",
                results=[],
                error_message="Evaluation cancelled by user"
            )
            
            # Clean up
            del self.active_evaluations[run_id]
            if run_id in self.progress_callbacks:
                del self.progress_callbacks[run_id]
            
            return True
        
        return False

