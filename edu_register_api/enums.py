import enum


class AppEnv(enum.StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prd"


class ItemType(enum.StrEnum):
    COURSE = "course"
    TEST = "test"


class RegistrationStatus(enum.StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    COMPLETED = "COMPLETED"
