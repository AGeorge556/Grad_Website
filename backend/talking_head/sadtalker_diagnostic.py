#!/usr/bin/env python3
"""
SadTalker Diagnostic Script

This script helps diagnose and identify bottlenecks in the SadTalker video generation process.
It can run standalone diagnostics or be integrated into the main pipeline.
"""

import os
import sys
import time
import json
import logging
import subprocess
import psutil
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SadTalkerDiagnostic:
    def __init__(self):
        self.sadtalker_dir = "D:\\University files\\Graduation Project\\SadTalker"
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {}
        
    def check_system_requirements(self):
        """Check system requirements for SadTalker"""
        logging.info("🔍 Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        logging.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check CPU and memory
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024**3)
        
        logging.info(f"CPU cores: {cpu_count}")
        logging.info(f"Total memory: {total_memory_gb:.1f} GB")
        
        # Check GPU availability
        gpu_available = False
        gpu_info = "Not available"
        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_info = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logging.info(f"GPU: {gpu_info} ({gpu_memory:.1f} GB)")
            else:
                logging.warning("GPU not available - will use CPU (slower)")
        except ImportError:
            logging.warning("PyTorch not available - cannot check GPU")
        
        self.results['system'] = {
            'python_version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            'cpu_count': cpu_count,
            'total_memory_gb': total_memory_gb,
            'gpu_available': gpu_available,
            'gpu_info': gpu_info
        }
        
        return self.results['system']
    
    def check_dependencies(self):
        """Check critical dependencies for SadTalker"""
        logging.info("🔍 Checking dependencies...")
        
        critical_deps = [
            'torch',
            'torchvision',
            'librosa',
            'face_alignment',
            'opencv-python',
            'numpy',
            'scipy',
            'imageio',
            'Pillow'
        ]
        
        missing_deps = []
        dependency_versions = {}
        
        for dep in critical_deps:
            try:
                if dep == 'opencv-python':
                    import cv2
                    dependency_versions[dep] = cv2.__version__
                elif dep == 'Pillow':
                    from PIL import Image
                    dependency_versions[dep] = Image.__version__
                else:
                    module = __import__(dep)
                    dependency_versions[dep] = getattr(module, '__version__', 'Unknown')
                
                logging.info(f"✅ {dep}: {dependency_versions[dep]}")
            except ImportError:
                logging.error(f"❌ {dep}: Missing")
                missing_deps.append(dep)
        
        self.results['dependencies'] = {
            'missing': missing_deps,
            'versions': dependency_versions
        }
        
        return self.results['dependencies']
    
    def check_model_files(self):
        """Check if required model files exist"""
        logging.info("🔍 Checking model files...")
        
        model_files = {
            'alignment_WFLW_4HG.pth': 'checkpoints/alignment_WFLW_4HG.pth',
            'BFM_Fitting': 'checkpoints/BFM_Fitting/',
            'auido2exp_00300-model.pth': 'checkpoints/auido2exp_00300-model.pth',
            'mapping_00109-model.pth.tar': 'checkpoints/mapping_00109-model.pth.tar',
            'mapping_00229-model.pth.tar': 'checkpoints/mapping_00229-model.pth.tar',
            'SadTalker_V002.safetensors': 'checkpoints/SadTalker_V002.safetensors'
        }
        
        missing_models = []
        existing_models = []
        
        for model_name, model_path in model_files.items():
            full_path = os.path.join(self.sadtalker_dir, model_path)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / (1024**2)  # MB
                logging.info(f"✅ {model_name}: {file_size:.1f} MB")
                existing_models.append(model_name)
            else:
                logging.error(f"❌ {model_name}: Missing")
                missing_models.append(model_name)
        
        self.results['models'] = {
            'missing': missing_models,
            'existing': existing_models
        }
        
        return self.results['models']
    
    def run_full_diagnostic(self, source_image_path=None, audio_path=None):
        """Run complete diagnostic suite"""
        logging.info("🚀 Starting full SadTalker diagnostic...")
        
        start_time = time.time()
        
        # Run all diagnostic checks
        self.check_system_requirements()
        self.check_dependencies()
        self.check_model_files()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Summary
        total_time = time.time() - start_time
        logging.info(f"🏁 Diagnostic completed in {total_time:.2f} seconds")
        
        # Save results
        self.save_diagnostic_report()
        
        return self.results
    
    def generate_recommendations(self):
        """Generate optimization recommendations based on diagnostic results"""
        logging.info("💡 Generating recommendations...")
        
        recommendations = []
        
        # Check system resources
        if 'system' in self.results:
            system = self.results['system']
            
            if not system['gpu_available']:
                recommendations.append({
                    'type': 'hardware',
                    'priority': 'high',
                    'title': 'GPU Not Available',
                    'description': 'SadTalker will run on CPU which is significantly slower',
                    'solution': 'Install CUDA-compatible GPU or use fast performance mode'
                })
            
            if system['total_memory_gb'] < 8:
                recommendations.append({
                    'type': 'hardware',
                    'priority': 'medium',
                    'title': 'Low Memory',
                    'description': f'System has {system["total_memory_gb"]:.1f}GB RAM, recommended 8GB+',
                    'solution': 'Add more RAM or use fast performance mode'
                })
        
        # Check dependencies
        if 'dependencies' in self.results:
            deps = self.results['dependencies']
            
            if deps['missing']:
                recommendations.append({
                    'type': 'dependencies',
                    'priority': 'critical',
                    'title': 'Missing Dependencies',
                    'description': f'Missing: {", ".join(deps["missing"])}',
                    'solution': f'Install missing packages: pip install {" ".join(deps["missing"])}'
                })
        
        # Check models
        if 'models' in self.results:
            models = self.results['models']
            
            if models['missing']:
                recommendations.append({
                    'type': 'models',
                    'priority': 'critical',
                    'title': 'Missing Model Files',
                    'description': f'Missing: {", ".join(models["missing"])}',
                    'solution': 'Download model files or run setup script'
                })
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def save_diagnostic_report(self):
        """Save diagnostic report to file"""
        report_path = os.path.join(self.backend_dir, "../media/sadtalker_diagnostic_report.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'summary': self.generate_summary()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"📄 Diagnostic report saved to: {report_path}")
    
    def generate_summary(self):
        """Generate a summary of the diagnostic results"""
        summary = {
            'status': 'unknown',
            'critical_issues': 0,
            'warnings': 0,
            'ready_for_production': False
        }
        
        if 'recommendations' in self.results:
            for rec in self.results['recommendations']:
                if rec['priority'] == 'critical':
                    summary['critical_issues'] += 1
                elif rec['priority'] in ['high', 'medium']:
                    summary['warnings'] += 1
        
        if summary['critical_issues'] == 0:
            if summary['warnings'] == 0:
                summary['status'] = 'excellent'
                summary['ready_for_production'] = True
            else:
                summary['status'] = 'good'
                summary['ready_for_production'] = True
        else:
            summary['status'] = 'needs_attention'
            summary['ready_for_production'] = False
        
        return summary

def main():
    """Main function for standalone execution"""
    diagnostic = SadTalkerDiagnostic()
    
    # Run diagnostic
    results = diagnostic.run_full_diagnostic()
    
    # Print summary
    print("\n" + "="*50)
    print("SADTALKER DIAGNOSTIC SUMMARY")
    print("="*50)
    
    summary = results.get('summary', {})
    print(f"Status: {summary.get('status', 'unknown').upper()}")
    print(f"Critical Issues: {summary.get('critical_issues', 0)}")
    print(f"Warnings: {summary.get('warnings', 0)}")
    print(f"Ready for Production: {'YES' if summary.get('ready_for_production', False) else 'NO'}")
    
    if 'recommendations' in results:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. [{rec['priority'].upper()}] {rec['title']}")
            print(f"   {rec['description']}")
            print(f"   Solution: {rec['solution']}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 