import heapq
from models import db, EmergencyContact

class EmergencyQueue:
    def __init__(self):
        self.queue = []

    def load_contacts(self):
        contacts = EmergencyContact.query.all()
        for contact in contacts:
            heapq.heappush(self.queue, (contact.distance, contact.name, contact.phone))

    def get_nearest_responder(self):
        if self.queue:
            return heapq.heappop(self.queue)
        return None
