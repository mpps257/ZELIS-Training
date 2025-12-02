"""
Version storage and management for EDA reports.
Stores previous versions of EDA reports with metadata for comparison.
"""
import os
import json
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil
 
__version__ = "1.0.0"
 
 
class VersionManager:
    """Manages versioned EDA reports and metadata."""
    
    def __init__(self, storage_dir='.eda_versions'):
        self.storage_dir = Path(storage_dir)
        self.metadata_file = self.storage_dir / 'versions.json'
        self.versions_dir = self.storage_dir / 'versions'
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage directories if they don't exist."""
        self.storage_dir.mkdir(exist_ok=True)
        self.versions_dir.mkdir(exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _load_metadata(self):
        """Load version metadata from disk."""
        if not self.metadata_file.exists():
            return {}
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata):
        """Save version metadata to disk."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _compute_data_hash(self, df):
        """Compute a hash of the dataframe for duplicate detection."""
        # Hash based on shape, column names, and sample of data
        hash_str = f"{df.shape}_{','.join(sorted(df.columns))}"
        # Add hash of first and last few rows
        if len(df) > 0:
            sample = pd.concat([df.head(5), df.tail(5)])
            hash_str += str(sample.values.tobytes())
        return hashlib.md5(hash_str.encode()).hexdigest()[:12]
    
    def save_version(self, source_name, df, analysis_results, quality_score, output_dir, version_id=None):
        """
        Save a new version of the EDA report.
        
        Args:
            source_name: Name/identifier of the data source
            df: The dataframe analyzed
            analysis_results: Dict containing all analysis results
            quality_score: Data quality score (0-100)
            output_dir: Directory where reports were saved
            version_id: Optional version ID (if None, will be generated)
        """
        metadata = self._load_metadata()
        
        # Compute data hash
        data_hash = self._compute_data_hash(df)
        
        # Create version entry
        if version_id is None:
            version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_key = f"{source_name}_{version_id}"
        
        # Copy reports to versioned storage
        version_path = self.versions_dir / version_key
        version_path.mkdir(exist_ok=True)
        
        # Check if output_dir is already the version_path (direct save)
        output_path = Path(output_dir).resolve()
        version_path_resolved = version_path.resolve()
        
        if output_path != version_path_resolved:
            # Copy markdown and HTML reports
            md_source = Path(output_dir) / 'eda_report.md'
            html_source = Path(output_dir) / 'eda_report.html'
            figs_source = Path(output_dir) / 'figs'
            
            if md_source.exists():
                shutil.copy2(md_source, version_path / 'eda_report.md')
            if html_source.exists():
                shutil.copy2(html_source, version_path / 'eda_report.html')
            if figs_source.exists():
                figs_dest = version_path / 'figs'
                if figs_dest.exists():
                    shutil.rmtree(figs_dest)
                shutil.copytree(figs_source, figs_dest)
        # If output_dir is already version_path, files are already there, no need to copy
        
        # Store analysis results as JSON for comparison
        analysis_file = version_path / 'analysis_results.json'
        analysis_to_save = {
            'numeric_df': analysis_results.get('numeric_df', pd.DataFrame()).to_dict('records') if isinstance(analysis_results.get('numeric_df'), pd.DataFrame) else [],
            'categorical_df': analysis_results.get('categorical_df', pd.DataFrame()).to_dict('records') if isinstance(analysis_results.get('categorical_df'), pd.DataFrame) else [],
            'missing_df': analysis_results.get('missing_df', pd.DataFrame()).to_dict('records') if isinstance(analysis_results.get('missing_df'), pd.DataFrame) else [],
            'missing_overall': analysis_results.get('missing_overall', {}),
            'corrs': {
                'pearson': analysis_results.get('corrs', {}).get('pearson', pd.DataFrame()).to_dict() if isinstance(analysis_results.get('corrs', {}).get('pearson'), pd.DataFrame) else {},
                'categorical': analysis_results.get('corrs', {}).get('categorical', pd.DataFrame()).to_dict() if isinstance(analysis_results.get('corrs', {}).get('categorical'), pd.DataFrame) else {},
            },
            'quality_breakdown': analysis_results.get('quality_breakdown', {})
        }
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_to_save, f, indent=2, default=str)
        
        # Store version metadata
        version_info = {
            'version_id': version_id,
            'source_name': source_name,
            'timestamp': datetime.now().isoformat(),
            'data_hash': data_hash,
            'shape': list(df.shape),
            'columns': list(df.columns),
            'quality_score': quality_score,
            'quality_breakdown': analysis_results.get('quality_breakdown', {}),
            'storage_path': str(version_path),
            'missing_pct': analysis_results.get('missing_overall', {}).get('total_missing_pct', 0),
            'numeric_cols': len(df.select_dtypes(include=['number']).columns),
            'categorical_cols': len(df.select_dtypes(include=['object', 'category']).columns),
        }
        
        # Add to metadata
        if source_name not in metadata:
            metadata[source_name] = []
        metadata[source_name].append(version_info)
        
        # Sort by timestamp (newest first)
        metadata[source_name].sort(key=lambda x: x['timestamp'], reverse=True)
        
        self._save_metadata(metadata)
        return version_info
    
    def get_versions(self, source_name=None):
        """
        Get all versions, optionally filtered by source name.
        
        Args:
            source_name: Optional source name filter
            
        Returns:
            Dict of source_name -> list of versions, or all sources if source_name is None
        """
        metadata = self._load_metadata()
        if source_name:
            return metadata.get(source_name, [])
        return metadata
    def get_latest_version(self, source_name):
        """Get the most recent version for a source."""
        versions = self.get_versions(source_name)
        if not versions:
            return None
        return versions[0]  # Already sorted newest first
    
    def get_best_version(self, source_name):
        """
        Get the version with the highest quality score for a source.
        
        Args:
            source_name: Source name to query
            
        Returns:
            Version info dict with highest quality score, or None if no versions
        """
        versions = self.get_versions(source_name)
        if not versions:
            return None
        
        best = max(versions, key=lambda x: x.get('quality_score', 0))
        return best
    
    def compare_versions(self, version1, version2):
            """
            Compare two versions and return differences.
            
            Args:
                version1: Version info dict
                version2: Version info dict
                
            Returns:
                Dict with comparison results
            """
            comparison = {
                'version1': version1['version_id'],
                'version2': version2['version_id'],
                'timestamp1': version1['timestamp'],
                'timestamp2': version2['timestamp'],
                'quality_score1': version1.get('quality_score', 0),
                'quality_score2': version2.get('quality_score', 0),
                'quality_diff': version2.get('quality_score', 0) - version1.get('quality_score', 0),
                'shape1': version1['shape'],
                'shape2': version2['shape'],
                'shape_changed': version1['shape'] != version2['shape'],
                'columns_added': set(version2['columns']) - set(version1['columns']),
                'columns_removed': set(version1['columns']) - set(version2['columns']),
                'columns_common': set(version1['columns']) & set(version2['columns']),
                'missing_pct1': version1.get('missing_pct', 0),
                'missing_pct2': version2.get('missing_pct', 0),
                'missing_diff': version2.get('missing_pct', 0) - version1.get('missing_pct', 0),
                'is_duplicate': version1['data_hash'] == version2['data_hash'],
            }
            
            # Determine which is better
            if comparison['quality_score2'] > comparison['quality_score1']:
                comparison['better_version'] = 'version2'
                comparison['better_version_id'] = version2['version_id']
            elif comparison['quality_score1'] > comparison['quality_score2']:
                comparison['better_version'] = 'version1'
                comparison['better_version_id'] = version1['version_id']
            else:
                comparison['better_version'] = 'equal'
                comparison['better_version_id'] = None
            
            return comparison
        
    def load_analysis_results(self, version_info):
                """
                Load analysis results for a version from stored JSON.
                
                Args:
                    version_info: Version info dict with storage_path
                    
                Returns:
                    Dict with analysis results (numeric_df, categorical_df, etc.)
                """
                analysis_file = Path(version_info['storage_path']) / 'analysis_results.json'
                if not analysis_file.exists():
                    return None
                
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert back to DataFrames
                results = {
                    'numeric_df': pd.DataFrame(data.get('numeric_df', [])),
                    'categorical_df': pd.DataFrame(data.get('categorical_df', [])),
                    'missing_df': pd.DataFrame(data.get('missing_df', [])),
                    'missing_overall': data.get('missing_overall', {}),
                    'corrs': {
                        'pearson': pd.DataFrame(data.get('corrs', {}).get('pearson', {})),
                        'categorical': pd.DataFrame(data.get('corrs', {}).get('categorical', {}))
                    },
                    'quality_breakdown': data.get('quality_breakdown', {})
                }
                
                return results
                
        