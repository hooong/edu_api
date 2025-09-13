import enum


class AppEnv(enum.StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prd"


class ItemType(enum.StrEnum):
    COURSE = "course"
    TEST = "test"
