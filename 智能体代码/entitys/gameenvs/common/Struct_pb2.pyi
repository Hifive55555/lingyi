from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EPostureStance(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Neutral: _ClassVar[EPostureStance]
    Friendly: _ClassVar[EPostureStance]
    Unfriendly: _ClassVar[EPostureStance]
    Hostile: _ClassVar[EPostureStance]
    Unknown: _ClassVar[EPostureStance]
Neutral: EPostureStance
Friendly: EPostureStance
Unfriendly: EPostureStance
Hostile: EPostureStance
Unknown: EPostureStance

class THVectorString(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, v: _Optional[_Iterable[str]] = ...) -> None: ...

class THVectorInt(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, v: _Optional[_Iterable[int]] = ...) -> None: ...

class THVectorBytes(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, v: _Optional[_Iterable[bytes]] = ...) -> None: ...

class THVectorGeoPoint(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedCompositeFieldContainer[THGeoPoint]
    def __init__(self, v: _Optional[_Iterable[_Union[THGeoPoint, _Mapping]]] = ...) -> None: ...

class THVectorWaypoint(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedCompositeFieldContainer[THWaypoint]
    def __init__(self, v: _Optional[_Iterable[_Union[THWaypoint, _Mapping]]] = ...) -> None: ...

class THVectorXSection(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedCompositeFieldContainer[THXSection]
    def __init__(self, v: _Optional[_Iterable[_Union[THXSection, _Mapping]]] = ...) -> None: ...

class THVectorCCS(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedCompositeFieldContainer[THCCS]
    def __init__(self, v: _Optional[_Iterable[_Union[THCCS, _Mapping]]] = ...) -> None: ...

class THVectorEmptySlot(_message.Message):
    __slots__ = ("v",)
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.RepeatedCompositeFieldContainer[THEmptySlot]
    def __init__(self, v: _Optional[_Iterable[_Union[THEmptySlot, _Mapping]]] = ...) -> None: ...

class THMapBytes(_message.Message):
    __slots__ = ("v",)
    class VEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.ScalarMap[str, bytes]
    def __init__(self, v: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class THMapString(_message.Message):
    __slots__ = ("v",)
    class VEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    V_FIELD_NUMBER: _ClassVar[int]
    v: _containers.ScalarMap[str, str]
    def __init__(self, v: _Optional[_Mapping[str, str]] = ...) -> None: ...

class THWeaponCancelInfo(_message.Message):
    __slots__ = ("FiringUnitID", "FiringUnitDBID", "FiringUnitName", "FiringUnitSideID", "WeaponID", "WeaponDBID", "WeaponName", "TargetContactActualUnitID", "TargetContactActualUnitName", "TargetContactActualUnitSideID")
    FIRINGUNITID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITDBID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    WEAPONNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    FiringUnitID: str
    FiringUnitDBID: int
    FiringUnitName: str
    FiringUnitSideID: str
    WeaponID: str
    WeaponDBID: int
    WeaponName: str
    TargetContactActualUnitID: str
    TargetContactActualUnitName: str
    TargetContactActualUnitSideID: str
    def __init__(self, FiringUnitID: _Optional[str] = ..., FiringUnitDBID: _Optional[int] = ..., FiringUnitName: _Optional[str] = ..., FiringUnitSideID: _Optional[str] = ..., WeaponID: _Optional[str] = ..., WeaponDBID: _Optional[int] = ..., WeaponName: _Optional[str] = ..., TargetContactActualUnitID: _Optional[str] = ..., TargetContactActualUnitName: _Optional[str] = ..., TargetContactActualUnitSideID: _Optional[str] = ...) -> None: ...

class THSensorStatusChangeInfo(_message.Message):
    __slots__ = ("ID", "Name", "DBID", "Type", "Status", "ExceptionStatus", "DamageSeverity", "IsActive", "MaxRange", "MinRange", "WorkFreq", "CanBeActive", "ParentUnitID", "ParentUnitName", "IsSonar", "IsRadar")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    DAMAGESEVERITY_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    MAXRANGE_FIELD_NUMBER: _ClassVar[int]
    MINRANGE_FIELD_NUMBER: _ClassVar[int]
    WORKFREQ_FIELD_NUMBER: _ClassVar[int]
    CANBEACTIVE_FIELD_NUMBER: _ClassVar[int]
    PARENTUNITID_FIELD_NUMBER: _ClassVar[int]
    PARENTUNITNAME_FIELD_NUMBER: _ClassVar[int]
    ISSONAR_FIELD_NUMBER: _ClassVar[int]
    ISRADAR_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    DBID: int
    Type: int
    Status: int
    ExceptionStatus: str
    DamageSeverity: int
    IsActive: bool
    MaxRange: float
    MinRange: float
    WorkFreq: int
    CanBeActive: bool
    ParentUnitID: str
    ParentUnitName: str
    IsSonar: bool
    IsRadar: bool
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., DBID: _Optional[int] = ..., Type: _Optional[int] = ..., Status: _Optional[int] = ..., ExceptionStatus: _Optional[str] = ..., DamageSeverity: _Optional[int] = ..., IsActive: bool = ..., MaxRange: _Optional[float] = ..., MinRange: _Optional[float] = ..., WorkFreq: _Optional[int] = ..., CanBeActive: bool = ..., ParentUnitID: _Optional[str] = ..., ParentUnitName: _Optional[str] = ..., IsSonar: bool = ..., IsRadar: bool = ...) -> None: ...

class THActiveUnitDevRel(_message.Message):
    __slots__ = ("DevRel",)
    class DevRelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DEVREL_FIELD_NUMBER: _ClassVar[int]
    DevRel: _containers.ScalarMap[str, str]
    def __init__(self, DevRel: _Optional[_Mapping[str, str]] = ...) -> None: ...

class THUnitNewbornInfo(_message.Message):
    __slots__ = ("UnitName", "UnitID", "Category", "Type", "DBID", "Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Pitch", "Roll", "CurrentSpeed", "AssignedMission", "AirOps", "DockingOps", "DockingCondition", "SideID", "UnitType")
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    ROLL_FIELD_NUMBER: _ClassVar[int]
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEDMISSION_FIELD_NUMBER: _ClassVar[int]
    AIROPS_FIELD_NUMBER: _ClassVar[int]
    DOCKINGOPS_FIELD_NUMBER: _ClassVar[int]
    DOCKINGCONDITION_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    UNITTYPE_FIELD_NUMBER: _ClassVar[int]
    UnitName: str
    UnitID: str
    Category: int
    Type: int
    DBID: int
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Pitch: float
    Roll: float
    CurrentSpeed: float
    AssignedMission: str
    AirOps: THAirOps
    DockingOps: THDockingOps
    DockingCondition: bool
    SideID: str
    UnitType: int
    def __init__(self, UnitName: _Optional[str] = ..., UnitID: _Optional[str] = ..., Category: _Optional[int] = ..., Type: _Optional[int] = ..., DBID: _Optional[int] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Pitch: _Optional[float] = ..., Roll: _Optional[float] = ..., CurrentSpeed: _Optional[float] = ..., AssignedMission: _Optional[str] = ..., AirOps: _Optional[_Union[THAirOps, _Mapping]] = ..., DockingOps: _Optional[_Union[THDockingOps, _Mapping]] = ..., DockingCondition: bool = ..., SideID: _Optional[str] = ..., UnitType: _Optional[int] = ...) -> None: ...

class THContactInfo(_message.Message):
    __slots__ = ("ID", "Name", "Type", "Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Pitch", "Roll", "ActualUnitID", "DBID", "IDStatus", "ActType", "ActCategory", "SideID", "Age", "CurrentSpeed")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    ROLL_FIELD_NUMBER: _ClassVar[int]
    ACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    IDSTATUS_FIELD_NUMBER: _ClassVar[int]
    ACTTYPE_FIELD_NUMBER: _ClassVar[int]
    ACTCATEGORY_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Type: int
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Pitch: float
    Roll: float
    ActualUnitID: str
    DBID: int
    IDStatus: int
    ActType: int
    ActCategory: int
    SideID: str
    Age: float
    CurrentSpeed: float
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Type: _Optional[int] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Pitch: _Optional[float] = ..., Roll: _Optional[float] = ..., ActualUnitID: _Optional[str] = ..., DBID: _Optional[int] = ..., IDStatus: _Optional[int] = ..., ActType: _Optional[int] = ..., ActCategory: _Optional[int] = ..., SideID: _Optional[str] = ..., Age: _Optional[float] = ..., CurrentSpeed: _Optional[float] = ...) -> None: ...

class THWeaponFiredInfo(_message.Message):
    __slots__ = ("FiringUnitID", "FiringUnitDBID", "FiringUnitName", "FiringUnitType", "FiringUnitClass", "FiringUnitSide", "FiringUnitLongitude", "FiringUnitLatitude", "FiringUnitCourse", "FiringUnitSpeed", "FiringUnitAltitude", "FiringUnitAGL", "WeaponID", "WeaponDBID", "WeaponName", "WeaponType", "WeaponClass", "TargetContactID", "TargetContactLongitude", "TargetContactLatitude", "TargetContactHeading", "TargetContactSpeed", "TargetContactAltitude", "TargetContactRangeHoriz", "TargetContactRangeSlant", "TargetContactActualUnitID", "TargetContactActualUnitName", "TargetContactActualUnitClass", "TargetContactActualUnitSide", "SalvoID", "SideID", "FiringDistance")
    FIRINGUNITID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITDBID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITTYPE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITSIDE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITLONGITUDE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITLATITUDE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITCOURSE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITSPEED_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITALTITUDE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITAGL_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    WEAPONNAME_FIELD_NUMBER: _ClassVar[int]
    WEAPONTYPE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTLONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTLATITUDE_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTHEADING_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTSPEED_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTRANGEHORIZ_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTRANGESLANT_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITSIDE_FIELD_NUMBER: _ClassVar[int]
    SALVOID_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    FIRINGDISTANCE_FIELD_NUMBER: _ClassVar[int]
    FiringUnitID: str
    FiringUnitDBID: int
    FiringUnitName: str
    FiringUnitType: int
    FiringUnitClass: str
    FiringUnitSide: str
    FiringUnitLongitude: float
    FiringUnitLatitude: float
    FiringUnitCourse: float
    FiringUnitSpeed: float
    FiringUnitAltitude: float
    FiringUnitAGL: float
    WeaponID: str
    WeaponDBID: int
    WeaponName: str
    WeaponType: int
    WeaponClass: str
    TargetContactID: str
    TargetContactLongitude: float
    TargetContactLatitude: float
    TargetContactHeading: float
    TargetContactSpeed: float
    TargetContactAltitude: float
    TargetContactRangeHoriz: float
    TargetContactRangeSlant: float
    TargetContactActualUnitID: str
    TargetContactActualUnitName: str
    TargetContactActualUnitClass: str
    TargetContactActualUnitSide: str
    SalvoID: str
    SideID: str
    FiringDistance: float
    def __init__(self, FiringUnitID: _Optional[str] = ..., FiringUnitDBID: _Optional[int] = ..., FiringUnitName: _Optional[str] = ..., FiringUnitType: _Optional[int] = ..., FiringUnitClass: _Optional[str] = ..., FiringUnitSide: _Optional[str] = ..., FiringUnitLongitude: _Optional[float] = ..., FiringUnitLatitude: _Optional[float] = ..., FiringUnitCourse: _Optional[float] = ..., FiringUnitSpeed: _Optional[float] = ..., FiringUnitAltitude: _Optional[float] = ..., FiringUnitAGL: _Optional[float] = ..., WeaponID: _Optional[str] = ..., WeaponDBID: _Optional[int] = ..., WeaponName: _Optional[str] = ..., WeaponType: _Optional[int] = ..., WeaponClass: _Optional[str] = ..., TargetContactID: _Optional[str] = ..., TargetContactLongitude: _Optional[float] = ..., TargetContactLatitude: _Optional[float] = ..., TargetContactHeading: _Optional[float] = ..., TargetContactSpeed: _Optional[float] = ..., TargetContactAltitude: _Optional[float] = ..., TargetContactRangeHoriz: _Optional[float] = ..., TargetContactRangeSlant: _Optional[float] = ..., TargetContactActualUnitID: _Optional[str] = ..., TargetContactActualUnitName: _Optional[str] = ..., TargetContactActualUnitClass: _Optional[str] = ..., TargetContactActualUnitSide: _Optional[str] = ..., SalvoID: _Optional[str] = ..., SideID: _Optional[str] = ..., FiringDistance: _Optional[float] = ...) -> None: ...

class WeaponImpactInfo(_message.Message):
    __slots__ = ("SideID", "ID", "Course", "Speed_KTS", "Longitude", "Latitude", "Altitude", "Type", "Age")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    SPEED_KTS_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    SideID: str
    ID: str
    Course: float
    Speed_KTS: float
    Longitude: float
    Latitude: float
    Altitude: float
    Type: int
    Age: float
    def __init__(self, SideID: _Optional[str] = ..., ID: _Optional[str] = ..., Course: _Optional[float] = ..., Speed_KTS: _Optional[float] = ..., Longitude: _Optional[float] = ..., Latitude: _Optional[float] = ..., Altitude: _Optional[float] = ..., Type: _Optional[int] = ..., Age: _Optional[float] = ...) -> None: ...

class ExplosionInfo(_message.Message):
    __slots__ = ("ExplosionID", "Longitude", "Latitude", "Altitude", "ExpYield", "WarheadType", "WeaponType", "ExplosiveType", "Duration", "MaxDuration", "DirectImpactUnitID", "DirectImpactAimpointID", "ExcludedUnitID", "ExcludedAimPointID", "SideID")
    EXPLOSIONID_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    EXPYIELD_FIELD_NUMBER: _ClassVar[int]
    WARHEADTYPE_FIELD_NUMBER: _ClassVar[int]
    WEAPONTYPE_FIELD_NUMBER: _ClassVar[int]
    EXPLOSIVETYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    MAXDURATION_FIELD_NUMBER: _ClassVar[int]
    DIRECTIMPACTUNITID_FIELD_NUMBER: _ClassVar[int]
    DIRECTIMPACTAIMPOINTID_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEDUNITID_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEDAIMPOINTID_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    ExplosionID: str
    Longitude: float
    Latitude: float
    Altitude: float
    ExpYield: float
    WarheadType: int
    WeaponType: int
    ExplosiveType: int
    Duration: float
    MaxDuration: float
    DirectImpactUnitID: str
    DirectImpactAimpointID: str
    ExcludedUnitID: str
    ExcludedAimPointID: str
    SideID: str
    def __init__(self, ExplosionID: _Optional[str] = ..., Longitude: _Optional[float] = ..., Latitude: _Optional[float] = ..., Altitude: _Optional[float] = ..., ExpYield: _Optional[float] = ..., WarheadType: _Optional[int] = ..., WeaponType: _Optional[int] = ..., ExplosiveType: _Optional[int] = ..., Duration: _Optional[float] = ..., MaxDuration: _Optional[float] = ..., DirectImpactUnitID: _Optional[str] = ..., DirectImpactAimpointID: _Optional[str] = ..., ExcludedUnitID: _Optional[str] = ..., ExcludedAimPointID: _Optional[str] = ..., SideID: _Optional[str] = ...) -> None: ...

class THWeaponSalvo(_message.Message):
    __slots__ = ("ID", "NumberOfShooters", "WeaponDBID", "QuantityTotal", "Target", "ManualFire", "Weapons", "Shooters", "WPoint", "mapdel")
    class ShootersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THShooter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THShooter, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFSHOOTERS_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    QUANTITYTOTAL_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    MANUALFIRE_FIELD_NUMBER: _ClassVar[int]
    WEAPONS_FIELD_NUMBER: _ClassVar[int]
    SHOOTERS_FIELD_NUMBER: _ClassVar[int]
    WPOINT_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    NumberOfShooters: int
    WeaponDBID: int
    QuantityTotal: int
    Target: str
    ManualFire: bool
    Weapons: bytes
    Shooters: _containers.MessageMap[str, THShooter]
    WPoint: bytes
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ID: _Optional[str] = ..., NumberOfShooters: _Optional[int] = ..., WeaponDBID: _Optional[int] = ..., QuantityTotal: _Optional[int] = ..., Target: _Optional[str] = ..., ManualFire: bool = ..., Weapons: _Optional[bytes] = ..., Shooters: _Optional[_Mapping[str, THShooter]] = ..., WPoint: _Optional[bytes] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THShooter(_message.Message):
    __slots__ = ("ID", "PrefMountID", "QuantityAssigned", "QuantityFired", "TimeToNextLaunch", "Timeout")
    ID_FIELD_NUMBER: _ClassVar[int]
    PREFMOUNTID_FIELD_NUMBER: _ClassVar[int]
    QUANTITYASSIGNED_FIELD_NUMBER: _ClassVar[int]
    QUANTITYFIRED_FIELD_NUMBER: _ClassVar[int]
    TIMETONEXTLAUNCH_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    PrefMountID: str
    QuantityAssigned: int
    QuantityFired: int
    TimeToNextLaunch: int
    Timeout: int
    def __init__(self, ID: _Optional[str] = ..., PrefMountID: _Optional[str] = ..., QuantityAssigned: _Optional[int] = ..., QuantityFired: _Optional[int] = ..., TimeToNextLaunch: _Optional[int] = ..., Timeout: _Optional[int] = ...) -> None: ...

class THMissionColl(_message.Message):
    __slots__ = ("Patrol", "Strike", "Cargo", "Ferry", "Support", "MineClearing", "Mining", "Custom", "mapdel")
    class PatrolEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionPatrol
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionPatrol, _Mapping]] = ...) -> None: ...
    class StrikeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionStrike
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionStrike, _Mapping]] = ...) -> None: ...
    class CargoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionCargo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionCargo, _Mapping]] = ...) -> None: ...
    class FerryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionFerry
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionFerry, _Mapping]] = ...) -> None: ...
    class SupportEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionSupport
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionSupport, _Mapping]] = ...) -> None: ...
    class MineClearingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionMineClearing
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionMineClearing, _Mapping]] = ...) -> None: ...
    class MiningEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionMining
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionMining, _Mapping]] = ...) -> None: ...
    class CustomEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMissionCustom
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMissionCustom, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    PATROL_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    CARGO_FIELD_NUMBER: _ClassVar[int]
    FERRY_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    MINECLEARING_FIELD_NUMBER: _ClassVar[int]
    MINING_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Patrol: _containers.MessageMap[str, THMissionPatrol]
    Strike: _containers.MessageMap[str, THMissionStrike]
    Cargo: _containers.MessageMap[str, THMissionCargo]
    Ferry: _containers.MessageMap[str, THMissionFerry]
    Support: _containers.MessageMap[str, THMissionSupport]
    MineClearing: _containers.MessageMap[str, THMissionMineClearing]
    Mining: _containers.MessageMap[str, THMissionMining]
    Custom: _containers.MessageMap[str, THMissionCustom]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Patrol: _Optional[_Mapping[str, THMissionPatrol]] = ..., Strike: _Optional[_Mapping[str, THMissionStrike]] = ..., Cargo: _Optional[_Mapping[str, THMissionCargo]] = ..., Ferry: _Optional[_Mapping[str, THMissionFerry]] = ..., Support: _Optional[_Mapping[str, THMissionSupport]] = ..., MineClearing: _Optional[_Mapping[str, THMissionMineClearing]] = ..., Mining: _Optional[_Mapping[str, THMissionMining]] = ..., Custom: _Optional[_Mapping[str, THMissionCustom]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THMissionPatrol(_message.Message):
    __slots__ = ("Mission", "Type", "PatrolArea", "ProsecutionArea", "OTR", "MNOS", "IOPA", "IWWR", "AEOIPA", "SAD", "TransitThrottle_Aircraft", "StationThrottle_Aircraft", "AttackThrottle_Aircraft", "TransitAltitude_Aircraft", "StationAltitude_Aircraft", "AttackAltitude_Aircraft", "AttackDistance_Aircraft", "TransitTerrainFollowing_Aircraft", "StationTerrainFollowing_Aircraft", "AttackTerrainFollowing_Aircraft", "TransitThrottle_Submarine", "StationThrottle_Submarine", "AttackThrottle_Submarine", "TransitDepth_Submarine", "StationDepth_Submarine", "AttackDepth_Submarine", "AttackDistance_Submarine", "TransitThrottle_Ship", "StationThrottle_Ship", "AttackThrottle_Ship", "AttackDistance_Ship", "TransitThrottle_Facility", "StationThrottle_Facility", "AttackThrottle_Facility", "Formation_Cruise", "Formation_Attack", "MinAircraftReq", "NumberOfFlights_Investigate", "NumberOfFlights_Engage", "WingmanEngageDistance", "NumberOfBoats_Investigate", "NumberOfBoats_Engage", "GroupMemberEngageDistance", "ContinousCoverage_Enable", "ContinousCoverage_AllowQRA", "ContinousCoverage_FlightGenerationMethod", "ContinousCoverage_StationTime", "ContinousCoverage_Overlap", "ContinousCoverage_Duration", "CCSList", "QRAs", "ContinousCoverage_QRANumberOfFlights", "ContinousCoverage_QRAFlightGenerationMethod", "ContinousCoverage_NumberOfFlightsNeededToAllowQRA", "MovementStyle")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PATROLAREA_FIELD_NUMBER: _ClassVar[int]
    PROSECUTIONAREA_FIELD_NUMBER: _ClassVar[int]
    OTR_FIELD_NUMBER: _ClassVar[int]
    MNOS_FIELD_NUMBER: _ClassVar[int]
    IOPA_FIELD_NUMBER: _ClassVar[int]
    IWWR_FIELD_NUMBER: _ClassVar[int]
    AEOIPA_FIELD_NUMBER: _ClassVar[int]
    SAD_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    ATTACKALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    ATTACKTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    ATTACKDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_SHIP_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    FORMATION_ATTACK_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFFLIGHTS_INVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFFLIGHTS_ENGAGE_FIELD_NUMBER: _ClassVar[int]
    WINGMANENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFBOATS_INVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    NUMBEROFBOATS_ENGAGE_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_ENABLE_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_ALLOWQRA_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_FLIGHTGENERATIONMETHOD_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_STATIONTIME_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_OVERLAP_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_DURATION_FIELD_NUMBER: _ClassVar[int]
    CCSLIST_FIELD_NUMBER: _ClassVar[int]
    QRAS_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_QRANUMBEROFFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_QRAFLIGHTGENERATIONMETHOD_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_NUMBEROFFLIGHTSNEEDEDTOALLOWQRA_FIELD_NUMBER: _ClassVar[int]
    MOVEMENTSTYLE_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    PatrolArea: bytes
    ProsecutionArea: bytes
    OTR: bool
    MNOS: int
    IOPA: bool
    IWWR: bool
    AEOIPA: bool
    SAD: bool
    TransitThrottle_Aircraft: int
    StationThrottle_Aircraft: int
    AttackThrottle_Aircraft: int
    TransitAltitude_Aircraft: float
    StationAltitude_Aircraft: float
    AttackAltitude_Aircraft: float
    AttackDistance_Aircraft: float
    TransitTerrainFollowing_Aircraft: bool
    StationTerrainFollowing_Aircraft: bool
    AttackTerrainFollowing_Aircraft: bool
    TransitThrottle_Submarine: int
    StationThrottle_Submarine: int
    AttackThrottle_Submarine: int
    TransitDepth_Submarine: float
    StationDepth_Submarine: float
    AttackDepth_Submarine: float
    AttackDistance_Submarine: float
    TransitThrottle_Ship: int
    StationThrottle_Ship: int
    AttackThrottle_Ship: int
    AttackDistance_Ship: float
    TransitThrottle_Facility: int
    StationThrottle_Facility: int
    AttackThrottle_Facility: int
    Formation_Cruise: int
    Formation_Attack: int
    MinAircraftReq: int
    NumberOfFlights_Investigate: int
    NumberOfFlights_Engage: int
    WingmanEngageDistance: int
    NumberOfBoats_Investigate: int
    NumberOfBoats_Engage: int
    GroupMemberEngageDistance: int
    ContinousCoverage_Enable: bool
    ContinousCoverage_AllowQRA: bool
    ContinousCoverage_FlightGenerationMethod: int
    ContinousCoverage_StationTime: int
    ContinousCoverage_Overlap: int
    ContinousCoverage_Duration: int
    CCSList: bytes
    QRAs: bytes
    ContinousCoverage_QRANumberOfFlights: int
    ContinousCoverage_QRAFlightGenerationMethod: int
    ContinousCoverage_NumberOfFlightsNeededToAllowQRA: int
    MovementStyle: int
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., PatrolArea: _Optional[bytes] = ..., ProsecutionArea: _Optional[bytes] = ..., OTR: bool = ..., MNOS: _Optional[int] = ..., IOPA: bool = ..., IWWR: bool = ..., AEOIPA: bool = ..., SAD: bool = ..., TransitThrottle_Aircraft: _Optional[int] = ..., StationThrottle_Aircraft: _Optional[int] = ..., AttackThrottle_Aircraft: _Optional[int] = ..., TransitAltitude_Aircraft: _Optional[float] = ..., StationAltitude_Aircraft: _Optional[float] = ..., AttackAltitude_Aircraft: _Optional[float] = ..., AttackDistance_Aircraft: _Optional[float] = ..., TransitTerrainFollowing_Aircraft: bool = ..., StationTerrainFollowing_Aircraft: bool = ..., AttackTerrainFollowing_Aircraft: bool = ..., TransitThrottle_Submarine: _Optional[int] = ..., StationThrottle_Submarine: _Optional[int] = ..., AttackThrottle_Submarine: _Optional[int] = ..., TransitDepth_Submarine: _Optional[float] = ..., StationDepth_Submarine: _Optional[float] = ..., AttackDepth_Submarine: _Optional[float] = ..., AttackDistance_Submarine: _Optional[float] = ..., TransitThrottle_Ship: _Optional[int] = ..., StationThrottle_Ship: _Optional[int] = ..., AttackThrottle_Ship: _Optional[int] = ..., AttackDistance_Ship: _Optional[float] = ..., TransitThrottle_Facility: _Optional[int] = ..., StationThrottle_Facility: _Optional[int] = ..., AttackThrottle_Facility: _Optional[int] = ..., Formation_Cruise: _Optional[int] = ..., Formation_Attack: _Optional[int] = ..., MinAircraftReq: _Optional[int] = ..., NumberOfFlights_Investigate: _Optional[int] = ..., NumberOfFlights_Engage: _Optional[int] = ..., WingmanEngageDistance: _Optional[int] = ..., NumberOfBoats_Investigate: _Optional[int] = ..., NumberOfBoats_Engage: _Optional[int] = ..., GroupMemberEngageDistance: _Optional[int] = ..., ContinousCoverage_Enable: bool = ..., ContinousCoverage_AllowQRA: bool = ..., ContinousCoverage_FlightGenerationMethod: _Optional[int] = ..., ContinousCoverage_StationTime: _Optional[int] = ..., ContinousCoverage_Overlap: _Optional[int] = ..., ContinousCoverage_Duration: _Optional[int] = ..., CCSList: _Optional[bytes] = ..., QRAs: _Optional[bytes] = ..., ContinousCoverage_QRANumberOfFlights: _Optional[int] = ..., ContinousCoverage_QRAFlightGenerationMethod: _Optional[int] = ..., ContinousCoverage_NumberOfFlightsNeededToAllowQRA: _Optional[int] = ..., MovementStyle: _Optional[int] = ...) -> None: ...

