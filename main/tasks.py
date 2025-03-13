import os
import logging
import subprocess
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def run_hyros_script():
    try:
        script_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"), "get_hryos_data.py")
        logger.info(f"Executing script: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Script executed successfully.")
            logger.info(result.stdout)
        else:
            logger.error(f"Script execution failed: {result.stderr}")
    
    except Exception as e:
        logger.error(f"Error while running script: {e}", exc_info=True)
