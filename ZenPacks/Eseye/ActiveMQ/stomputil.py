
# support code for using stomp.py
# Copyright (C) 2014 Chaskiel Grundman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import stomp
import threading
import logging
import Queue

thelog=logging.getLogger(__name__)
class AppListener(stomp.ConnectionListener):
    def __init__(self):
        super(AppListener, self).__init__()
        self.__lock=threading.Lock()
        self.__cond=threading.Event()
        self.__cond.clear()
        self.q=Queue.Queue()
        self.errors=False
        self.connected=False
        self.expect_disconnect=False
        self.found=False
        self.messages=0
    def reset_errors(self):
        with self.__lock:
            self.errors=False
            self.__cond.clear()
    def get_error_message(self):
        with self.__lock:
            if self.errors:
                return self.error_message
    def ok(self):
        with self.__lock:
            #thelog.info("Errors is %s" % self.errors)
            return self.connected and not self.errors
    def wait(self, timeout=None):
        return self.__cond.wait(timeout=timeout)
    def lastwaitfor(self):
        with self.__lock:
            f=self.found
            if self.found:
               self.found=None
               self.wait_for=None
               if self.messages == 0:
                   self.__cond.clear()
        return f
    def prepare_wait(self, receipt):
        with self.__lock:
            self.found=None
            self.wait_for=receipt
    def get_message(self):
        ret=None
        with self.__lock:
           if self.messages > 0:
               self.messages=self.messages-1
               if self.messages == 0:
                   self.__cond.clear()
               ret=self.q.get(block=0)
        return ret
    def on_error(self, headers, message):
        #print headers
        m=''
        if 'message' in headers:
            thelog.debug('received an error %s' % headers['message'])
            m=headers['message']
            #print message
        else:
            thelog.debug('received an error\n%s' % message)
            m=message
        with self.__lock:
            self.errors=True
	    self.error_message=m
        self.__cond.set()
    def on_connected(self, headers, message):
        thelog.debug('connection complete')
        with self.__lock:
            self.connected=True
        self.__cond.set()
    def on_connecting(self, host_and_port):
        with self.__lock:
            self.connected=False
            self.expect_disconnect=False
            self.errors=False
            self.q=Queue.Queue()
            self.found=None
            self.expect_disconnect=True
            self.messages=0
            self.__cond.clear()
    def on_send(self, frame):
        if frame.cmd.lower() == 'disconnect':
            with self.__lock:
                self.expect_disconnect=True
        with self.__lock:
            self.errors=False
            if self.messages == 0:
                self.__cond.clear()
    def on_message(self, headers, message):
        with self.__lock:
            self.messages=self.messages+1
        thelog.debug('received a message %s' % message)
        self.q.put([headers, message])
        self.__cond.set()
        #print 'headers %s' % headers
    def on_receipt(self, headers, message):
        #print 'received reciept'
        with self.__lock:
            if 'receipt-id' in headers:
                r=headers['receipt-id']
                if r == self.wait_for:
                    thelog.debug('receipt matched')
                    self.found=r
                    self.__cond.set()
                elif self.wait_for:
                    thelog.debug('receipt not matched')
                else:
                    thelog.debug('unexpected receipt')
    def on_disconnected(self):
        dowarn=True
        with self.__lock:
            self.connected=False
            if not self.expect_disconnect:
               dowarn=False
        if dowarn:
            thelog.warning('lost connection')
        self.__cond.set()
    def on_heartbeat_timeout(self):
        with self.__lock:
            self.connected=False
        thelog.warning('no heartbeat')
        self.__cond.set()