class THMissionStrike(_message.Message):
    __slots__ = ("Mission", "Type", "Doctrine_Escorts", "SpecificTargets", "STargName", "MCSTT", "UP", "Formation_Cruise", "Formation_Attack", "Bingo", "TargeteeringMethod", "Escort_FlightSize_Shooter", "Escort_FlightSize_NonShooter", "Escort_Formation_Cruise", "Escort_Formation_Attack", "Escort_TransitThrottle", "Escort_StationThrottle", "Escort_TransitAltitude", "Escort_StationAltitude", "Escort_TransitTerrainFollowing", "Escort_AttackTerrainFollowing", "Escort_ResponseRadius", "Escort_GroupSize", "MinAircraftReq_Strikers", "MaxAircraftToFly_Strikers", "MinAircraftReq_Escorts_Shooter", "MaxAircraftToFly_Escort_Shooter", "MinAircraftReq_Escorts_NonShooter", "MaxAircraftToFly_Escort_NonShooter", "MinResponseRadius_Aircraft", "MaxResponseRadius_Aircraft", "MinResponseRadius_Ship", "MaxResponseRadius_Ship", "PrePlannedOnly", "OneTimeOnly", "OneTimeOnlyFlown", "RadarBehaviour", "AttackMethod", "SplitDistance", "UseFlightSizeHardLimit_Escort", "UseGroupSizeHardLimit_Escort", "Escort_NumberOfFlights_Investigate", "Escort_NumberOfFlights_Engage", "Escort_WingmanEngageDistance", "Escort_NumberOfBoats_Investigate", "Escort_NumberOfBoats_Engage", "Escort_GroupMemberEngageDistance")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_ESCORTS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICTARGETS_FIELD_NUMBER: _ClassVar[int]
    STARGNAME_FIELD_NUMBER: _ClassVar[int]
    MCSTT_FIELD_NUMBER: _ClassVar[int]
    UP_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    FORMATION_ATTACK_FIELD_NUMBER: _ClassVar[int]
    BINGO_FIELD_NUMBER: _ClassVar[int]
    TARGETEERINGMETHOD_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FLIGHTSIZE_SHOOTER_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FLIGHTSIZE_NONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FORMATION_ATTACK_FIELD_NUMBER: _ClassVar[int]
    ESCORT_TRANSITTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_STATIONTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_TRANSITALTITUDE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_STATIONALTITUDE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_TRANSITTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    ESCORT_ATTACKTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    ESCORT_RESPONSERADIUS_FIELD_NUMBER: _ClassVar[int]
    ESCORT_GROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_STRIKERS_FIELD_NUMBER: _ClassVar[int]
    MAXAIRCRAFTTOFLY_STRIKERS_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_ESCORTS_SHOOTER_FIELD_NUMBER: _ClassVar[int]
    MAXAIRCRAFTTOFLY_ESCORT_SHOOTER_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_ESCORTS_NONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    MAXAIRCRAFTTOFLY_ESCORT_NONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    MINRESPONSERADIUS_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    MAXRESPONSERADIUS_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    MINRESPONSERADIUS_SHIP_FIELD_NUMBER: _ClassVar[int]
    MAXRESPONSERADIUS_SHIP_FIELD_NUMBER: _ClassVar[int]
    PREPLANNEDONLY_FIELD_NUMBER: _ClassVar[int]
    ONETIMEONLY_FIELD_NUMBER: _ClassVar[int]
    ONETIMEONLYFLOWN_FIELD_NUMBER: _ClassVar[int]
    RADARBEHAVIOUR_FIELD_NUMBER: _ClassVar[int]
    ATTACKMETHOD_FIELD_NUMBER: _ClassVar[int]
    SPLITDISTANCE_FIELD_NUMBER: _ClassVar[int]
    USEFLIGHTSIZEHARDLIMIT_ESCORT_FIELD_NUMBER: _ClassVar[int]
    USEGROUPSIZEHARDLIMIT_ESCORT_FIELD_NUMBER: _ClassVar[int]
    ESCORT_NUMBEROFFLIGHTS_INVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_NUMBEROFFLIGHTS_ENGAGE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_WINGMANENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_NUMBEROFBOATS_INVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_NUMBEROFBOATS_ENGAGE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_GROUPMEMBERENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    Doctrine_Escorts: THDoctrine
    SpecificTargets: bytes
    STargName: bytes
    MCSTT: int
    UP: bool
    Formation_Cruise: int
    Formation_Attack: int
    Bingo: int
    TargeteeringMethod: int
    Escort_FlightSize_Shooter: int
    Escort_FlightSize_NonShooter: int
    Escort_Formation_Cruise: int
    Escort_Formation_Attack: int
    Escort_TransitThrottle: int
    Escort_StationThrottle: int
    Escort_TransitAltitude: float
    Escort_StationAltitude: float
    Escort_TransitTerrainFollowing: bool
    Escort_AttackTerrainFollowing: bool
    Escort_ResponseRadius: float
    Escort_GroupSize: int
    MinAircraftReq_Strikers: int
    MaxAircraftToFly_Strikers: int
    MinAircraftReq_Escorts_Shooter: int
    MaxAircraftToFly_Escort_Shooter: int
    MinAircraftReq_Escorts_NonShooter: int
    MaxAircraftToFly_Escort_NonShooter: int
    MinResponseRadius_Aircraft: float
    MaxResponseRadius_Aircraft: float
    MinResponseRadius_Ship: float
    MaxResponseRadius_Ship: float
    PrePlannedOnly: bool
    OneTimeOnly: bool
    OneTimeOnlyFlown: bool
    RadarBehaviour: int
    AttackMethod: int
    SplitDistance: int
    UseFlightSizeHardLimit_Escort: bool
    UseGroupSizeHardLimit_Escort: bool
    Escort_NumberOfFlights_Investigate: int
    Escort_NumberOfFlights_Engage: int
    Escort_WingmanEngageDistance: float
    Escort_NumberOfBoats_Investigate: int
    Escort_NumberOfBoats_Engage: int
    Escort_GroupMemberEngageDistance: float
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., Doctrine_Escorts: _Optional[_Union[THDoctrine, _Mapping]] = ..., SpecificTargets: _Optional[bytes] = ..., STargName: _Optional[bytes] = ..., MCSTT: _Optional[int] = ..., UP: bool = ..., Formation_Cruise: _Optional[int] = ..., Formation_Attack: _Optional[int] = ..., Bingo: _Optional[int] = ..., TargeteeringMethod: _Optional[int] = ..., Escort_FlightSize_Shooter: _Optional[int] = ..., Escort_FlightSize_NonShooter: _Optional[int] = ..., Escort_Formation_Cruise: _Optional[int] = ..., Escort_Formation_Attack: _Optional[int] = ..., Escort_TransitThrottle: _Optional[int] = ..., Escort_StationThrottle: _Optional[int] = ..., Escort_TransitAltitude: _Optional[float] = ..., Escort_StationAltitude: _Optional[float] = ..., Escort_TransitTerrainFollowing: bool = ..., Escort_AttackTerrainFollowing: bool = ..., Escort_ResponseRadius: _Optional[float] = ..., Escort_GroupSize: _Optional[int] = ..., MinAircraftReq_Strikers: _Optional[int] = ..., MaxAircraftToFly_Strikers: _Optional[int] = ..., MinAircraftReq_Escorts_Shooter: _Optional[int] = ..., MaxAircraftToFly_Escort_Shooter: _Optional[int] = ..., MinAircraftReq_Escorts_NonShooter: _Optional[int] = ..., MaxAircraftToFly_Escort_NonShooter: _Optional[int] = ..., MinResponseRadius_Aircraft: _Optional[float] = ..., MaxResponseRadius_Aircraft: _Optional[float] = ..., MinResponseRadius_Ship: _Optional[float] = ..., MaxResponseRadius_Ship: _Optional[float] = ..., PrePlannedOnly: bool = ..., OneTimeOnly: bool = ..., OneTimeOnlyFlown: bool = ..., RadarBehaviour: _Optional[int] = ..., AttackMethod: _Optional[int] = ..., SplitDistance: _Optional[int] = ..., UseFlightSizeHardLimit_Escort: bool = ..., UseGroupSizeHardLimit_Escort: bool = ..., Escort_NumberOfFlights_Investigate: _Optional[int] = ..., Escort_NumberOfFlights_Engage: _Optional[int] = ..., Escort_WingmanEngageDistance: _Optional[float] = ..., Escort_NumberOfBoats_Investigate: _Optional[int] = ..., Escort_NumberOfBoats_Engage: _Optional[int] = ..., Escort_GroupMemberEngageDistance: _Optional[float] = ...) -> None: ...

class THMissionCargo(_message.Message):
    __slots__ = ("Mission", "Type", "TransitThrottle_Aircraft", "StationThrottle_Aircraft", "TransitAltitude_Aircraft", "StationAltitude_Aircraft", "TransitThrottle_Ship", "StationThrottle_Ship", "Area", "MountsToUnload", "mapdel")
    class MountsToUnloadEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorInt
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorInt, _Mapping]] = ...) -> None: ...
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    MOUNTSTOUNLOAD_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    TransitThrottle_Aircraft: int
    StationThrottle_Aircraft: int
    TransitAltitude_Aircraft: float
    StationAltitude_Aircraft: float
    TransitThrottle_Ship: int
    StationThrottle_Ship: int
    Area: bytes
    MountsToUnload: _containers.ScalarMap[int, int]
    mapdel: _containers.MessageMap[str, THVectorInt]
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., TransitThrottle_Aircraft: _Optional[int] = ..., StationThrottle_Aircraft: _Optional[int] = ..., TransitAltitude_Aircraft: _Optional[float] = ..., StationAltitude_Aircraft: _Optional[float] = ..., TransitThrottle_Ship: _Optional[int] = ..., StationThrottle_Ship: _Optional[int] = ..., Area: _Optional[bytes] = ..., MountsToUnload: _Optional[_Mapping[int, int]] = ..., mapdel: _Optional[_Mapping[str, THVectorInt]] = ...) -> None: ...

class THMissionFerry(_message.Message):
    __slots__ = ("Mission", "Type", "NDH", "FerryThrottle_Aircraft", "FerryAltitude_Aircraft", "FerryTerrainFollowing_Aircraft", "FerryThrottle_Ship", "FerryThrottle_Submarine", "FerryAltitude_Submarine", "Formation_Cruise", "MinAircraftReq", "Behavior")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NDH_FIELD_NUMBER: _ClassVar[int]
    FERRYTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FERRYALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FERRYTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FERRYTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    FERRYTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    FERRYALTITUDE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    NDH: str
    FerryThrottle_Aircraft: int
    FerryAltitude_Aircraft: float
    FerryTerrainFollowing_Aircraft: bool
    FerryThrottle_Ship: int
    FerryThrottle_Submarine: int
    FerryAltitude_Submarine: float
    Formation_Cruise: int
    MinAircraftReq: float
    Behavior: int
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., NDH: _Optional[str] = ..., FerryThrottle_Aircraft: _Optional[int] = ..., FerryAltitude_Aircraft: _Optional[float] = ..., FerryTerrainFollowing_Aircraft: bool = ..., FerryThrottle_Ship: _Optional[int] = ..., FerryThrottle_Submarine: _Optional[int] = ..., FerryAltitude_Submarine: _Optional[float] = ..., Formation_Cruise: _Optional[int] = ..., MinAircraftReq: _Optional[float] = ..., Behavior: _Optional[int] = ...) -> None: ...

class THMissionSupport(_message.Message):
    __slots__ = ("Mission", "Type", "Area", "NLT", "OTR", "MNOS", "OTO", "AEOOS", "TransitThrottle_Aircraft", "StationThrottle_Aircraft", "TransitAltitude_Aircraft", "StationAltitude_Aircraft", "TransitTerrainFollowing_Aircraft", "StationTerrainFollowing_Aircraft", "TransitThrottle_Submarine", "StationThrottle_Submarine", "TransitDepth_Submarine", "StationDepth_Submarine", "TransitThrottle_Ship", "StationThrottle_Ship", "TransitThrottle_Facility", "StationThrottle_Facility", "Formation_Cruise", "A2AR_MaxNumberOfReceiversPerTanker", "A2AR_OneTankingCycleOnly", "MinAircraftReq", "ContinousCoverage_Enable", "ContinousCoverage_AllowQRA", "ContinousCoverage_FlightGenerationMethod", "ContinousCoverage_StationTime", "ContinousCoverage_Overlap", "ContinousCoverage_Duration", "CCSList", "QRAs", "ContinousCoverage_QRANumberOfFlights", "ContinousCoverage_QRAFlightGenerationMethod", "ContinousCoverage_NumberOfFlightsNeededToAllowQRA")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    NLT_FIELD_NUMBER: _ClassVar[int]
    OTR_FIELD_NUMBER: _ClassVar[int]
    MNOS_FIELD_NUMBER: _ClassVar[int]
    OTO_FIELD_NUMBER: _ClassVar[int]
    AEOOS_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    A2AR_MAXNUMBEROFRECEIVERSPERTANKER_FIELD_NUMBER: _ClassVar[int]
    A2AR_ONETANKINGCYCLEONLY_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_ENABLE_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_ALLOWQRA_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_FLIGHTGENERATIONMETHOD_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_STATIONTIME_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_OVERLAP_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_DURATION_FIELD_NUMBER: _ClassVar[int]
    CCSLIST_FIELD_NUMBER: _ClassVar[int]
    QRAS_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_QRANUMBEROFFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_QRAFLIGHTGENERATIONMETHOD_FIELD_NUMBER: _ClassVar[int]
    CONTINOUSCOVERAGE_NUMBEROFFLIGHTSNEEDEDTOALLOWQRA_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    Area: bytes
    NLT: int
    OTR: bool
    MNOS: int
    OTO: bool
    AEOOS: bool
    TransitThrottle_Aircraft: int
    StationThrottle_Aircraft: int
    TransitAltitude_Aircraft: float
    StationAltitude_Aircraft: float
    TransitTerrainFollowing_Aircraft: bool
    StationTerrainFollowing_Aircraft: bool
    TransitThrottle_Submarine: int
    StationThrottle_Submarine: int
    TransitDepth_Submarine: float
    StationDepth_Submarine: float
    TransitThrottle_Ship: int
    StationThrottle_Ship: int
    TransitThrottle_Facility: int
    StationThrottle_Facility: int
    Formation_Cruise: int
    A2AR_MaxNumberOfReceiversPerTanker: int
    A2AR_OneTankingCycleOnly: bool
    MinAircraftReq: int
    ContinousCoverage_Enable: bool
    ContinousCoverage_AllowQRA: bool
    ContinousCoverage_FlightGenerationMethod: int
    ContinousCoverage_StationTime: int
    ContinousCoverage_Overlap: int
    ContinousCoverage_Duration: int
    CCSList: bytes
    QRAs: bytes
    ContinousCoverage_QRANumberOfFlights: int
    ContinousCoverage_QRAFlightGenerationMethod: int
    ContinousCoverage_NumberOfFlightsNeededToAllowQRA: int
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., Area: _Optional[bytes] = ..., NLT: _Optional[int] = ..., OTR: bool = ..., MNOS: _Optional[int] = ..., OTO: bool = ..., AEOOS: bool = ..., TransitThrottle_Aircraft: _Optional[int] = ..., StationThrottle_Aircraft: _Optional[int] = ..., TransitAltitude_Aircraft: _Optional[float] = ..., StationAltitude_Aircraft: _Optional[float] = ..., TransitTerrainFollowing_Aircraft: bool = ..., StationTerrainFollowing_Aircraft: bool = ..., TransitThrottle_Submarine: _Optional[int] = ..., StationThrottle_Submarine: _Optional[int] = ..., TransitDepth_Submarine: _Optional[float] = ..., StationDepth_Submarine: _Optional[float] = ..., TransitThrottle_Ship: _Optional[int] = ..., StationThrottle_Ship: _Optional[int] = ..., TransitThrottle_Facility: _Optional[int] = ..., StationThrottle_Facility: _Optional[int] = ..., Formation_Cruise: _Optional[int] = ..., A2AR_MaxNumberOfReceiversPerTanker: _Optional[int] = ..., A2AR_OneTankingCycleOnly: bool = ..., MinAircraftReq: _Optional[int] = ..., ContinousCoverage_Enable: bool = ..., ContinousCoverage_AllowQRA: bool = ..., ContinousCoverage_FlightGenerationMethod: _Optional[int] = ..., ContinousCoverage_StationTime: _Optional[int] = ..., ContinousCoverage_Overlap: _Optional[int] = ..., ContinousCoverage_Duration: _Optional[int] = ..., CCSList: _Optional[bytes] = ..., QRAs: _Optional[bytes] = ..., ContinousCoverage_QRANumberOfFlights: _Optional[int] = ..., ContinousCoverage_QRAFlightGenerationMethod: _Optional[int] = ..., ContinousCoverage_NumberOfFlightsNeededToAllowQRA: _Optional[int] = ...) -> None: ...

class THMissionMineClearing(_message.Message):
    __slots__ = ("Mission", "Type", "Area", "OTR", "TransitThrottle_Aircraft", "StationThrottle_Aircraft", "TransitAltitude_Aircraft", "StationAltitude_Aircraft", "TransitTerrainFollowing_Aircraft", "StationTerrainFollowing_Aircraft", "TransitThrottle_Submarine", "StationThrottle_Submarine", "TransitDepth_Submarine", "StationDepth_Submarine", "TransitThrottle_Ship", "StationThrottle_Ship", "TransitThrottle_Facility", "StationThrottle_Facility", "Formation_Cruise", "Formation_Attack", "MinAircraftReq")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    OTR_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    FORMATION_ATTACK_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    Area: bytes
    OTR: bool
    TransitThrottle_Aircraft: int
    StationThrottle_Aircraft: int
    TransitAltitude_Aircraft: float
    StationAltitude_Aircraft: float
    TransitTerrainFollowing_Aircraft: bool
    StationTerrainFollowing_Aircraft: bool
    TransitThrottle_Submarine: int
    StationThrottle_Submarine: int
    TransitDepth_Submarine: float
    StationDepth_Submarine: float
    TransitThrottle_Ship: int
    StationThrottle_Ship: int
    TransitThrottle_Facility: int
    StationThrottle_Facility: int
    Formation_Cruise: int
    Formation_Attack: int
    MinAircraftReq: int
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., Area: _Optional[bytes] = ..., OTR: bool = ..., TransitThrottle_Aircraft: _Optional[int] = ..., StationThrottle_Aircraft: _Optional[int] = ..., TransitAltitude_Aircraft: _Optional[float] = ..., StationAltitude_Aircraft: _Optional[float] = ..., TransitTerrainFollowing_Aircraft: bool = ..., StationTerrainFollowing_Aircraft: bool = ..., TransitThrottle_Submarine: _Optional[int] = ..., StationThrottle_Submarine: _Optional[int] = ..., TransitDepth_Submarine: _Optional[float] = ..., StationDepth_Submarine: _Optional[float] = ..., TransitThrottle_Ship: _Optional[int] = ..., StationThrottle_Ship: _Optional[int] = ..., TransitThrottle_Facility: _Optional[int] = ..., StationThrottle_Facility: _Optional[int] = ..., Formation_Cruise: _Optional[int] = ..., Formation_Attack: _Optional[int] = ..., MinAircraftReq: _Optional[int] = ...) -> None: ...

class THMissionMining(_message.Message):
    __slots__ = ("Mission", "Type", "Area", "OTR", "TransitThrottle_Aircraft", "StationThrottle_Aircraft", "TransitAltitude_Aircraft", "StationAltitude_Aircraft", "TransitTerrainFollowing_Aircraft", "StationTerrainFollowing_Aircraft", "TransitThrottle_Submarine", "StationThrottle_Submarine", "TransitDepth_Submarine", "StationDepth_Submarine", "TransitThrottle_Ship", "StationThrottle_Ship", "TransitThrottle_Facility", "StationThrottle_Facility", "Formation_Cruise", "AD", "MinAircraftReq")
    MISSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    OTR_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    STATIONTERRAINFOLLOWING_AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    STATIONDEPTH_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_SHIP_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FACILITY_FIELD_NUMBER: _ClassVar[int]
    FORMATION_CRUISE_FIELD_NUMBER: _ClassVar[int]
    AD_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    Type: int
    Area: bytes
    OTR: bool
    TransitThrottle_Aircraft: int
    StationThrottle_Aircraft: int
    TransitAltitude_Aircraft: float
    StationAltitude_Aircraft: float
    TransitTerrainFollowing_Aircraft: bool
    StationTerrainFollowing_Aircraft: bool
    TransitThrottle_Submarine: int
    StationThrottle_Submarine: int
    TransitDepth_Submarine: float
    StationDepth_Submarine: float
    TransitThrottle_Ship: int
    StationThrottle_Ship: int
    TransitThrottle_Facility: int
    StationThrottle_Facility: int
    Formation_Cruise: int
    AD: int
    MinAircraftReq: int
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ..., Type: _Optional[int] = ..., Area: _Optional[bytes] = ..., OTR: bool = ..., TransitThrottle_Aircraft: _Optional[int] = ..., StationThrottle_Aircraft: _Optional[int] = ..., TransitAltitude_Aircraft: _Optional[float] = ..., StationAltitude_Aircraft: _Optional[float] = ..., TransitTerrainFollowing_Aircraft: bool = ..., StationTerrainFollowing_Aircraft: bool = ..., TransitThrottle_Submarine: _Optional[int] = ..., StationThrottle_Submarine: _Optional[int] = ..., TransitDepth_Submarine: _Optional[float] = ..., StationDepth_Submarine: _Optional[float] = ..., TransitThrottle_Ship: _Optional[int] = ..., StationThrottle_Ship: _Optional[int] = ..., TransitThrottle_Facility: _Optional[int] = ..., StationThrottle_Facility: _Optional[int] = ..., Formation_Cruise: _Optional[int] = ..., AD: _Optional[int] = ..., MinAircraftReq: _Optional[int] = ...) -> None: ...

