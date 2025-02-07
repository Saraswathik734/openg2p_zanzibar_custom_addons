from enum import Enum


class G2PRegistryType(Enum):
    FARMER = "farmer"
    STUDENT = "student"
    OTHER = "other"

    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields."""
        # Each tuple is of the form (value, label)
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
