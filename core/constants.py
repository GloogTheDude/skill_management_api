from enum import Enum

class PermissionProfile(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    HR = "HR"

def coerce_permission_profile(value):
    if isinstance(value, PermissionProfile):
        return value
    if isinstance(value, int):
        return {1: PermissionProfile.EMPLOYEE, 2: PermissionProfile.MANAGER, 3: PermissionProfile.HR}.get(value)
    return value

class TRAININGREQUESTSTATUS(Enum):
    PENDING = "PENDING"
    VALIDATED ="VALIDATED"
    REFUSED = "REFUSED"

class PARTICIPATIONSTATUS(Enum):
    REGISTERED = "REGISTERED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABSENT = "ABSENT"
    CANCELLED = "CANCELLED"

class SKILLSTATUS(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    MIXED = "MIXED"
    MANUALLY_VALIDATED = "MANUALLY_VALIDATED"

class SKILLSOURCETYPE(Enum):
    DIPLOMA = "DIPLOMA"
    CERTIFICATION = "CERTIFICATION"
    TRAINING = "TRAINING"
    VALIDATION = "VALIDATION"

class TYPEPARTICIPATIONDTO(Enum):
    DIPLOMA = "DIPLOMA"
    CERTIFICATION = "CERTIFICATION"
    SKILL = "SKILL"

class CERTIFICATIONSTATUS(Enum):
    VALID = "VALID"
    EXPIRING_SOON = "EXPIRING_SOON"
    URGENT = "URGENT"
    EXPIRED = "EXPIRED"