class THMissionCustom(_message.Message):
    __slots__ = ("Mission",)
    MISSION_FIELD_NUMBER: _ClassVar[int]
    Mission: THMission
    def __init__(self, Mission: _Optional[_Union[THMission, _Mapping]] = ...) -> None: ...

class THMission(_message.Message):
    __slots__ = ("ID", "Name", "Category", "Status", "START", "END", "Doctrine", "TakeOffTime", "TimeOnTarget", "SISIH", "UseFlightplan", "UseFlightplansOnly", "IncludeInATO", "TankerUsage", "TankerMissionList", "FlightSize", "GroupSize", "GroupName", "Deactivation_UnassignUnits", "CheckBox_OrderRTB", "CheckBox_DeleteMission", "LaunchMissionWithoutTankersInPlace", "TankerMinNumber_Total", "TankerMinNumber_Airborne", "TankerMinNumber_Station", "MaxReceiversInQueuePerTanker_Airborne", "FuelQtyToStartLookingForTanker_Airborne", "TankerMaxDistance_Airborne", "TankerFollowsReceivers", "UseFlightSizeHardLimit", "UseGroupSizeHardLimit", "Flight", "EmptySlotsList", "ListNavigation1", "ListNavigation2", "ListNavigation3", "CreateTime", "mapdel")
    class FlightEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THFlight
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THFlight, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_FIELD_NUMBER: _ClassVar[int]
    TAKEOFFTIME_FIELD_NUMBER: _ClassVar[int]
    TIMEONTARGET_FIELD_NUMBER: _ClassVar[int]
    SISIH_FIELD_NUMBER: _ClassVar[int]
    USEFLIGHTPLAN_FIELD_NUMBER: _ClassVar[int]
    USEFLIGHTPLANSONLY_FIELD_NUMBER: _ClassVar[int]
    INCLUDEINATO_FIELD_NUMBER: _ClassVar[int]
    TANKERUSAGE_FIELD_NUMBER: _ClassVar[int]
    TANKERMISSIONLIST_FIELD_NUMBER: _ClassVar[int]
    FLIGHTSIZE_FIELD_NUMBER: _ClassVar[int]
    GROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATION_UNASSIGNUNITS_FIELD_NUMBER: _ClassVar[int]
    CHECKBOX_ORDERRTB_FIELD_NUMBER: _ClassVar[int]
    CHECKBOX_DELETEMISSION_FIELD_NUMBER: _ClassVar[int]
    LAUNCHMISSIONWITHOUTTANKERSINPLACE_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBER_TOTAL_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBER_AIRBORNE_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBER_STATION_FIELD_NUMBER: _ClassVar[int]
    MAXRECEIVERSINQUEUEPERTANKER_AIRBORNE_FIELD_NUMBER: _ClassVar[int]
    FUELQTYTOSTARTLOOKINGFORTANKER_AIRBORNE_FIELD_NUMBER: _ClassVar[int]
    TANKERMAXDISTANCE_AIRBORNE_FIELD_NUMBER: _ClassVar[int]
    TANKERFOLLOWSRECEIVERS_FIELD_NUMBER: _ClassVar[int]
    USEFLIGHTSIZEHARDLIMIT_FIELD_NUMBER: _ClassVar[int]
    USEGROUPSIZEHARDLIMIT_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_FIELD_NUMBER: _ClassVar[int]
    EMPTYSLOTSLIST_FIELD_NUMBER: _ClassVar[int]
    LISTNAVIGATION1_FIELD_NUMBER: _ClassVar[int]
    LISTNAVIGATION2_FIELD_NUMBER: _ClassVar[int]
    LISTNAVIGATION3_FIELD_NUMBER: _ClassVar[int]
    CREATETIME_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Category: int
    Status: int
    START: int
    END: int
    Doctrine: THDoctrine
    TakeOffTime: int
    TimeOnTarget: int
    SISIH: bool
    UseFlightplan: bool
    UseFlightplansOnly: bool
    IncludeInATO: bool
    TankerUsage: int
    TankerMissionList: bytes
    FlightSize: int
    GroupSize: int
    GroupName: str
    Deactivation_UnassignUnits: bool
    CheckBox_OrderRTB: bool
    CheckBox_DeleteMission: bool
    LaunchMissionWithoutTankersInPlace: bool
    TankerMinNumber_Total: int
    TankerMinNumber_Airborne: int
    TankerMinNumber_Station: int
    MaxReceiversInQueuePerTanker_Airborne: int
    FuelQtyToStartLookingForTanker_Airborne: int
    TankerMaxDistance_Airborne: int
    TankerFollowsReceivers: bool
    UseFlightSizeHardLimit: bool
    UseGroupSizeHardLimit: bool
    Flight: _containers.MessageMap[str, THFlight]
    EmptySlotsList: bytes
    ListNavigation1: bytes
    ListNavigation2: bytes
    ListNavigation3: bytes
    CreateTime: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Category: _Optional[int] = ..., Status: _Optional[int] = ..., START: _Optional[int] = ..., END: _Optional[int] = ..., Doctrine: _Optional[_Union[THDoctrine, _Mapping]] = ..., TakeOffTime: _Optional[int] = ..., TimeOnTarget: _Optional[int] = ..., SISIH: bool = ..., UseFlightplan: bool = ..., UseFlightplansOnly: bool = ..., IncludeInATO: bool = ..., TankerUsage: _Optional[int] = ..., TankerMissionList: _Optional[bytes] = ..., FlightSize: _Optional[int] = ..., GroupSize: _Optional[int] = ..., GroupName: _Optional[str] = ..., Deactivation_UnassignUnits: bool = ..., CheckBox_OrderRTB: bool = ..., CheckBox_DeleteMission: bool = ..., LaunchMissionWithoutTankersInPlace: bool = ..., TankerMinNumber_Total: _Optional[int] = ..., TankerMinNumber_Airborne: _Optional[int] = ..., TankerMinNumber_Station: _Optional[int] = ..., MaxReceiversInQueuePerTanker_Airborne: _Optional[int] = ..., FuelQtyToStartLookingForTanker_Airborne: _Optional[int] = ..., TankerMaxDistance_Airborne: _Optional[int] = ..., TankerFollowsReceivers: bool = ..., UseFlightSizeHardLimit: bool = ..., UseGroupSizeHardLimit: bool = ..., Flight: _Optional[_Mapping[str, THFlight]] = ..., EmptySlotsList: _Optional[bytes] = ..., ListNavigation1: _Optional[bytes] = ..., ListNavigation2: _Optional[bytes] = ..., ListNavigation3: _Optional[bytes] = ..., CreateTime: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THFlight(_message.Message):
    __slots__ = ("ID", "ParentMissionOrPackageObjectID", "ParentMissionOrPackageName", "Callsign", "Task", "Type", "TakeOffLocation_HostUnitObjectID", "TakeOffLocation_HostUnitObjectName", "LandingLocation_HostUnitObjectID", "LandingLocation_HostUnitObjectName", "AlternativeLandingLocation_HostUnitObjectID", "AlternativeLandingLocation_HostUnitObjectName", "EarliestTaskingTime", "LatestTaskingTime", "EarliestLaunchTime", "LatestLaunchTime", "MaxReadyTime", "Priority", "Status", "CreatedBy", "EditedBy", "DesiredAircraftQty", "MinimumAircraftQty", "AssignedAircraftQty", "ReadyAircraftQty", "ReferenceUnit_DBID", "ReferenceUnit_ObjectID", "ReferenceUnit_Name", "LoadoutDBID", "LoadoutName", "UsedByFlight", "IsEscort", "TaskPool_ID", "PrimaryTarget_ID", "TaskPool_Name", "Age", "FlightPlan", "ErrorList", "NotificationList", "HasCriticalError")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENTMISSIONORPACKAGEOBJECTID_FIELD_NUMBER: _ClassVar[int]
    PARENTMISSIONORPACKAGENAME_FIELD_NUMBER: _ClassVar[int]
    CALLSIGN_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TAKEOFFLOCATION_HOSTUNITOBJECTID_FIELD_NUMBER: _ClassVar[int]
    TAKEOFFLOCATION_HOSTUNITOBJECTNAME_FIELD_NUMBER: _ClassVar[int]
    LANDINGLOCATION_HOSTUNITOBJECTID_FIELD_NUMBER: _ClassVar[int]
    LANDINGLOCATION_HOSTUNITOBJECTNAME_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVELANDINGLOCATION_HOSTUNITOBJECTID_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVELANDINGLOCATION_HOSTUNITOBJECTNAME_FIELD_NUMBER: _ClassVar[int]
    EARLIESTTASKINGTIME_FIELD_NUMBER: _ClassVar[int]
    LATESTTASKINGTIME_FIELD_NUMBER: _ClassVar[int]
    EARLIESTLAUNCHTIME_FIELD_NUMBER: _ClassVar[int]
    LATESTLAUNCHTIME_FIELD_NUMBER: _ClassVar[int]
    MAXREADYTIME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATEDBY_FIELD_NUMBER: _ClassVar[int]
    EDITEDBY_FIELD_NUMBER: _ClassVar[int]
    DESIREDAIRCRAFTQTY_FIELD_NUMBER: _ClassVar[int]
    MINIMUMAIRCRAFTQTY_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEDAIRCRAFTQTY_FIELD_NUMBER: _ClassVar[int]
    READYAIRCRAFTQTY_FIELD_NUMBER: _ClassVar[int]
    REFERENCEUNIT_DBID_FIELD_NUMBER: _ClassVar[int]
    REFERENCEUNIT_OBJECTID_FIELD_NUMBER: _ClassVar[int]
    REFERENCEUNIT_NAME_FIELD_NUMBER: _ClassVar[int]
    LOADOUTDBID_FIELD_NUMBER: _ClassVar[int]
    LOADOUTNAME_FIELD_NUMBER: _ClassVar[int]
    USEDBYFLIGHT_FIELD_NUMBER: _ClassVar[int]
    ISESCORT_FIELD_NUMBER: _ClassVar[int]
    TASKPOOL_ID_FIELD_NUMBER: _ClassVar[int]
    PRIMARYTARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TASKPOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    FLIGHTPLAN_FIELD_NUMBER: _ClassVar[int]
    ERRORLIST_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATIONLIST_FIELD_NUMBER: _ClassVar[int]
    HASCRITICALERROR_FIELD_NUMBER: _ClassVar[int]
    ID: str
    ParentMissionOrPackageObjectID: str
    ParentMissionOrPackageName: str
    Callsign: str
    Task: int
    Type: int
    TakeOffLocation_HostUnitObjectID: str
    TakeOffLocation_HostUnitObjectName: str
    LandingLocation_HostUnitObjectID: str
    LandingLocation_HostUnitObjectName: str
    AlternativeLandingLocation_HostUnitObjectID: str
    AlternativeLandingLocation_HostUnitObjectName: str
    EarliestTaskingTime: int
    LatestTaskingTime: int
    EarliestLaunchTime: int
    LatestLaunchTime: int
    MaxReadyTime: float
    Priority: int
    Status: int
    CreatedBy: int
    EditedBy: int
    DesiredAircraftQty: int
    MinimumAircraftQty: int
    AssignedAircraftQty: int
    ReadyAircraftQty: int
    ReferenceUnit_DBID: int
    ReferenceUnit_ObjectID: str
    ReferenceUnit_Name: str
    LoadoutDBID: int
    LoadoutName: str
    UsedByFlight: bool
    IsEscort: bool
    TaskPool_ID: str
    PrimaryTarget_ID: str
    TaskPool_Name: str
    Age: int
    FlightPlan: bytes
    ErrorList: bytes
    NotificationList: bytes
    HasCriticalError: bool
    def __init__(self, ID: _Optional[str] = ..., ParentMissionOrPackageObjectID: _Optional[str] = ..., ParentMissionOrPackageName: _Optional[str] = ..., Callsign: _Optional[str] = ..., Task: _Optional[int] = ..., Type: _Optional[int] = ..., TakeOffLocation_HostUnitObjectID: _Optional[str] = ..., TakeOffLocation_HostUnitObjectName: _Optional[str] = ..., LandingLocation_HostUnitObjectID: _Optional[str] = ..., LandingLocation_HostUnitObjectName: _Optional[str] = ..., AlternativeLandingLocation_HostUnitObjectID: _Optional[str] = ..., AlternativeLandingLocation_HostUnitObjectName: _Optional[str] = ..., EarliestTaskingTime: _Optional[int] = ..., LatestTaskingTime: _Optional[int] = ..., EarliestLaunchTime: _Optional[int] = ..., LatestLaunchTime: _Optional[int] = ..., MaxReadyTime: _Optional[float] = ..., Priority: _Optional[int] = ..., Status: _Optional[int] = ..., CreatedBy: _Optional[int] = ..., EditedBy: _Optional[int] = ..., DesiredAircraftQty: _Optional[int] = ..., MinimumAircraftQty: _Optional[int] = ..., AssignedAircraftQty: _Optional[int] = ..., ReadyAircraftQty: _Optional[int] = ..., ReferenceUnit_DBID: _Optional[int] = ..., ReferenceUnit_ObjectID: _Optional[str] = ..., ReferenceUnit_Name: _Optional[str] = ..., LoadoutDBID: _Optional[int] = ..., LoadoutName: _Optional[str] = ..., UsedByFlight: bool = ..., IsEscort: bool = ..., TaskPool_ID: _Optional[str] = ..., PrimaryTarget_ID: _Optional[str] = ..., TaskPool_Name: _Optional[str] = ..., Age: _Optional[int] = ..., FlightPlan: _Optional[bytes] = ..., ErrorList: _Optional[bytes] = ..., NotificationList: _Optional[bytes] = ..., HasCriticalError: bool = ...) -> None: ...

class THEmptySlot(_message.Message):
    __slots__ = ("DBID", "UnitClass", "LoadoutDBID", "LoadoutName", "Loadout_ExcludeOptionalWeapons", "Loadout_QuickTurnaround", "Loadout_QuickTurnaround_NumberOfSorties", "Loadout_QuickTurnaround_MaxSorties", "CurrentHostUnit_ObjectID", "CurrentHostUnit_Name", "IsEscort", "MissionFlight_ObjectID")
    DBID_FIELD_NUMBER: _ClassVar[int]
    UNITCLASS_FIELD_NUMBER: _ClassVar[int]
    LOADOUTDBID_FIELD_NUMBER: _ClassVar[int]
    LOADOUTNAME_FIELD_NUMBER: _ClassVar[int]
    LOADOUT_EXCLUDEOPTIONALWEAPONS_FIELD_NUMBER: _ClassVar[int]
    LOADOUT_QUICKTURNAROUND_FIELD_NUMBER: _ClassVar[int]
    LOADOUT_QUICKTURNAROUND_NUMBEROFSORTIES_FIELD_NUMBER: _ClassVar[int]
    LOADOUT_QUICKTURNAROUND_MAXSORTIES_FIELD_NUMBER: _ClassVar[int]
    CURRENTHOSTUNIT_OBJECTID_FIELD_NUMBER: _ClassVar[int]
    CURRENTHOSTUNIT_NAME_FIELD_NUMBER: _ClassVar[int]
    ISESCORT_FIELD_NUMBER: _ClassVar[int]
    MISSIONFLIGHT_OBJECTID_FIELD_NUMBER: _ClassVar[int]
    DBID: int
    UnitClass: str
    LoadoutDBID: int
    LoadoutName: str
    Loadout_ExcludeOptionalWeapons: bool
    Loadout_QuickTurnaround: bool
    Loadout_QuickTurnaround_NumberOfSorties: int
    Loadout_QuickTurnaround_MaxSorties: int
    CurrentHostUnit_ObjectID: str
    CurrentHostUnit_Name: str
    IsEscort: bool
    MissionFlight_ObjectID: str
    def __init__(self, DBID: _Optional[int] = ..., UnitClass: _Optional[str] = ..., LoadoutDBID: _Optional[int] = ..., LoadoutName: _Optional[str] = ..., Loadout_ExcludeOptionalWeapons: bool = ..., Loadout_QuickTurnaround: bool = ..., Loadout_QuickTurnaround_NumberOfSorties: _Optional[int] = ..., Loadout_QuickTurnaround_MaxSorties: _Optional[int] = ..., CurrentHostUnit_ObjectID: _Optional[str] = ..., CurrentHostUnit_Name: _Optional[str] = ..., IsEscort: bool = ..., MissionFlight_ObjectID: _Optional[str] = ...) -> None: ...

class THEventColl(_message.Message):
    __slots__ = ("EventTriggers", "EventConditions", "EventActions", "SimEvents", "mapdel")
    class SimEventsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THSimEvent
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THSimEvent, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    EVENTTRIGGERS_FIELD_NUMBER: _ClassVar[int]
    EVENTCONDITIONS_FIELD_NUMBER: _ClassVar[int]
    EVENTACTIONS_FIELD_NUMBER: _ClassVar[int]
    SIMEVENTS_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    EventTriggers: THEventTriggerColl
    EventConditions: THEventConditionColl
    EventActions: THEventActionColl
    SimEvents: _containers.MessageMap[str, THSimEvent]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, EventTriggers: _Optional[_Union[THEventTriggerColl, _Mapping]] = ..., EventConditions: _Optional[_Union[THEventConditionColl, _Mapping]] = ..., EventActions: _Optional[_Union[THEventActionColl, _Mapping]] = ..., SimEvents: _Optional[_Mapping[str, THSimEvent]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THEventTriggerColl(_message.Message):
    __slots__ = ("EventTrigger_UnitDestroyed", "EventTrigger_UnitDamaged", "EventTrigger_Points", "EventTrigger_Time", "EventTrigger_UnitRemainsInArea", "EventTrigger_UnitEntersArea", "EventTrigger_RandomTime", "EventTrigger_UnitDetected", "EventTrigger_ScenLoaded", "EventTrigger_RegularTime", "EventTrigger_ScenEnded", "mapdel")
    class EventTriggerUnitDestroyedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_UnitDestroyed
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_UnitDestroyed, _Mapping]] = ...) -> None: ...
    class EventTriggerUnitDamagedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_UnitDamaged
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_UnitDamaged, _Mapping]] = ...) -> None: ...
    class EventTriggerPointsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_Points
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_Points, _Mapping]] = ...) -> None: ...
    class EventTriggerTimeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_Time
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_Time, _Mapping]] = ...) -> None: ...
    class EventTriggerUnitRemainsInAreaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_UnitRemainsInArea
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_UnitRemainsInArea, _Mapping]] = ...) -> None: ...
    class EventTriggerUnitEntersAreaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_UnitEntersArea
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_UnitEntersArea, _Mapping]] = ...) -> None: ...
    class EventTriggerRandomTimeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_RandomTime
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_RandomTime, _Mapping]] = ...) -> None: ...
    class EventTriggerUnitDetectedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_UnitDetected
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_UnitDetected, _Mapping]] = ...) -> None: ...
    class EventTriggerScenLoadedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_ScenLoaded
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_ScenLoaded, _Mapping]] = ...) -> None: ...
    class EventTriggerRegularTimeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_RegularTime
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_RegularTime, _Mapping]] = ...) -> None: ...
    class EventTriggerScenEndedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventTrigger_ScenEnded
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventTrigger_ScenEnded, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    EVENTTRIGGER_UNITDESTROYED_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_UNITDAMAGED_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_POINTS_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_TIME_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_UNITREMAINSINAREA_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_UNITENTERSAREA_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_RANDOMTIME_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_UNITDETECTED_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_SCENLOADED_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_REGULARTIME_FIELD_NUMBER: _ClassVar[int]
    EVENTTRIGGER_SCENENDED_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    EventTrigger_UnitDestroyed: _containers.MessageMap[str, THEventTrigger_UnitDestroyed]
    EventTrigger_UnitDamaged: _containers.MessageMap[str, THEventTrigger_UnitDamaged]
    EventTrigger_Points: _containers.MessageMap[str, THEventTrigger_Points]
    EventTrigger_Time: _containers.MessageMap[str, THEventTrigger_Time]
    EventTrigger_UnitRemainsInArea: _containers.MessageMap[str, THEventTrigger_UnitRemainsInArea]
    EventTrigger_UnitEntersArea: _containers.MessageMap[str, THEventTrigger_UnitEntersArea]
    EventTrigger_RandomTime: _containers.MessageMap[str, THEventTrigger_RandomTime]
    EventTrigger_UnitDetected: _containers.MessageMap[str, THEventTrigger_UnitDetected]
    EventTrigger_ScenLoaded: _containers.MessageMap[str, THEventTrigger_ScenLoaded]
    EventTrigger_RegularTime: _containers.MessageMap[str, THEventTrigger_RegularTime]
    EventTrigger_ScenEnded: _containers.MessageMap[str, THEventTrigger_ScenEnded]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, EventTrigger_UnitDestroyed: _Optional[_Mapping[str, THEventTrigger_UnitDestroyed]] = ..., EventTrigger_UnitDamaged: _Optional[_Mapping[str, THEventTrigger_UnitDamaged]] = ..., EventTrigger_Points: _Optional[_Mapping[str, THEventTrigger_Points]] = ..., EventTrigger_Time: _Optional[_Mapping[str, THEventTrigger_Time]] = ..., EventTrigger_UnitRemainsInArea: _Optional[_Mapping[str, THEventTrigger_UnitRemainsInArea]] = ..., EventTrigger_UnitEntersArea: _Optional[_Mapping[str, THEventTrigger_UnitEntersArea]] = ..., EventTrigger_RandomTime: _Optional[_Mapping[str, THEventTrigger_RandomTime]] = ..., EventTrigger_UnitDetected: _Optional[_Mapping[str, THEventTrigger_UnitDetected]] = ..., EventTrigger_ScenLoaded: _Optional[_Mapping[str, THEventTrigger_ScenLoaded]] = ..., EventTrigger_RegularTime: _Optional[_Mapping[str, THEventTrigger_RegularTime]] = ..., EventTrigger_ScenEnded: _Optional[_Mapping[str, THEventTrigger_ScenEnded]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THEventConditionColl(_message.Message):
    __slots__ = ("EventCondition_SidePosture", "EventCondition_ScenHasStarted", "EventCondition_LuaScript", "mapdel")
    class EventConditionSidePostureEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventCondition_SidePosture
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventCondition_SidePosture, _Mapping]] = ...) -> None: ...
    class EventConditionScenHasStartedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventCondition_ScenHasStarted
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventCondition_ScenHasStarted, _Mapping]] = ...) -> None: ...
    class EventConditionLuaScriptEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventCondition_LuaScript
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventCondition_LuaScript, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    EVENTCONDITION_SIDEPOSTURE_FIELD_NUMBER: _ClassVar[int]
    EVENTCONDITION_SCENHASSTARTED_FIELD_NUMBER: _ClassVar[int]
    EVENTCONDITION_LUASCRIPT_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    EventCondition_SidePosture: _containers.MessageMap[str, THEventCondition_SidePosture]
    EventCondition_ScenHasStarted: _containers.MessageMap[str, THEventCondition_ScenHasStarted]
    EventCondition_LuaScript: _containers.MessageMap[str, THEventCondition_LuaScript]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, EventCondition_SidePosture: _Optional[_Mapping[str, THEventCondition_SidePosture]] = ..., EventCondition_ScenHasStarted: _Optional[_Mapping[str, THEventCondition_ScenHasStarted]] = ..., EventCondition_LuaScript: _Optional[_Mapping[str, THEventCondition_LuaScript]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THEventActionColl(_message.Message):
    __slots__ = ("EventAction_Points", "EventAction_EndScenario", "EventAction_TeleportInArea", "EventAction_Message", "EventAction_ChangeMissionStatus", "EventAction_LuaScript", "mapdel")
    class EventActionPointsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_Points
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_Points, _Mapping]] = ...) -> None: ...
    class EventActionEndScenarioEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_EndScenario
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_EndScenario, _Mapping]] = ...) -> None: ...
    class EventActionTeleportInAreaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_TeleportInArea
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_TeleportInArea, _Mapping]] = ...) -> None: ...
    class EventActionMessageEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_Message
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_Message, _Mapping]] = ...) -> None: ...
    class EventActionChangeMissionStatusEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_ChangeMissionStatus
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_ChangeMissionStatus, _Mapping]] = ...) -> None: ...
    class EventActionLuaScriptEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventAction_LuaScript
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventAction_LuaScript, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    EVENTACTION_POINTS_FIELD_NUMBER: _ClassVar[int]
    EVENTACTION_ENDSCENARIO_FIELD_NUMBER: _ClassVar[int]
    EVENTACTION_TELEPORTINAREA_FIELD_NUMBER: _ClassVar[int]
    EVENTACTION_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EVENTACTION_CHANGEMISSIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    EVENTACTION_LUASCRIPT_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    EventAction_Points: _containers.MessageMap[str, THEventAction_Points]
    EventAction_EndScenario: _containers.MessageMap[str, THEventAction_EndScenario]
    EventAction_TeleportInArea: _containers.MessageMap[str, THEventAction_TeleportInArea]
    EventAction_Message: _containers.MessageMap[str, THEventAction_Message]
    EventAction_ChangeMissionStatus: _containers.MessageMap[str, THEventAction_ChangeMissionStatus]
    EventAction_LuaScript: _containers.MessageMap[str, THEventAction_LuaScript]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, EventAction_Points: _Optional[_Mapping[str, THEventAction_Points]] = ..., EventAction_EndScenario: _Optional[_Mapping[str, THEventAction_EndScenario]] = ..., EventAction_TeleportInArea: _Optional[_Mapping[str, THEventAction_TeleportInArea]] = ..., EventAction_Message: _Optional[_Mapping[str, THEventAction_Message]] = ..., EventAction_ChangeMissionStatus: _Optional[_Mapping[str, THEventAction_ChangeMissionStatus]] = ..., EventAction_LuaScript: _Optional[_Mapping[str, THEventAction_LuaScript]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSimEvent(_message.Message):
    __slots__ = ("ID", "Description", "IsRepeatable", "IsActive", "IsShown", "Probability", "Triggers", "Conditions", "Actions", "IsTrigger", "mapdel")
    class TriggersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ConditionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ActionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ISREPEATABLE_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    ISSHOWN_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    ISTRIGGER_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    IsRepeatable: bool
    IsActive: bool
    IsShown: bool
    Probability: int
    Triggers: _containers.ScalarMap[str, str]
    Conditions: _containers.ScalarMap[str, str]
    Actions: _containers.ScalarMap[str, str]
    IsTrigger: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., IsRepeatable: bool = ..., IsActive: bool = ..., IsShown: bool = ..., Probability: _Optional[int] = ..., Triggers: _Optional[_Mapping[str, str]] = ..., Conditions: _Optional[_Mapping[str, str]] = ..., Actions: _Optional[_Mapping[str, str]] = ..., IsTrigger: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THEventTrigger_UnitDestroyed(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ...) -> None: ...

class THTargetFilter(_message.Message):
    __slots__ = ("ID", "TargetSide", "TargetType", "TargetSubType", "SpecificUnitClass", "SpecificUnitID", "WeaponSide", "WeaponID")
    ID_FIELD_NUMBER: _ClassVar[int]
    TARGETSIDE_FIELD_NUMBER: _ClassVar[int]
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETSUBTYPE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICUNITID_FIELD_NUMBER: _ClassVar[int]
    WEAPONSIDE_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    ID: str
    TargetSide: str
    TargetType: int
    TargetSubType: int
    SpecificUnitClass: int
    SpecificUnitID: str
    WeaponSide: str
    WeaponID: str
    def __init__(self, ID: _Optional[str] = ..., TargetSide: _Optional[str] = ..., TargetType: _Optional[int] = ..., TargetSubType: _Optional[int] = ..., SpecificUnitClass: _Optional[int] = ..., SpecificUnitID: _Optional[str] = ..., WeaponSide: _Optional[str] = ..., WeaponID: _Optional[str] = ...) -> None: ...

class THEventTrigger_UnitDamaged(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter", "DamagePercent")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    DAMAGEPERCENT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    DamagePercent: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ..., DamagePercent: _Optional[int] = ...) -> None: ...

class THEventTrigger_Points(_message.Message):
    __slots__ = ("ID", "Description", "SideID", "PointValue", "ReachDirection")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    POINTVALUE_FIELD_NUMBER: _ClassVar[int]
    REACHDIRECTION_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    SideID: str
    PointValue: int
    ReachDirection: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., SideID: _Optional[str] = ..., PointValue: _Optional[int] = ..., ReachDirection: _Optional[int] = ...) -> None: ...

class THEventTrigger_Time(_message.Message):
    __slots__ = ("ID", "Description", "Time")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Time: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Time: _Optional[int] = ...) -> None: ...

