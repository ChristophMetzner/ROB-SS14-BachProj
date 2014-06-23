# coding=utf-8

import pickle
import logging
import logging.handlers
import SocketServer
import struct
import threading
import time

class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)

class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 logger_name = None,
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = False
        self.running = False
        self.timeout = 1
        if logger_name is None:
            ip, port = self.server_address
            self.logname = "log_server_" + str(ip).replace(".","_") + "_" + str(port)
        else:
            self.logname = logger_name

    def serve_until_stopped(self):
        import select
        self.abort = False
        self.running = True
        abort = False
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort
        self.running = False
        


class LogServerThread(threading.Thread):
    def __init__(self, port, logger_name = None, handlers = None, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.port = port
        self.daemon = True
        self.handlers = handlers
        
        self.tcpserver = LogRecordSocketReceiver(host="localhost",
                                                 port=self.port,
                                                 logger_name=logger_name,
                                                 handler=LogRecordStreamHandler)
        self.logger = logging.getLogger(self.tcpserver.logname)
        if self.handlers is not None:
            for handler in self.handlers:
                self.logger.addHandler(handler)
        self.ip, self.port = self.tcpserver.server_address
    
    def run(self):
        self.tcpserver.serve_until_stopped()
    def stop(self):
        if self.is_alive():
            self.tcpserver.abort = True
            while self.tcpserver.running:
                time.sleep(0.010)
            if self.handlers is not None:
                for handler in self.handlers:
                    self.logger.removeHandler(handler)
                    handler.flush()
                    handler.close()
            

def initFileLogServer(log_file,
                      port,
                      file_level = logging.NOTSET,
                      console_level = logging.INFO,
                      logger_name=None,
                      suppress_console_output = True,
                      formatString = "%(asctime)s %(name)s %(levelname)s: %(message)s"):
    """Configures the a logger and returns the Server instance

    Uses by default the root logger.
    """
    
    formatter = logging.Formatter(formatString)
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(file_level)
    fh.setFormatter(formatter)
    handlers = [fh]
    if not suppress_console_output:
        ch = logging.StreamHandler()        
        ch.setLevel(console_level)
        ch.setFormatter(formatter)
        handlers += [ch]
    logServer = LogServerThread(port, logger_name, handlers = handlers)

    logger = logging.getLogger(logServer.tcpserver.logname)
    # Level is very low, because the above Server will bypass any filtering anyway.
    logger.setLevel(1)
    logger.propagate = False
    return logServer
