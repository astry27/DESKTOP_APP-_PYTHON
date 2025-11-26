# Path: client/threading_utils.py
# Threading utilities untuk async operations di PyQt5

from PyQt5.QtCore import QThread, pyqtSignal, QObject, QThreadPool
from typing import Callable, Any, Optional
import traceback


class WorkerSignals(QObject):
    """Signals untuk worker thread"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QThread):
    """Worker thread untuk menjalankan long-running tasks"""

    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_running = True

    def run(self):
        """Jalankan function di background thread"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
            traceback.print_exc()
        finally:
            self.signals.finished.emit()

    def stop(self):
        """Stop thread gracefully"""
        self._is_running = False


class AsyncAPICall(QThread):
    """Specialized worker untuk API calls dengan better error handling"""

    finished = pyqtSignal()
    error = pyqtSignal(str, str)  # error_type, error_message
    success = pyqtSignal(dict)  # result data
    progress = pyqtSignal(str)  # status message

    def __init__(self, api_func: Callable, *args, **kwargs):
        super().__init__()
        self.api_func = api_func
        self.args = args
        self.kwargs = kwargs
        self._is_running = True

    def run(self):
        """Execute API call in background"""
        try:
            self.progress.emit("Processing...")
            result = self.api_func(*self.args, **self.kwargs)

            # Emit success dengan result
            if isinstance(result, dict):
                self.success.emit(result)
            else:
                self.success.emit({"data": result})

        except TimeoutError as e:
            self.error.emit("Timeout", "API request timeout (>10 seconds). Server might be offline.")
        except ConnectionError as e:
            self.error.emit("Connection", "Cannot connect to API server. Check internet connection.")
        except Exception as e:
            self.error.emit("Error", str(e))
            traceback.print_exc()
        finally:
            self.finished.emit()

    def stop(self):
        """Stop thread gracefully"""
        self._is_running = False


class ParallelDataLoader(QObject):
    """Load multiple data sources in parallel threads"""

    all_finished = pyqtSignal()
    item_finished = pyqtSignal(str, dict)  # component_name, result
    error_occurred = pyqtSignal(str, str)  # component_name, error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool()
        self.active_threads = {}
        self.results = {}

    def load_item(self, name: str, api_func: Callable, *args, **kwargs):
        """Load a single data item in parallel"""
        worker = AsyncAPICall(api_func, *args, **kwargs)
        worker.success.connect(
            lambda result: self._on_item_success(name, result)
        )
        worker.error.connect(
            lambda err_type, err_msg: self._on_item_error(name, f"{err_type}: {err_msg}")
        )
        worker.finished.connect(
            lambda: self._on_item_finished(name)
        )

        self.active_threads[name] = worker
        worker.start()

    def _on_item_success(self, name: str, result: dict):
        """Handle successful item load"""
        self.results[name] = result
        self.item_finished.emit(name, result)

    def _on_item_error(self, name: str, error_msg: str):
        """Handle item load error"""
        self.error_occurred.emit(name, error_msg)

    def _on_item_finished(self, name: str):
        """Check if all items finished"""
        if name in self.active_threads:
            del self.active_threads[name]

        # If all threads finished, emit signal
        if len(self.active_threads) == 0:
            self.all_finished.emit()

    def get_results(self):
        """Get all loaded results"""
        return self.results

    def is_loading(self):
        """Check if any threads are still loading"""
        return len(self.active_threads) > 0