class THEventTrigger_UnitRemainsInArea(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter", "Area", "TD", "TA")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    TD_FIELD_NUMBER: _ClassVar[int]
    TA_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    Area: bytes
    TD: int
    TA: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ..., Area: _Optional[bytes] = ..., TD: _Optional[int] = ..., TA: _Optional[int] = ...) -> None: ...

class THEventTrigger_UnitEntersArea(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter", "Area", "ETOA", "LTOA", "ExitArea")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    ETOA_FIELD_NUMBER: _ClassVar[int]
    LTOA_FIELD_NUMBER: _ClassVar[int]
    EXITAREA_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    Area: bytes
    ETOA: int
    LTOA: int
    ExitArea: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ..., Area: _Optional[bytes] = ..., ETOA: _Optional[int] = ..., LTOA: _Optional[int] = ..., ExitArea: _Optional[int] = ...) -> None: ...

class THEventTrigger_RandomTime(_message.Message):
    __slots__ = ("ID", "Description", "EarliestTime", "LatestTime")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EARLIESTTIME_FIELD_NUMBER: _ClassVar[int]
    LATESTTIME_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    EarliestTime: int
    LatestTime: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., EarliestTime: _Optional[int] = ..., LatestTime: _Optional[int] = ...) -> None: ...

class THEventTrigger_UnitDetected(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter", "Area", "DetectorSideID", "MCL")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    DETECTORSIDEID_FIELD_NUMBER: _ClassVar[int]
    MCL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    Area: bytes
    DetectorSideID: str
    MCL: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ..., Area: _Optional[bytes] = ..., DetectorSideID: _Optional[str] = ..., MCL: _Optional[int] = ...) -> None: ...

class THEventTrigger_ScenLoaded(_message.Message):
    __slots__ = ("ID", "Description")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ...) -> None: ...

class THEventTrigger_RegularTime(_message.Message):
    __slots__ = ("ID", "Description", "Interval")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Interval: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Interval: _Optional[int] = ...) -> None: ...

class THEventTrigger_ScenEnded(_message.Message):
    __slots__ = ("ID", "Description")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ...) -> None: ...

class THEventTrigger_UnitExpend(_message.Message):
    __slots__ = ("ID", "Description", "TargetFilter")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TARGETFILTER_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    TargetFilter: THTargetFilter
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., TargetFilter: _Optional[_Union[THTargetFilter, _Mapping]] = ...) -> None: ...

class THEventCondition_SidePosture(_message.Message):
    __slots__ = ("ID", "Description", "ObserverSideID", "TargetSideID", "TargetPosture", "NOT")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OBSERVERSIDEID_FIELD_NUMBER: _ClassVar[int]
    TARGETSIDEID_FIELD_NUMBER: _ClassVar[int]
    TARGETPOSTURE_FIELD_NUMBER: _ClassVar[int]
    NOT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    ObserverSideID: str
    TargetSideID: str
    TargetPosture: int
    NOT: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., ObserverSideID: _Optional[str] = ..., TargetSideID: _Optional[str] = ..., TargetPosture: _Optional[int] = ..., NOT: _Optional[int] = ...) -> None: ...

class THEventCondition_ScenHasStarted(_message.Message):
    __slots__ = ("ID", "Description", "NOT")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NOT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    NOT: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., NOT: _Optional[int] = ...) -> None: ...

class THEventCondition_LuaScript(_message.Message):
    __slots__ = ("ID", "Description", "ScriptText")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    ScriptText: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., ScriptText: _Optional[str] = ...) -> None: ...

class THEventAction_Points(_message.Message):
    __slots__ = ("ID", "Description", "SideID", "PointChange")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    POINTCHANGE_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    SideID: str
    PointChange: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., SideID: _Optional[str] = ..., PointChange: _Optional[int] = ...) -> None: ...

class THEventAction_EndScenario(_message.Message):
    __slots__ = ("ID", "Description")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ...) -> None: ...

class THEventAction_TeleportInArea(_message.Message):
    __slots__ = ("ID", "Description", "UnitIDs", "Area")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    UNITIDS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    UnitIDs: bytes
    Area: bytes
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., UnitIDs: _Optional[bytes] = ..., Area: _Optional[bytes] = ...) -> None: ...

class THEventAction_Message(_message.Message):
    __slots__ = ("ID", "Description", "SideID", "UnitID", "Text")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    SideID: str
    UnitID: str
    Text: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., SideID: _Optional[str] = ..., UnitID: _Optional[str] = ..., Text: _Optional[str] = ...) -> None: ...

class THEventAction_ChangeMissionStatus(_message.Message):
    __slots__ = ("ID", "Description", "MissionID", "NewStatus")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MISSIONID_FIELD_NUMBER: _ClassVar[int]
    NEWSTATUS_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    MissionID: str
    NewStatus: int
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., MissionID: _Optional[str] = ..., NewStatus: _Optional[int] = ...) -> None: ...

class THEventAction_LuaScript(_message.Message):
    __slots__ = ("ID", "Description", "ScriptText")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    ScriptText: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., ScriptText: _Optional[str] = ...) -> None: ...

class THExclusionZone(_message.Message):
    __slots__ = ("ID", "Description", "Area", "AffectedUnitTypes", "MarkViolatorAs", "IsActive", "Alt")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDUNITTYPES_FIELD_NUMBER: _ClassVar[int]
    MARKVIOLATORAS_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Area: bytes
    AffectedUnitTypes: str
    MarkViolatorAs: int
    IsActive: bool
    Alt: float
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Area: _Optional[bytes] = ..., AffectedUnitTypes: _Optional[str] = ..., MarkViolatorAs: _Optional[int] = ..., IsActive: bool = ..., Alt: _Optional[float] = ...) -> None: ...

class THNoNavZone(_message.Message):
    __slots__ = ("ID", "Description", "Area", "AffectedUnitTypes", "IsLocked", "IsActive", "Alt")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDUNITTYPES_FIELD_NUMBER: _ClassVar[int]
    ISLOCKED_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Area: bytes
    AffectedUnitTypes: str
    IsLocked: bool
    IsActive: bool
    Alt: float
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Area: _Optional[bytes] = ..., AffectedUnitTypes: _Optional[str] = ..., IsLocked: bool = ..., IsActive: bool = ..., Alt: _Optional[float] = ...) -> None: ...

class THAirCorridorZone(_message.Message):
    __slots__ = ("ID", "Description", "Area", "AffectedUnitTypes", "IsActive", "Diameter", "Alt")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    AFFECTEDUNITTYPES_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Area: bytes
    AffectedUnitTypes: str
    IsActive: bool
    Diameter: float
    Alt: float
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Area: _Optional[bytes] = ..., AffectedUnitTypes: _Optional[str] = ..., IsActive: bool = ..., Diameter: _Optional[float] = ..., Alt: _Optional[float] = ...) -> None: ...

class THSpecialAction(_message.Message):
    __slots__ = ("ID", "Description", "Name", "IsRepeatable", "IsActive", "ScriptText")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ISREPEATABLE_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Description: str
    Name: str
    IsRepeatable: bool
    IsActive: bool
    ScriptText: str
    def __init__(self, ID: _Optional[str] = ..., Description: _Optional[str] = ..., Name: _Optional[str] = ..., IsRepeatable: bool = ..., IsActive: bool = ..., ScriptText: _Optional[str] = ...) -> None: ...

class THNonActiveUnitColl(_message.Message):
    __slots__ = ("Explosions", "WeaponImpacts", "UnguidedWeapons", "ChaffClouds", "mapdel")
    class ExplosionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THExplosion
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THExplosion, _Mapping]] = ...) -> None: ...
    class WeaponImpactsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponImpact
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponImpact, _Mapping]] = ...) -> None: ...
    class UnguidedWeaponsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnguidedWeapon
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnguidedWeapon, _Mapping]] = ...) -> None: ...
    class ChaffCloudsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THChaffCloud
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THChaffCloud, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    EXPLOSIONS_FIELD_NUMBER: _ClassVar[int]
    WEAPONIMPACTS_FIELD_NUMBER: _ClassVar[int]
    UNGUIDEDWEAPONS_FIELD_NUMBER: _ClassVar[int]
    CHAFFCLOUDS_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Explosions: _containers.MessageMap[str, THExplosion]
    WeaponImpacts: _containers.MessageMap[str, THWeaponImpact]
    UnguidedWeapons: _containers.MessageMap[str, THUnguidedWeapon]
    ChaffClouds: _containers.MessageMap[str, THChaffCloud]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Explosions: _Optional[_Mapping[str, THExplosion]] = ..., WeaponImpacts: _Optional[_Mapping[str, THWeaponImpact]] = ..., UnguidedWeapons: _Optional[_Mapping[str, THUnguidedWeapon]] = ..., ChaffClouds: _Optional[_Mapping[str, THChaffCloud]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THExplosion(_message.Message):
    __slots__ = ("ID", "Name", "Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Pitch", "Roll", "CurrentSpeed", "Lon_Graphics", "Lat_Graphics", "Yield", "Yield_Graphics", "TTL", "WarheadType", "WeaponType", "ExpType", "ExcludedUnit")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    ROLL_FIELD_NUMBER: _ClassVar[int]
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    LON_GRAPHICS_FIELD_NUMBER: _ClassVar[int]
    LAT_GRAPHICS_FIELD_NUMBER: _ClassVar[int]
    YIELD_FIELD_NUMBER: _ClassVar[int]
    YIELD_GRAPHICS_FIELD_NUMBER: _ClassVar[int]
    TTL_FIELD_NUMBER: _ClassVar[int]
    WARHEADTYPE_FIELD_NUMBER: _ClassVar[int]
    WEAPONTYPE_FIELD_NUMBER: _ClassVar[int]
    EXPTYPE_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEDUNIT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Pitch: float
    Roll: float
    CurrentSpeed: float
    Lon_Graphics: float
    Lat_Graphics: float
    Yield: float
    Yield_Graphics: float
    TTL: float
    WarheadType: int
    WeaponType: int
    ExpType: int
    ExcludedUnit: str
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Pitch: _Optional[float] = ..., Roll: _Optional[float] = ..., CurrentSpeed: _Optional[float] = ..., Lon_Graphics: _Optional[float] = ..., Lat_Graphics: _Optional[float] = ..., Yield: _Optional[float] = ..., Yield_Graphics: _Optional[float] = ..., TTL: _Optional[float] = ..., WarheadType: _Optional[int] = ..., WeaponType: _Optional[int] = ..., ExpType: _Optional[int] = ..., ExcludedUnit: _Optional[str] = ...) -> None: ...

class THWeaponImpact(_message.Message):
    __slots__ = ("ID", "Longitude", "Latitude", "CurrentAltitude", "Type", "Age", "message")
    ID_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Longitude: float
    Latitude: float
    CurrentAltitude: float
    Type: int
    Age: float
    message: str
    def __init__(self, ID: _Optional[str] = ..., Longitude: _Optional[float] = ..., Latitude: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., Type: _Optional[int] = ..., Age: _Optional[float] = ..., message: _Optional[str] = ...) -> None: ...

class THUnguidedWeapon(_message.Message):
    __slots__ = ("ID", "Name", "Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Pitch", "Roll", "CurrentSpeed", "side", "DBID", "ImpactAltitude", "CEP_Surface", "CEP_Land", "Target", "TimeToLive", "TimeToDetonate", "LaunchPoint", "FiringParent")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    ROLL_FIELD_NUMBER: _ClassVar[int]
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    IMPACTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CEP_SURFACE_FIELD_NUMBER: _ClassVar[int]
    CEP_LAND_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    TIMETOLIVE_FIELD_NUMBER: _ClassVar[int]
    TIMETODETONATE_FIELD_NUMBER: _ClassVar[int]
    LAUNCHPOINT_FIELD_NUMBER: _ClassVar[int]
    FIRINGPARENT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Pitch: float
    Roll: float
    CurrentSpeed: float
    side: str
    DBID: int
    ImpactAltitude: float
    CEP_Surface: float
    CEP_Land: float
    Target: str
    TimeToLive: float
    TimeToDetonate: float
    LaunchPoint: THGeoPoint
    FiringParent: str
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Pitch: _Optional[float] = ..., Roll: _Optional[float] = ..., CurrentSpeed: _Optional[float] = ..., side: _Optional[str] = ..., DBID: _Optional[int] = ..., ImpactAltitude: _Optional[float] = ..., CEP_Surface: _Optional[float] = ..., CEP_Land: _Optional[float] = ..., Target: _Optional[str] = ..., TimeToLive: _Optional[float] = ..., TimeToDetonate: _Optional[float] = ..., LaunchPoint: _Optional[_Union[THGeoPoint, _Mapping]] = ..., FiringParent: _Optional[str] = ...) -> None: ...

class THChaffCloud(_message.Message):
    __slots__ = ("ID", "Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Age")
    ID_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Age: float
    def __init__(self, ID: _Optional[str] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Age: _Optional[float] = ...) -> None: ...

class THWeatherProfile(_message.Message):
    __slots__ = ("Temp", "Pressure", "RL", "GRC", "DN", "SDH", "EDH", "RFR", "FUR", "SS", "EC", "ECB", "EE", "EEB")
    TEMP_FIELD_NUMBER: _ClassVar[int]
    PRESSURE_FIELD_NUMBER: _ClassVar[int]
    RL_FIELD_NUMBER: _ClassVar[int]
    GRC_FIELD_NUMBER: _ClassVar[int]
    DN_FIELD_NUMBER: _ClassVar[int]
    SDH_FIELD_NUMBER: _ClassVar[int]
    EDH_FIELD_NUMBER: _ClassVar[int]
    RFR_FIELD_NUMBER: _ClassVar[int]
    FUR_FIELD_NUMBER: _ClassVar[int]
    SS_FIELD_NUMBER: _ClassVar[int]
    EC_FIELD_NUMBER: _ClassVar[int]
    ECB_FIELD_NUMBER: _ClassVar[int]
    EE_FIELD_NUMBER: _ClassVar[int]
    EEB_FIELD_NUMBER: _ClassVar[int]
    Temp: float
    Pressure: float
    RL: float
    GRC: float
    DN: float
    SDH: float
    EDH: float
    RFR: float
    FUR: float
    SS: int
    EC: int
    ECB: int
    EE: int
    EEB: int
    def __init__(self, Temp: _Optional[float] = ..., Pressure: _Optional[float] = ..., RL: _Optional[float] = ..., GRC: _Optional[float] = ..., DN: _Optional[float] = ..., SDH: _Optional[float] = ..., EDH: _Optional[float] = ..., RFR: _Optional[float] = ..., FUR: _Optional[float] = ..., SS: _Optional[int] = ..., EC: _Optional[int] = ..., ECB: _Optional[int] = ..., EE: _Optional[int] = ..., EEB: _Optional[int] = ...) -> None: ...

class THFeatureOption(_message.Message):
    __slots__ = ("DetailedGunFireControl", "UnlimitedBaseMags", "AircraftDamage", "CommsJamming", "CommsDisruption", "RealisticSubComms", "LandTypeEffects", "WeatherAffectsShipSpeed")
    DETAILEDGUNFIRECONTROL_FIELD_NUMBER: _ClassVar[int]
    UNLIMITEDBASEMAGS_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTDAMAGE_FIELD_NUMBER: _ClassVar[int]
    COMMSJAMMING_FIELD_NUMBER: _ClassVar[int]
    COMMSDISRUPTION_FIELD_NUMBER: _ClassVar[int]
    REALISTICSUBCOMMS_FIELD_NUMBER: _ClassVar[int]
    LANDTYPEEFFECTS_FIELD_NUMBER: _ClassVar[int]
    WEATHERAFFECTSSHIPSPEED_FIELD_NUMBER: _ClassVar[int]
    DetailedGunFireControl: bool
    UnlimitedBaseMags: bool
    AircraftDamage: bool
    CommsJamming: bool
    CommsDisruption: bool
    RealisticSubComms: bool
    LandTypeEffects: bool
    WeatherAffectsShipSpeed: bool
    def __init__(self, DetailedGunFireControl: bool = ..., UnlimitedBaseMags: bool = ..., AircraftDamage: bool = ..., CommsJamming: bool = ..., CommsDisruption: bool = ..., RealisticSubComms: bool = ..., LandTypeEffects: bool = ..., WeatherAffectsShipSpeed: bool = ...) -> None: ...

class THTargetingEntry(_message.Message):
    __slots__ = ("ID", "ActualUnitID", "BHVR")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    BHVR_FIELD_NUMBER: _ClassVar[int]
    ID: str
    ActualUnitID: str
    BHVR: int
    def __init__(self, ID: _Optional[str] = ..., ActualUnitID: _Optional[str] = ..., BHVR: _Optional[int] = ...) -> None: ...

class THAI(_message.Message):
    __slots__ = ("AltitudePreset", "PTOE", "FCLIO", "ET_E", "DPT_E", "IE", "HPos", "TargetList", "PrimaryTarget", "PrimaryTarget_Type", "mapdel")
    class TargetListEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THTargetingEntry
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THTargetingEntry, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ALTITUDEPRESET_FIELD_NUMBER: _ClassVar[int]
    PTOE_FIELD_NUMBER: _ClassVar[int]
    FCLIO_FIELD_NUMBER: _ClassVar[int]
    ET_E_FIELD_NUMBER: _ClassVar[int]
    DPT_E_FIELD_NUMBER: _ClassVar[int]
    IE_FIELD_NUMBER: _ClassVar[int]
    HPOS_FIELD_NUMBER: _ClassVar[int]
    TARGETLIST_FIELD_NUMBER: _ClassVar[int]
    PRIMARYTARGET_FIELD_NUMBER: _ClassVar[int]
    PRIMARYTARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    AltitudePreset: int
    PTOE: bool
    FCLIO: bool
    ET_E: bool
    DPT_E: bool
    IE: bool
    HPos: bool
    TargetList: _containers.MessageMap[str, THTargetingEntry]
    PrimaryTarget: str
    PrimaryTarget_Type: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, AltitudePreset: _Optional[int] = ..., PTOE: bool = ..., FCLIO: bool = ..., ET_E: bool = ..., DPT_E: bool = ..., IE: bool = ..., HPos: bool = ..., TargetList: _Optional[_Mapping[str, THTargetingEntry]] = ..., PrimaryTarget: _Optional[str] = ..., PrimaryTarget_Type: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THWaypoint(_message.Message):
    __slots__ = ("GeoPoint", "Type", "Category", "ThrottlePreset", "AltitudePreset", "DepthPreset", "TurnRate", "Hold_Time", "Station_Time", "Description")
    GEOPOINT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    THROTTLEPRESET_FIELD_NUMBER: _ClassVar[int]
    ALTITUDEPRESET_FIELD_NUMBER: _ClassVar[int]
    DEPTHPRESET_FIELD_NUMBER: _ClassVar[int]
    TURNRATE_FIELD_NUMBER: _ClassVar[int]
    HOLD_TIME_FIELD_NUMBER: _ClassVar[int]
    STATION_TIME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GeoPoint: THGeoPoint
    Type: int
    Category: int
    ThrottlePreset: int
    AltitudePreset: int
    DepthPreset: int
    TurnRate: int
    Hold_Time: float
    Station_Time: float
    Description: str
    def __init__(self, GeoPoint: _Optional[_Union[THGeoPoint, _Mapping]] = ..., Type: _Optional[int] = ..., Category: _Optional[int] = ..., ThrottlePreset: _Optional[int] = ..., AltitudePreset: _Optional[int] = ..., DepthPreset: _Optional[int] = ..., TurnRate: _Optional[int] = ..., Hold_Time: _Optional[float] = ..., Station_Time: _Optional[float] = ..., Description: _Optional[str] = ...) -> None: ...

class THWeaponAssignments(_message.Message):
    __slots__ = ("ID", "Weapon", "Quantity", "Target", "ScheduledFireTime", "PlottedCourse", "ManualFire")
    ID_FIELD_NUMBER: _ClassVar[int]
    WEAPON_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    SCHEDULEDFIRETIME_FIELD_NUMBER: _ClassVar[int]
    PLOTTEDCOURSE_FIELD_NUMBER: _ClassVar[int]
    MANUALFIRE_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Weapon: int
    Quantity: int
    Target: str
    ScheduledFireTime: int
    PlottedCourse: bytes
    ManualFire: bool
    def __init__(self, ID: _Optional[str] = ..., Weapon: _Optional[int] = ..., Quantity: _Optional[int] = ..., Target: _Optional[str] = ..., ScheduledFireTime: _Optional[int] = ..., PlottedCourse: _Optional[bytes] = ..., ManualFire: bool = ...) -> None: ...

