import pytest
from bg_task.zendesk_tasks import ZendeskWebhookHandler


class TestZendeskWebhookHandler:

    def test_match_weight_medicine_type(self):
        assert 'ozempic' == ZendeskWebhookHandler.match_weight_medicine_type(
            'semaglutide 2 mg/1.5 mL (0.25 mg or 0.5 mg dose) subcutaneous solution')

        assert 'contrave' == ZendeskWebhookHandler.match_weight_medicine_type(
            'bupropion 2 mg/1.5 mL (0.25 mg or 0.5 mg dose) subcutaneous solution')
