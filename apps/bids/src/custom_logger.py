import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):    
        config = getattr(record, 'config', None)
        pod_config = getattr(record, 'pod_config', None)
        payload = getattr(record, 'payload', None)
        log_record = {
            'severity': record.levelname,
            'message': record.getMessage(),
            'name': record.name,
            'timestamp': self.formatTime(record, self.datefmt),            
            'additional_info': {
                'file_name': record.filename,
                'function_name': record.funcName,
                'line_no': record.lineno,
                'config' : config or {},
                'pod_config' : pod_config or {},
                'payload': payload or {}
            }
        }
        return json.dumps(log_record)