class THWeaponry(_message.Message):
    __slots__ = ("WeaponAssignments", "LCS", "IDLZ")
    WEAPONASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    LCS_FIELD_NUMBER: _ClassVar[int]
    IDLZ_FIELD_NUMBER: _ClassVar[int]
    WeaponAssignments: THWeaponAssignments
    LCS: bool
    IDLZ: bool
    def __init__(self, WeaponAssignments: _Optional[_Union[THWeaponAssignments, _Mapping]] = ..., LCS: bool = ..., IDLZ: bool = ...) -> None: ...

class THKinematics(_message.Message):
    __slots__ = ("AMV", "DOA", "ReserveFuel", "SP", "SADC", "bDSO", "Cavitation")
    AMV_FIELD_NUMBER: _ClassVar[int]
    DOA_FIELD_NUMBER: _ClassVar[int]
    RESERVEFUEL_FIELD_NUMBER: _ClassVar[int]
    SP_FIELD_NUMBER: _ClassVar[int]
    SADC_FIELD_NUMBER: _ClassVar[int]
    BDSO_FIELD_NUMBER: _ClassVar[int]
    CAVITATION_FIELD_NUMBER: _ClassVar[int]
    AMV: int
    DOA: bool
    ReserveFuel: float
    SP: int
    SADC: int
    bDSO: bool
    Cavitation: str
    def __init__(self, AMV: _Optional[int] = ..., DOA: bool = ..., ReserveFuel: _Optional[float] = ..., SP: _Optional[int] = ..., SADC: _Optional[int] = ..., bDSO: bool = ..., Cavitation: _Optional[str] = ...) -> None: ...

class THNavigator(_message.Message):
    __slots__ = ("PC", "AvoidCavitation", "SprintDrift", "StationPoint")
    PC_FIELD_NUMBER: _ClassVar[int]
    AVOIDCAVITATION_FIELD_NUMBER: _ClassVar[int]
    SPRINTDRIFT_FIELD_NUMBER: _ClassVar[int]
    STATIONPOINT_FIELD_NUMBER: _ClassVar[int]
    PC: bytes
    AvoidCavitation: bool
    SprintDrift: bool
    StationPoint: THPoint
    def __init__(self, PC: _Optional[bytes] = ..., AvoidCavitation: bool = ..., SprintDrift: bool = ..., StationPoint: _Optional[_Union[THPoint, _Mapping]] = ...) -> None: ...

class THSensory(_message.Message):
    __slots__ = ("ObE", "ContactEntry", "JammerHas")
    OBE_FIELD_NUMBER: _ClassVar[int]
    CONTACTENTRY_FIELD_NUMBER: _ClassVar[int]
    JAMMERHAS_FIELD_NUMBER: _ClassVar[int]
    ObE: bool
    ContactEntry: str
    JammerHas: bool
    def __init__(self, ObE: bool = ..., ContactEntry: _Optional[str] = ..., JammerHas: bool = ...) -> None: ...

class THDamage(_message.Message):
    __slots__ = ("Fire", "Flood", "TTNSDC")
    FIRE_FIELD_NUMBER: _ClassVar[int]
    FLOOD_FIELD_NUMBER: _ClassVar[int]
    TTNSDC_FIELD_NUMBER: _ClassVar[int]
    Fire: int
    Flood: int
    TTNSDC: float
    def __init__(self, Fire: _Optional[int] = ..., Flood: _Optional[int] = ..., TTNSDC: _Optional[float] = ...) -> None: ...

class THCommStuff(_message.Message):
    __slots__ = ("OOC", "ICS", "HBS")
    OOC_FIELD_NUMBER: _ClassVar[int]
    ICS_FIELD_NUMBER: _ClassVar[int]
    HBS_FIELD_NUMBER: _ClassVar[int]
    OOC: bool
    ICS: bool
    HBS: bool
    def __init__(self, OOC: bool = ..., ICS: bool = ..., HBS: bool = ...) -> None: ...

class THWRA(_message.Message):
    __slots__ = ("WeaponQty", "ShooterQty", "SelfDefenceRange", "FiringRange")
    WEAPONQTY_FIELD_NUMBER: _ClassVar[int]
    SHOOTERQTY_FIELD_NUMBER: _ClassVar[int]
    SELFDEFENCERANGE_FIELD_NUMBER: _ClassVar[int]
    FIRINGRANGE_FIELD_NUMBER: _ClassVar[int]
    WeaponQty: int
    ShooterQty: int
    SelfDefenceRange: int
    FiringRange: int
    def __init__(self, WeaponQty: _Optional[int] = ..., ShooterQty: _Optional[int] = ..., SelfDefenceRange: _Optional[int] = ..., FiringRange: _Optional[int] = ...) -> None: ...

class THCCS(_message.Message):
    __slots__ = ("FlightObjectID", "AircraftDBID", "LoadoutDBID", "HostUnitObjectID", "StationStartTime", "StationEndTime", "FlightplanTemplateObjectID")
    FLIGHTOBJECTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTDBID_FIELD_NUMBER: _ClassVar[int]
    LOADOUTDBID_FIELD_NUMBER: _ClassVar[int]
    HOSTUNITOBJECTID_FIELD_NUMBER: _ClassVar[int]
    STATIONSTARTTIME_FIELD_NUMBER: _ClassVar[int]
    STATIONENDTIME_FIELD_NUMBER: _ClassVar[int]
    FLIGHTPLANTEMPLATEOBJECTID_FIELD_NUMBER: _ClassVar[int]
    FlightObjectID: str
    AircraftDBID: int
    LoadoutDBID: int
    HostUnitObjectID: str
    StationStartTime: int
    StationEndTime: int
    FlightplanTemplateObjectID: str
    def __init__(self, FlightObjectID: _Optional[str] = ..., AircraftDBID: _Optional[int] = ..., LoadoutDBID: _Optional[int] = ..., HostUnitObjectID: _Optional[str] = ..., StationStartTime: _Optional[int] = ..., StationEndTime: _Optional[int] = ..., FlightplanTemplateObjectID: _Optional[str] = ...) -> None: ...

class THPoint(_message.Message):
    __slots__ = ("Lon", "Lat")
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    Lon: float
    Lat: float
    def __init__(self, Lon: _Optional[float] = ..., Lat: _Optional[float] = ...) -> None: ...

class THGeoPoint(_message.Message):
    __slots__ = ("ID", "Name", "Lon", "Lat", "Alt")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Lon: float
    Lat: float
    Alt: float
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., Alt: _Optional[float] = ...) -> None: ...

class THRefPoint(_message.Message):
    __slots__ = ("OriType", "OriUnitID", "ID", "Name", "Lon", "Lat", "Alt")
    ORITYPE_FIELD_NUMBER: _ClassVar[int]
    ORIUNITID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    OriType: int
    OriUnitID: str
    ID: str
    Name: str
    Lon: float
    Lat: float
    Alt: float
    def __init__(self, OriType: _Optional[int] = ..., OriUnitID: _Optional[str] = ..., ID: _Optional[str] = ..., Name: _Optional[str] = ..., Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., Alt: _Optional[float] = ...) -> None: ...

class THPosition(_message.Message):
    __slots__ = ("Lon", "Lat", "CurrentAltitude", "CurrentHeading", "Pitch", "Roll")
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    CURRENTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CURRENTHEADING_FIELD_NUMBER: _ClassVar[int]
    PITCH_FIELD_NUMBER: _ClassVar[int]
    ROLL_FIELD_NUMBER: _ClassVar[int]
    Lon: float
    Lat: float
    CurrentAltitude: float
    CurrentHeading: float
    Pitch: float
    Roll: float
    def __init__(self, Lon: _Optional[float] = ..., Lat: _Optional[float] = ..., CurrentAltitude: _Optional[float] = ..., CurrentHeading: _Optional[float] = ..., Pitch: _Optional[float] = ..., Roll: _Optional[float] = ...) -> None: ...

class THMapWRA(_message.Message):
    __slots__ = ("v", "mapdel")
    class VEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWRA
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWRA, _Mapping]] = ...) -> None: ...
    V_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    v: _containers.MessageMap[str, THWRA]
    mapdel: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, v: _Optional[_Mapping[str, THWRA]] = ..., mapdel: _Optional[_Iterable[str]] = ...) -> None: ...

class THDoctrine(_message.Message):
    __slots__ = ("Nukes", "WCS_Air", "WCS_Surface", "WCS_Submarine", "WCS_Land", "IPCWA", "WinchesterShotgunRTB", "BingoJokerRTB", "JettisonOrdnance", "BVRLogic", "BTAT", "AE", "MS", "GS", "UR", "RS", "ST", "SAM_ASUW", "QuickTurnAround", "AirOpsTempo", "BingoJoker", "WinchesterShotgun", "IgnoreEMCONUnderAttack", "UseTorpedoesKinematicRange", "RefuelAllies", "AvoidContact", "DiveWhenThreatsDetected", "RechargePercentagePatrol", "RechargePercentageAttack", "AIPUsage", "DippingSonar", "SurfNav", "SubNav", "LandNav", "E_Radar", "E_Sonar", "E_OECM", "WithdrawDamageThreshold", "WithdrawFuelThreshold", "WithdrawAttackThreshold", "WithdrawDefenceThreshold", "RedeployDamageThreshold", "RedeployFuelThreshold", "RedeployAttackThreshold", "RedeployDefenceThreshold", "BitAuthority", "BitInherit", "WRA", "mapdel")
    class WRAEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THMapWRA
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THMapWRA, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    NUKES_FIELD_NUMBER: _ClassVar[int]
    WCS_AIR_FIELD_NUMBER: _ClassVar[int]
    WCS_SURFACE_FIELD_NUMBER: _ClassVar[int]
    WCS_SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    WCS_LAND_FIELD_NUMBER: _ClassVar[int]
    IPCWA_FIELD_NUMBER: _ClassVar[int]
    WINCHESTERSHOTGUNRTB_FIELD_NUMBER: _ClassVar[int]
    BINGOJOKERRTB_FIELD_NUMBER: _ClassVar[int]
    JETTISONORDNANCE_FIELD_NUMBER: _ClassVar[int]
    BVRLOGIC_FIELD_NUMBER: _ClassVar[int]
    BTAT_FIELD_NUMBER: _ClassVar[int]
    AE_FIELD_NUMBER: _ClassVar[int]
    MS_FIELD_NUMBER: _ClassVar[int]
    GS_FIELD_NUMBER: _ClassVar[int]
    UR_FIELD_NUMBER: _ClassVar[int]
    RS_FIELD_NUMBER: _ClassVar[int]
    ST_FIELD_NUMBER: _ClassVar[int]
    SAM_ASUW_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_FIELD_NUMBER: _ClassVar[int]
    AIROPSTEMPO_FIELD_NUMBER: _ClassVar[int]
    BINGOJOKER_FIELD_NUMBER: _ClassVar[int]
    WINCHESTERSHOTGUN_FIELD_NUMBER: _ClassVar[int]
    IGNOREEMCONUNDERATTACK_FIELD_NUMBER: _ClassVar[int]
    USETORPEDOESKINEMATICRANGE_FIELD_NUMBER: _ClassVar[int]
    REFUELALLIES_FIELD_NUMBER: _ClassVar[int]
    AVOIDCONTACT_FIELD_NUMBER: _ClassVar[int]
    DIVEWHENTHREATSDETECTED_FIELD_NUMBER: _ClassVar[int]
    RECHARGEPERCENTAGEPATROL_FIELD_NUMBER: _ClassVar[int]
    RECHARGEPERCENTAGEATTACK_FIELD_NUMBER: _ClassVar[int]
    AIPUSAGE_FIELD_NUMBER: _ClassVar[int]
    DIPPINGSONAR_FIELD_NUMBER: _ClassVar[int]
    SURFNAV_FIELD_NUMBER: _ClassVar[int]
    SUBNAV_FIELD_NUMBER: _ClassVar[int]
    LANDNAV_FIELD_NUMBER: _ClassVar[int]
    E_RADAR_FIELD_NUMBER: _ClassVar[int]
    E_SONAR_FIELD_NUMBER: _ClassVar[int]
    E_OECM_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWDAMAGETHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWFUELTHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWATTACKTHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWDEFENCETHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDEPLOYDAMAGETHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDEPLOYFUELTHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDEPLOYATTACKTHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDEPLOYDEFENCETHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    BITAUTHORITY_FIELD_NUMBER: _ClassVar[int]
    BITINHERIT_FIELD_NUMBER: _ClassVar[int]
    WRA_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Nukes: int
    WCS_Air: int
    WCS_Surface: int
    WCS_Submarine: int
    WCS_Land: int
    IPCWA: int
    WinchesterShotgunRTB: int
    BingoJokerRTB: int
    JettisonOrdnance: int
    BVRLogic: int
    BTAT: int
    AE: int
    MS: int
    GS: int
    UR: int
    RS: int
    ST: int
    SAM_ASUW: int
    QuickTurnAround: int
    AirOpsTempo: int
    BingoJoker: int
    WinchesterShotgun: int
    IgnoreEMCONUnderAttack: int
    UseTorpedoesKinematicRange: int
    RefuelAllies: int
    AvoidContact: int
    DiveWhenThreatsDetected: int
    RechargePercentagePatrol: int
    RechargePercentageAttack: int
    AIPUsage: int
    DippingSonar: int
    SurfNav: int
    SubNav: int
    LandNav: int
    E_Radar: int
    E_Sonar: int
    E_OECM: int
    WithdrawDamageThreshold: int
    WithdrawFuelThreshold: int
    WithdrawAttackThreshold: int
    WithdrawDefenceThreshold: int
    RedeployDamageThreshold: int
    RedeployFuelThreshold: int
    RedeployAttackThreshold: int
    RedeployDefenceThreshold: int
    BitAuthority: int
    BitInherit: int
    WRA: _containers.MessageMap[str, THMapWRA]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Nukes: _Optional[int] = ..., WCS_Air: _Optional[int] = ..., WCS_Surface: _Optional[int] = ..., WCS_Submarine: _Optional[int] = ..., WCS_Land: _Optional[int] = ..., IPCWA: _Optional[int] = ..., WinchesterShotgunRTB: _Optional[int] = ..., BingoJokerRTB: _Optional[int] = ..., JettisonOrdnance: _Optional[int] = ..., BVRLogic: _Optional[int] = ..., BTAT: _Optional[int] = ..., AE: _Optional[int] = ..., MS: _Optional[int] = ..., GS: _Optional[int] = ..., UR: _Optional[int] = ..., RS: _Optional[int] = ..., ST: _Optional[int] = ..., SAM_ASUW: _Optional[int] = ..., QuickTurnAround: _Optional[int] = ..., AirOpsTempo: _Optional[int] = ..., BingoJoker: _Optional[int] = ..., WinchesterShotgun: _Optional[int] = ..., IgnoreEMCONUnderAttack: _Optional[int] = ..., UseTorpedoesKinematicRange: _Optional[int] = ..., RefuelAllies: _Optional[int] = ..., AvoidContact: _Optional[int] = ..., DiveWhenThreatsDetected: _Optional[int] = ..., RechargePercentagePatrol: _Optional[int] = ..., RechargePercentageAttack: _Optional[int] = ..., AIPUsage: _Optional[int] = ..., DippingSonar: _Optional[int] = ..., SurfNav: _Optional[int] = ..., SubNav: _Optional[int] = ..., LandNav: _Optional[int] = ..., E_Radar: _Optional[int] = ..., E_Sonar: _Optional[int] = ..., E_OECM: _Optional[int] = ..., WithdrawDamageThreshold: _Optional[int] = ..., WithdrawFuelThreshold: _Optional[int] = ..., WithdrawAttackThreshold: _Optional[int] = ..., WithdrawDefenceThreshold: _Optional[int] = ..., RedeployDamageThreshold: _Optional[int] = ..., RedeployFuelThreshold: _Optional[int] = ..., RedeployAttackThreshold: _Optional[int] = ..., RedeployDefenceThreshold: _Optional[int] = ..., BitAuthority: _Optional[int] = ..., BitInherit: _Optional[int] = ..., WRA: _Optional[_Mapping[str, THMapWRA]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THWarhead(_message.Message):
    __slots__ = ("DBID", "DP", "Type", "ExpType", "Cal", "NOW", "CBDAL", "CBDAW")
    DBID_FIELD_NUMBER: _ClassVar[int]
    DP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPTYPE_FIELD_NUMBER: _ClassVar[int]
    CAL_FIELD_NUMBER: _ClassVar[int]
    NOW_FIELD_NUMBER: _ClassVar[int]
    CBDAL_FIELD_NUMBER: _ClassVar[int]
    CBDAW_FIELD_NUMBER: _ClassVar[int]
    DBID: int
    DP: float
    Type: int
    ExpType: int
    Cal: int
    NOW: int
    CBDAL: int
    CBDAW: int
    def __init__(self, DBID: _Optional[int] = ..., DP: _Optional[float] = ..., Type: _Optional[int] = ..., ExpType: _Optional[int] = ..., Cal: _Optional[int] = ..., NOW: _Optional[int] = ..., CBDAL: _Optional[int] = ..., CBDAW: _Optional[int] = ...) -> None: ...

class THWeaponRec(_message.Message):
    __slots__ = ("Name", "DefaultLoad", "CurrentLoad", "MaxLoad", "ROF", "OW", "IW", "Multiple", "WeaponDBID", "TimeToFire", "IsTank", "FuelTank", "AirRangeMax", "AirRangeMin", "SurfaceRangeMax", "SurfaceRangeMin", "LandRangeMax", "LandRangeMin", "SubsurfaceRangeMax", "SubsurfaceRangeMin", "Warheads", "Guidance", "mapdel")
    class WarheadsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWarhead
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWarhead, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULTLOAD_FIELD_NUMBER: _ClassVar[int]
    CURRENTLOAD_FIELD_NUMBER: _ClassVar[int]
    MAXLOAD_FIELD_NUMBER: _ClassVar[int]
    ROF_FIELD_NUMBER: _ClassVar[int]
    OW_FIELD_NUMBER: _ClassVar[int]
    IW_FIELD_NUMBER: _ClassVar[int]
    MULTIPLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    TIMETOFIRE_FIELD_NUMBER: _ClassVar[int]
    ISTANK_FIELD_NUMBER: _ClassVar[int]
    FUELTANK_FIELD_NUMBER: _ClassVar[int]
    AIRRANGEMAX_FIELD_NUMBER: _ClassVar[int]
    AIRRANGEMIN_FIELD_NUMBER: _ClassVar[int]
    SURFACERANGEMAX_FIELD_NUMBER: _ClassVar[int]
    SURFACERANGEMIN_FIELD_NUMBER: _ClassVar[int]
    LANDRANGEMAX_FIELD_NUMBER: _ClassVar[int]
    LANDRANGEMIN_FIELD_NUMBER: _ClassVar[int]
    SUBSURFACERANGEMAX_FIELD_NUMBER: _ClassVar[int]
    SUBSURFACERANGEMIN_FIELD_NUMBER: _ClassVar[int]
    WARHEADS_FIELD_NUMBER: _ClassVar[int]
    GUIDANCE_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Name: str
    DefaultLoad: int
    CurrentLoad: int
    MaxLoad: int
    ROF: int
    OW: bool
    IW: bool
    Multiple: int
    WeaponDBID: int
    TimeToFire: float
    IsTank: bool
    FuelTank: float
    AirRangeMax: float
    AirRangeMin: float
    SurfaceRangeMax: float
    SurfaceRangeMin: float
    LandRangeMax: float
    LandRangeMin: float
    SubsurfaceRangeMax: float
    SubsurfaceRangeMin: float
    Warheads: _containers.MessageMap[str, THWarhead]
    Guidance: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Name: _Optional[str] = ..., DefaultLoad: _Optional[int] = ..., CurrentLoad: _Optional[int] = ..., MaxLoad: _Optional[int] = ..., ROF: _Optional[int] = ..., OW: bool = ..., IW: bool = ..., Multiple: _Optional[int] = ..., WeaponDBID: _Optional[int] = ..., TimeToFire: _Optional[float] = ..., IsTank: bool = ..., FuelTank: _Optional[float] = ..., AirRangeMax: _Optional[float] = ..., AirRangeMin: _Optional[float] = ..., SurfaceRangeMax: _Optional[float] = ..., SurfaceRangeMin: _Optional[float] = ..., LandRangeMax: _Optional[float] = ..., LandRangeMin: _Optional[float] = ..., SubsurfaceRangeMax: _Optional[float] = ..., SubsurfaceRangeMin: _Optional[float] = ..., Warheads: _Optional[_Mapping[str, THWarhead]] = ..., Guidance: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THComponent(_message.Message):
    __slots__ = ("DBID", "Type", "Status", "Name", "ExceptionStatus", "DamageSeverity")
    DBID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXCEPTIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    DAMAGESEVERITY_FIELD_NUMBER: _ClassVar[int]
    DBID: int
    Type: int
    Status: int
    Name: str
    ExceptionStatus: str
    DamageSeverity: int
    def __init__(self, DBID: _Optional[int] = ..., Type: _Optional[int] = ..., Status: _Optional[int] = ..., Name: _Optional[str] = ..., ExceptionStatus: _Optional[str] = ..., DamageSeverity: _Optional[int] = ...) -> None: ...

class THComponentCommDevice(_message.Message):
    __slots__ = ("Component", "OC", "IJ", "PS", "IsActive", "Link", "mapdel")
    class LinkEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    OC_FIELD_NUMBER: _ClassVar[int]
    IJ_FIELD_NUMBER: _ClassVar[int]
    PS_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    OC: int
    IJ: bool
    PS: bool
    IsActive: bool
    Link: _containers.ScalarMap[str, str]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., OC: _Optional[int] = ..., IJ: bool = ..., PS: bool = ..., IsActive: bool = ..., Link: _Optional[_Mapping[str, str]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THComponentSensor(_message.Message):
    __slots__ = ("Component", "IsActive", "MaxRange", "MinRange", "WorkFreq", "CanBeActive", "Role", "Cov", "Cov_Ill")
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    MAXRANGE_FIELD_NUMBER: _ClassVar[int]
    MINRANGE_FIELD_NUMBER: _ClassVar[int]
    WORKFREQ_FIELD_NUMBER: _ClassVar[int]
    CANBEACTIVE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    COV_FIELD_NUMBER: _ClassVar[int]
    COV_ILL_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    IsActive: bool
    MaxRange: float
    MinRange: float
    WorkFreq: int
    CanBeActive: bool
    Role: int
    Cov: str
    Cov_Ill: str
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., IsActive: bool = ..., MaxRange: _Optional[float] = ..., MinRange: _Optional[float] = ..., WorkFreq: _Optional[int] = ..., CanBeActive: bool = ..., Role: _Optional[int] = ..., Cov: _Optional[str] = ..., Cov_Ill: _Optional[str] = ...) -> None: ...

class THComponentMount(_message.Message):
    __slots__ = ("Component", "FireTime", "TTF", "ReloadStatus", "DP", "RPriority", "AO_B", "AO_D", "TTRA", "WeaponRecs", "MagazineWeaponRecs", "Capacity", "mapdel")
    class WeaponRecsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponRec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponRec, _Mapping]] = ...) -> None: ...
    class MagazineWeaponRecsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponRec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponRec, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    FIRETIME_FIELD_NUMBER: _ClassVar[int]
    TTF_FIELD_NUMBER: _ClassVar[int]
    RELOADSTATUS_FIELD_NUMBER: _ClassVar[int]
    DP_FIELD_NUMBER: _ClassVar[int]
    RPRIORITY_FIELD_NUMBER: _ClassVar[int]
    AO_B_FIELD_NUMBER: _ClassVar[int]
    AO_D_FIELD_NUMBER: _ClassVar[int]
    TTRA_FIELD_NUMBER: _ClassVar[int]
    WEAPONRECS_FIELD_NUMBER: _ClassVar[int]
    MAGAZINEWEAPONRECS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    FireTime: str
    TTF: float
    ReloadStatus: int
    DP: float
    RPriority: str
    AO_B: float
    AO_D: float
    TTRA: float
    WeaponRecs: _containers.MessageMap[str, THWeaponRec]
    MagazineWeaponRecs: _containers.MessageMap[str, THWeaponRec]
    Capacity: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., FireTime: _Optional[str] = ..., TTF: _Optional[float] = ..., ReloadStatus: _Optional[int] = ..., DP: _Optional[float] = ..., RPriority: _Optional[str] = ..., AO_B: _Optional[float] = ..., AO_D: _Optional[float] = ..., TTRA: _Optional[float] = ..., WeaponRecs: _Optional[_Mapping[str, THWeaponRec]] = ..., MagazineWeaponRecs: _Optional[_Mapping[str, THWeaponRec]] = ..., Capacity: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THComponentMagazine(_message.Message):
    __slots__ = ("Component", "Weapons", "Capacity", "mapdel")
    class WeaponsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponRec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponRec, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    WEAPONS_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    Weapons: _containers.MessageMap[str, THWeaponRec]
    Capacity: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., Weapons: _Optional[_Mapping[str, THWeaponRec]] = ..., Capacity: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THComponentCargo(_message.Message):
    __slots__ = ("Component", "Mission", "Mounts", "mapdel")
    class MountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentMount
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentMount, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    MISSION_FIELD_NUMBER: _ClassVar[int]
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    Mission: str
    Mounts: _containers.MessageMap[str, THComponentMount]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., Mission: _Optional[str] = ..., Mounts: _Optional[_Mapping[str, THComponentMount]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THComponentAirFacility(_message.Message):
    __slots__ = ("Component", "Size", "Capacity")
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    Size: int
    Capacity: int
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ..., Size: _Optional[int] = ..., Capacity: _Optional[int] = ...) -> None: ...

