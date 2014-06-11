# coding=utf-8

import pickle
import logging
import logging.handlers
import SocketServer
import struct
import threading

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
                 loggerName = "",
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = loggerName

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


class LogServerThread(threading.Thread):
    def __init__(self, port, loggerName="",  *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.port = port
        self.loggerName = loggerName
        self.daemon = True

        logging.basicConfig(
            format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
        self.tcpserver = LogRecordSocketReceiver(host="localhost",
                                                 port=self.port,
                                                 loggerName=self.loggerName,
                                                 handler=LogRecordStreamHandler)
        self.ip, self.port = self.tcpserver.server_address
    
    def run(self):
        self.tcpserver.serve_until_stopped()

def initFileLogServer(logFile,
                      port,
                      level=logging.NOTSET,
                      loggerName="",
                      printToChat=False,
                      formatString="%(asctime)s %(name)s %(levelname)s: %(message)s"):
    """Configures the a logger and returns the Server instance

    Uses by default the root logger.
    """
    logger = logging.getLogger(loggerName)
    # Level is very low, because the above Server will bypass any filtering anyway.
    logger.setLevel(1)
    fh = logging.FileHandler(logFile)

    fh.setLevel(level)

    formatter = logging.Formatter(formatString)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    if printToChat:
        ch = logging.StreamHandler()        
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    logServer = LogServerThread(port, loggerName)
    return logServer
