import http.server
import socketserver
import socket
import os
import threading

PORT = int(os.environ.get("PORT", 10000))

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(4096)
        if not data:
            return
        
        try:
            # قراءة طلب CONNECT
            header = data.decode('utf-8', errors='ignore')
            if header.startswith('CONNECT'):
                target = header.split(' ')[1]
                host, port = target.split(':')
                port = int(port)
                
                self.request.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                
                # الاتصال بالسيرفر الحقيقي
                remote = socket.create_connection((host, port), timeout=10)
                
                # دالة لنقل البيانات
                def relay(src, dst):
                    try:
                        while True:
                            buf = src.recv(4096)
                            if not buf: break
                            dst.sendall(buf)
                    except: pass
                
                # تشغيل النقل في الاتجاهين
                t1 = threading.Thread(target=relay, args=(self.request, remote))
                t2 = threading.Thread(target=relay, args=(remote, self.request))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
                remote.close()
        except Exception as e:
            pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    with ThreadedTCPServer(("", PORT), ThreadedTCPRequestHandler) as server:
        print(f"Server running on port {PORT}")
        server.serve_forever()