class THComponentDockFacility(_message.Message):
    __slots__ = ("Component",)
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ...) -> None: ...

class THComponentPropulsion(_message.Message):
    __slots__ = ("Component",)
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    Component: THComponent
    def __init__(self, Component: _Optional[_Union[THComponent, _Mapping]] = ...) -> None: ...

class THFuelRec(_message.Message):
    __slots__ = ("DBID", "MQ", "CQ", "FT")
    DBID_FIELD_NUMBER: _ClassVar[int]
    MQ_FIELD_NUMBER: _ClassVar[int]
    CQ_FIELD_NUMBER: _ClassVar[int]
    FT_FIELD_NUMBER: _ClassVar[int]
    DBID: int
    MQ: float
    CQ: float
    FT: int
    def __init__(self, DBID: _Optional[int] = ..., MQ: _Optional[float] = ..., CQ: _Optional[float] = ..., FT: _Optional[int] = ...) -> None: ...

class THLoadout(_message.Message):
    __slots__ = ("DBID", "Name", "WeaponRecs", "QuickTurnaround", "QuickTurnaround_ReadyTime", "QuickTurnaround_AirborneTime", "QuickTurnaround_MaxSorties", "QuickTurnaround_AdditionalTimePenalty", "mapdel")
    class WeaponRecsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponRec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponRec, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    DBID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    WEAPONRECS_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_READYTIME_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_AIRBORNETIME_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_MAXSORTIES_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_ADDITIONALTIMEPENALTY_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    DBID: int
    Name: str
    WeaponRecs: _containers.MessageMap[str, THWeaponRec]
    QuickTurnaround: bool
    QuickTurnaround_ReadyTime: int
    QuickTurnaround_AirborneTime: int
    QuickTurnaround_MaxSorties: int
    QuickTurnaround_AdditionalTimePenalty: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, DBID: _Optional[int] = ..., Name: _Optional[str] = ..., WeaponRecs: _Optional[_Mapping[str, THWeaponRec]] = ..., QuickTurnaround: bool = ..., QuickTurnaround_ReadyTime: _Optional[int] = ..., QuickTurnaround_AirborneTime: _Optional[int] = ..., QuickTurnaround_MaxSorties: _Optional[int] = ..., QuickTurnaround_AdditionalTimePenalty: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THRangeSymbol(_message.Message):
    __slots__ = ("Range", "LeftArc", "RightArc", "Type", "Color")
    RANGE_FIELD_NUMBER: _ClassVar[int]
    LEFTARC_FIELD_NUMBER: _ClassVar[int]
    RIGHTARC_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    Range: float
    LeftArc: float
    RightArc: float
    Type: int
    Color: int
    def __init__(self, Range: _Optional[float] = ..., LeftArc: _Optional[float] = ..., RightArc: _Optional[float] = ..., Type: _Optional[int] = ..., Color: _Optional[int] = ...) -> None: ...

class THXSection(_message.Message):
    __slots__ = ("Type", "Front", "Side", "Rear", "Top")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FRONT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    REAR_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    Type: int
    Front: float
    Side: float
    Rear: float
    Top: float
    def __init__(self, Type: _Optional[int] = ..., Front: _Optional[float] = ..., Side: _Optional[float] = ..., Rear: _Optional[float] = ..., Top: _Optional[float] = ...) -> None: ...

class THAirOps(_message.Message):
    __slots__ = ("HAF", "AHU", "CHU", "Status", "ReadyTime", "QuickTurnaround", "QTAroEna", "Condition", "CT", "RQ")
    HAF_FIELD_NUMBER: _ClassVar[int]
    AHU_FIELD_NUMBER: _ClassVar[int]
    CHU_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    READYTIME_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUND_FIELD_NUMBER: _ClassVar[int]
    QTAROENA_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    CT_FIELD_NUMBER: _ClassVar[int]
    RQ_FIELD_NUMBER: _ClassVar[int]
    HAF: str
    AHU: str
    CHU: str
    Status: str
    ReadyTime: str
    QuickTurnaround: str
    QTAroEna: bool
    Condition: int
    CT: float
    RQ: bytes
    def __init__(self, HAF: _Optional[str] = ..., AHU: _Optional[str] = ..., CHU: _Optional[str] = ..., Status: _Optional[str] = ..., ReadyTime: _Optional[str] = ..., QuickTurnaround: _Optional[str] = ..., QTAroEna: bool = ..., Condition: _Optional[int] = ..., CT: _Optional[float] = ..., RQ: _Optional[bytes] = ...) -> None: ...

class THDockingOps(_message.Message):
    __slots__ = ("HDF", "AHU", "CHU", "Status", "ReadyTime", "Condition")
    HDF_FIELD_NUMBER: _ClassVar[int]
    AHU_FIELD_NUMBER: _ClassVar[int]
    CHU_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    READYTIME_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    HDF: str
    AHU: str
    CHU: str
    Status: str
    ReadyTime: str
    Condition: int
    def __init__(self, HDF: _Optional[str] = ..., AHU: _Optional[str] = ..., CHU: _Optional[str] = ..., Status: _Optional[str] = ..., ReadyTime: _Optional[str] = ..., Condition: _Optional[int] = ...) -> None: ...

class THContact(_message.Message):
    __slots__ = ("Side", "Name", "Type", "CurrentSpeed", "ActualUnitID", "DBID", "IDStatus", "ActType", "ActCategory", "Age", "HeldFor", "UncertaintyArea", "Stance", "ShowMark", "BatchNum", "NetNodeID", "mapdel")
    class StanceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    ACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    IDSTATUS_FIELD_NUMBER: _ClassVar[int]
    ACTTYPE_FIELD_NUMBER: _ClassVar[int]
    ACTCATEGORY_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    HELDFOR_FIELD_NUMBER: _ClassVar[int]
    UNCERTAINTYAREA_FIELD_NUMBER: _ClassVar[int]
    STANCE_FIELD_NUMBER: _ClassVar[int]
    SHOWMARK_FIELD_NUMBER: _ClassVar[int]
    BATCHNUM_FIELD_NUMBER: _ClassVar[int]
    NETNODEID_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Side: str
    Name: str
    Type: int
    CurrentSpeed: float
    ActualUnitID: str
    DBID: int
    IDStatus: int
    ActType: int
    ActCategory: int
    Age: float
    HeldFor: float
    UncertaintyArea: bytes
    Stance: _containers.ScalarMap[str, int]
    ShowMark: bool
    BatchNum: str
    NetNodeID: str
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Side: _Optional[str] = ..., Name: _Optional[str] = ..., Type: _Optional[int] = ..., CurrentSpeed: _Optional[float] = ..., ActualUnitID: _Optional[str] = ..., DBID: _Optional[int] = ..., IDStatus: _Optional[int] = ..., ActType: _Optional[int] = ..., ActCategory: _Optional[int] = ..., Age: _Optional[float] = ..., HeldFor: _Optional[float] = ..., UncertaintyArea: _Optional[bytes] = ..., Stance: _Optional[_Mapping[str, int]] = ..., ShowMark: bool = ..., BatchNum: _Optional[str] = ..., NetNodeID: _Optional[str] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THCommNode(_message.Message):
    __slots__ = ("CommLink", "CommPPLI", "RevisedCommunicationDistance", "RevisedCommunicationBandwidth")
    COMMLINK_FIELD_NUMBER: _ClassVar[int]
    COMMPPLI_FIELD_NUMBER: _ClassVar[int]
    REVISEDCOMMUNICATIONDISTANCE_FIELD_NUMBER: _ClassVar[int]
    REVISEDCOMMUNICATIONBANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    CommLink: str
    CommPPLI: str
    RevisedCommunicationDistance: float
    RevisedCommunicationBandwidth: int
    def __init__(self, CommLink: _Optional[str] = ..., CommPPLI: _Optional[str] = ..., RevisedCommunicationDistance: _Optional[float] = ..., RevisedCommunicationBandwidth: _Optional[int] = ...) -> None: ...

class THClCommBRule(_message.Message):
    __slots__ = ("MaxMemberNumber", "SupType")
    MAXMEMBERNUMBER_FIELD_NUMBER: _ClassVar[int]
    SUPTYPE_FIELD_NUMBER: _ClassVar[int]
    MaxMemberNumber: int
    SupType: int
    def __init__(self, MaxMemberNumber: _Optional[int] = ..., SupType: _Optional[int] = ...) -> None: ...

class THClCommARule(_message.Message):
    __slots__ = ("ClCommBRule", "StartTime", "EndTime", "IsFixed", "Regio", "Radius", "UnitID", "UnitLat", "UnitLon")
    CLCOMMBRULE_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    ISFIXED_FIELD_NUMBER: _ClassVar[int]
    REGIO_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    UNITLAT_FIELD_NUMBER: _ClassVar[int]
    UNITLON_FIELD_NUMBER: _ClassVar[int]
    ClCommBRule: THClCommBRule
    StartTime: str
    EndTime: str
    IsFixed: bool
    Regio: str
    Radius: float
    UnitID: str
    UnitLat: float
    UnitLon: float
    def __init__(self, ClCommBRule: _Optional[_Union[THClCommBRule, _Mapping]] = ..., StartTime: _Optional[str] = ..., EndTime: _Optional[str] = ..., IsFixed: bool = ..., Regio: _Optional[str] = ..., Radius: _Optional[float] = ..., UnitID: _Optional[str] = ..., UnitLat: _Optional[float] = ..., UnitLon: _Optional[float] = ...) -> None: ...

class THCLComm(_message.Message):
    __slots__ = ("CLColor", "CLSideID", "CLComLat", "CLComLon", "CLMember", "CLType", "CLRule", "CLComPlan", "CLComPPLI", "CLInforCenterID", "CLName", "CommLinkLines", "CommLines", "mapdel")
    class CommLinkLinesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class CommLinesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    CLCOLOR_FIELD_NUMBER: _ClassVar[int]
    CLSIDEID_FIELD_NUMBER: _ClassVar[int]
    CLCOMLAT_FIELD_NUMBER: _ClassVar[int]
    CLCOMLON_FIELD_NUMBER: _ClassVar[int]
    CLMEMBER_FIELD_NUMBER: _ClassVar[int]
    CLTYPE_FIELD_NUMBER: _ClassVar[int]
    CLRULE_FIELD_NUMBER: _ClassVar[int]
    CLCOMPLAN_FIELD_NUMBER: _ClassVar[int]
    CLCOMPPLI_FIELD_NUMBER: _ClassVar[int]
    CLINFORCENTERID_FIELD_NUMBER: _ClassVar[int]
    CLNAME_FIELD_NUMBER: _ClassVar[int]
    COMMLINKLINES_FIELD_NUMBER: _ClassVar[int]
    COMMLINES_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    CLColor: int
    CLSideID: str
    CLComLat: float
    CLComLon: float
    CLMember: str
    CLType: int
    CLRule: THClCommARule
    CLComPlan: str
    CLComPPLI: str
    CLInforCenterID: str
    CLName: str
    CommLinkLines: _containers.ScalarMap[str, str]
    CommLines: _containers.ScalarMap[str, str]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, CLColor: _Optional[int] = ..., CLSideID: _Optional[str] = ..., CLComLat: _Optional[float] = ..., CLComLon: _Optional[float] = ..., CLMember: _Optional[str] = ..., CLType: _Optional[int] = ..., CLRule: _Optional[_Union[THClCommARule, _Mapping]] = ..., CLComPlan: _Optional[str] = ..., CLComPPLI: _Optional[str] = ..., CLInforCenterID: _Optional[str] = ..., CLName: _Optional[str] = ..., CommLinkLines: _Optional[_Mapping[str, str]] = ..., CommLines: _Optional[_Mapping[str, str]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THLastDetection(_message.Message):
    __slots__ = ("UnitID", "SensorID", "DetectionRange", "POSSUB", "DetectionTime", "ContactID", "UnitName", "SensorName", "SideName")
    UNITID_FIELD_NUMBER: _ClassVar[int]
    SENSORID_FIELD_NUMBER: _ClassVar[int]
    DETECTIONRANGE_FIELD_NUMBER: _ClassVar[int]
    POSSUB_FIELD_NUMBER: _ClassVar[int]
    DETECTIONTIME_FIELD_NUMBER: _ClassVar[int]
    CONTACTID_FIELD_NUMBER: _ClassVar[int]
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    SENSORNAME_FIELD_NUMBER: _ClassVar[int]
    SIDENAME_FIELD_NUMBER: _ClassVar[int]
    UnitID: str
    SensorID: str
    DetectionRange: float
    POSSUB: int
    DetectionTime: int
    ContactID: str
    UnitName: str
    SensorName: str
    SideName: str
    def __init__(self, UnitID: _Optional[str] = ..., SensorID: _Optional[str] = ..., DetectionRange: _Optional[float] = ..., POSSUB: _Optional[int] = ..., DetectionTime: _Optional[int] = ..., ContactID: _Optional[str] = ..., UnitName: _Optional[str] = ..., SensorName: _Optional[str] = ..., SideName: _Optional[str] = ...) -> None: ...

class THLastDetectionList(_message.Message):
    __slots__ = ("LastDetectionList",)
    LASTDETECTIONLIST_FIELD_NUMBER: _ClassVar[int]
    LastDetectionList: _containers.RepeatedCompositeFieldContainer[THLastDetection]
    def __init__(self, LastDetectionList: _Optional[_Iterable[_Union[THLastDetection, _Mapping]]] = ...) -> None: ...

class THUnitLosseInfo(_message.Message):
    __slots__ = ("Time", "GUID", "Name", "UnitType", "Category", "SubType", "DBID", "AttackerGUID", "AttackerName", "AttackerDBID")
    TIME_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNITTYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    SUBTYPE_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    ATTACKERGUID_FIELD_NUMBER: _ClassVar[int]
    ATTACKERNAME_FIELD_NUMBER: _ClassVar[int]
    ATTACKERDBID_FIELD_NUMBER: _ClassVar[int]
    Time: int
    GUID: str
    Name: str
    UnitType: int
    Category: int
    SubType: int
    DBID: int
    AttackerGUID: str
    AttackerName: str
    AttackerDBID: int
    def __init__(self, Time: _Optional[int] = ..., GUID: _Optional[str] = ..., Name: _Optional[str] = ..., UnitType: _Optional[int] = ..., Category: _Optional[int] = ..., SubType: _Optional[int] = ..., DBID: _Optional[int] = ..., AttackerGUID: _Optional[str] = ..., AttackerName: _Optional[str] = ..., AttackerDBID: _Optional[int] = ...) -> None: ...

class THWeaponExpenditureInfo(_message.Message):
    __slots__ = ("Time", "DBID", "Quantity", "TargetGUID", "TargetName")
    TIME_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TARGETGUID_FIELD_NUMBER: _ClassVar[int]
    TARGETNAME_FIELD_NUMBER: _ClassVar[int]
    Time: int
    DBID: int
    Quantity: int
    TargetGUID: str
    TargetName: str
    def __init__(self, Time: _Optional[int] = ..., DBID: _Optional[int] = ..., Quantity: _Optional[int] = ..., TargetGUID: _Optional[str] = ..., TargetName: _Optional[str] = ...) -> None: ...

class THWeaponLostInfo(_message.Message):
    __slots__ = ("Time", "DBID", "Quantity", "Reason")
    TIME_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    Time: int
    DBID: int
    Quantity: int
    Reason: str
    def __init__(self, Time: _Optional[int] = ..., DBID: _Optional[int] = ..., Quantity: _Optional[int] = ..., Reason: _Optional[str] = ...) -> None: ...

class THAARDetails(_message.Message):
    __slots__ = ("Losses", "Expenditures", "WeaponsLost")
    LOSSES_FIELD_NUMBER: _ClassVar[int]
    EXPENDITURES_FIELD_NUMBER: _ClassVar[int]
    WEAPONSLOST_FIELD_NUMBER: _ClassVar[int]
    Losses: _containers.RepeatedCompositeFieldContainer[THUnitLosseInfo]
    Expenditures: _containers.RepeatedCompositeFieldContainer[THWeaponExpenditureInfo]
    WeaponsLost: _containers.RepeatedCompositeFieldContainer[THWeaponLostInfo]
    def __init__(self, Losses: _Optional[_Iterable[_Union[THUnitLosseInfo, _Mapping]]] = ..., Expenditures: _Optional[_Iterable[_Union[THWeaponExpenditureInfo, _Mapping]]] = ..., WeaponsLost: _Optional[_Iterable[_Union[THWeaponLostInfo, _Mapping]]] = ...) -> None: ...

class THScoreChangeReason(_message.Message):
    __slots__ = ("Time", "Name", "ID", "Type", "Para1", "Para2", "PointChange", "TargetSideName")
    TIME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PARA1_FIELD_NUMBER: _ClassVar[int]
    PARA2_FIELD_NUMBER: _ClassVar[int]
    POINTCHANGE_FIELD_NUMBER: _ClassVar[int]
    TARGETSIDENAME_FIELD_NUMBER: _ClassVar[int]
    Time: int
    Name: str
    ID: str
    Type: int
    Para1: str
    Para2: str
    PointChange: int
    TargetSideName: str
    def __init__(self, Time: _Optional[int] = ..., Name: _Optional[str] = ..., ID: _Optional[str] = ..., Type: _Optional[int] = ..., Para1: _Optional[str] = ..., Para2: _Optional[str] = ..., PointChange: _Optional[int] = ..., TargetSideName: _Optional[str] = ...) -> None: ...

class THScoreChange(_message.Message):
    __slots__ = ("Reasons",)
    REASONS_FIELD_NUMBER: _ClassVar[int]
    Reasons: _containers.RepeatedCompositeFieldContainer[THScoreChangeReason]
    def __init__(self, Reasons: _Optional[_Iterable[_Union[THScoreChangeReason, _Mapping]]] = ...) -> None: ...

class THAAR(_message.Message):
    __slots__ = ("Losses", "Expenditures")
    class LossesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    class ExpendituresEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    LOSSES_FIELD_NUMBER: _ClassVar[int]
    EXPENDITURES_FIELD_NUMBER: _ClassVar[int]
    Losses: _containers.MessageMap[str, THVectorString]
    Expenditures: _containers.ScalarMap[str, int]
    def __init__(self, Losses: _Optional[_Mapping[str, THVectorString]] = ..., Expenditures: _Optional[_Mapping[str, int]] = ...) -> None: ...

class THLoggedMessage(_message.Message):
    __slots__ = ("ID", "Increment", "Text", "Summary", "TimeStamp", "Level", "Type", "ReporterID", "TargetID", "FiringParent", "Side", "Location")
    ID_FIELD_NUMBER: _ClassVar[int]
    INCREMENT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORTERID_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    FIRINGPARENT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Increment: int
    Text: str
    Summary: str
    TimeStamp: int
    Level: int
    Type: int
    ReporterID: str
    TargetID: str
    FiringParent: str
    Side: str
    Location: str
    def __init__(self, ID: _Optional[str] = ..., Increment: _Optional[int] = ..., Text: _Optional[str] = ..., Summary: _Optional[str] = ..., TimeStamp: _Optional[int] = ..., Level: _Optional[int] = ..., Type: _Optional[int] = ..., ReporterID: _Optional[str] = ..., TargetID: _Optional[str] = ..., FiringParent: _Optional[str] = ..., Side: _Optional[str] = ..., Location: _Optional[str] = ...) -> None: ...

class THLoggedMessageList(_message.Message):
    __slots__ = ("LogList",)
    LOGLIST_FIELD_NUMBER: _ClassVar[int]
    LogList: _containers.RepeatedCompositeFieldContainer[THLoggedMessage]
    def __init__(self, LogList: _Optional[_Iterable[_Union[THLoggedMessage, _Mapping]]] = ...) -> None: ...

class THActiveUnitInfo(_message.Message):
    __slots__ = ("Category", "Type", "DBID", "ProficiencyLevel", "Side", "Name", "Doctrine", "XSections", "UnitType")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    PROFICIENCYLEVEL_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_FIELD_NUMBER: _ClassVar[int]
    XSECTIONS_FIELD_NUMBER: _ClassVar[int]
    UNITTYPE_FIELD_NUMBER: _ClassVar[int]
    Category: int
    Type: int
    DBID: int
    ProficiencyLevel: int
    Side: str
    Name: str
    Doctrine: THDoctrine
    XSections: bytes
    UnitType: int
    def __init__(self, Category: _Optional[int] = ..., Type: _Optional[int] = ..., DBID: _Optional[int] = ..., ProficiencyLevel: _Optional[int] = ..., Side: _Optional[str] = ..., Name: _Optional[str] = ..., Doctrine: _Optional[_Union[THDoctrine, _Mapping]] = ..., XSections: _Optional[bytes] = ..., UnitType: _Optional[int] = ...) -> None: ...

class THActiveUnit(_message.Message):
    __slots__ = ("CurrentSpeed", "Acc", "CargoToMission", "DockingCondition", "Throttle", "Status", "FuelState", "WeaponState", "DesiredSpeed", "DesiredAltitude", "DamagePts", "DamagePercent", "AssignedMission", "GroupID", "IsAD", "AI", "Weaponry", "Kinematics", "Navigator", "Sensory", "Damage", "CommDevices", "Sensors", "Mounts", "Magazines", "Cargos", "AirFacilitys", "DockFacilitys", "Propulsions", "FuelRecs", "Loadouts", "RangeSymbols", "Source", "CommLink", "ClCommID", "CommStuff", "CommLinkLines", "mapdel")
    class CommDevicesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentCommDevice
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentCommDevice, _Mapping]] = ...) -> None: ...
    class SensorsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentSensor
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentSensor, _Mapping]] = ...) -> None: ...
    class MountsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentMount
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentMount, _Mapping]] = ...) -> None: ...
    class MagazinesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentMagazine
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentMagazine, _Mapping]] = ...) -> None: ...
    class CargosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentCargo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentCargo, _Mapping]] = ...) -> None: ...
    class AirFacilitysEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentAirFacility
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentAirFacility, _Mapping]] = ...) -> None: ...
    class DockFacilitysEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentDockFacility
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentDockFacility, _Mapping]] = ...) -> None: ...
    class PropulsionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THComponentPropulsion
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THComponentPropulsion, _Mapping]] = ...) -> None: ...
    class FuelRecsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THFuelRec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THFuelRec, _Mapping]] = ...) -> None: ...
    class LoadoutsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THLoadout
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THLoadout, _Mapping]] = ...) -> None: ...
    class RangeSymbolsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THRangeSymbol
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THRangeSymbol, _Mapping]] = ...) -> None: ...
    class CommLinkLinesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    CURRENTSPEED_FIELD_NUMBER: _ClassVar[int]
    ACC_FIELD_NUMBER: _ClassVar[int]
    CARGOTOMISSION_FIELD_NUMBER: _ClassVar[int]
    DOCKINGCONDITION_FIELD_NUMBER: _ClassVar[int]
    THROTTLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FUELSTATE_FIELD_NUMBER: _ClassVar[int]
    WEAPONSTATE_FIELD_NUMBER: _ClassVar[int]
    DESIREDSPEED_FIELD_NUMBER: _ClassVar[int]
    DESIREDALTITUDE_FIELD_NUMBER: _ClassVar[int]
    DAMAGEPTS_FIELD_NUMBER: _ClassVar[int]
    DAMAGEPERCENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEDMISSION_FIELD_NUMBER: _ClassVar[int]
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    ISAD_FIELD_NUMBER: _ClassVar[int]
    AI_FIELD_NUMBER: _ClassVar[int]
    WEAPONRY_FIELD_NUMBER: _ClassVar[int]
    KINEMATICS_FIELD_NUMBER: _ClassVar[int]
    NAVIGATOR_FIELD_NUMBER: _ClassVar[int]
    SENSORY_FIELD_NUMBER: _ClassVar[int]
    DAMAGE_FIELD_NUMBER: _ClassVar[int]
    COMMDEVICES_FIELD_NUMBER: _ClassVar[int]
    SENSORS_FIELD_NUMBER: _ClassVar[int]
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    MAGAZINES_FIELD_NUMBER: _ClassVar[int]
    CARGOS_FIELD_NUMBER: _ClassVar[int]
    AIRFACILITYS_FIELD_NUMBER: _ClassVar[int]
    DOCKFACILITYS_FIELD_NUMBER: _ClassVar[int]
    PROPULSIONS_FIELD_NUMBER: _ClassVar[int]
    FUELRECS_FIELD_NUMBER: _ClassVar[int]
    LOADOUTS_FIELD_NUMBER: _ClassVar[int]
    RANGESYMBOLS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    COMMLINK_FIELD_NUMBER: _ClassVar[int]
    CLCOMMID_FIELD_NUMBER: _ClassVar[int]
    COMMSTUFF_FIELD_NUMBER: _ClassVar[int]
    COMMLINKLINES_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    CurrentSpeed: float
    Acc: float
    CargoToMission: str
    DockingCondition: bool
    Throttle: int
    Status: int
    FuelState: int
    WeaponState: int
    DesiredSpeed: float
    DesiredAltitude: float
    DamagePts: float
    DamagePercent: float
    AssignedMission: str
    GroupID: str
    IsAD: bool
    AI: THAI
    Weaponry: THWeaponry
    Kinematics: THKinematics
    Navigator: THNavigator
    Sensory: THSensory
    Damage: THDamage
    CommDevices: _containers.MessageMap[str, THComponentCommDevice]
    Sensors: _containers.MessageMap[str, THComponentSensor]
    Mounts: _containers.MessageMap[str, THComponentMount]
    Magazines: _containers.MessageMap[str, THComponentMagazine]
    Cargos: _containers.MessageMap[str, THComponentCargo]
    AirFacilitys: _containers.MessageMap[str, THComponentAirFacility]
    DockFacilitys: _containers.MessageMap[str, THComponentDockFacility]
    Propulsions: _containers.MessageMap[str, THComponentPropulsion]
    FuelRecs: _containers.MessageMap[str, THFuelRec]
    Loadouts: _containers.MessageMap[str, THLoadout]
    RangeSymbols: _containers.MessageMap[str, THRangeSymbol]
    Source: int
    CommLink: str
    ClCommID: str
    CommStuff: THCommStuff
    CommLinkLines: _containers.ScalarMap[str, str]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, CurrentSpeed: _Optional[float] = ..., Acc: _Optional[float] = ..., CargoToMission: _Optional[str] = ..., DockingCondition: bool = ..., Throttle: _Optional[int] = ..., Status: _Optional[int] = ..., FuelState: _Optional[int] = ..., WeaponState: _Optional[int] = ..., DesiredSpeed: _Optional[float] = ..., DesiredAltitude: _Optional[float] = ..., DamagePts: _Optional[float] = ..., DamagePercent: _Optional[float] = ..., AssignedMission: _Optional[str] = ..., GroupID: _Optional[str] = ..., IsAD: bool = ..., AI: _Optional[_Union[THAI, _Mapping]] = ..., Weaponry: _Optional[_Union[THWeaponry, _Mapping]] = ..., Kinematics: _Optional[_Union[THKinematics, _Mapping]] = ..., Navigator: _Optional[_Union[THNavigator, _Mapping]] = ..., Sensory: _Optional[_Union[THSensory, _Mapping]] = ..., Damage: _Optional[_Union[THDamage, _Mapping]] = ..., CommDevices: _Optional[_Mapping[str, THComponentCommDevice]] = ..., Sensors: _Optional[_Mapping[str, THComponentSensor]] = ..., Mounts: _Optional[_Mapping[str, THComponentMount]] = ..., Magazines: _Optional[_Mapping[str, THComponentMagazine]] = ..., Cargos: _Optional[_Mapping[str, THComponentCargo]] = ..., AirFacilitys: _Optional[_Mapping[str, THComponentAirFacility]] = ..., DockFacilitys: _Optional[_Mapping[str, THComponentDockFacility]] = ..., Propulsions: _Optional[_Mapping[str, THComponentPropulsion]] = ..., FuelRecs: _Optional[_Mapping[str, THFuelRec]] = ..., Loadouts: _Optional[_Mapping[str, THLoadout]] = ..., RangeSymbols: _Optional[_Mapping[str, THRangeSymbol]] = ..., Source: _Optional[int] = ..., CommLink: _Optional[str] = ..., ClCommID: _Optional[str] = ..., CommStuff: _Optional[_Union[THCommStuff, _Mapping]] = ..., CommLinkLines: _Optional[_Mapping[str, str]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THUnitAircraft(_message.Message):
    __slots__ = ("ActiveUnit", "FlightRole", "AirborneTime", "AltitudePreset", "AirOps", "Type", "FuelRate")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    FLIGHTROLE_FIELD_NUMBER: _ClassVar[int]
    AIRBORNETIME_FIELD_NUMBER: _ClassVar[int]
    ALTITUDEPRESET_FIELD_NUMBER: _ClassVar[int]
    AIROPS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FUELRATE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    FlightRole: int
    AirborneTime: float
    AltitudePreset: int
    AirOps: THAirOps
    Type: int
    FuelRate: float
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., FlightRole: _Optional[int] = ..., AirborneTime: _Optional[float] = ..., AltitudePreset: _Optional[int] = ..., AirOps: _Optional[_Union[THAirOps, _Mapping]] = ..., Type: _Optional[int] = ..., FuelRate: _Optional[float] = ...) -> None: ...

