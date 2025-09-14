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


class PaymentMethod(enum.StrEnum):
    CARD = "card"
    KAKAOPAY = "kakaopay"
    NAVERPAY = "naverpay"


class PaymentStatus(enum.StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class PaymentStatusFilter(enum.StrEnum):
    PAID = "PAID"
    CANCELED = "CANCELED"
