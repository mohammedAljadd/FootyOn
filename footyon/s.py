from .matches.models import Match
import uuid

for m in Match.objects.filter(qr_token__isnull=True):
    m.qr_token = uuid.uuid4()
    m.save()