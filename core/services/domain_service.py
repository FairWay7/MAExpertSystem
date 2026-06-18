from typing import Dict


class DomainService:
    def add_domain(self, domain: Dict) -> str:
        """Добавление предметной области"""
        domain_id = domain.get('id')
        if not domain_id:
            import uuid
            domain_id = str(uuid.uuid4())
            domain['id'] = domain_id

        self.domains[domain_id] = domain
        return domain_id