import sys
from pathlib import Path
from threading import Lock
from datetime import datetime


_log_file = None
_lock = Lock()


# Generate a timestamp prefix for log messages
def _timestamp_prefix():
    return f"{datetime.now():%Y-%m-%d %H:%M:%S} | "


# Set up logging to a file and console.
# Overwrites existing file on startup.
# Called once at the start of the application.
def setup_logging(log_path="log.txt"):
    global _log_file
    if _log_file is not None:
        return

    repo_root = Path(__file__).resolve().parents[2]
    path = Path(log_path)
    if not path.is_absolute():
        path = repo_root / path

    path.parent.mkdir(parents=True, exist_ok=True)
    # Overwrite any existing file on startup
    with open(path, "w", encoding="utf-8"):
        pass
    
    _log_file = open(path, "a", encoding="utf-8")


# Log a message to both console and the log file, with a timestamp prefix.
def log(*args, sep=" ", end="\n"):
    global _log_file
    
    # Convert all arguments to strings for logging
    try:
        msg = sep.join(str(a) for a in args)
    except Exception:
        msg = " ".join(map(str, args))
    
    line = _timestamp_prefix() + msg + end
    
    # Ensure that printing to console and writing to the log file is thread-safe
    with _lock:
        try:
            print(line, end="", file=sys.stdout)
        except Exception:
            try:
                print(line, end="", file=sys.stderr)
            except Exception:
                pass
        
        if _log_file:
            try:
                _log_file.write(line)
                _log_file.flush()
            except Exception:
                print(_timestamp_prefix() + "Failed to write to log file\n", file=sys.stderr)


# Clean up resources, such as closing the log file.
# Called on application shutdown.
def teardown():
    global _log_file
    
    if _log_file:
        try:
            _log_file.close()
        except Exception:
            pass
        
        _log_file = None
