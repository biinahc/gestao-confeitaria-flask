# service.py
import os
import sys
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil

# Adiciona a pasta do projeto ao path para encontrar o 'app'
project_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(project_path)

from waitress import serve
from app import app # Importa a sua aplicação Flask

class DoceControleService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DoceControle"
    _svc_display_name_ = "Doce Controle Web Service"
    _svc_description_ = "Serviço que hospeda a aplicação de gestão Confeitando com Artes."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        # O Waitress serve a sua aplicação na porta 5000
        # O host 0.0.0.0 permite acesso de outros dispositivos na rede
        serve(app, host='0.0.0.0', port=5000)
        while self.is_running:
            win32event.WaitForSingleObject(self.hWaitStop, 5000)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DoceControleService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DoceControleService)

