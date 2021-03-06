import logging
import socketserver

from core.runners.downloader import FileTransmitter
from core.socket_errors import InvalidTransmissionKeyError, SocketError, InvalidTransmissionTypeError
from database.models import Transmissions
from database.repositories import TransmissionRepository


class SocketRequestHandler(socketserver.BaseRequestHandler):
    """
    Handles the traffic received over a TCP socket. The request must specify a
    transmission key (generated using the REST API)
    """

    def handle(self):
        """Hook that handles traffic."""

        # Receive the initial 8-character Transmission Key
        transmission_key = self.request.recv(16).decode()

        transmission_repo = TransmissionRepository(use_new_session=True)

        tran = None
        try:

            tran = transmission_repo.get_by_transmission_key(transmission_key)
            if not tran:
                raise InvalidTransmissionKeyError()

            if tran.transmission_type == Transmissions.TYPE_GET:
                # Run the GET FILE runner
                FileTransmitter(tran.user, self.request).run()

            elif tran.transmission_type == Transmissions.TYPE_UPLOAD:
                # TODO Add support for uploads
                pass
            else:
                raise InvalidTransmissionTypeError()

        except SocketError as err:
            logging.error(f"{err.get_error_code()}: Ran into an error white serving {self.client_address}", err)
            self.request.send(f"{err.get_error_code()}")
        finally:
            # Always end the transmission
            if tran:
                transmission_repo.delete(tran)
