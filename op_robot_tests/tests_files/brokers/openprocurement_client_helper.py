from openprocurement_client.client import Client
from openprocurement_client.utils import get_tender_id_by_uaid
from openprocurement_client.exceptions import IdNotFound
from restkit.errors import RequestFailed
from retrying import retry


def retry_if_request_failed(exception):
    return isinstance(exception, RequestFailed)


class StableClient(Client):
    @retry(stop_max_attempt_number=10, wait_fixed=2000, retry_on_exception=retry_if_request_failed)
    def request(self, *args, **kwargs):
        return super(StableClient, self).request(self, *args, **kwargs)


def prepare_api_wrapper(key, host_url, api_version):
    return StableClient(key, host_url, api_version)


def get_complaint_internal_id(tender, complaintID):
    try:
        for complaint in tender.data.complaints:
            if complaint.complaintID == complaintID:
                return complaint.id
    except AttributeError:
        pass
    try:
        for award in tender.data.awards:
            for complaint in award.complaints:
                if complaint.complaintID == complaintID:
                    return complaint.id
    except AttributeError:
        pass
    raise IdNotFound
