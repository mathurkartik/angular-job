import time
import threading
from utils.logger import get_logger

logger = get_logger("groq_rate_limiter")

class GroqRateLimiter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(GroqRateLimiter, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, tpm_limit: int = 5500, rpm_limit: int = 25):
        with self._lock:
            if self._initialized:
                return
            self.tpm_limit = tpm_limit
            self.rpm_limit = rpm_limit
            # history holds (timestamp, token_count)
            self.history = []
            self._initialized = True

    def wait_if_needed(self, estimated_tokens: int):
        with self._lock:
            while True:
                now = time.time()
                # Remove history older than 60s
                self.history = [item for item in self.history if now - item[0] < 60]
                
                current_tpm = sum(item[1] for item in self.history)
                current_rpm = len(self.history)
                
                if (current_tpm + estimated_tokens <= self.tpm_limit) and (current_rpm < self.rpm_limit):
                    # Allocate estimated tokens
                    self.history.append((now, estimated_tokens))
                    break
                else:
                    reason = []
                    if current_tpm + estimated_tokens > self.tpm_limit:
                        reason.append(f"TPM {current_tpm}/{self.tpm_limit}")
                    if current_rpm >= self.rpm_limit:
                        reason.append(f"RPM {current_rpm}/{self.rpm_limit}")
                    
                    logger.info(
                        f"[GroqRateLimiter] Near rate limit ({', '.join(reason)}). "
                        f"Pacing request of estimated {estimated_tokens} tokens by sleeping 3s..."
                    )
                    # Release lock during sleep so other threads/runs can proceed or update
                    self._lock.release()
                    time.sleep(3.0)
                    self._lock.acquire()

    def update_actual_usage(self, estimated_tokens: int, actual_tokens: int):
        with self._lock:
            # Update the most recent estimation with actual tokens used
            for i in range(len(self.history) - 1, -1, -1):
                ts, val = self.history[i]
                if val == estimated_tokens:
                    self.history[i] = (ts, actual_tokens)
                    break