class THUnitFacility(_message.Message):
    __slots__ = ("ActiveUnit", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., Type: _Optional[int] = ...) -> None: ...

class THUnitShip(_message.Message):
    __slots__ = ("ActiveUnit", "DockingOps", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    DOCKINGOPS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    DockingOps: THDockingOps
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., DockingOps: _Optional[_Union[THDockingOps, _Mapping]] = ..., Type: _Optional[int] = ...) -> None: ...

class THUnitSubmarine(_message.Message):
    __slots__ = ("ActiveUnit", "DepthPreset", "DockingOps", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    DEPTHPRESET_FIELD_NUMBER: _ClassVar[int]
    DOCKINGOPS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    DepthPreset: int
    DockingOps: THDockingOps
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., DepthPreset: _Optional[int] = ..., DockingOps: _Optional[_Union[THDockingOps, _Mapping]] = ..., Type: _Optional[int] = ...) -> None: ...

class THUnitSatellite(_message.Message):
    __slots__ = ("ActiveUnit", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., Type: _Optional[int] = ...) -> None: ...

class THUnitWeapon(_message.Message):
    __slots__ = ("ActiveUnit", "ImpactAltitude", "CEP_Surface", "CEP_Land", "FiringParent", "Warheads", "Guidance", "Type", "mapdel")
    class WarheadsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWarhead
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWarhead, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    IMPACTALTITUDE_FIELD_NUMBER: _ClassVar[int]
    CEP_SURFACE_FIELD_NUMBER: _ClassVar[int]
    CEP_LAND_FIELD_NUMBER: _ClassVar[int]
    FIRINGPARENT_FIELD_NUMBER: _ClassVar[int]
    WARHEADS_FIELD_NUMBER: _ClassVar[int]
    GUIDANCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    ImpactAltitude: float
    CEP_Surface: float
    CEP_Land: float
    FiringParent: str
    Warheads: _containers.MessageMap[str, THWarhead]
    Guidance: int
    Type: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., ImpactAltitude: _Optional[float] = ..., CEP_Surface: _Optional[float] = ..., CEP_Land: _Optional[float] = ..., FiringParent: _Optional[str] = ..., Warheads: _Optional[_Mapping[str, THWarhead]] = ..., Guidance: _Optional[int] = ..., Type: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THUnitGroup(_message.Message):
    __slots__ = ("ActiveUnit", "GroupLead", "Members", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    GROUPLEAD_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    GroupLead: str
    Members: bytes
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., GroupLead: _Optional[str] = ..., Members: _Optional[bytes] = ..., Type: _Optional[int] = ...) -> None: ...

class THUnitVehicle(_message.Message):
    __slots__ = ("ActiveUnit", "Type")
    ACTIVEUNIT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ActiveUnit: THActiveUnit
    Type: int
    def __init__(self, ActiveUnit: _Optional[_Union[THActiveUnit, _Mapping]] = ..., Type: _Optional[int] = ...) -> None: ...

class THActiveUnitColl(_message.Message):
    __slots__ = ("Aircraft", "Facility", "Ship", "Submarine", "Satellite", "Weapon", "Group", "ClComm", "CommNode", "Vehicle", "CommLinkLines", "mapdel")
    class AircraftEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitAircraft
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitAircraft, _Mapping]] = ...) -> None: ...
    class FacilityEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitFacility
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitFacility, _Mapping]] = ...) -> None: ...
    class ShipEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitShip
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitShip, _Mapping]] = ...) -> None: ...
    class SubmarineEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitSubmarine
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitSubmarine, _Mapping]] = ...) -> None: ...
    class SatelliteEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitSatellite
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitSatellite, _Mapping]] = ...) -> None: ...
    class WeaponEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitWeapon
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitWeapon, _Mapping]] = ...) -> None: ...
    class GroupEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitGroup
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitGroup, _Mapping]] = ...) -> None: ...
    class ClCommEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THCLComm
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THCLComm, _Mapping]] = ...) -> None: ...
    class CommNodeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THCommNode
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THCommNode, _Mapping]] = ...) -> None: ...
    class VehicleEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THUnitVehicle
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THUnitVehicle, _Mapping]] = ...) -> None: ...
    class CommLinkLinesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    SHIP_FIELD_NUMBER: _ClassVar[int]
    SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    SATELLITE_FIELD_NUMBER: _ClassVar[int]
    WEAPON_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    CLCOMM_FIELD_NUMBER: _ClassVar[int]
    COMMNODE_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_FIELD_NUMBER: _ClassVar[int]
    COMMLINKLINES_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Aircraft: _containers.MessageMap[str, THUnitAircraft]
    Facility: _containers.MessageMap[str, THUnitFacility]
    Ship: _containers.MessageMap[str, THUnitShip]
    Submarine: _containers.MessageMap[str, THUnitSubmarine]
    Satellite: _containers.MessageMap[str, THUnitSatellite]
    Weapon: _containers.MessageMap[str, THUnitWeapon]
    Group: _containers.MessageMap[str, THUnitGroup]
    ClComm: _containers.MessageMap[str, THCLComm]
    CommNode: _containers.MessageMap[str, THCommNode]
    Vehicle: _containers.MessageMap[str, THUnitVehicle]
    CommLinkLines: _containers.ScalarMap[str, str]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Aircraft: _Optional[_Mapping[str, THUnitAircraft]] = ..., Facility: _Optional[_Mapping[str, THUnitFacility]] = ..., Ship: _Optional[_Mapping[str, THUnitShip]] = ..., Submarine: _Optional[_Mapping[str, THUnitSubmarine]] = ..., Satellite: _Optional[_Mapping[str, THUnitSatellite]] = ..., Weapon: _Optional[_Mapping[str, THUnitWeapon]] = ..., Group: _Optional[_Mapping[str, THUnitGroup]] = ..., ClComm: _Optional[_Mapping[str, THCLComm]] = ..., CommNode: _Optional[_Mapping[str, THCommNode]] = ..., Vehicle: _Optional[_Mapping[str, THUnitVehicle]] = ..., CommLinkLines: _Optional[_Mapping[str, str]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSideInfo(_message.Message):
    __slots__ = ("ID", "Name", "Postures", "CollectiveResponsibility", "CATC", "CameraAlt", "AwarenessLevel", "ProficiencyLevel", "MapCenter", "Scoring_Disaster", "Scoring_Triumph", "Briefing", "IsAIOnly", "ClusterNetWork", "mapdel")
    class PosturesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POSTURES_FIELD_NUMBER: _ClassVar[int]
    COLLECTIVERESPONSIBILITY_FIELD_NUMBER: _ClassVar[int]
    CATC_FIELD_NUMBER: _ClassVar[int]
    CAMERAALT_FIELD_NUMBER: _ClassVar[int]
    AWARENESSLEVEL_FIELD_NUMBER: _ClassVar[int]
    PROFICIENCYLEVEL_FIELD_NUMBER: _ClassVar[int]
    MAPCENTER_FIELD_NUMBER: _ClassVar[int]
    SCORING_DISASTER_FIELD_NUMBER: _ClassVar[int]
    SCORING_TRIUMPH_FIELD_NUMBER: _ClassVar[int]
    BRIEFING_FIELD_NUMBER: _ClassVar[int]
    ISAIONLY_FIELD_NUMBER: _ClassVar[int]
    CLUSTERNETWORK_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    Postures: _containers.ScalarMap[str, int]
    CollectiveResponsibility: bool
    CATC: bool
    CameraAlt: float
    AwarenessLevel: int
    ProficiencyLevel: int
    MapCenter: THGeoPoint
    Scoring_Disaster: int
    Scoring_Triumph: int
    Briefing: str
    IsAIOnly: bool
    ClusterNetWork: int
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ..., Postures: _Optional[_Mapping[str, int]] = ..., CollectiveResponsibility: bool = ..., CATC: bool = ..., CameraAlt: _Optional[float] = ..., AwarenessLevel: _Optional[int] = ..., ProficiencyLevel: _Optional[int] = ..., MapCenter: _Optional[_Union[THGeoPoint, _Mapping]] = ..., Scoring_Disaster: _Optional[int] = ..., Scoring_Triumph: _Optional[int] = ..., Briefing: _Optional[str] = ..., IsAIOnly: bool = ..., ClusterNetWork: _Optional[int] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSide(_message.Message):
    __slots__ = ("Missions", "Doctrine", "ReferencePoints", "SpecialActions", "ActiveUnitsInfo", "ExclusionZones", "NoNavZones", "AirCorridorZones", "CommandList", "mapdel")
    class ReferencePointsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THRefPoint
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THRefPoint, _Mapping]] = ...) -> None: ...
    class SpecialActionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THSpecialAction
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THSpecialAction, _Mapping]] = ...) -> None: ...
    class ActiveUnitsInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THActiveUnitInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THActiveUnitInfo, _Mapping]] = ...) -> None: ...
    class ExclusionZonesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THExclusionZone
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THExclusionZone, _Mapping]] = ...) -> None: ...
    class NoNavZonesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THNoNavZone
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THNoNavZone, _Mapping]] = ...) -> None: ...
    class AirCorridorZonesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THAirCorridorZone
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THAirCorridorZone, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    MISSIONS_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_FIELD_NUMBER: _ClassVar[int]
    REFERENCEPOINTS_FIELD_NUMBER: _ClassVar[int]
    SPECIALACTIONS_FIELD_NUMBER: _ClassVar[int]
    ACTIVEUNITSINFO_FIELD_NUMBER: _ClassVar[int]
    EXCLUSIONZONES_FIELD_NUMBER: _ClassVar[int]
    NONAVZONES_FIELD_NUMBER: _ClassVar[int]
    AIRCORRIDORZONES_FIELD_NUMBER: _ClassVar[int]
    COMMANDLIST_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Missions: THMissionColl
    Doctrine: THDoctrine
    ReferencePoints: _containers.MessageMap[str, THRefPoint]
    SpecialActions: _containers.MessageMap[str, THSpecialAction]
    ActiveUnitsInfo: _containers.MessageMap[str, THActiveUnitInfo]
    ExclusionZones: _containers.MessageMap[str, THExclusionZone]
    NoNavZones: _containers.MessageMap[str, THNoNavZone]
    AirCorridorZones: _containers.MessageMap[str, THAirCorridorZone]
    CommandList: str
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Missions: _Optional[_Union[THMissionColl, _Mapping]] = ..., Doctrine: _Optional[_Union[THDoctrine, _Mapping]] = ..., ReferencePoints: _Optional[_Mapping[str, THRefPoint]] = ..., SpecialActions: _Optional[_Mapping[str, THSpecialAction]] = ..., ActiveUnitsInfo: _Optional[_Mapping[str, THActiveUnitInfo]] = ..., ExclusionZones: _Optional[_Mapping[str, THExclusionZone]] = ..., NoNavZones: _Optional[_Mapping[str, THNoNavZone]] = ..., AirCorridorZones: _Optional[_Mapping[str, THAirCorridorZone]] = ..., CommandList: _Optional[str] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSideReal(_message.Message):
    __slots__ = ("ContactAutoIncrement", "WeaponSalvos", "TotalScore", "Contacts", "ActiveUnits", "mapdel")
    class WeaponSalvosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponSalvo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponSalvo, _Mapping]] = ...) -> None: ...
    class ContactsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THContact
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THContact, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    CONTACTAUTOINCREMENT_FIELD_NUMBER: _ClassVar[int]
    WEAPONSALVOS_FIELD_NUMBER: _ClassVar[int]
    TOTALSCORE_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVEUNITS_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ContactAutoIncrement: int
    WeaponSalvos: _containers.MessageMap[str, THWeaponSalvo]
    TotalScore: int
    Contacts: _containers.MessageMap[str, THContact]
    ActiveUnits: THActiveUnitColl
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ContactAutoIncrement: _Optional[int] = ..., WeaponSalvos: _Optional[_Mapping[str, THWeaponSalvo]] = ..., TotalScore: _Optional[int] = ..., Contacts: _Optional[_Mapping[str, THContact]] = ..., ActiveUnits: _Optional[_Union[THActiveUnitColl, _Mapping]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSidePosition(_message.Message):
    __slots__ = ("Aircraft", "Facility", "Ship", "Submarine", "Satellite", "Weapon", "Group", "Contacts", "Vehicle", "mapdel")
    class AircraftEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class FacilityEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class ShipEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class SubmarineEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class SatelliteEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class WeaponEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class GroupEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class ContactsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class VehicleEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THPosition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THPosition, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    AIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    SHIP_FIELD_NUMBER: _ClassVar[int]
    SUBMARINE_FIELD_NUMBER: _ClassVar[int]
    SATELLITE_FIELD_NUMBER: _ClassVar[int]
    WEAPON_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    CONTACTS_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Aircraft: _containers.MessageMap[str, THPosition]
    Facility: _containers.MessageMap[str, THPosition]
    Ship: _containers.MessageMap[str, THPosition]
    Submarine: _containers.MessageMap[str, THPosition]
    Satellite: _containers.MessageMap[str, THPosition]
    Weapon: _containers.MessageMap[str, THPosition]
    Group: _containers.MessageMap[str, THPosition]
    Contacts: _containers.MessageMap[str, THPosition]
    Vehicle: _containers.MessageMap[str, THPosition]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Aircraft: _Optional[_Mapping[str, THPosition]] = ..., Facility: _Optional[_Mapping[str, THPosition]] = ..., Ship: _Optional[_Mapping[str, THPosition]] = ..., Submarine: _Optional[_Mapping[str, THPosition]] = ..., Satellite: _Optional[_Mapping[str, THPosition]] = ..., Weapon: _Optional[_Mapping[str, THPosition]] = ..., Group: _Optional[_Mapping[str, THPosition]] = ..., Contacts: _Optional[_Mapping[str, THPosition]] = ..., Vehicle: _Optional[_Mapping[str, THPosition]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THAircraftTakeOffInfo(_message.Message):
    __slots__ = ("AircraftID", "AircraftName", "HostAirFacility", "AssignedHostUnit", "CurrentHostUnit", "Condition", "CT")
    AIRCRAFTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTNAME_FIELD_NUMBER: _ClassVar[int]
    HOSTAIRFACILITY_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEDHOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    CURRENTHOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    CT_FIELD_NUMBER: _ClassVar[int]
    AircraftID: str
    AircraftName: str
    HostAirFacility: str
    AssignedHostUnit: str
    CurrentHostUnit: str
    Condition: int
    CT: float
    def __init__(self, AircraftID: _Optional[str] = ..., AircraftName: _Optional[str] = ..., HostAirFacility: _Optional[str] = ..., AssignedHostUnit: _Optional[str] = ..., CurrentHostUnit: _Optional[str] = ..., Condition: _Optional[int] = ..., CT: _Optional[float] = ...) -> None: ...

class THAircraftAttemptToRTBInfo(_message.Message):
    __slots__ = ("AircraftID", "AircraftName", "HostAirFacility", "HostUnit", "ManuallyOrdered", "ActiveUnitStatus", "Condition")
    AIRCRAFTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTNAME_FIELD_NUMBER: _ClassVar[int]
    HOSTAIRFACILITY_FIELD_NUMBER: _ClassVar[int]
    HOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    MANUALLYORDERED_FIELD_NUMBER: _ClassVar[int]
    ACTIVEUNITSTATUS_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    AircraftID: str
    AircraftName: str
    HostAirFacility: str
    HostUnit: str
    ManuallyOrdered: bool
    ActiveUnitStatus: int
    Condition: int
    def __init__(self, AircraftID: _Optional[str] = ..., AircraftName: _Optional[str] = ..., HostAirFacility: _Optional[str] = ..., HostUnit: _Optional[str] = ..., ManuallyOrdered: bool = ..., ActiveUnitStatus: _Optional[int] = ..., Condition: _Optional[int] = ...) -> None: ...

class THAircraftTouchDownInfo(_message.Message):
    __slots__ = ("AircraftID", "AircraftName", "HostAirFacility", "HostUnit", "Condition", "NormalLanding")
    AIRCRAFTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTNAME_FIELD_NUMBER: _ClassVar[int]
    HOSTAIRFACILITY_FIELD_NUMBER: _ClassVar[int]
    HOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    NORMALLANDING_FIELD_NUMBER: _ClassVar[int]
    AircraftID: str
    AircraftName: str
    HostAirFacility: str
    HostUnit: str
    Condition: int
    NormalLanding: bool
    def __init__(self, AircraftID: _Optional[str] = ..., AircraftName: _Optional[str] = ..., HostAirFacility: _Optional[str] = ..., HostUnit: _Optional[str] = ..., Condition: _Optional[int] = ..., NormalLanding: bool = ...) -> None: ...

class THAircraftDeckAbortInfo(_message.Message):
    __slots__ = ("AircraftID", "AircraftName", "HostAirFacility", "HostUnit", "Reason", "message")
    AIRCRAFTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTNAME_FIELD_NUMBER: _ClassVar[int]
    HOSTAIRFACILITY_FIELD_NUMBER: _ClassVar[int]
    HOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AircraftID: str
    AircraftName: str
    HostAirFacility: str
    HostUnit: str
    Reason: int
    message: str
    def __init__(self, AircraftID: _Optional[str] = ..., AircraftName: _Optional[str] = ..., HostAirFacility: _Optional[str] = ..., HostUnit: _Optional[str] = ..., Reason: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class THAircraftDisruptInfo(_message.Message):
    __slots__ = ("AircraftID", "AircraftName", "HostAirFacility", "HostUnit", "Reason", "message")
    AIRCRAFTID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTNAME_FIELD_NUMBER: _ClassVar[int]
    HOSTAIRFACILITY_FIELD_NUMBER: _ClassVar[int]
    HOSTUNIT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AircraftID: str
    AircraftName: str
    HostAirFacility: str
    HostUnit: str
    Reason: int
    message: str
    def __init__(self, AircraftID: _Optional[str] = ..., AircraftName: _Optional[str] = ..., HostAirFacility: _Optional[str] = ..., HostUnit: _Optional[str] = ..., Reason: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class THUnitDestroyedInfo(_message.Message):
    __slots__ = ("IsDamaged", "SideID", "UnitName", "UnitID", "UnitClass", "Reason", "Cause", "DamagePercent", "DestroyType")
    ISDAMAGED_FIELD_NUMBER: _ClassVar[int]
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    UNITCLASS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CAUSE_FIELD_NUMBER: _ClassVar[int]
    DAMAGEPERCENT_FIELD_NUMBER: _ClassVar[int]
    DESTROYTYPE_FIELD_NUMBER: _ClassVar[int]
    IsDamaged: bool
    SideID: str
    UnitName: str
    UnitID: str
    UnitClass: str
    Reason: str
    Cause: str
    DamagePercent: float
    DestroyType: int
    def __init__(self, IsDamaged: bool = ..., SideID: _Optional[str] = ..., UnitName: _Optional[str] = ..., UnitID: _Optional[str] = ..., UnitClass: _Optional[str] = ..., Reason: _Optional[str] = ..., Cause: _Optional[str] = ..., DamagePercent: _Optional[float] = ..., DestroyType: _Optional[int] = ...) -> None: ...

class THWeaponEndgameInfo(_message.Message):
    __slots__ = ("WeaponID", "WeaponName", "WeaponSide", "ParentFiringUnitID", "ParentFiringUnitName", "TargetID", "TargetName", "TargetSide", "TargetLongitude", "TargetLatitude", "TargetAltitude", "MissDistance", "DistanceFromFiringUnit_Horiz", "Result")
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    WEAPONNAME_FIELD_NUMBER: _ClassVar[int]
    WEAPONSIDE_FIELD_NUMBER: _ClassVar[int]
    PARENTFIRINGUNITID_FIELD_NUMBER: _ClassVar[int]
    PARENTFIRINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    TARGETNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETSIDE_FIELD_NUMBER: _ClassVar[int]
    TARGETLONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TARGETLATITUDE_FIELD_NUMBER: _ClassVar[int]
    TARGETALTITUDE_FIELD_NUMBER: _ClassVar[int]
    MISSDISTANCE_FIELD_NUMBER: _ClassVar[int]
    DISTANCEFROMFIRINGUNIT_HORIZ_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    WeaponID: str
    WeaponName: str
    WeaponSide: str
    ParentFiringUnitID: str
    ParentFiringUnitName: str
    TargetID: str
    TargetName: str
    TargetSide: str
    TargetLongitude: float
    TargetLatitude: float
    TargetAltitude: float
    MissDistance: float
    DistanceFromFiringUnit_Horiz: float
    Result: int
    def __init__(self, WeaponID: _Optional[str] = ..., WeaponName: _Optional[str] = ..., WeaponSide: _Optional[str] = ..., ParentFiringUnitID: _Optional[str] = ..., ParentFiringUnitName: _Optional[str] = ..., TargetID: _Optional[str] = ..., TargetName: _Optional[str] = ..., TargetSide: _Optional[str] = ..., TargetLongitude: _Optional[float] = ..., TargetLatitude: _Optional[float] = ..., TargetAltitude: _Optional[float] = ..., MissDistance: _Optional[float] = ..., DistanceFromFiringUnit_Horiz: _Optional[float] = ..., Result: _Optional[int] = ...) -> None: ...

class THWeaponFaultInfo(_message.Message):
    __slots__ = ("FiringUnitID", "FiringUnitDBID", "FiringUnitName", "FiringUnitType", "FiringUnitClass", "FiringUnitSideID", "WeaponID", "WeaponDBID", "WeaponName", "WeaponType", "WeaponClass", "TargetContactActualUnitID", "TargetContactActualUnitName", "TargetContactActualUnitClass", "TargetContactActualUnitSideID")
    FIRINGUNITID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITDBID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITTYPE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    WEAPONNAME_FIELD_NUMBER: _ClassVar[int]
    WEAPONTYPE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    FiringUnitID: str
    FiringUnitDBID: int
    FiringUnitName: str
    FiringUnitType: int
    FiringUnitClass: str
    FiringUnitSideID: str
    WeaponID: str
    WeaponDBID: int
    WeaponName: str
    WeaponType: int
    WeaponClass: str
    TargetContactActualUnitID: str
    TargetContactActualUnitName: str
    TargetContactActualUnitClass: str
    TargetContactActualUnitSideID: str
    def __init__(self, FiringUnitID: _Optional[str] = ..., FiringUnitDBID: _Optional[int] = ..., FiringUnitName: _Optional[str] = ..., FiringUnitType: _Optional[int] = ..., FiringUnitClass: _Optional[str] = ..., FiringUnitSideID: _Optional[str] = ..., WeaponID: _Optional[str] = ..., WeaponDBID: _Optional[int] = ..., WeaponName: _Optional[str] = ..., WeaponType: _Optional[int] = ..., WeaponClass: _Optional[str] = ..., TargetContactActualUnitID: _Optional[str] = ..., TargetContactActualUnitName: _Optional[str] = ..., TargetContactActualUnitClass: _Optional[str] = ..., TargetContactActualUnitSideID: _Optional[str] = ...) -> None: ...

class THLoadScenarioInfo(_message.Message):
    __slots__ = ("EngieGUID", "ScenarioName")
    ENGIEGUID_FIELD_NUMBER: _ClassVar[int]
    SCENARIONAME_FIELD_NUMBER: _ClassVar[int]
    EngieGUID: str
    ScenarioName: str
    def __init__(self, EngieGUID: _Optional[str] = ..., ScenarioName: _Optional[str] = ...) -> None: ...

class THSimStatusInfo(_message.Message):
    __slots__ = ("SimStatus",)
    SIMSTATUS_FIELD_NUMBER: _ClassVar[int]
    SimStatus: int
    def __init__(self, SimStatus: _Optional[int] = ...) -> None: ...

class THAdjustTimeCompressionInfo(_message.Message):
    __slots__ = ("TimeCompression",)
    TIMECOMPRESSION_FIELD_NUMBER: _ClassVar[int]
    TimeCompression: int
    def __init__(self, TimeCompression: _Optional[int] = ...) -> None: ...

class THSimEndInfo(_message.Message):
    __slots__ = ("HasEnded",)
    HASENDED_FIELD_NUMBER: _ClassVar[int]
    HasEnded: bool
    def __init__(self, HasEnded: bool = ...) -> None: ...

class THWeaponDestroyedInfo(_message.Message):
    __slots__ = ("FiringUnitID", "FiringUnitDBID", "FiringUnitName", "FiringUnitType", "FiringUnitClass", "FiringUnitSideID", "WeaponID", "WeaponDBID", "WeaponName", "WeaponType", "WeaponClass", "TargetContactID", "TargetContactActualUnitID", "TargetContactActualUnitName", "TargetContactActualUnitClass", "TargetContactActualUnitSideID", "Reason", "MissDistance")
    FIRINGUNITID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITDBID_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITTYPE_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    FIRINGUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    WEAPONNAME_FIELD_NUMBER: _ClassVar[int]
    WEAPONTYPE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITID_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITNAME_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    TARGETCONTACTACTUALUNITSIDEID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MISSDISTANCE_FIELD_NUMBER: _ClassVar[int]
    FiringUnitID: str
    FiringUnitDBID: int
    FiringUnitName: str
    FiringUnitType: int
    FiringUnitClass: str
    FiringUnitSideID: str
    WeaponID: str
    WeaponDBID: int
    WeaponName: str
    WeaponType: int
    WeaponClass: str
    TargetContactID: str
    TargetContactActualUnitID: str
    TargetContactActualUnitName: str
    TargetContactActualUnitClass: str
    TargetContactActualUnitSideID: str
    Reason: int
    MissDistance: float
    def __init__(self, FiringUnitID: _Optional[str] = ..., FiringUnitDBID: _Optional[int] = ..., FiringUnitName: _Optional[str] = ..., FiringUnitType: _Optional[int] = ..., FiringUnitClass: _Optional[str] = ..., FiringUnitSideID: _Optional[str] = ..., WeaponID: _Optional[str] = ..., WeaponDBID: _Optional[int] = ..., WeaponName: _Optional[str] = ..., WeaponType: _Optional[int] = ..., WeaponClass: _Optional[str] = ..., TargetContactID: _Optional[str] = ..., TargetContactActualUnitID: _Optional[str] = ..., TargetContactActualUnitName: _Optional[str] = ..., TargetContactActualUnitClass: _Optional[str] = ..., TargetContactActualUnitSideID: _Optional[str] = ..., Reason: _Optional[int] = ..., MissDistance: _Optional[float] = ...) -> None: ...

class THJamingInfo(_message.Message):
    __slots__ = ("JamType", "AttackUnitIDList", "TargetUnitID")
    JAMTYPE_FIELD_NUMBER: _ClassVar[int]
    ATTACKUNITIDLIST_FIELD_NUMBER: _ClassVar[int]
    TARGETUNITID_FIELD_NUMBER: _ClassVar[int]
    JamType: int
    AttackUnitIDList: _containers.RepeatedScalarFieldContainer[str]
    TargetUnitID: str
    def __init__(self, JamType: _Optional[int] = ..., AttackUnitIDList: _Optional[_Iterable[str]] = ..., TargetUnitID: _Optional[str] = ...) -> None: ...

class THJamingInfoList(_message.Message):
    __slots__ = ("JamingInfo",)
    JAMINGINFO_FIELD_NUMBER: _ClassVar[int]
    JamingInfo: _containers.RepeatedCompositeFieldContainer[THJamingInfo]
    def __init__(self, JamingInfo: _Optional[_Iterable[_Union[THJamingInfo, _Mapping]]] = ...) -> None: ...

class THComponentStatusChangeInfo(_message.Message):
    __slots__ = ("ParentUnitID", "ComponentID", "ComponentName", "ComponentType", "Status")
    PARENTUNITID_FIELD_NUMBER: _ClassVar[int]
    COMPONENTID_FIELD_NUMBER: _ClassVar[int]
    COMPONENTNAME_FIELD_NUMBER: _ClassVar[int]
    COMPONENTTYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ParentUnitID: str
    ComponentID: str
    ComponentName: str
    ComponentType: int
    Status: int
    def __init__(self, ParentUnitID: _Optional[str] = ..., ComponentID: _Optional[str] = ..., ComponentName: _Optional[str] = ..., ComponentType: _Optional[int] = ..., Status: _Optional[int] = ...) -> None: ...

class THScenarioInfo(_message.Message):
    __slots__ = ("ScenarioID", "Title", "Description", "FileName", "Meta_Complexity", "Meta_Difficulty", "Meta_ScenSetting", "PostureColor", "StartTime", "Duration", "SideInfo", "FeatureOption", "DBName", "mapdel")
    class SideInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THSideInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THSideInfo, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    SCENARIOID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    META_COMPLEXITY_FIELD_NUMBER: _ClassVar[int]
    META_DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    META_SCENSETTING_FIELD_NUMBER: _ClassVar[int]
    POSTURECOLOR_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SIDEINFO_FIELD_NUMBER: _ClassVar[int]
    FEATUREOPTION_FIELD_NUMBER: _ClassVar[int]
    DBNAME_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    ScenarioID: str
    Title: str
    Description: str
    FileName: str
    Meta_Complexity: int
    Meta_Difficulty: int
    Meta_ScenSetting: str
    PostureColor: str
    StartTime: int
    Duration: int
    SideInfo: _containers.MessageMap[str, THSideInfo]
    FeatureOption: THFeatureOption
    DBName: str
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, ScenarioID: _Optional[str] = ..., Title: _Optional[str] = ..., Description: _Optional[str] = ..., FileName: _Optional[str] = ..., Meta_Complexity: _Optional[int] = ..., Meta_Difficulty: _Optional[int] = ..., Meta_ScenSetting: _Optional[str] = ..., PostureColor: _Optional[str] = ..., StartTime: _Optional[int] = ..., Duration: _Optional[int] = ..., SideInfo: _Optional[_Mapping[str, THSideInfo]] = ..., FeatureOption: _Optional[_Union[THFeatureOption, _Mapping]] = ..., DBName: _Optional[str] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSituationInfo(_message.Message):
    __slots__ = ("Time", "Status", "LoadTime", "RecordTime", "Speed", "Seed", "FirstRunTime", "NonActiveUnits", "WeatherModel", "WeatherProfile", "Resolution", "ReferencePoints", "mapdel")
    class ReferencePointsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THRefPoint
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THRefPoint, _Mapping]] = ...) -> None: ...
    class MapdelEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THVectorString
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THVectorString, _Mapping]] = ...) -> None: ...
    TIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOADTIME_FIELD_NUMBER: _ClassVar[int]
    RECORDTIME_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    FIRSTRUNTIME_FIELD_NUMBER: _ClassVar[int]
    NONACTIVEUNITS_FIELD_NUMBER: _ClassVar[int]
    WEATHERMODEL_FIELD_NUMBER: _ClassVar[int]
    WEATHERPROFILE_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    REFERENCEPOINTS_FIELD_NUMBER: _ClassVar[int]
    MAPDEL_FIELD_NUMBER: _ClassVar[int]
    Time: int
    Status: str
    LoadTime: int
    RecordTime: str
    Speed: int
    Seed: int
    FirstRunTime: int
    NonActiveUnits: THNonActiveUnitColl
    WeatherModel: int
    WeatherProfile: THWeatherProfile
    Resolution: int
    ReferencePoints: _containers.MessageMap[str, THRefPoint]
    mapdel: _containers.MessageMap[str, THVectorString]
    def __init__(self, Time: _Optional[int] = ..., Status: _Optional[str] = ..., LoadTime: _Optional[int] = ..., RecordTime: _Optional[str] = ..., Speed: _Optional[int] = ..., Seed: _Optional[int] = ..., FirstRunTime: _Optional[int] = ..., NonActiveUnits: _Optional[_Union[THNonActiveUnitColl, _Mapping]] = ..., WeatherModel: _Optional[int] = ..., WeatherProfile: _Optional[_Union[THWeatherProfile, _Mapping]] = ..., Resolution: _Optional[int] = ..., ReferencePoints: _Optional[_Mapping[str, THRefPoint]] = ..., mapdel: _Optional[_Mapping[str, THVectorString]] = ...) -> None: ...

class THSituationSide(_message.Message):
    __slots__ = ("Side", "SideReal", "SidePosition")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SIDEREAL_FIELD_NUMBER: _ClassVar[int]
    SIDEPOSITION_FIELD_NUMBER: _ClassVar[int]
    Side: THSide
    SideReal: THSideReal
    SidePosition: THSidePosition
    def __init__(self, Side: _Optional[_Union[THSide, _Mapping]] = ..., SideReal: _Optional[_Union[THSideReal, _Mapping]] = ..., SidePosition: _Optional[_Union[THSidePosition, _Mapping]] = ...) -> None: ...

class THSituation(_message.Message):
    __slots__ = ("SituationInfo", "SituationSides")
    class SituationSidesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THSituationSide
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THSituationSide, _Mapping]] = ...) -> None: ...
    SITUATIONINFO_FIELD_NUMBER: _ClassVar[int]
    SITUATIONSIDES_FIELD_NUMBER: _ClassVar[int]
    SituationInfo: THSituationInfo
    SituationSides: _containers.MessageMap[str, THSituationSide]
    def __init__(self, SituationInfo: _Optional[_Union[THSituationInfo, _Mapping]] = ..., SituationSides: _Optional[_Mapping[str, THSituationSide]] = ...) -> None: ...

class THSituationFull(_message.Message):
    __slots__ = ("ScenarioInfo", "Events", "Situation")
    SCENARIOINFO_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    SITUATION_FIELD_NUMBER: _ClassVar[int]
    ScenarioInfo: THScenarioInfo
    Events: THEventColl
    Situation: THSituation
    def __init__(self, ScenarioInfo: _Optional[_Union[THScenarioInfo, _Mapping]] = ..., Events: _Optional[_Union[THEventColl, _Mapping]] = ..., Situation: _Optional[_Union[THSituation, _Mapping]] = ...) -> None: ...

class THUnitOffGridInfo(_message.Message):
    __slots__ = ("SideID", "UnitName", "UnitID", "UnitClass", "Reason")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    UNITCLASS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SideID: str
    UnitName: str
    UnitID: str
    UnitClass: str
    Reason: str
    def __init__(self, SideID: _Optional[str] = ..., UnitName: _Optional[str] = ..., UnitID: _Optional[str] = ..., UnitClass: _Optional[str] = ..., Reason: _Optional[str] = ...) -> None: ...

class THWeaponSalvoList(_message.Message):
    __slots__ = ("SideID", "WeaponSalvos")
    class WeaponSalvosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THWeaponSalvo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THWeaponSalvo, _Mapping]] = ...) -> None: ...
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    WEAPONSALVOS_FIELD_NUMBER: _ClassVar[int]
    SideID: str
    WeaponSalvos: _containers.MessageMap[str, THWeaponSalvo]
    def __init__(self, SideID: _Optional[str] = ..., WeaponSalvos: _Optional[_Mapping[str, THWeaponSalvo]] = ...) -> None: ...

class THMissionInfo(_message.Message):
    __slots__ = ("RoomID", "MissionID", "MissionName", "MissionClass", "Time", "Type")
    ROOMID_FIELD_NUMBER: _ClassVar[int]
    MISSIONID_FIELD_NUMBER: _ClassVar[int]
    MISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    MISSIONCLASS_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RoomID: str
    MissionID: str
    MissionName: str
    MissionClass: int
    Time: int
    Type: int
    def __init__(self, RoomID: _Optional[str] = ..., MissionID: _Optional[str] = ..., MissionName: _Optional[str] = ..., MissionClass: _Optional[int] = ..., Time: _Optional[int] = ..., Type: _Optional[int] = ...) -> None: ...

class THContactRemoveInfo(_message.Message):
    __slots__ = ("ID", "Name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID: str
    Name: str
    def __init__(self, ID: _Optional[str] = ..., Name: _Optional[str] = ...) -> None: ...

class THSideChange(_message.Message):
    __slots__ = ("IsAddSide", "SideInfo")
    ISADDSIDE_FIELD_NUMBER: _ClassVar[int]
    SIDEINFO_FIELD_NUMBER: _ClassVar[int]
    IsAddSide: bool
    SideInfo: THSideInfo
    def __init__(self, IsAddSide: bool = ..., SideInfo: _Optional[_Union[THSideInfo, _Mapping]] = ...) -> None: ...

class THEventActive(_message.Message):
    __slots__ = ("Name", "Status", "Time", "ID", "Type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Status: bool
    Time: int
    ID: str
    Type: int
    def __init__(self, Name: _Optional[str] = ..., Status: bool = ..., Time: _Optional[int] = ..., ID: _Optional[str] = ..., Type: _Optional[int] = ...) -> None: ...

class THEventTriggers_Status(_message.Message):
    __slots__ = ("EventActives",)
    class EventActivesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: THEventActive
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[THEventActive, _Mapping]] = ...) -> None: ...
    EVENTACTIVES_FIELD_NUMBER: _ClassVar[int]
    EventActives: _containers.MessageMap[str, THEventActive]
    def __init__(self, EventActives: _Optional[_Mapping[str, THEventActive]] = ...) -> None: ...

class THMissionMinningInfo(_message.Message):
    __slots__ = ("Type", "MinningUnitID", "MinningUnitName", "Position", "MineType", "MineNum")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MINNINGUNITID_FIELD_NUMBER: _ClassVar[int]
    MINNINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    MINETYPE_FIELD_NUMBER: _ClassVar[int]
    MINENUM_FIELD_NUMBER: _ClassVar[int]
    Type: int
    MinningUnitID: str
    MinningUnitName: str
    Position: THPosition
    MineType: int
    MineNum: int
    def __init__(self, Type: _Optional[int] = ..., MinningUnitID: _Optional[str] = ..., MinningUnitName: _Optional[str] = ..., Position: _Optional[_Union[THPosition, _Mapping]] = ..., MineType: _Optional[int] = ..., MineNum: _Optional[int] = ...) -> None: ...

class THMissionMineClearingInfo(_message.Message):
    __slots__ = ("Type", "MineClearingUnitID", "MineClearingUnitName", "Position", "MineClearingType", "MineClearingNum")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MINECLEARINGUNITID_FIELD_NUMBER: _ClassVar[int]
    MINECLEARINGUNITNAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    MINECLEARINGTYPE_FIELD_NUMBER: _ClassVar[int]
    MINECLEARINGNUM_FIELD_NUMBER: _ClassVar[int]
    Type: int
    MineClearingUnitID: str
    MineClearingUnitName: str
    Position: THPosition
    MineClearingType: int
    MineClearingNum: int
    def __init__(self, Type: _Optional[int] = ..., MineClearingUnitID: _Optional[str] = ..., MineClearingUnitName: _Optional[str] = ..., Position: _Optional[_Union[THPosition, _Mapping]] = ..., MineClearingType: _Optional[int] = ..., MineClearingNum: _Optional[int] = ...) -> None: ...

class THRefuelingInfo(_message.Message):
    __slots__ = ("Type", "FuelUnitID", "FuelUnitName", "RefuelUnitID", "RefuelUnitName", "FuelType", "FuelCapacity")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FUELUNITID_FIELD_NUMBER: _ClassVar[int]
    FUELUNITNAME_FIELD_NUMBER: _ClassVar[int]
    REFUELUNITID_FIELD_NUMBER: _ClassVar[int]
    REFUELUNITNAME_FIELD_NUMBER: _ClassVar[int]
    FUELTYPE_FIELD_NUMBER: _ClassVar[int]
    FUELCAPACITY_FIELD_NUMBER: _ClassVar[int]
    Type: int
    FuelUnitID: str
    FuelUnitName: str
    RefuelUnitID: str
    RefuelUnitName: str
    FuelType: bytes
    FuelCapacity: int
    def __init__(self, Type: _Optional[int] = ..., FuelUnitID: _Optional[str] = ..., FuelUnitName: _Optional[str] = ..., RefuelUnitID: _Optional[str] = ..., RefuelUnitName: _Optional[str] = ..., FuelType: _Optional[bytes] = ..., FuelCapacity: _Optional[int] = ...) -> None: ...

class THCommunicationEventInfo(_message.Message):
    __slots__ = ("dfSimTime", "SendID", "SendName", "SendSideID", "ReceiverID", "ReceiverName", "ReceiverSideID", "ResultType", "Time")
    DFSIMTIME_FIELD_NUMBER: _ClassVar[int]
    SENDID_FIELD_NUMBER: _ClassVar[int]
    SENDNAME_FIELD_NUMBER: _ClassVar[int]
    SENDSIDEID_FIELD_NUMBER: _ClassVar[int]
    RECEIVERID_FIELD_NUMBER: _ClassVar[int]
    RECEIVERNAME_FIELD_NUMBER: _ClassVar[int]
    RECEIVERSIDEID_FIELD_NUMBER: _ClassVar[int]
    RESULTTYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    dfSimTime: float
    SendID: str
    SendName: str
    SendSideID: str
    ReceiverID: str
    ReceiverName: str
    ReceiverSideID: str
    ResultType: int
    Time: int
    def __init__(self, dfSimTime: _Optional[float] = ..., SendID: _Optional[str] = ..., SendName: _Optional[str] = ..., SendSideID: _Optional[str] = ..., ReceiverID: _Optional[str] = ..., ReceiverName: _Optional[str] = ..., ReceiverSideID: _Optional[str] = ..., ResultType: _Optional[int] = ..., Time: _Optional[int] = ...) -> None: ...

class THCommandLogInfo(_message.Message):
    __slots__ = ("commandName", "commandParam")
    COMMANDNAME_FIELD_NUMBER: _ClassVar[int]
    COMMANDPARAM_FIELD_NUMBER: _ClassVar[int]
    commandName: str
    commandParam: str
    def __init__(self, commandName: _Optional[str] = ..., commandParam: _Optional[str] = ...) -> None: ...

class THCargoInfo(_message.Message):
    __slots__ = ("Type", "CargoUnitID", "CargoType", "CargoVal", "CargoID")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CARGOUNITID_FIELD_NUMBER: _ClassVar[int]
    CARGOTYPE_FIELD_NUMBER: _ClassVar[int]
    CARGOVAL_FIELD_NUMBER: _ClassVar[int]
    CARGOID_FIELD_NUMBER: _ClassVar[int]
    Type: int
    CargoUnitID: str
    CargoType: int
    CargoVal: int
    CargoID: str
    def __init__(self, Type: _Optional[int] = ..., CargoUnitID: _Optional[str] = ..., CargoType: _Optional[int] = ..., CargoVal: _Optional[int] = ..., CargoID: _Optional[str] = ...) -> None: ...

class THNewBornClcomm(_message.Message):
    __slots__ = ("sideID", "clcommType", "clcommID", "memberIDs", "clcommName")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    CLCOMMTYPE_FIELD_NUMBER: _ClassVar[int]
    CLCOMMID_FIELD_NUMBER: _ClassVar[int]
    MEMBERIDS_FIELD_NUMBER: _ClassVar[int]
    CLCOMMNAME_FIELD_NUMBER: _ClassVar[int]
    sideID: str
    clcommType: int
    clcommID: str
    memberIDs: _containers.RepeatedScalarFieldContainer[str]
    clcommName: str
    def __init__(self, sideID: _Optional[str] = ..., clcommType: _Optional[int] = ..., clcommID: _Optional[str] = ..., memberIDs: _Optional[_Iterable[str]] = ..., clcommName: _Optional[str] = ...) -> None: ...

class THDeleteClcomm(_message.Message):
    __slots__ = ("sideID", "clcommID")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    CLCOMMID_FIELD_NUMBER: _ClassVar[int]
    sideID: str
    clcommID: str
    def __init__(self, sideID: _Optional[str] = ..., clcommID: _Optional[str] = ...) -> None: ...
