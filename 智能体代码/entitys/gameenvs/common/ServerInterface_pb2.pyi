from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EWRA_WeaponTargetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Null: _ClassVar[EWRA_WeaponTargetType]
    None: _ClassVar[EWRA_WeaponTargetType]
    Decoy: _ClassVar[EWRA_WeaponTargetType]
    Air_Contact_Unknown_Type: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_5th_Generation: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_4th_Generation: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_3rd_Generation: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Less_Capable: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_High_Perf_Bombers: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Medium_Perf_Bombers: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Low_Perf_Bombers: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_High_Perf_Recon_EW: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Medium_Perf_Recon_EW: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Low_Perf_Recon_EW: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_AEW: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_MicroUAV: _ClassVar[EWRA_WeaponTargetType]
    Aircraft_Tanker: _ClassVar[EWRA_WeaponTargetType]
    Helicopter_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Supersonic_Sea_Skimming: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Subsonic_Sea_Skimming: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Supersonic: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Subsonic: _ClassVar[EWRA_WeaponTargetType]
    Guided_Weapon_Ballistic: _ClassVar[EWRA_WeaponTargetType]
    Satellite_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    C_RAM: _ClassVar[EWRA_WeaponTargetType]
    Surface_Contact_Unknown_Type: _ClassVar[EWRA_WeaponTargetType]
    Ship_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Ship_Carrier_0_25000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Carrier_25001_45000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Carrier_45001_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Carrier_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_0_500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_501_1500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_1501_5000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_5001_10000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_10001_25000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_25001_45000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_45001_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Surface_Combatant_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_0_500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_501_1500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_1501_5000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_5001_10000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_10001_25000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_25001_45000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_45001_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Amphibious_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_0_500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_501_1500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_1501_5000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_5001_10000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_10001_25000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_25001_45000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_45001_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Auxiliary_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_0_500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_501_1500_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_1501_5000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_5001_10000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_10001_25000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_25001_45000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_45001_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Ship_Merchant_Civilian_95000_tons: _ClassVar[EWRA_WeaponTargetType]
    Submarine_Surfaced: _ClassVar[EWRA_WeaponTargetType]
    Subsurface_Contact_Unknown_Type: _ClassVar[EWRA_WeaponTargetType]
    Submarine_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Land_Contact_Unknown_Type: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Building_Surface: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Building_Reveted: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Structure_Open: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Structure_Reveted: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Soft_Aerostat_Moring: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Building_Surface: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Building_Reveted: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Building_Bunker: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Building_Underground: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Structure_Open: _ClassVar[EWRA_WeaponTargetType]
    Land_Structure_Hardened_Structure_Reveted: _ClassVar[EWRA_WeaponTargetType]
    Runway_Facility_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Runway: _ClassVar[EWRA_WeaponTargetType]
    Runway_Grade_Taxiway: _ClassVar[EWRA_WeaponTargetType]
    Runway_Access_Point: _ClassVar[EWRA_WeaponTargetType]
    Radar_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Mobile_Target_Soft_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Mobile_Target_Soft_Mobile_Vehicle: _ClassVar[EWRA_WeaponTargetType]
    Mobile_Target_Soft_Mobile_Personnel: _ClassVar[EWRA_WeaponTargetType]
    Mobile_Target_Hardened_Unspecified: _ClassVar[EWRA_WeaponTargetType]
    Mobile_Target_Hardened_Mobile_Vehicle: _ClassVar[EWRA_WeaponTargetType]
    Underwater_Structure: _ClassVar[EWRA_WeaponTargetType]
    Air_Base_Single_Unit_Airfield: _ClassVar[EWRA_WeaponTargetType]
Null: EWRA_WeaponTargetType
None: EWRA_WeaponTargetType
Decoy: EWRA_WeaponTargetType
Air_Contact_Unknown_Type: EWRA_WeaponTargetType
Aircraft_Unspecified: EWRA_WeaponTargetType
Aircraft_5th_Generation: EWRA_WeaponTargetType
Aircraft_4th_Generation: EWRA_WeaponTargetType
Aircraft_3rd_Generation: EWRA_WeaponTargetType
Aircraft_Less_Capable: EWRA_WeaponTargetType
Aircraft_High_Perf_Bombers: EWRA_WeaponTargetType
Aircraft_Medium_Perf_Bombers: EWRA_WeaponTargetType
Aircraft_Low_Perf_Bombers: EWRA_WeaponTargetType
Aircraft_High_Perf_Recon_EW: EWRA_WeaponTargetType
Aircraft_Medium_Perf_Recon_EW: EWRA_WeaponTargetType
Aircraft_Low_Perf_Recon_EW: EWRA_WeaponTargetType
Aircraft_AEW: EWRA_WeaponTargetType
Aircraft_MicroUAV: EWRA_WeaponTargetType
Aircraft_Tanker: EWRA_WeaponTargetType
Helicopter_Unspecified: EWRA_WeaponTargetType
Guided_Weapon_Unspecified: EWRA_WeaponTargetType
Guided_Weapon_Supersonic_Sea_Skimming: EWRA_WeaponTargetType
Guided_Weapon_Subsonic_Sea_Skimming: EWRA_WeaponTargetType
Guided_Weapon_Supersonic: EWRA_WeaponTargetType
Guided_Weapon_Subsonic: EWRA_WeaponTargetType
Guided_Weapon_Ballistic: EWRA_WeaponTargetType
Satellite_Unspecified: EWRA_WeaponTargetType
C_RAM: EWRA_WeaponTargetType
Surface_Contact_Unknown_Type: EWRA_WeaponTargetType
Ship_Unspecified: EWRA_WeaponTargetType
Ship_Carrier_0_25000_tons: EWRA_WeaponTargetType
Ship_Carrier_25001_45000_tons: EWRA_WeaponTargetType
Ship_Carrier_45001_95000_tons: EWRA_WeaponTargetType
Ship_Carrier_95000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_0_500_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_501_1500_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_1501_5000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_5001_10000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_10001_25000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_25001_45000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_45001_95000_tons: EWRA_WeaponTargetType
Ship_Surface_Combatant_95000_tons: EWRA_WeaponTargetType
Ship_Amphibious_0_500_tons: EWRA_WeaponTargetType
Ship_Amphibious_501_1500_tons: EWRA_WeaponTargetType
Ship_Amphibious_1501_5000_tons: EWRA_WeaponTargetType
Ship_Amphibious_5001_10000_tons: EWRA_WeaponTargetType
Ship_Amphibious_10001_25000_tons: EWRA_WeaponTargetType
Ship_Amphibious_25001_45000_tons: EWRA_WeaponTargetType
Ship_Amphibious_45001_95000_tons: EWRA_WeaponTargetType
Ship_Amphibious_95000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_0_500_tons: EWRA_WeaponTargetType
Ship_Auxiliary_501_1500_tons: EWRA_WeaponTargetType
Ship_Auxiliary_1501_5000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_5001_10000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_10001_25000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_25001_45000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_45001_95000_tons: EWRA_WeaponTargetType
Ship_Auxiliary_95000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_0_500_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_501_1500_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_1501_5000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_5001_10000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_10001_25000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_25001_45000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_45001_95000_tons: EWRA_WeaponTargetType
Ship_Merchant_Civilian_95000_tons: EWRA_WeaponTargetType
Submarine_Surfaced: EWRA_WeaponTargetType
Subsurface_Contact_Unknown_Type: EWRA_WeaponTargetType
Submarine_Unspecified: EWRA_WeaponTargetType
Land_Contact_Unknown_Type: EWRA_WeaponTargetType
Land_Structure_Soft_Unspecified: EWRA_WeaponTargetType
Land_Structure_Soft_Building_Surface: EWRA_WeaponTargetType
Land_Structure_Soft_Building_Reveted: EWRA_WeaponTargetType
Land_Structure_Soft_Structure_Open: EWRA_WeaponTargetType
Land_Structure_Soft_Structure_Reveted: EWRA_WeaponTargetType
Land_Structure_Soft_Aerostat_Moring: EWRA_WeaponTargetType
Land_Structure_Hardened_Unspecified: EWRA_WeaponTargetType
Land_Structure_Hardened_Building_Surface: EWRA_WeaponTargetType
Land_Structure_Hardened_Building_Reveted: EWRA_WeaponTargetType
Land_Structure_Hardened_Building_Bunker: EWRA_WeaponTargetType
Land_Structure_Hardened_Building_Underground: EWRA_WeaponTargetType
Land_Structure_Hardened_Structure_Open: EWRA_WeaponTargetType
Land_Structure_Hardened_Structure_Reveted: EWRA_WeaponTargetType
Runway_Facility_Unspecified: EWRA_WeaponTargetType
Runway: EWRA_WeaponTargetType
Runway_Grade_Taxiway: EWRA_WeaponTargetType
Runway_Access_Point: EWRA_WeaponTargetType
Radar_Unspecified: EWRA_WeaponTargetType
Mobile_Target_Soft_Unspecified: EWRA_WeaponTargetType
Mobile_Target_Soft_Mobile_Vehicle: EWRA_WeaponTargetType
Mobile_Target_Soft_Mobile_Personnel: EWRA_WeaponTargetType
Mobile_Target_Hardened_Unspecified: EWRA_WeaponTargetType
Mobile_Target_Hardened_Mobile_Vehicle: EWRA_WeaponTargetType
Underwater_Structure: EWRA_WeaponTargetType
Air_Base_Single_Unit_Airfield: EWRA_WeaponTargetType

class RequestEmpty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RequestExecuteRegister(_message.Message):
    __slots__ = ("rid", "exit", "side", "aiagent", "username", "cmdsrc", "runmode")
    RID_FIELD_NUMBER: _ClassVar[int]
    EXIT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    AIAGENT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CMDSRC_FIELD_NUMBER: _ClassVar[int]
    RUNMODE_FIELD_NUMBER: _ClassVar[int]
    rid: int
    exit: bool
    side: str
    aiagent: str
    username: str
    cmdsrc: int
    runmode: int
    def __init__(self, rid: _Optional[int] = ..., exit: bool = ..., side: _Optional[str] = ..., aiagent: _Optional[str] = ..., username: _Optional[str] = ..., cmdsrc: _Optional[int] = ..., runmode: _Optional[int] = ...) -> None: ...

class ReplyExecuteRegister(_message.Message):
    __slots__ = ("code", "message", "version", "rid")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RID_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    version: str
    rid: int
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., version: _Optional[str] = ..., rid: _Optional[int] = ...) -> None: ...

class Reply(_message.Message):
    __slots__ = ("code", "result")
    CODE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    code: int
    result: bytes
    def __init__(self, code: _Optional[int] = ..., result: _Optional[bytes] = ...) -> None: ...

class ExecuteBatchPara(_message.Message):
    __slots__ = ("function", "para")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    PARA_FIELD_NUMBER: _ClassVar[int]
    function: str
    para: bytes
    def __init__(self, function: _Optional[str] = ..., para: _Optional[bytes] = ...) -> None: ...

class RequestExecuteBatch(_message.Message):
    __slots__ = ("jumpError", "batchPara")
    JUMPERROR_FIELD_NUMBER: _ClassVar[int]
    BATCHPARA_FIELD_NUMBER: _ClassVar[int]
    jumpError: bool
    batchPara: _containers.RepeatedCompositeFieldContainer[ExecuteBatchPara]
    def __init__(self, jumpError: bool = ..., batchPara: _Optional[_Iterable[_Union[ExecuteBatchPara, _Mapping]]] = ...) -> None: ...

class ReplyExecuteBatch(_message.Message):
    __slots__ = ("reply",)
    REPLY_FIELD_NUMBER: _ClassVar[int]
    reply: _containers.RepeatedCompositeFieldContainer[Reply]
    def __init__(self, reply: _Optional[_Iterable[_Union[Reply, _Mapping]]] = ...) -> None: ...

class RequestExecuteLua(_message.Message):
    __slots__ = ("script",)
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    script: str
    def __init__(self, script: _Optional[str] = ...) -> None: ...

class GeoPosition(_message.Message):
    __slots__ = ("longitude", "latitude", "altitude")
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    longitude: float
    latitude: float
    altitude: float
    def __init__(self, longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., altitude: _Optional[float] = ...) -> None: ...

class Waypoint(_message.Message):
    __slots__ = ("position", "speed", "altitude", "name")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    position: GeoPosition
    speed: float
    altitude: float
    name: str
    def __init__(self, position: _Optional[_Union[GeoPosition, _Mapping]] = ..., speed: _Optional[float] = ..., altitude: _Optional[float] = ..., name: _Optional[str] = ...) -> None: ...

class BaseUnitInfo(_message.Message):
    __slots__ = ("guid", "side", "name")
    GUID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    side: str
    name: str
    def __init__(self, guid: _Optional[str] = ..., side: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class BaseMissionInfo(_message.Message):
    __slots__ = ("side", "missionName", "missionGuid", "missionType")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    MISSIONTYPE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionName: str
    missionGuid: str
    missionType: str
    def __init__(self, side: _Optional[str] = ..., missionName: _Optional[str] = ..., missionGuid: _Optional[str] = ..., missionType: _Optional[str] = ...) -> None: ...

class SimpleRequest(_message.Message):
    __slots__ = ("rid", "type", "para", "remark")
    RID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PARA_FIELD_NUMBER: _ClassVar[int]
    REMARK_FIELD_NUMBER: _ClassVar[int]
    rid: int
    type: int
    para: str
    remark: str
    def __init__(self, rid: _Optional[int] = ..., type: _Optional[int] = ..., para: _Optional[str] = ..., remark: _Optional[str] = ...) -> None: ...

class RequestDelete(_message.Message):
    __slots__ = ("guids",)
    GUIDS_FIELD_NUMBER: _ClassVar[int]
    guids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, guids: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestRename(_message.Message):
    __slots__ = ("guid", "name")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RequestGet(_message.Message):
    __slots__ = ("guid",)
    GUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    def __init__(self, guid: _Optional[str] = ...) -> None: ...

class RequestMissionDelete(_message.Message):
    __slots__ = ("side", "missionid")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONID_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionid: str
    def __init__(self, side: _Optional[str] = ..., missionid: _Optional[str] = ...) -> None: ...

class RequestMissionRename(_message.Message):
    __slots__ = ("side", "missionid", "newname")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONID_FIELD_NUMBER: _ClassVar[int]
    NEWNAME_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionid: str
    newname: str
    def __init__(self, side: _Optional[str] = ..., missionid: _Optional[str] = ..., newname: _Optional[str] = ...) -> None: ...

class RequestNewScenario(_message.Message):
    __slots__ = ("scenName", "dbName")
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    DBNAME_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    dbName: str
    def __init__(self, scenName: _Optional[str] = ..., dbName: _Optional[str] = ...) -> None: ...

class RequestLoadScenario(_message.Message):
    __slots__ = ("scenName", "loadScheme")
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    LOADSCHEME_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    loadScheme: int
    def __init__(self, scenName: _Optional[str] = ..., loadScheme: _Optional[int] = ...) -> None: ...

class RequestSaveScenario(_message.Message):
    __slots__ = ("scenName", "scenContent")
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    SCENCONTENT_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    scenContent: str
    def __init__(self, scenName: _Optional[str] = ..., scenContent: _Optional[str] = ...) -> None: ...

class RequestSetScenarioInfo(_message.Message):
    __slots__ = ("currentTime", "startTime", "duration", "complexity", "difficulty", "location", "featureOption", "title", "description", "postureColor")
    CURRENTTIME_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    COMPLEXITY_FIELD_NUMBER: _ClassVar[int]
    DIFFICULTY_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    FEATUREOPTION_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    POSTURECOLOR_FIELD_NUMBER: _ClassVar[int]
    currentTime: str
    startTime: str
    duration: int
    complexity: int
    difficulty: int
    location: str
    featureOption: str
    title: str
    description: str
    postureColor: str
    def __init__(self, currentTime: _Optional[str] = ..., startTime: _Optional[str] = ..., duration: _Optional[int] = ..., complexity: _Optional[int] = ..., difficulty: _Optional[int] = ..., location: _Optional[str] = ..., featureOption: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., postureColor: _Optional[str] = ...) -> None: ...

class RequestGetScenarioInfo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MIFileInfo(_message.Message):
    __slots__ = ("name", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class MIFileList(_message.Message):
    __slots__ = ("fileinfos",)
    FILEINFOS_FIELD_NUMBER: _ClassVar[int]
    fileinfos: _containers.RepeatedCompositeFieldContainer[MIFileInfo]
    def __init__(self, fileinfos: _Optional[_Iterable[_Union[MIFileInfo, _Mapping]]] = ...) -> None: ...

class RequestGetScenarioList(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RequestGetScenarioBasicInfo(_message.Message):
    __slots__ = ("scenName",)
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    def __init__(self, scenName: _Optional[str] = ...) -> None: ...

class RequestGetScenarioContent(_message.Message):
    __slots__ = ("scenName",)
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    def __init__(self, scenName: _Optional[str] = ...) -> None: ...

class RequestSetSimulationStatus(_message.Message):
    __slots__ = ("status", "duration")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    status: str
    duration: int
    def __init__(self, status: _Optional[str] = ..., duration: _Optional[int] = ...) -> None: ...

class RequestSetSimulationSpeed(_message.Message):
    __slots__ = ("speed",)
    SPEED_FIELD_NUMBER: _ClassVar[int]
    speed: int
    def __init__(self, speed: _Optional[int] = ...) -> None: ...

class RequestAddSide(_message.Message):
    __slots__ = ("guid", "name")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RequestRemoveSide(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class MISideList(_message.Message):
    __slots__ = ("infos",)
    class InfosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INFOS_FIELD_NUMBER: _ClassVar[int]
    infos: _containers.ScalarMap[str, str]
    def __init__(self, infos: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RequestGetSideList(_message.Message):
    __slots__ = ("scenName",)
    SCENNAME_FIELD_NUMBER: _ClassVar[int]
    scenName: str
    def __init__(self, scenName: _Optional[str] = ...) -> None: ...

class RequestSetSidePosture(_message.Message):
    __slots__ = ("sideA", "sideB", "posture")
    SIDEA_FIELD_NUMBER: _ClassVar[int]
    SIDEB_FIELD_NUMBER: _ClassVar[int]
    POSTURE_FIELD_NUMBER: _ClassVar[int]
    sideA: str
    sideB: str
    posture: str
    def __init__(self, sideA: _Optional[str] = ..., sideB: _Optional[str] = ..., posture: _Optional[str] = ...) -> None: ...

class RequestGetSidePosture(_message.Message):
    __slots__ = ("sideA", "sideB")
    SIDEA_FIELD_NUMBER: _ClassVar[int]
    SIDEB_FIELD_NUMBER: _ClassVar[int]
    sideA: str
    sideB: str
    def __init__(self, sideA: _Optional[str] = ..., sideB: _Optional[str] = ...) -> None: ...

class RequestSetSideOptions(_message.Message):
    __slots__ = ("side", "awareness", "proficiency", "isAIOnly", "cameraLon", "cameraLat", "cameraAlt")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    AWARENESS_FIELD_NUMBER: _ClassVar[int]
    PROFICIENCY_FIELD_NUMBER: _ClassVar[int]
    ISAIONLY_FIELD_NUMBER: _ClassVar[int]
    CAMERALON_FIELD_NUMBER: _ClassVar[int]
    CAMERALAT_FIELD_NUMBER: _ClassVar[int]
    CAMERAALT_FIELD_NUMBER: _ClassVar[int]
    side: str
    awareness: str
    proficiency: str
    isAIOnly: bool
    cameraLon: float
    cameraLat: float
    cameraAlt: float
    def __init__(self, side: _Optional[str] = ..., awareness: _Optional[str] = ..., proficiency: _Optional[str] = ..., isAIOnly: bool = ..., cameraLon: _Optional[float] = ..., cameraLat: _Optional[float] = ..., cameraAlt: _Optional[float] = ...) -> None: ...

class RequestGetSideOptions(_message.Message):
    __slots__ = ("side",)
    SIDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    def __init__(self, side: _Optional[str] = ...) -> None: ...

class RequestSetSideScore(_message.Message):
    __slots__ = ("side", "score", "reason")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    side: str
    score: int
    reason: str
    def __init__(self, side: _Optional[str] = ..., score: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class RequestGetSideScore(_message.Message):
    __slots__ = ("side",)
    SIDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    def __init__(self, side: _Optional[str] = ...) -> None: ...

class RequestGetSideUnitLoss(_message.Message):
    __slots__ = ("side",)
    SIDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    def __init__(self, side: _Optional[str] = ...) -> None: ...

class RequestAddUnit(_message.Message):
    __slots__ = ("side", "unitType", "name", "position", "heading", "dbid", "guid", "loadoutid", "orbit", "base", "count", "source")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    UNITTYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    LOADOUTID_FIELD_NUMBER: _ClassVar[int]
    ORBIT_FIELD_NUMBER: _ClassVar[int]
    BASE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    unitType: str
    name: str
    position: GeoPosition
    heading: float
    dbid: int
    guid: str
    loadoutid: int
    orbit: int
    base: str
    count: int
    source: int
    def __init__(self, side: _Optional[str] = ..., unitType: _Optional[str] = ..., name: _Optional[str] = ..., position: _Optional[_Union[GeoPosition, _Mapping]] = ..., heading: _Optional[float] = ..., dbid: _Optional[int] = ..., guid: _Optional[str] = ..., loadoutid: _Optional[int] = ..., orbit: _Optional[int] = ..., base: _Optional[str] = ..., count: _Optional[int] = ..., source: _Optional[int] = ...) -> None: ...

class RequestKillUnit(_message.Message):
    __slots__ = ("guid",)
    GUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    def __init__(self, guid: _Optional[str] = ...) -> None: ...

class RequestSetUnitPosition(_message.Message):
    __slots__ = ("guid", "latitude", "longitude")
    GUID_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    latitude: float
    longitude: float
    def __init__(self, guid: _Optional[str] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class RequestSetUnitHeading(_message.Message):
    __slots__ = ("guid", "heading")
    GUID_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    guid: str
    heading: float
    def __init__(self, guid: _Optional[str] = ..., heading: _Optional[float] = ...) -> None: ...

class RequestSetUnitSpeed(_message.Message):
    __slots__ = ("guid", "speed")
    GUID_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    guid: str
    speed: float
    def __init__(self, guid: _Optional[str] = ..., speed: _Optional[float] = ...) -> None: ...

class RequestSetUnitHeight(_message.Message):
    __slots__ = ("guid", "height")
    GUID_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    height: str
    def __init__(self, guid: _Optional[str] = ..., height: _Optional[str] = ...) -> None: ...

class RequestSetUnitDesiredHeight(_message.Message):
    __slots__ = ("guid", "desiredHeight")
    GUID_FIELD_NUMBER: _ClassVar[int]
    DESIREDHEIGHT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    desiredHeight: str
    def __init__(self, guid: _Optional[str] = ..., desiredHeight: _Optional[str] = ...) -> None: ...

class RequestSetUnitPresetHeight(_message.Message):
    __slots__ = ("guid", "presetHeight")
    GUID_FIELD_NUMBER: _ClassVar[int]
    PRESETHEIGHT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    presetHeight: str
    def __init__(self, guid: _Optional[str] = ..., presetHeight: _Optional[str] = ...) -> None: ...

class RequestSetUnitDesiredSpeed(_message.Message):
    __slots__ = ("guid", "desiredSpeed")
    GUID_FIELD_NUMBER: _ClassVar[int]
    DESIREDSPEED_FIELD_NUMBER: _ClassVar[int]
    guid: str
    desiredSpeed: str
    def __init__(self, guid: _Optional[str] = ..., desiredSpeed: _Optional[str] = ...) -> None: ...

class RequestSetUnitPresetThrottle(_message.Message):
    __slots__ = ("guid", "presetThrottle")
    GUID_FIELD_NUMBER: _ClassVar[int]
    PRESETTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    presetThrottle: str
    def __init__(self, guid: _Optional[str] = ..., presetThrottle: _Optional[str] = ...) -> None: ...

class RequestSetUnitAutoDetectable(_message.Message):
    __slots__ = ("guid", "autoDetectable")
    GUID_FIELD_NUMBER: _ClassVar[int]
    AUTODETECTABLE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    autoDetectable: bool
    def __init__(self, guid: _Optional[str] = ..., autoDetectable: bool = ...) -> None: ...

class RequestSetUnitSide(_message.Message):
    __slots__ = ("guid", "newSide")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NEWSIDE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    newSide: str
    def __init__(self, guid: _Optional[str] = ..., newSide: _Optional[str] = ...) -> None: ...

class RequestSetUnitDamage(_message.Message):
    __slots__ = ("guid", "damageValue")
    GUID_FIELD_NUMBER: _ClassVar[int]
    DAMAGEVALUE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    damageValue: float
    def __init__(self, guid: _Optional[str] = ..., damageValue: _Optional[float] = ...) -> None: ...

class THFuelInfo(_message.Message):
    __slots__ = ("type", "capacity")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    type: int
    capacity: int
    def __init__(self, type: _Optional[int] = ..., capacity: _Optional[int] = ...) -> None: ...

class RequestSetUnitFuel(_message.Message):
    __slots__ = ("guid", "fuel")
    GUID_FIELD_NUMBER: _ClassVar[int]
    FUEL_FIELD_NUMBER: _ClassVar[int]
    guid: str
    fuel: _containers.RepeatedCompositeFieldContainer[THFuelInfo]
    def __init__(self, guid: _Optional[str] = ..., fuel: _Optional[_Iterable[_Union[THFuelInfo, _Mapping]]] = ...) -> None: ...

class RequestSetUnitReturnToBase(_message.Message):
    __slots__ = ("guid", "returnToBase")
    GUID_FIELD_NUMBER: _ClassVar[int]
    RETURNTOBASE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    returnToBase: bool
    def __init__(self, guid: _Optional[str] = ..., returnToBase: bool = ...) -> None: ...

class RequestRefuelUnit(_message.Message):
    __slots__ = ("guid",)
    GUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    def __init__(self, guid: _Optional[str] = ...) -> None: ...

class RequestSetUnitTerrainFollow(_message.Message):
    __slots__ = ("guid", "terrainFollow")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TERRAINFOLLOW_FIELD_NUMBER: _ClassVar[int]
    guid: str
    terrainFollow: bool
    def __init__(self, guid: _Optional[str] = ..., terrainFollow: bool = ...) -> None: ...

class RequestSetUnitCourse(_message.Message):
    __slots__ = ("guid", "course")
    GUID_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    course: _containers.RepeatedCompositeFieldContainer[Waypoint]
    def __init__(self, guid: _Optional[str] = ..., course: _Optional[_Iterable[_Union[Waypoint, _Mapping]]] = ...) -> None: ...

class RequestAssignUnitToMission(_message.Message):
    __slots__ = ("unitGuids", "missionGuid")
    UNITGUIDS_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    unitGuids: _containers.RepeatedScalarFieldContainer[str]
    missionGuid: str
    def __init__(self, unitGuids: _Optional[_Iterable[str]] = ..., missionGuid: _Optional[str] = ...) -> None: ...

class RequestSetUnitSensorClassSwitch(_message.Message):
    __slots__ = ("guid", "radar", "sonar", "oecm")
    GUID_FIELD_NUMBER: _ClassVar[int]
    RADAR_FIELD_NUMBER: _ClassVar[int]
    SONAR_FIELD_NUMBER: _ClassVar[int]
    OECM_FIELD_NUMBER: _ClassVar[int]
    guid: str
    radar: bool
    sonar: bool
    oecm: bool
    def __init__(self, guid: _Optional[str] = ..., radar: bool = ..., sonar: bool = ..., oecm: bool = ...) -> None: ...

class RequestSetUnitSensorSwitch(_message.Message):
    __slots__ = ("guid", "sensorId", "active")
    GUID_FIELD_NUMBER: _ClassVar[int]
    SENSORID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    sensorId: str
    active: bool
    def __init__(self, guid: _Optional[str] = ..., sensorId: _Optional[str] = ..., active: bool = ...) -> None: ...

class RequestSetUnitEMCONAbide(_message.Message):
    __slots__ = ("guid", "abide")
    GUID_FIELD_NUMBER: _ClassVar[int]
    ABIDE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    abide: bool
    def __init__(self, guid: _Optional[str] = ..., abide: bool = ...) -> None: ...

class RequestAddUnitMount(_message.Message):
    __slots__ = ("guid", "mountDBID", "angle")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTDBID_FIELD_NUMBER: _ClassVar[int]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    mountDBID: int
    angle: str
    def __init__(self, guid: _Optional[str] = ..., mountDBID: _Optional[int] = ..., angle: _Optional[str] = ...) -> None: ...

class RequestDeleteUnitMount(_message.Message):
    __slots__ = ("guid", "mountGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    mountGuid: str
    def __init__(self, guid: _Optional[str] = ..., mountGuid: _Optional[str] = ...) -> None: ...

class RequestAddUnitMagazine(_message.Message):
    __slots__ = ("guid", "magazineDBID")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MAGAZINEDBID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    magazineDBID: int
    def __init__(self, guid: _Optional[str] = ..., magazineDBID: _Optional[int] = ...) -> None: ...

class RequestDeleteUnitMagazine(_message.Message):
    __slots__ = ("guid", "magazineGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MAGAZINEGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    magazineGuid: str
    def __init__(self, guid: _Optional[str] = ..., magazineGuid: _Optional[str] = ...) -> None: ...

class RequestAddUnitWeapon(_message.Message):
    __slots__ = ("guid", "mountGuid", "magazineGuid", "weaponDBID", "count", "weaponGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTGUID_FIELD_NUMBER: _ClassVar[int]
    MAGAZINEGUID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    WEAPONGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    mountGuid: str
    magazineGuid: str
    weaponDBID: int
    count: int
    weaponGuid: str
    def __init__(self, guid: _Optional[str] = ..., mountGuid: _Optional[str] = ..., magazineGuid: _Optional[str] = ..., weaponDBID: _Optional[int] = ..., count: _Optional[int] = ..., weaponGuid: _Optional[str] = ...) -> None: ...

class RequestDeleteUnitWeapon(_message.Message):
    __slots__ = ("guid", "mountGuid", "magazineGuid", "weaponGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTGUID_FIELD_NUMBER: _ClassVar[int]
    MAGAZINEGUID_FIELD_NUMBER: _ClassVar[int]
    WEAPONGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    mountGuid: str
    magazineGuid: str
    weaponGuid: str
    def __init__(self, guid: _Optional[str] = ..., mountGuid: _Optional[str] = ..., magazineGuid: _Optional[str] = ..., weaponGuid: _Optional[str] = ...) -> None: ...

class RequestAddUnitSensor(_message.Message):
    __slots__ = ("guid", "sensorDBID", "arcDetect", "arcTrack")
    GUID_FIELD_NUMBER: _ClassVar[int]
    SENSORDBID_FIELD_NUMBER: _ClassVar[int]
    ARCDETECT_FIELD_NUMBER: _ClassVar[int]
    ARCTRACK_FIELD_NUMBER: _ClassVar[int]
    guid: str
    sensorDBID: int
    arcDetect: _containers.RepeatedScalarFieldContainer[str]
    arcTrack: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, guid: _Optional[str] = ..., sensorDBID: _Optional[int] = ..., arcDetect: _Optional[_Iterable[str]] = ..., arcTrack: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestDeleteUnitSensor(_message.Message):
    __slots__ = ("guid", "sensorGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    SENSORGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    sensorGuid: str
    def __init__(self, guid: _Optional[str] = ..., sensorGuid: _Optional[str] = ...) -> None: ...

class RequestSetUnitWeaponReloadPriority(_message.Message):
    __slots__ = ("guid", "mountGuid", "weaponDBID", "enabled")
    GUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTGUID_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    guid: str
    mountGuid: str
    weaponDBID: int
    enabled: bool
    def __init__(self, guid: _Optional[str] = ..., mountGuid: _Optional[str] = ..., weaponDBID: _Optional[int] = ..., enabled: bool = ...) -> None: ...

class RequestSetUnitHoldPosition(_message.Message):
    __slots__ = ("side", "unitGuids", "hold")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    UNITGUIDS_FIELD_NUMBER: _ClassVar[int]
    HOLD_FIELD_NUMBER: _ClassVar[int]
    side: str
    unitGuids: _containers.RepeatedScalarFieldContainer[str]
    hold: bool
    def __init__(self, side: _Optional[str] = ..., unitGuids: _Optional[_Iterable[str]] = ..., hold: bool = ...) -> None: ...

class RequestFillUnitMagazinesForLoadout(_message.Message):
    __slots__ = ("guid", "loadoutId", "quantity")
    GUID_FIELD_NUMBER: _ClassVar[int]
    LOADOUTID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    guid: str
    loadoutId: int
    quantity: int
    def __init__(self, guid: _Optional[str] = ..., loadoutId: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class MIUnitWeaponDistributionInfo(_message.Message):
    __slots__ = ("status", "ammoTotal", "ammoDist", "salvoCount", "autoFire", "authorize", "manualFire")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AMMOTOTAL_FIELD_NUMBER: _ClassVar[int]
    AMMODIST_FIELD_NUMBER: _ClassVar[int]
    SALVOCOUNT_FIELD_NUMBER: _ClassVar[int]
    AUTOFIRE_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZE_FIELD_NUMBER: _ClassVar[int]
    MANUALFIRE_FIELD_NUMBER: _ClassVar[int]
    status: str
    ammoTotal: str
    ammoDist: str
    salvoCount: str
    autoFire: str
    authorize: str
    manualFire: str
    def __init__(self, status: _Optional[str] = ..., ammoTotal: _Optional[str] = ..., ammoDist: _Optional[str] = ..., salvoCount: _Optional[str] = ..., autoFire: _Optional[str] = ..., authorize: _Optional[str] = ..., manualFire: _Optional[str] = ...) -> None: ...

class MIUnitWeaponDistribution(_message.Message):
    __slots__ = ("infos",)
    class InfosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MIUnitWeaponDistributionInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MIUnitWeaponDistributionInfo, _Mapping]] = ...) -> None: ...
    INFOS_FIELD_NUMBER: _ClassVar[int]
    infos: _containers.MessageMap[str, MIUnitWeaponDistributionInfo]
    def __init__(self, infos: _Optional[_Mapping[str, MIUnitWeaponDistributionInfo]] = ...) -> None: ...

class RequestGetUnitWeaponDistributionInfo(_message.Message):
    __slots__ = ("guid", "targetId")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    targetId: str
    def __init__(self, guid: _Optional[str] = ..., targetId: _Optional[str] = ...) -> None: ...

class RequestCalculateUnitFuelByAirTime(_message.Message):
    __slots__ = ("guid", "airTime")
    GUID_FIELD_NUMBER: _ClassVar[int]
    AIRTIME_FIELD_NUMBER: _ClassVar[int]
    guid: str
    airTime: float
    def __init__(self, guid: _Optional[str] = ..., airTime: _Optional[float] = ...) -> None: ...

class RequestCreateGroup(_message.Message):
    __slots__ = ("side", "groupName", "groupGuid", "unitGuids")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    GROUPGUID_FIELD_NUMBER: _ClassVar[int]
    UNITGUIDS_FIELD_NUMBER: _ClassVar[int]
    side: str
    groupName: str
    groupGuid: str
    unitGuids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., groupName: _Optional[str] = ..., groupGuid: _Optional[str] = ..., unitGuids: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestDetachUnitFromGroup(_message.Message):
    __slots__ = ("side", "unitGuids")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    UNITGUIDS_FIELD_NUMBER: _ClassVar[int]
    side: str
    unitGuids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., unitGuids: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestAddUnitToGroup(_message.Message):
    __slots__ = ("side", "groupId", "unitGuids")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    UNITGUIDS_FIELD_NUMBER: _ClassVar[int]
    side: str
    groupId: str
    unitGuids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., groupId: _Optional[str] = ..., unitGuids: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetGroupLeader(_message.Message):
    __slots__ = ("unitGuid",)
    UNITGUID_FIELD_NUMBER: _ClassVar[int]
    unitGuid: str
    def __init__(self, unitGuid: _Optional[str] = ...) -> None: ...

class RequestSetGroupUnitBearing(_message.Message):
    __slots__ = ("unitGuid", "longitude", "latitude", "mode")
    UNITGUID_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    unitGuid: str
    longitude: float
    latitude: float
    mode: int
    def __init__(self, unitGuid: _Optional[str] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., mode: _Optional[int] = ...) -> None: ...

class RequestSetGroupFormation(_message.Message):
    __slots__ = ("groupId", "formation", "distance", "teleportToStation")
    GROUPID_FIELD_NUMBER: _ClassVar[int]
    FORMATION_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    TELEPORTTOSTATION_FIELD_NUMBER: _ClassVar[int]
    groupId: str
    formation: str
    distance: int
    teleportToStation: bool
    def __init__(self, groupId: _Optional[str] = ..., formation: _Optional[str] = ..., distance: _Optional[int] = ..., teleportToStation: bool = ...) -> None: ...

class MissionConfiguration(_message.Message):
    __slots__ = ("type", "subType", "isActive", "startTime", "endTime", "flightSize", "minAircraft", "maxFlightBatches", "strikeRadius", "oneTimeOnly", "patrolZones", "activeEMCON")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBTYPE_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    FLIGHTSIZE_FIELD_NUMBER: _ClassVar[int]
    MINAIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    MAXFLIGHTBATCHES_FIELD_NUMBER: _ClassVar[int]
    STRIKERADIUS_FIELD_NUMBER: _ClassVar[int]
    ONETIMEONLY_FIELD_NUMBER: _ClassVar[int]
    PATROLZONES_FIELD_NUMBER: _ClassVar[int]
    ACTIVEEMCON_FIELD_NUMBER: _ClassVar[int]
    type: str
    subType: str
    isActive: bool
    startTime: str
    endTime: str
    flightSize: int
    minAircraft: int
    maxFlightBatches: int
    strikeRadius: int
    oneTimeOnly: bool
    patrolZones: _containers.RepeatedScalarFieldContainer[str]
    activeEMCON: bool
    def __init__(self, type: _Optional[str] = ..., subType: _Optional[str] = ..., isActive: bool = ..., startTime: _Optional[str] = ..., endTime: _Optional[str] = ..., flightSize: _Optional[int] = ..., minAircraft: _Optional[int] = ..., maxFlightBatches: _Optional[int] = ..., strikeRadius: _Optional[int] = ..., oneTimeOnly: bool = ..., patrolZones: _Optional[_Iterable[str]] = ..., activeEMCON: bool = ...) -> None: ...

class RequestAddMission(_message.Message):
    __slots__ = ("side", "missionName", "missionGuid", "missionType", "missionSubtype", "isActive", "destinationGuid", "zonePoints", "createTime")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    MISSIONTYPE_FIELD_NUMBER: _ClassVar[int]
    MISSIONSUBTYPE_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    DESTINATIONGUID_FIELD_NUMBER: _ClassVar[int]
    ZONEPOINTS_FIELD_NUMBER: _ClassVar[int]
    CREATETIME_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionName: str
    missionGuid: str
    missionType: str
    missionSubtype: str
    isActive: bool
    destinationGuid: str
    zonePoints: _containers.RepeatedScalarFieldContainer[str]
    createTime: int
    def __init__(self, side: _Optional[str] = ..., missionName: _Optional[str] = ..., missionGuid: _Optional[str] = ..., missionType: _Optional[str] = ..., missionSubtype: _Optional[str] = ..., isActive: bool = ..., destinationGuid: _Optional[str] = ..., zonePoints: _Optional[_Iterable[str]] = ..., createTime: _Optional[int] = ...) -> None: ...

class RequestSetMissionTime(_message.Message):
    __slots__ = ("side", "missionGuid", "startTime", "endTime")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    startTime: str
    endTime: str
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., startTime: _Optional[str] = ..., endTime: _Optional[str] = ...) -> None: ...

class RequestSetMissionStrikeMinimumTrigger(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeMinimumTrigger")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEMINIMUMTRIGGER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeMinimumTrigger: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeMinimumTrigger: _Optional[int] = ...) -> None: ...

class RequestSetMissionAircraftGroupSize(_message.Message):
    __slots__ = ("side", "missionGuid", "groupSize")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    GROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    groupSize: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., groupSize: _Optional[int] = ...) -> None: ...

class RequestSetMissionBoatGroupSize(_message.Message):
    __slots__ = ("side", "missionGuid", "groupSize", "missionType")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    GROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    MISSIONTYPE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    groupSize: int
    missionType: str
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., groupSize: _Optional[int] = ..., missionType: _Optional[str] = ...) -> None: ...

class RequestSetMissionStrikeFuelAmmo(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeFuelAmmo")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEFUELAMMO_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeFuelAmmo: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeFuelAmmo: _Optional[int] = ...) -> None: ...

class RequestSetMissionMinAircraftRequired(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeMinAircraftReq")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEMINAIRCRAFTREQ_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeMinAircraftReq: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeMinAircraftReq: _Optional[int] = ...) -> None: ...

class RequestSetMissionMaxAircraftAction(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeMax")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEMAX_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeMax: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeMax: _Optional[int] = ...) -> None: ...

class RequestSetMissionStrikeAircraftMinMaxRadius(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeMinDist", "strikeMaxDist")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEMINDIST_FIELD_NUMBER: _ClassVar[int]
    STRIKEMAXDIST_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeMinDist: int
    strikeMaxDist: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeMinDist: _Optional[int] = ..., strikeMaxDist: _Optional[int] = ...) -> None: ...

class RequestSetMissionStrikeBoatMinMaxRadius(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeMinDist", "strikeMaxDist")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEMINDIST_FIELD_NUMBER: _ClassVar[int]
    STRIKEMAXDIST_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeMinDist: int
    strikeMaxDist: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeMinDist: _Optional[int] = ..., strikeMaxDist: _Optional[int] = ...) -> None: ...

class RequestSetMissionRadarUsageRule(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeRadarUsage")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKERADARUSAGE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeRadarUsage: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeRadarUsage: _Optional[int] = ...) -> None: ...

class MITankerConfig(_message.Message):
    __slots__ = ("tankerUsage", "tankerMissionList", "tankerFollowsReceivers", "launchMissionWithoutTankersInPlace", "tankerMinNumberTotal", "tankerMinNumberAirborne", "tankerMinNumberStation", "maxReceiversInQueuePerTankerAirborne", "fuelQtyToStartLookingForTankerAirborne", "tankerMaxDistanceAirborne")
    TANKERUSAGE_FIELD_NUMBER: _ClassVar[int]
    TANKERMISSIONLIST_FIELD_NUMBER: _ClassVar[int]
    TANKERFOLLOWSRECEIVERS_FIELD_NUMBER: _ClassVar[int]
    LAUNCHMISSIONWITHOUTTANKERSINPLACE_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBERTOTAL_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBERAIRBORNE_FIELD_NUMBER: _ClassVar[int]
    TANKERMINNUMBERSTATION_FIELD_NUMBER: _ClassVar[int]
    MAXRECEIVERSINQUEUEPERTANKERAIRBORNE_FIELD_NUMBER: _ClassVar[int]
    FUELQTYTOSTARTLOOKINGFORTANKERAIRBORNE_FIELD_NUMBER: _ClassVar[int]
    TANKERMAXDISTANCEAIRBORNE_FIELD_NUMBER: _ClassVar[int]
    tankerUsage: str
    tankerMissionList: _containers.RepeatedScalarFieldContainer[str]
    tankerFollowsReceivers: bool
    launchMissionWithoutTankersInPlace: bool
    tankerMinNumberTotal: int
    tankerMinNumberAirborne: int
    tankerMinNumberStation: int
    maxReceiversInQueuePerTankerAirborne: int
    fuelQtyToStartLookingForTankerAirborne: int
    tankerMaxDistanceAirborne: str
    def __init__(self, tankerUsage: _Optional[str] = ..., tankerMissionList: _Optional[_Iterable[str]] = ..., tankerFollowsReceivers: bool = ..., launchMissionWithoutTankersInPlace: bool = ..., tankerMinNumberTotal: _Optional[int] = ..., tankerMinNumberAirborne: _Optional[int] = ..., tankerMinNumberStation: _Optional[int] = ..., maxReceiversInQueuePerTankerAirborne: _Optional[int] = ..., fuelQtyToStartLookingForTankerAirborne: _Optional[int] = ..., tankerMaxDistanceAirborne: _Optional[str] = ...) -> None: ...

class RequestSetMissionTankerConfig(_message.Message):
    __slots__ = ("side", "missionGuid", "tankerConfig")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TANKERCONFIG_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    tankerConfig: MITankerConfig
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., tankerConfig: _Optional[_Union[MITankerConfig, _Mapping]] = ...) -> None: ...

class RequestSetMissionAircraftGroupSizeRequired(_message.Message):
    __slots__ = ("side", "missionGuid", "useGroupSize")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    USEGROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    useGroupSize: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., useGroupSize: bool = ...) -> None: ...

class RequestSetMissionBoatGroupSizeRequired(_message.Message):
    __slots__ = ("side", "missionGuid", "useGroupSize")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    USEGROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    useGroupSize: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., useGroupSize: bool = ...) -> None: ...

class RequestSetMissionStrikeAutoPlanner(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeAutoPlanner")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEAUTOPLANNER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeAutoPlanner: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeAutoPlanner: bool = ...) -> None: ...

class RequestSetMissionStrikeOneTimeOnly(_message.Message):
    __slots__ = ("side", "missionGuid", "strikeOneTimeOnly")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEONETIMEONLY_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikeOneTimeOnly: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikeOneTimeOnly: bool = ...) -> None: ...

class RequestSetMissionIncludeInATO(_message.Message):
    __slots__ = ("side", "missionGuid", "includeInATO")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    INCLUDEINATO_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    includeInATO: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., includeInATO: bool = ...) -> None: ...

class RequestSetMissionPreplanTargetsOnly(_message.Message):
    __slots__ = ("side", "missionGuid", "strikePreplan")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    STRIKEPREPLAN_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    strikePreplan: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., strikePreplan: bool = ...) -> None: ...

class RequestSetMissionEscortAircraftGroupSize(_message.Message):
    __slots__ = ("side", "missionGuid", "escortGroupSize", "escortGroupSizeNonshooter")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ESCORTGROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    ESCORTGROUPSIZENONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    escortGroupSize: int
    escortGroupSizeNonshooter: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., escortGroupSize: _Optional[int] = ..., escortGroupSizeNonshooter: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortBoatGroupSize(_message.Message):
    __slots__ = ("side", "missionGuid", "escortGroupSize", "escortGroupSizeNonshooter")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ESCORTGROUPSIZE_FIELD_NUMBER: _ClassVar[int]
    ESCORTGROUPSIZENONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    escortGroupSize: int
    escortGroupSizeNonshooter: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., escortGroupSize: _Optional[int] = ..., escortGroupSizeNonshooter: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortMinAircraftRequired(_message.Message):
    __slots__ = ("side", "missionGuid", "escortMinShooter", "escortMinNonshooter")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ESCORTMINSHOOTER_FIELD_NUMBER: _ClassVar[int]
    ESCORTMINNONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    escortMinShooter: int
    escortMinNonshooter: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., escortMinShooter: _Optional[int] = ..., escortMinNonshooter: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortMaxAircraftAction(_message.Message):
    __slots__ = ("side", "missionGuid", "escortMaxShooter", "escortMaxNonshooter")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ESCORTMAXSHOOTER_FIELD_NUMBER: _ClassVar[int]
    ESCORTMAXNONSHOOTER_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    escortMaxShooter: int
    escortMaxNonshooter: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., escortMaxShooter: _Optional[int] = ..., escortMaxNonshooter: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortResponseRadius(_message.Message):
    __slots__ = ("side", "missionGuid", "escortResponseRadius")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ESCORTRESPONSERADIUS_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    escortResponseRadius: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., escortResponseRadius: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortAircraftStoinvestigate(_message.Message):
    __slots__ = ("side", "missionGuid", "flightStoinvestigate")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    FLIGHTSTOINVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    flightStoinvestigate: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., flightStoinvestigate: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortAircraftStoengage(_message.Message):
    __slots__ = ("side", "missionGuid", "flightStoengage")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    FLIGHTSTOENGAGE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    flightStoengage: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., flightStoengage: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortWingmanEngageDistance(_message.Message):
    __slots__ = ("side", "missionGuid", "wingmanEngageDistance")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    WINGMANENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    wingmanEngageDistance: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., wingmanEngageDistance: _Optional[float] = ...) -> None: ...

class RequestSetMissionEscortBoatStoinvestigate(_message.Message):
    __slots__ = ("side", "missionGuid", "boatStoinvestigate")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    BOATSTOINVESTIGATE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    boatStoinvestigate: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., boatStoinvestigate: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortBoatStoengage(_message.Message):
    __slots__ = ("side", "missionGuid", "boatStoengage")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    BOATSTOENGAGE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    boatStoengage: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., boatStoengage: _Optional[int] = ...) -> None: ...

class RequestSetMissionEscortBoatEngageDistance(_message.Message):
    __slots__ = ("side", "missionGuid", "groupmemberEngageDistance")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    GROUPMEMBERENGAGEDISTANCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    groupmemberEngageDistance: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., groupmemberEngageDistance: _Optional[float] = ...) -> None: ...

class RequestSetMissionPatrolZone(_message.Message):
    __slots__ = ("side", "missionGuid", "patrolZones")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    PATROLZONES_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    patrolZones: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., patrolZones: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetMissionPatrolOnStation(_message.Message):
    __slots__ = ("side", "missionGuid", "onStation")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ONSTATION_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    onStation: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., onStation: _Optional[int] = ...) -> None: ...

class RequestSetMissionPatrolOneThirdRule(_message.Message):
    __slots__ = ("side", "missionGuid", "oneThirdRule")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ONETHIRDRULE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    oneThirdRule: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., oneThirdRule: bool = ...) -> None: ...

class RequestSetMissionPatrolCheckOutsidePatrol(_message.Message):
    __slots__ = ("side", "missionGuid", "checkOPA")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    CHECKOPA_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    checkOPA: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., checkOPA: bool = ...) -> None: ...

class RequestSetMissionPatrolCheckWeaponRange(_message.Message):
    __slots__ = ("side", "missionGuid", "checkWWR")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    CHECKWWR_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    checkWWR: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., checkWWR: bool = ...) -> None: ...

class RequestSetMissionPatrolActiveEMCONInZone(_message.Message):
    __slots__ = ("side", "missionGuid", "activeEMCON")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ACTIVEEMCON_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    activeEMCON: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., activeEMCON: bool = ...) -> None: ...

class RequestSetMissionPatrolProsecutionZone(_message.Message):
    __slots__ = ("side", "missionGuid", "prosecutionZones")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    PROSECUTIONZONES_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    prosecutionZones: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., prosecutionZones: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetMissionPatrolMovementStyle(_message.Message):
    __slots__ = ("side", "missionGuid", "movementStyle")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    MOVEMENTSTYLE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    movementStyle: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., movementStyle: _Optional[int] = ...) -> None: ...

class RequestSetMissionPatrolAircraftThrottle(_message.Message):
    __slots__ = ("side", "missionGuid", "transitThrottle", "stationThrottle")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    transitThrottle: str
    stationThrottle: str
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., transitThrottle: _Optional[str] = ..., stationThrottle: _Optional[str] = ...) -> None: ...

class RequestSetMissionPatrolAircraftTerrainFollowing(_message.Message):
    __slots__ = ("side", "missionGuid", "transitTerrainFollowing", "stationTerrainFollowing")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TRANSITTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    STATIONTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    transitTerrainFollowing: bool
    stationTerrainFollowing: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., transitTerrainFollowing: bool = ..., stationTerrainFollowing: bool = ...) -> None: ...

class RequestSetMissionPatrolSubmarineConfig(_message.Message):
    __slots__ = ("side", "missionGuid", "transitThrottle", "transitDepth", "stationDepth", "stationThrottle")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    TRANSITDEPTH_FIELD_NUMBER: _ClassVar[int]
    STATIONDEPTH_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    transitThrottle: str
    transitDepth: float
    stationDepth: float
    stationThrottle: str
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., transitThrottle: _Optional[str] = ..., transitDepth: _Optional[float] = ..., stationDepth: _Optional[float] = ..., stationThrottle: _Optional[str] = ...) -> None: ...

class RequestSetMissionPatrolShipThrottle(_message.Message):
    __slots__ = ("side", "missionGuid", "transitThrottle", "stationThrottle")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TRANSITTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    STATIONTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    transitThrottle: str
    stationThrottle: str
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., transitThrottle: _Optional[str] = ..., stationThrottle: _Optional[str] = ...) -> None: ...

class RequestSetMissionPatrolAircraftAltitude(_message.Message):
    __slots__ = ("side", "missionGuid", "transitAltitude", "stationAltitude")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    TRANSITALTITUDE_FIELD_NUMBER: _ClassVar[int]
    STATIONALTITUDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    transitAltitude: float
    stationAltitude: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., transitAltitude: _Optional[float] = ..., stationAltitude: _Optional[float] = ...) -> None: ...

class RequestSetMissionPatrolAircraftAttackConfig(_message.Message):
    __slots__ = ("side", "missionGuid", "attackThrottle", "attackTerrainFollowing", "attackAltitude", "attackDistance")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    ATTACKTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    ATTACKALTITUDE_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    attackThrottle: str
    attackTerrainFollowing: bool
    attackAltitude: float
    attackDistance: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., attackThrottle: _Optional[str] = ..., attackTerrainFollowing: bool = ..., attackAltitude: _Optional[float] = ..., attackDistance: _Optional[float] = ...) -> None: ...

class RequestSetMissionPatrolSubmarineAttackConfig(_message.Message):
    __slots__ = ("side", "missionGuid", "attackThrottle", "attackDepth", "attackDistance")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    ATTACKDEPTH_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    attackThrottle: str
    attackDepth: float
    attackDistance: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., attackThrottle: _Optional[str] = ..., attackDepth: _Optional[float] = ..., attackDistance: _Optional[float] = ...) -> None: ...

class RequestSetMissionPatrolShipAttackConfig(_message.Message):
    __slots__ = ("side", "missionGuid", "attackThrottle", "attackDistance")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ATTACKTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    ATTACKDISTANCE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    attackThrottle: str
    attackDistance: float
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., attackThrottle: _Optional[str] = ..., attackDistance: _Optional[float] = ...) -> None: ...

class RequestSetMissionSupportOneTimeOnly(_message.Message):
    __slots__ = ("side", "missionGuid", "oneTimeOnly")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    ONETIMEONLY_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    oneTimeOnly: bool
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., oneTimeOnly: bool = ...) -> None: ...

class RequestSetMissionSupportLoopType(_message.Message):
    __slots__ = ("side", "missionGuid", "loopType")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MISSIONGUID_FIELD_NUMBER: _ClassVar[int]
    LOOPTYPE_FIELD_NUMBER: _ClassVar[int]
    side: str
    missionGuid: str
    loopType: int
    def __init__(self, side: _Optional[str] = ..., missionGuid: _Optional[str] = ..., loopType: _Optional[int] = ...) -> None: ...

class RequestSetMissionFerryConfig(_message.Message):
    __slots__ = ("baseInfo", "ferryBehavior", "ferryThrottle", "ferryAltitude", "ferryTerrainFollowing")
    BASEINFO_FIELD_NUMBER: _ClassVar[int]
    FERRYBEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    FERRYTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    FERRYALTITUDE_FIELD_NUMBER: _ClassVar[int]
    FERRYTERRAINFOLLOWING_FIELD_NUMBER: _ClassVar[int]
    baseInfo: BaseMissionInfo
    ferryBehavior: str
    ferryThrottle: str
    ferryAltitude: float
    ferryTerrainFollowing: bool
    def __init__(self, baseInfo: _Optional[_Union[BaseMissionInfo, _Mapping]] = ..., ferryBehavior: _Optional[str] = ..., ferryThrottle: _Optional[str] = ..., ferryAltitude: _Optional[float] = ..., ferryTerrainFollowing: bool = ...) -> None: ...

class RequestSetMissionFerryShipThrottle(_message.Message):
    __slots__ = ("baseInfo", "ferryShipThrottle")
    BASEINFO_FIELD_NUMBER: _ClassVar[int]
    FERRYSHIPTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    baseInfo: BaseMissionInfo
    ferryShipThrottle: str
    def __init__(self, baseInfo: _Optional[_Union[BaseMissionInfo, _Mapping]] = ..., ferryShipThrottle: _Optional[str] = ...) -> None: ...

class RequestSetMissionFerrySubThrottle(_message.Message):
    __slots__ = ("baseInfo", "ferrySubThrottle")
    BASEINFO_FIELD_NUMBER: _ClassVar[int]
    FERRYSUBTHROTTLE_FIELD_NUMBER: _ClassVar[int]
    baseInfo: BaseMissionInfo
    ferrySubThrottle: str
    def __init__(self, baseInfo: _Optional[_Union[BaseMissionInfo, _Mapping]] = ..., ferrySubThrottle: _Optional[str] = ...) -> None: ...

class RequestSetMissionFerrySubDepth(_message.Message):
    __slots__ = ("baseInfo", "ferrySubDepth")
    BASEINFO_FIELD_NUMBER: _ClassVar[int]
    FERRYSUBDEPTH_FIELD_NUMBER: _ClassVar[int]
    baseInfo: BaseMissionInfo
    ferrySubDepth: float
    def __init__(self, baseInfo: _Optional[_Union[BaseMissionInfo, _Mapping]] = ..., ferrySubDepth: _Optional[float] = ...) -> None: ...

class RequestSetMissionMineArmingDelay(_message.Message):
    __slots__ = ("baseInfo", "armingDelay")
    BASEINFO_FIELD_NUMBER: _ClassVar[int]
    ARMINGDELAY_FIELD_NUMBER: _ClassVar[int]
    baseInfo: BaseMissionInfo
    armingDelay: str
    def __init__(self, baseInfo: _Optional[_Union[BaseMissionInfo, _Mapping]] = ..., armingDelay: _Optional[str] = ...) -> None: ...

class StrategicWeaponConfig(_message.Message):
    __slots__ = ("useNuclearWeapons", "useNuclearWeaponsEditable")
    USENUCLEARWEAPONS_FIELD_NUMBER: _ClassVar[int]
    USENUCLEARWEAPONSEDITABLE_FIELD_NUMBER: _ClassVar[int]
    useNuclearWeapons: str
    useNuclearWeaponsEditable: bool
    def __init__(self, useNuclearWeapons: _Optional[str] = ..., useNuclearWeaponsEditable: bool = ...) -> None: ...

class RulesOfEngagementConfig(_message.Message):
    __slots__ = ("weaponControlAir", "weaponControlSurface", "weaponControlSubsurface", "weaponControlLand", "ignorePlottedCourse", "engagingAmbiguousTargets", "engageOpportunityTargets", "weaponControlAirEditable", "weaponControlSurfaceEditable", "weaponControlSubsurfaceEditable", "weaponControlLandEditable", "ignorePlottedCourseEditable", "engagingAmbiguousTargetsEditable", "engageOpportunityTargetsEditable")
    WEAPONCONTROLAIR_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLSURFACE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLSUBSURFACE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLLAND_FIELD_NUMBER: _ClassVar[int]
    IGNOREPLOTTEDCOURSE_FIELD_NUMBER: _ClassVar[int]
    ENGAGINGAMBIGUOUSTARGETS_FIELD_NUMBER: _ClassVar[int]
    ENGAGEOPPORTUNITYTARGETS_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLAIREDITABLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLSURFACEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLSUBSURFACEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONCONTROLLANDEDITABLE_FIELD_NUMBER: _ClassVar[int]
    IGNOREPLOTTEDCOURSEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    ENGAGINGAMBIGUOUSTARGETSEDITABLE_FIELD_NUMBER: _ClassVar[int]
    ENGAGEOPPORTUNITYTARGETSEDITABLE_FIELD_NUMBER: _ClassVar[int]
    weaponControlAir: str
    weaponControlSurface: str
    weaponControlSubsurface: str
    weaponControlLand: str
    ignorePlottedCourse: str
    engagingAmbiguousTargets: str
    engageOpportunityTargets: str
    weaponControlAirEditable: bool
    weaponControlSurfaceEditable: bool
    weaponControlSubsurfaceEditable: bool
    weaponControlLandEditable: bool
    ignorePlottedCourseEditable: bool
    engagingAmbiguousTargetsEditable: bool
    engageOpportunityTargetsEditable: bool
    def __init__(self, weaponControlAir: _Optional[str] = ..., weaponControlSurface: _Optional[str] = ..., weaponControlSubsurface: _Optional[str] = ..., weaponControlLand: _Optional[str] = ..., ignorePlottedCourse: _Optional[str] = ..., engagingAmbiguousTargets: _Optional[str] = ..., engageOpportunityTargets: _Optional[str] = ..., weaponControlAirEditable: bool = ..., weaponControlSurfaceEditable: bool = ..., weaponControlSubsurfaceEditable: bool = ..., weaponControlLandEditable: bool = ..., ignorePlottedCourseEditable: bool = ..., engagingAmbiguousTargetsEditable: bool = ..., engageOpportunityTargetsEditable: bool = ...) -> None: ...

class ElectromagneticSpectrumManagementConfig(_message.Message):
    __slots__ = ("ignoreEmconWhileUnderAttack", "ignoreEmconWhileUnderAttackEditable")
    IGNOREEMCONWHILEUNDERATTACK_FIELD_NUMBER: _ClassVar[int]
    IGNOREEMCONWHILEUNDERATTACKEDITABLE_FIELD_NUMBER: _ClassVar[int]
    ignoreEmconWhileUnderAttack: str
    ignoreEmconWhileUnderAttackEditable: bool
    def __init__(self, ignoreEmconWhileUnderAttack: _Optional[str] = ..., ignoreEmconWhileUnderAttackEditable: bool = ...) -> None: ...

class MiscellaneousConfig(_message.Message):
    __slots__ = ("kinematicRangeForTorpedoes", "automaticEvasion", "useRefuelUnrep", "refuelUnrepSelection", "refuelUnrepAllied", "kinematicRangeForTorpedoesEditable", "automaticEvasionEditable", "useRefuelUnrepEditable", "refuelUnrepSelectionEditable", "refuelUnrepAlliedEditable")
    KINEMATICRANGEFORTORPEDOES_FIELD_NUMBER: _ClassVar[int]
    AUTOMATICEVASION_FIELD_NUMBER: _ClassVar[int]
    USEREFUELUNREP_FIELD_NUMBER: _ClassVar[int]
    REFUELUNREPSELECTION_FIELD_NUMBER: _ClassVar[int]
    REFUELUNREPALLIED_FIELD_NUMBER: _ClassVar[int]
    KINEMATICRANGEFORTORPEDOESEDITABLE_FIELD_NUMBER: _ClassVar[int]
    AUTOMATICEVASIONEDITABLE_FIELD_NUMBER: _ClassVar[int]
    USEREFUELUNREPEDITABLE_FIELD_NUMBER: _ClassVar[int]
    REFUELUNREPSELECTIONEDITABLE_FIELD_NUMBER: _ClassVar[int]
    REFUELUNREPALLIEDEDITABLE_FIELD_NUMBER: _ClassVar[int]
    kinematicRangeForTorpedoes: str
    automaticEvasion: str
    useRefuelUnrep: str
    refuelUnrepSelection: str
    refuelUnrepAllied: str
    kinematicRangeForTorpedoesEditable: bool
    automaticEvasionEditable: bool
    useRefuelUnrepEditable: bool
    refuelUnrepSelectionEditable: bool
    refuelUnrepAlliedEditable: bool
    def __init__(self, kinematicRangeForTorpedoes: _Optional[str] = ..., automaticEvasion: _Optional[str] = ..., useRefuelUnrep: _Optional[str] = ..., refuelUnrepSelection: _Optional[str] = ..., refuelUnrepAllied: _Optional[str] = ..., kinematicRangeForTorpedoesEditable: bool = ..., automaticEvasionEditable: bool = ..., useRefuelUnrepEditable: bool = ..., refuelUnrepSelectionEditable: bool = ..., refuelUnrepAlliedEditable: bool = ...) -> None: ...

class AirOperationsConfig(_message.Message):
    __slots__ = ("airOperationsTempo", "quickTurnaroundForAircraft", "fuelStatePlanned", "fuelStateRtb", "weaponStatePlanned", "weaponStateRtb", "gunStrafing", "jettisonOrdnance", "bvrLogic", "airOperationsTempoEditable", "quickTurnaroundForAircraftEditable", "fuelStatePlannedEditable", "fuelStateRtbEditable", "weaponStatePlannedEditable", "weaponStateRtbEditable", "gunStrafingEditable", "jettisonOrdnanceEditable", "bvrLogicEditable")
    AIROPERATIONSTEMPO_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUNDFORAIRCRAFT_FIELD_NUMBER: _ClassVar[int]
    FUELSTATEPLANNED_FIELD_NUMBER: _ClassVar[int]
    FUELSTATERTB_FIELD_NUMBER: _ClassVar[int]
    WEAPONSTATEPLANNED_FIELD_NUMBER: _ClassVar[int]
    WEAPONSTATERTB_FIELD_NUMBER: _ClassVar[int]
    GUNSTRAFING_FIELD_NUMBER: _ClassVar[int]
    JETTISONORDNANCE_FIELD_NUMBER: _ClassVar[int]
    BVRLOGIC_FIELD_NUMBER: _ClassVar[int]
    AIROPERATIONSTEMPOEDITABLE_FIELD_NUMBER: _ClassVar[int]
    QUICKTURNAROUNDFORAIRCRAFTEDITABLE_FIELD_NUMBER: _ClassVar[int]
    FUELSTATEPLANNEDEDITABLE_FIELD_NUMBER: _ClassVar[int]
    FUELSTATERTBEDITABLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONSTATEPLANNEDEDITABLE_FIELD_NUMBER: _ClassVar[int]
    WEAPONSTATERTBEDITABLE_FIELD_NUMBER: _ClassVar[int]
    GUNSTRAFINGEDITABLE_FIELD_NUMBER: _ClassVar[int]
    JETTISONORDNANCEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    BVRLOGICEDITABLE_FIELD_NUMBER: _ClassVar[int]
    airOperationsTempo: str
    quickTurnaroundForAircraft: str
    fuelStatePlanned: str
    fuelStateRtb: str
    weaponStatePlanned: str
    weaponStateRtb: str
    gunStrafing: str
    jettisonOrdnance: str
    bvrLogic: str
    airOperationsTempoEditable: bool
    quickTurnaroundForAircraftEditable: bool
    fuelStatePlannedEditable: bool
    fuelStateRtbEditable: bool
    weaponStatePlannedEditable: bool
    weaponStateRtbEditable: bool
    gunStrafingEditable: bool
    jettisonOrdnanceEditable: bool
    bvrLogicEditable: bool
    def __init__(self, airOperationsTempo: _Optional[str] = ..., quickTurnaroundForAircraft: _Optional[str] = ..., fuelStatePlanned: _Optional[str] = ..., fuelStateRtb: _Optional[str] = ..., weaponStatePlanned: _Optional[str] = ..., weaponStateRtb: _Optional[str] = ..., gunStrafing: _Optional[str] = ..., jettisonOrdnance: _Optional[str] = ..., bvrLogic: _Optional[str] = ..., airOperationsTempoEditable: bool = ..., quickTurnaroundForAircraftEditable: bool = ..., fuelStatePlannedEditable: bool = ..., fuelStateRtbEditable: bool = ..., weaponStatePlannedEditable: bool = ..., weaponStateRtbEditable: bool = ..., gunStrafingEditable: bool = ..., jettisonOrdnanceEditable: bool = ..., bvrLogicEditable: bool = ...) -> None: ...

class AntiSurfaceOperationsConfig(_message.Message):
    __slots__ = ("useSamsInAntiSurfaceMode", "maintainStandoff", "useSamsInAntiSurfaceModeEditable", "maintainStandoffEditable")
    USESAMSINANTISURFACEMODE_FIELD_NUMBER: _ClassVar[int]
    MAINTAINSTANDOFF_FIELD_NUMBER: _ClassVar[int]
    USESAMSINANTISURFACEMODEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    MAINTAINSTANDOFFEDITABLE_FIELD_NUMBER: _ClassVar[int]
    useSamsInAntiSurfaceMode: str
    maintainStandoff: str
    useSamsInAntiSurfaceModeEditable: bool
    maintainStandoffEditable: bool
    def __init__(self, useSamsInAntiSurfaceMode: _Optional[str] = ..., maintainStandoff: _Optional[str] = ..., useSamsInAntiSurfaceModeEditable: bool = ..., maintainStandoffEditable: bool = ...) -> None: ...

class AntiSubmarineOperationsConfig(_message.Message):
    __slots__ = ("avoidContact", "diveOnThreat", "rechargeOnPatrol", "rechargeOnAttack", "useAip", "dippingSonar", "avoidContactEditable", "diveOnThreatEditable", "rechargeOnPatrolEditable", "rechargeOnAttackEditable", "useAipEditable", "dippingSonarEditable")
    AVOIDCONTACT_FIELD_NUMBER: _ClassVar[int]
    DIVEONTHREAT_FIELD_NUMBER: _ClassVar[int]
    RECHARGEONPATROL_FIELD_NUMBER: _ClassVar[int]
    RECHARGEONATTACK_FIELD_NUMBER: _ClassVar[int]
    USEAIP_FIELD_NUMBER: _ClassVar[int]
    DIPPINGSONAR_FIELD_NUMBER: _ClassVar[int]
    AVOIDCONTACTEDITABLE_FIELD_NUMBER: _ClassVar[int]
    DIVEONTHREATEDITABLE_FIELD_NUMBER: _ClassVar[int]
    RECHARGEONPATROLEDITABLE_FIELD_NUMBER: _ClassVar[int]
    RECHARGEONATTACKEDITABLE_FIELD_NUMBER: _ClassVar[int]
    USEAIPEDITABLE_FIELD_NUMBER: _ClassVar[int]
    DIPPINGSONAREDITABLE_FIELD_NUMBER: _ClassVar[int]
    avoidContact: str
    diveOnThreat: str
    rechargeOnPatrol: str
    rechargeOnAttack: str
    useAip: str
    dippingSonar: str
    avoidContactEditable: bool
    diveOnThreatEditable: bool
    rechargeOnPatrolEditable: bool
    rechargeOnAttackEditable: bool
    useAipEditable: bool
    dippingSonarEditable: bool
    def __init__(self, avoidContact: _Optional[str] = ..., diveOnThreat: _Optional[str] = ..., rechargeOnPatrol: _Optional[str] = ..., rechargeOnAttack: _Optional[str] = ..., useAip: _Optional[str] = ..., dippingSonar: _Optional[str] = ..., avoidContactEditable: bool = ..., diveOnThreatEditable: bool = ..., rechargeOnPatrolEditable: bool = ..., rechargeOnAttackEditable: bool = ..., useAipEditable: bool = ..., dippingSonarEditable: bool = ...) -> None: ...

class WithdrawalAndRedeploymentConfig(_message.Message):
    __slots__ = ("withdrawOnDamage", "withdrawOnFuel", "withdrawOnAttack", "withdrawOnDefence", "deployOnDamage", "deployOnFuel", "deployOnAttack", "deployOnDefence")
    WITHDRAWONDAMAGE_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWONFUEL_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWONATTACK_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWONDEFENCE_FIELD_NUMBER: _ClassVar[int]
    DEPLOYONDAMAGE_FIELD_NUMBER: _ClassVar[int]
    DEPLOYONFUEL_FIELD_NUMBER: _ClassVar[int]
    DEPLOYONATTACK_FIELD_NUMBER: _ClassVar[int]
    DEPLOYONDEFENCE_FIELD_NUMBER: _ClassVar[int]
    withdrawOnDamage: str
    withdrawOnFuel: str
    withdrawOnAttack: str
    withdrawOnDefence: str
    deployOnDamage: str
    deployOnFuel: str
    deployOnAttack: str
    deployOnDefence: str
    def __init__(self, withdrawOnDamage: _Optional[str] = ..., withdrawOnFuel: _Optional[str] = ..., withdrawOnAttack: _Optional[str] = ..., withdrawOnDefence: _Optional[str] = ..., deployOnDamage: _Optional[str] = ..., deployOnFuel: _Optional[str] = ..., deployOnAttack: _Optional[str] = ..., deployOnDefence: _Optional[str] = ...) -> None: ...

class MIDoctrineSettings(_message.Message):
    __slots__ = ("strategicWeaponConfig", "rulesOfEngagementConfig", "electromagneticSpectrumManagementConfig", "miscellaneousConfig", "airOperationsConfig", "antiSurfaceOperationsConfig", "antiSubmarineOperationsConfig", "withdrawalAndRedeploymentConfig", "navigationSurfaceMode", "navigationSubsurfaceMode", "navigationLandMode", "navigationSurfaceModeEditable", "navigationSubsurfaceModeEditable", "navigationLandModeEditable")
    STRATEGICWEAPONCONFIG_FIELD_NUMBER: _ClassVar[int]
    RULESOFENGAGEMENTCONFIG_FIELD_NUMBER: _ClassVar[int]
    ELECTROMAGNETICSPECTRUMMANAGEMENTCONFIG_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUSCONFIG_FIELD_NUMBER: _ClassVar[int]
    AIROPERATIONSCONFIG_FIELD_NUMBER: _ClassVar[int]
    ANTISURFACEOPERATIONSCONFIG_FIELD_NUMBER: _ClassVar[int]
    ANTISUBMARINEOPERATIONSCONFIG_FIELD_NUMBER: _ClassVar[int]
    WITHDRAWALANDREDEPLOYMENTCONFIG_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONSURFACEMODE_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONSUBSURFACEMODE_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONLANDMODE_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONSURFACEMODEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONSUBSURFACEMODEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONLANDMODEEDITABLE_FIELD_NUMBER: _ClassVar[int]
    strategicWeaponConfig: StrategicWeaponConfig
    rulesOfEngagementConfig: RulesOfEngagementConfig
    electromagneticSpectrumManagementConfig: ElectromagneticSpectrumManagementConfig
    miscellaneousConfig: MiscellaneousConfig
    airOperationsConfig: AirOperationsConfig
    antiSurfaceOperationsConfig: AntiSurfaceOperationsConfig
    antiSubmarineOperationsConfig: AntiSubmarineOperationsConfig
    withdrawalAndRedeploymentConfig: WithdrawalAndRedeploymentConfig
    navigationSurfaceMode: str
    navigationSubsurfaceMode: str
    navigationLandMode: str
    navigationSurfaceModeEditable: bool
    navigationSubsurfaceModeEditable: bool
    navigationLandModeEditable: bool
    def __init__(self, strategicWeaponConfig: _Optional[_Union[StrategicWeaponConfig, _Mapping]] = ..., rulesOfEngagementConfig: _Optional[_Union[RulesOfEngagementConfig, _Mapping]] = ..., electromagneticSpectrumManagementConfig: _Optional[_Union[ElectromagneticSpectrumManagementConfig, _Mapping]] = ..., miscellaneousConfig: _Optional[_Union[MiscellaneousConfig, _Mapping]] = ..., airOperationsConfig: _Optional[_Union[AirOperationsConfig, _Mapping]] = ..., antiSurfaceOperationsConfig: _Optional[_Union[AntiSurfaceOperationsConfig, _Mapping]] = ..., antiSubmarineOperationsConfig: _Optional[_Union[AntiSubmarineOperationsConfig, _Mapping]] = ..., withdrawalAndRedeploymentConfig: _Optional[_Union[WithdrawalAndRedeploymentConfig, _Mapping]] = ..., navigationSurfaceMode: _Optional[str] = ..., navigationSubsurfaceMode: _Optional[str] = ..., navigationLandMode: _Optional[str] = ..., navigationSurfaceModeEditable: bool = ..., navigationSubsurfaceModeEditable: bool = ..., navigationLandModeEditable: bool = ...) -> None: ...

class RequestSetDoctrine(_message.Message):
    __slots__ = ("targetType", "targetId", "doctrine", "side", "escort")
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FIELD_NUMBER: _ClassVar[int]
    targetType: str
    targetId: str
    doctrine: MIDoctrineSettings
    side: str
    escort: bool
    def __init__(self, targetType: _Optional[str] = ..., targetId: _Optional[str] = ..., doctrine: _Optional[_Union[MIDoctrineSettings, _Mapping]] = ..., side: _Optional[str] = ..., escort: bool = ...) -> None: ...

class RequestGetDoctrine(_message.Message):
    __slots__ = ("targetType", "targetId", "side", "escort")
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FIELD_NUMBER: _ClassVar[int]
    targetType: str
    targetId: str
    side: str
    escort: bool
    def __init__(self, targetType: _Optional[str] = ..., targetId: _Optional[str] = ..., side: _Optional[str] = ..., escort: bool = ...) -> None: ...

class RequestSetDoctrineWRA(_message.Message):
    __slots__ = ("targetType", "targetId", "weaponId", "side", "doctrineWRAInfo")
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    DOCTRINEWRAINFO_FIELD_NUMBER: _ClassVar[int]
    targetType: str
    targetId: str
    weaponId: str
    side: str
    doctrineWRAInfo: MIDoctrineWRAInfo
    def __init__(self, targetType: _Optional[str] = ..., targetId: _Optional[str] = ..., weaponId: _Optional[str] = ..., side: _Optional[str] = ..., doctrineWRAInfo: _Optional[_Union[MIDoctrineWRAInfo, _Mapping]] = ...) -> None: ...

class MIDoctrineWRAInfo(_message.Message):
    __slots__ = ("targetTypeEnum", "weaponQty", "shooterQty", "firingRange", "selfDefenceRange")
    TARGETTYPEENUM_FIELD_NUMBER: _ClassVar[int]
    WEAPONQTY_FIELD_NUMBER: _ClassVar[int]
    SHOOTERQTY_FIELD_NUMBER: _ClassVar[int]
    FIRINGRANGE_FIELD_NUMBER: _ClassVar[int]
    SELFDEFENCERANGE_FIELD_NUMBER: _ClassVar[int]
    targetTypeEnum: EWRA_WeaponTargetType
    weaponQty: str
    shooterQty: str
    firingRange: str
    selfDefenceRange: str
    def __init__(self, targetTypeEnum: _Optional[_Union[EWRA_WeaponTargetType, str]] = ..., weaponQty: _Optional[str] = ..., shooterQty: _Optional[str] = ..., firingRange: _Optional[str] = ..., selfDefenceRange: _Optional[str] = ...) -> None: ...

class MIDoctrineWRAList(_message.Message):
    __slots__ = ("doctrineWRAInfos",)
    class DoctrineWRAInfosEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MIDoctrineWRAInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MIDoctrineWRAInfo, _Mapping]] = ...) -> None: ...
    DOCTRINEWRAINFOS_FIELD_NUMBER: _ClassVar[int]
    doctrineWRAInfos: _containers.MessageMap[str, MIDoctrineWRAInfo]
    def __init__(self, doctrineWRAInfos: _Optional[_Mapping[str, MIDoctrineWRAInfo]] = ...) -> None: ...

class RequestGetDoctrineWRA(_message.Message):
    __slots__ = ("targetType", "targetId", "side", "escort")
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FIELD_NUMBER: _ClassVar[int]
    targetType: str
    targetId: str
    side: str
    escort: bool
    def __init__(self, targetType: _Optional[str] = ..., targetId: _Optional[str] = ..., side: _Optional[str] = ..., escort: bool = ...) -> None: ...

class RequestSetEMCON(_message.Message):
    __slots__ = ("category", "nameId", "content")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    NAMEID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    category: str
    nameId: str
    content: str
    def __init__(self, category: _Optional[str] = ..., nameId: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class RequestSetWaypoint(_message.Message):
    __slots__ = ("guid", "pointid", "speed", "altitude")
    GUID_FIELD_NUMBER: _ClassVar[int]
    POINTID_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    pointid: str
    speed: str
    altitude: str
    def __init__(self, guid: _Optional[str] = ..., pointid: _Optional[str] = ..., speed: _Optional[str] = ..., altitude: _Optional[str] = ...) -> None: ...

class RequestSetWaypointDoctrine(_message.Message):
    __slots__ = ("guid", "pointid", "escort", "doctrine")
    GUID_FIELD_NUMBER: _ClassVar[int]
    POINTID_FIELD_NUMBER: _ClassVar[int]
    ESCORT_FIELD_NUMBER: _ClassVar[int]
    DOCTRINE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    pointid: str
    escort: bool
    doctrine: MIDoctrineSettings
    def __init__(self, guid: _Optional[str] = ..., pointid: _Optional[str] = ..., escort: bool = ..., doctrine: _Optional[_Union[MIDoctrineSettings, _Mapping]] = ...) -> None: ...

class RequestSetWaypointSensorSwitch(_message.Message):
    __slots__ = ("guid", "pointid", "sensorid", "radar", "sonar", "OECM")
    GUID_FIELD_NUMBER: _ClassVar[int]
    POINTID_FIELD_NUMBER: _ClassVar[int]
    SENSORID_FIELD_NUMBER: _ClassVar[int]
    RADAR_FIELD_NUMBER: _ClassVar[int]
    SONAR_FIELD_NUMBER: _ClassVar[int]
    OECM_FIELD_NUMBER: _ClassVar[int]
    guid: str
    pointid: str
    sensorid: str
    radar: bool
    sonar: bool
    OECM: bool
    def __init__(self, guid: _Optional[str] = ..., pointid: _Optional[str] = ..., sensorid: _Optional[str] = ..., radar: bool = ..., sonar: bool = ..., OECM: bool = ...) -> None: ...

class RequestSetWeather(_message.Message):
    __slots__ = ("temperature", "rainfall", "cloudCover", "seaState")
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    RAINFALL_FIELD_NUMBER: _ClassVar[int]
    CLOUDCOVER_FIELD_NUMBER: _ClassVar[int]
    SEASTATE_FIELD_NUMBER: _ClassVar[int]
    temperature: int
    rainfall: int
    cloudCover: float
    seaState: float
    def __init__(self, temperature: _Optional[int] = ..., rainfall: _Optional[int] = ..., cloudCover: _Optional[float] = ..., seaState: _Optional[float] = ...) -> None: ...

class RequestGetWeather(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class MIWeather(_message.Message):
    __slots__ = ("temperature", "rainfall", "cloudCover", "seaState")
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    RAINFALL_FIELD_NUMBER: _ClassVar[int]
    CLOUDCOVER_FIELD_NUMBER: _ClassVar[int]
    SEASTATE_FIELD_NUMBER: _ClassVar[int]
    temperature: int
    rainfall: int
    cloudCover: float
    seaState: float
    def __init__(self, temperature: _Optional[int] = ..., rainfall: _Optional[int] = ..., cloudCover: _Optional[float] = ..., seaState: _Optional[float] = ...) -> None: ...

class RequestGetElevation(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: str
    longitude: str
    def __init__(self, latitude: _Optional[str] = ..., longitude: _Optional[str] = ...) -> None: ...

class RequestSetElectromagneticBase(_message.Message):
    __slots__ = ("electromagneticComplexityBase", "electromagneticEnergyBase")
    ELECTROMAGNETICCOMPLEXITYBASE_FIELD_NUMBER: _ClassVar[int]
    ELECTROMAGNETICENERGYBASE_FIELD_NUMBER: _ClassVar[int]
    electromagneticComplexityBase: float
    electromagneticEnergyBase: float
    def __init__(self, electromagneticComplexityBase: _Optional[float] = ..., electromagneticEnergyBase: _Optional[float] = ...) -> None: ...

class RequestSetElectromagnetic(_message.Message):
    __slots__ = ("ElectromagneticComplexity", "ElectromagneticEnergy")
    ELECTROMAGNETICCOMPLEXITY_FIELD_NUMBER: _ClassVar[int]
    ELECTROMAGNETICENERGY_FIELD_NUMBER: _ClassVar[int]
    ElectromagneticComplexity: float
    ElectromagneticEnergy: float
    def __init__(self, ElectromagneticComplexity: _Optional[float] = ..., ElectromagneticEnergy: _Optional[float] = ...) -> None: ...

class RequestAddReferencePoint(_message.Message):
    __slots__ = ("side", "name", "longitude", "latitude", "guid")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    side: str
    name: str
    longitude: float
    latitude: float
    guid: str
    def __init__(self, side: _Optional[str] = ..., name: _Optional[str] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., guid: _Optional[str] = ...) -> None: ...

class RequestDeleteReferencePoint(_message.Message):
    __slots__ = ("side", "deletePoints")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    DELETEPOINTS_FIELD_NUMBER: _ClassVar[int]
    side: str
    deletePoints: RequestDelete
    def __init__(self, side: _Optional[str] = ..., deletePoints: _Optional[_Union[RequestDelete, _Mapping]] = ...) -> None: ...

class RequestSetReferencePoint(_message.Message):
    __slots__ = ("side", "name", "longitude", "latitude")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    name: str
    longitude: float
    latitude: float
    def __init__(self, side: _Optional[str] = ..., name: _Optional[str] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ...) -> None: ...

class RequestGetReferencePoints(_message.Message):
    __slots__ = ("side", "area")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    side: str
    area: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., area: _Optional[_Iterable[str]] = ...) -> None: ...

class MIReferencePointInfo(_message.Message):
    __slots__ = ("side", "name", "longitude", "latitude", "guid", "locked", "bearingtype", "relativeto")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    BEARINGTYPE_FIELD_NUMBER: _ClassVar[int]
    RELATIVETO_FIELD_NUMBER: _ClassVar[int]
    side: str
    name: str
    longitude: float
    latitude: float
    guid: str
    locked: bool
    bearingtype: str
    relativeto: str
    def __init__(self, side: _Optional[str] = ..., name: _Optional[str] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., guid: _Optional[str] = ..., locked: bool = ..., bearingtype: _Optional[str] = ..., relativeto: _Optional[str] = ...) -> None: ...

class MIReferencePoints(_message.Message):
    __slots__ = ("points",)
    POINTS_FIELD_NUMBER: _ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[MIReferencePointInfo]
    def __init__(self, points: _Optional[_Iterable[_Union[MIReferencePointInfo, _Mapping]]] = ...) -> None: ...

class RequestSetAxisPoint(_message.Message):
    __slots__ = ("unitid", "orientationtype", "referencenpoints")
    UNITID_FIELD_NUMBER: _ClassVar[int]
    ORIENTATIONTYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCENPOINTS_FIELD_NUMBER: _ClassVar[int]
    unitid: str
    orientationtype: str
    referencenpoints: str
    def __init__(self, unitid: _Optional[str] = ..., orientationtype: _Optional[str] = ..., referencenpoints: _Optional[str] = ...) -> None: ...

class AircraftActionBase(_message.Message):
    __slots__ = ("side", "guids")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUIDS_FIELD_NUMBER: _ClassVar[int]
    side: str
    guids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., guids: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestExecuteAircraftSingleAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestExecuteAircraftGroupAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestStopAircraftAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestPrepareAircraftAction(_message.Message):
    __slots__ = ("unitName", "loadoutID", "mode", "timeToReadyMinutes")
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    LOADOUTID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    TIMETOREADYMINUTES_FIELD_NUMBER: _ClassVar[int]
    unitName: str
    loadoutID: int
    mode: int
    timeToReadyMinutes: int
    def __init__(self, unitName: _Optional[str] = ..., loadoutID: _Optional[int] = ..., mode: _Optional[int] = ..., timeToReadyMinutes: _Optional[int] = ...) -> None: ...

class RequestSetAircraftReadyTime(_message.Message):
    __slots__ = ("base", "seconds")
    BASE_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    seconds: int
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ..., seconds: _Optional[int] = ...) -> None: ...

class RequestSetAircraftLoadout(_message.Message):
    __slots__ = ("unitName", "loadoutID", "timeToReadyMinutes")
    UNITNAME_FIELD_NUMBER: _ClassVar[int]
    LOADOUTID_FIELD_NUMBER: _ClassVar[int]
    TIMETOREADYMINUTES_FIELD_NUMBER: _ClassVar[int]
    unitName: str
    loadoutID: int
    timeToReadyMinutes: int
    def __init__(self, unitName: _Optional[str] = ..., loadoutID: _Optional[int] = ..., timeToReadyMinutes: _Optional[int] = ...) -> None: ...

class RequestExecuteShipSingleAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestExecuteShipGroupAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestStopShipAction(_message.Message):
    __slots__ = ("base",)
    BASE_FIELD_NUMBER: _ClassVar[int]
    base: AircraftActionBase
    def __init__(self, base: _Optional[_Union[AircraftActionBase, _Mapping]] = ...) -> None: ...

class RequestGetContact(_message.Message):
    __slots__ = ("side", "guid")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    side: str
    guid: str
    def __init__(self, side: _Optional[str] = ..., guid: _Optional[str] = ...) -> None: ...

class RequestGetSideContacts(_message.Message):
    __slots__ = ("side",)
    SIDE_FIELD_NUMBER: _ClassVar[int]
    side: str
    def __init__(self, side: _Optional[str] = ...) -> None: ...

class RequestSetContactPosture(_message.Message):
    __slots__ = ("side", "guidList", "posture")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUIDLIST_FIELD_NUMBER: _ClassVar[int]
    POSTURE_FIELD_NUMBER: _ClassVar[int]
    side: str
    guidList: _containers.RepeatedScalarFieldContainer[str]
    posture: str
    def __init__(self, side: _Optional[str] = ..., guidList: _Optional[_Iterable[str]] = ..., posture: _Optional[str] = ...) -> None: ...

class RequestDropContactTargets(_message.Message):
    __slots__ = ("side", "guidList")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUIDLIST_FIELD_NUMBER: _ClassVar[int]
    side: str
    guidList: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, side: _Optional[str] = ..., guidList: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestMarkContactPosition(_message.Message):
    __slots__ = ("side", "guid", "newName")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    NEWNAME_FIELD_NUMBER: _ClassVar[int]
    side: str
    guid: str
    newName: str
    def __init__(self, side: _Optional[str] = ..., guid: _Optional[str] = ..., newName: _Optional[str] = ...) -> None: ...

class RequestSetContactUserData(_message.Message):
    __slots__ = ("side", "guid", "newName")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    NEWNAME_FIELD_NUMBER: _ClassVar[int]
    side: str
    guid: str
    newName: str
    def __init__(self, side: _Optional[str] = ..., guid: _Optional[str] = ..., newName: _Optional[str] = ...) -> None: ...

class AttackArrange(_message.Message):
    __slots__ = ("mode", "mount", "weapon", "qty", "latitude", "longitude", "course", "guid")
    MODE_FIELD_NUMBER: _ClassVar[int]
    MOUNT_FIELD_NUMBER: _ClassVar[int]
    WEAPON_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    mode: int
    mount: int
    weapon: int
    qty: int
    latitude: str
    longitude: str
    course: _containers.RepeatedCompositeFieldContainer[Waypoint]
    guid: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, mode: _Optional[int] = ..., mount: _Optional[int] = ..., weapon: _Optional[int] = ..., qty: _Optional[int] = ..., latitude: _Optional[str] = ..., longitude: _Optional[str] = ..., course: _Optional[_Iterable[_Union[Waypoint, _Mapping]]] = ..., guid: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestDropTarget(_message.Message):
    __slots__ = ("side", "unitId", "targetId")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    TARGETID_FIELD_NUMBER: _ClassVar[int]
    side: str
    unitId: str
    targetId: str
    def __init__(self, side: _Optional[str] = ..., unitId: _Optional[str] = ..., targetId: _Optional[str] = ...) -> None: ...

class RequestDropAllTargets(_message.Message):
    __slots__ = ("side", "unitId")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    UNITID_FIELD_NUMBER: _ClassVar[int]
    side: str
    unitId: str
    def __init__(self, side: _Optional[str] = ..., unitId: _Optional[str] = ...) -> None: ...

class RequestAttackContactAuto(_message.Message):
    __slots__ = ("guid", "target", "mode")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    target: str
    mode: int
    def __init__(self, guid: _Optional[str] = ..., target: _Optional[str] = ..., mode: _Optional[int] = ...) -> None: ...

class RequestAttackContactManual(_message.Message):
    __slots__ = ("guid", "target", "arrange")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    ARRANGE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    target: str
    arrange: AttackArrange
    def __init__(self, guid: _Optional[str] = ..., target: _Optional[str] = ..., arrange: _Optional[_Union[AttackArrange, _Mapping]] = ...) -> None: ...

class RequestCancelAttackContact(_message.Message):
    __slots__ = ("guid", "targetGuid", "mountID", "weaponID", "count")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TARGETGUID_FIELD_NUMBER: _ClassVar[int]
    MOUNTID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    targetGuid: str
    mountID: int
    weaponID: int
    count: int
    def __init__(self, guid: _Optional[str] = ..., targetGuid: _Optional[str] = ..., mountID: _Optional[int] = ..., weaponID: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class RequestSetAttackCourse(_message.Message):
    __slots__ = ("attacker", "target", "weaponDBID", "course")
    ATTACKER_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    WEAPONDBID_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    attacker: str
    target: str
    weaponDBID: int
    course: _containers.RepeatedCompositeFieldContainer[Waypoint]
    def __init__(self, attacker: _Optional[str] = ..., target: _Optional[str] = ..., weaponDBID: _Optional[int] = ..., course: _Optional[_Iterable[_Union[Waypoint, _Mapping]]] = ...) -> None: ...

class RequestAttackUnitsAuto(_message.Message):
    __slots__ = ("attackList",)
    ATTACKLIST_FIELD_NUMBER: _ClassVar[int]
    attackList: _containers.RepeatedCompositeFieldContainer[RequestAttackContactAuto]
    def __init__(self, attackList: _Optional[_Iterable[_Union[RequestAttackContactAuto, _Mapping]]] = ...) -> None: ...

class RequestAttackUnitsManual(_message.Message):
    __slots__ = ("attackList",)
    ATTACKLIST_FIELD_NUMBER: _ClassVar[int]
    attackList: _containers.RepeatedCompositeFieldContainer[RequestAttackContactManual]
    def __init__(self, attackList: _Optional[_Iterable[_Union[RequestAttackContactManual, _Mapping]]] = ...) -> None: ...

class RequestAttackBearing(_message.Message):
    __slots__ = ("guid", "target", "mode", "mount", "weapon", "qty", "latitude", "longitude", "course", "missileGuid")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MOUNT_FIELD_NUMBER: _ClassVar[int]
    WEAPON_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    MISSILEGUID_FIELD_NUMBER: _ClassVar[int]
    guid: str
    target: str
    mode: int
    mount: int
    weapon: int
    qty: int
    latitude: str
    longitude: str
    course: _containers.RepeatedCompositeFieldContainer[Waypoint]
    missileGuid: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, guid: _Optional[str] = ..., target: _Optional[str] = ..., mode: _Optional[int] = ..., mount: _Optional[int] = ..., weapon: _Optional[int] = ..., qty: _Optional[int] = ..., latitude: _Optional[str] = ..., longitude: _Optional[str] = ..., course: _Optional[_Iterable[_Union[Waypoint, _Mapping]]] = ..., missileGuid: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestExecuteChaffBurst(_message.Message):
    __slots__ = ("unitId", "enabled", "continuous")
    UNITID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    unitId: str
    enabled: bool
    continuous: bool
    def __init__(self, unitId: _Optional[str] = ..., enabled: bool = ..., continuous: bool = ...) -> None: ...

class RequestCreateExplosion(_message.Message):
    __slots__ = ("warheadId", "latitude", "longitude", "altitude", "radius")
    WARHEADID_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    warheadId: int
    latitude: float
    longitude: float
    altitude: float
    radius: float
    def __init__(self, warheadId: _Optional[int] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., altitude: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class RequestDeploySonar(_message.Message):
    __slots__ = ("guid", "type", "shallow")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SHALLOW_FIELD_NUMBER: _ClassVar[int]
    guid: str
    type: str
    shallow: bool
    def __init__(self, guid: _Optional[str] = ..., type: _Optional[str] = ..., shallow: bool = ...) -> None: ...

class RequestAddUnitCargo(_message.Message):
    __slots__ = ("count", "cargoid")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CARGOID_FIELD_NUMBER: _ClassVar[int]
    count: int
    cargoid: int
    def __init__(self, count: _Optional[int] = ..., cargoid: _Optional[int] = ...) -> None: ...

class RequestUpdateUnitCargo(_message.Message):
    __slots__ = ("guid", "ADD_CARGO", "REMOVE_CARGO")
    GUID_FIELD_NUMBER: _ClassVar[int]
    ADD_CARGO_FIELD_NUMBER: _ClassVar[int]
    REMOVE_CARGO_FIELD_NUMBER: _ClassVar[int]
    guid: str
    ADD_CARGO: _containers.RepeatedCompositeFieldContainer[RequestAddUnitCargo]
    REMOVE_CARGO: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, guid: _Optional[str] = ..., ADD_CARGO: _Optional[_Iterable[_Union[RequestAddUnitCargo, _Mapping]]] = ..., REMOVE_CARGO: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestExecuteCargoLoadOperation(_message.Message):
    __slots__ = ("hostGuid", "targetGuid", "cargoToUnit", "cargoToHost")
    HOSTGUID_FIELD_NUMBER: _ClassVar[int]
    TARGETGUID_FIELD_NUMBER: _ClassVar[int]
    CARGOTOUNIT_FIELD_NUMBER: _ClassVar[int]
    CARGOTOHOST_FIELD_NUMBER: _ClassVar[int]
    hostGuid: str
    targetGuid: str
    cargoToUnit: _containers.RepeatedScalarFieldContainer[str]
    cargoToHost: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, hostGuid: _Optional[str] = ..., targetGuid: _Optional[str] = ..., cargoToUnit: _Optional[_Iterable[str]] = ..., cargoToHost: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestImportInstFile(_message.Message):
    __slots__ = ("side", "fileContent")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    FILECONTENT_FIELD_NUMBER: _ClassVar[int]
    side: str
    fileContent: str
    def __init__(self, side: _Optional[str] = ..., fileContent: _Optional[str] = ...) -> None: ...

class RequestExportUnitToFile(_message.Message):
    __slots__ = ("side", "guidList", "filename", "name", "comment")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    GUIDLIST_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    side: str
    guidList: _containers.RepeatedScalarFieldContainer[str]
    filename: str
    name: str
    comment: str
    def __init__(self, side: _Optional[str] = ..., guidList: _Optional[_Iterable[str]] = ..., filename: _Optional[str] = ..., name: _Optional[str] = ..., comment: _Optional[str] = ...) -> None: ...

class RequestQueryDatabase(_message.Message):
    __slots__ = ("objectType", "dbid")
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    DBID_FIELD_NUMBER: _ClassVar[int]
    objectType: str
    dbid: int
    def __init__(self, objectType: _Optional[str] = ..., dbid: _Optional[int] = ...) -> None: ...

class RequestGetFacilityMaxCapacity(_message.Message):
    __slots__ = ("dbid", "guid", "addtype")
    DBID_FIELD_NUMBER: _ClassVar[int]
    GUID_FIELD_NUMBER: _ClassVar[int]
    ADDTYPE_FIELD_NUMBER: _ClassVar[int]
    dbid: str
    guid: str
    addtype: int
    def __init__(self, dbid: _Optional[str] = ..., guid: _Optional[str] = ..., addtype: _Optional[int] = ...) -> None: ...

class RequestGetWeaponSalvoQuantity(_message.Message):
    __slots__ = ("attackerID", "contactId", "weaponId")
    ATTACKERID_FIELD_NUMBER: _ClassVar[int]
    CONTACTID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    attackerID: str
    contactId: str
    weaponId: str
    def __init__(self, attackerID: _Optional[str] = ..., contactId: _Optional[str] = ..., weaponId: _Optional[str] = ...) -> None: ...

class MISatPredictionTimeInfo(_message.Message):
    __slots__ = ("satelliteID", "enterTime", "remainTime")
    SATELLITEID_FIELD_NUMBER: _ClassVar[int]
    ENTERTIME_FIELD_NUMBER: _ClassVar[int]
    REMAINTIME_FIELD_NUMBER: _ClassVar[int]
    satelliteID: str
    enterTime: float
    remainTime: float
    def __init__(self, satelliteID: _Optional[str] = ..., enterTime: _Optional[float] = ..., remainTime: _Optional[float] = ...) -> None: ...

class MISatPredictionTime(_message.Message):
    __slots__ = ("satPredictionTimes",)
    SATPREDICTIONTIMES_FIELD_NUMBER: _ClassVar[int]
    satPredictionTimes: _containers.RepeatedCompositeFieldContainer[MISatPredictionTimeInfo]
    def __init__(self, satPredictionTimes: _Optional[_Iterable[_Union[MISatPredictionTimeInfo, _Mapping]]] = ...) -> None: ...

class RequestPredictSatelliteOverflight(_message.Message):
    __slots__ = ("guidList", "longitude", "latitude", "totalSeconds")
    GUIDLIST_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    TOTALSECONDS_FIELD_NUMBER: _ClassVar[int]
    guidList: _containers.RepeatedScalarFieldContainer[str]
    longitude: float
    latitude: float
    totalSeconds: int
    def __init__(self, guidList: _Optional[_Iterable[str]] = ..., longitude: _Optional[float] = ..., latitude: _Optional[float] = ..., totalSeconds: _Optional[int] = ...) -> None: ...

class RequestSetPointsTrigger(_message.Message):
    __slots__ = ("sideID", "pointValue", "reachDirection")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    POINTVALUE_FIELD_NUMBER: _ClassVar[int]
    REACHDIRECTION_FIELD_NUMBER: _ClassVar[int]
    sideID: str
    pointValue: str
    reachDirection: str
    def __init__(self, sideID: _Optional[str] = ..., pointValue: _Optional[str] = ..., reachDirection: _Optional[str] = ...) -> None: ...

class RequestSetRandomTimeTrigger(_message.Message):
    __slots__ = ("earliestTime", "latestTime")
    EARLIESTTIME_FIELD_NUMBER: _ClassVar[int]
    LATESTTIME_FIELD_NUMBER: _ClassVar[int]
    earliestTime: str
    latestTime: str
    def __init__(self, earliestTime: _Optional[str] = ..., latestTime: _Optional[str] = ...) -> None: ...

class RequestSetRegularTimeTrigger(_message.Message):
    __slots__ = ("interval",)
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    interval: str
    def __init__(self, interval: _Optional[str] = ...) -> None: ...

class RequestSetTimeTrigger(_message.Message):
    __slots__ = ("time",)
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: str
    def __init__(self, time: _Optional[str] = ...) -> None: ...

class RequestTargetTriggerInfo(_message.Message):
    __slots__ = ("targetSide", "targetType", "targetSubType", "specificUnitClass", "specificUnitID", "weaponID")
    TARGETSIDE_FIELD_NUMBER: _ClassVar[int]
    TARGETTYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETSUBTYPE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICUNITCLASS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICUNITID_FIELD_NUMBER: _ClassVar[int]
    WEAPONID_FIELD_NUMBER: _ClassVar[int]
    targetSide: str
    targetType: str
    targetSubType: str
    specificUnitClass: str
    specificUnitID: str
    weaponID: str
    def __init__(self, targetSide: _Optional[str] = ..., targetType: _Optional[str] = ..., targetSubType: _Optional[str] = ..., specificUnitClass: _Optional[str] = ..., specificUnitID: _Optional[str] = ..., weaponID: _Optional[str] = ...) -> None: ...

class RequestSetUnitDamagedTrigger(_message.Message):
    __slots__ = ("damagePercent", "unitDamagedTarget")
    DAMAGEPERCENT_FIELD_NUMBER: _ClassVar[int]
    UNITDAMAGEDTARGET_FIELD_NUMBER: _ClassVar[int]
    damagePercent: str
    unitDamagedTarget: RequestTargetTriggerInfo
    def __init__(self, damagePercent: _Optional[str] = ..., unitDamagedTarget: _Optional[_Union[RequestTargetTriggerInfo, _Mapping]] = ...) -> None: ...

class RequestSetUnitDestroyedTrigger(_message.Message):
    __slots__ = ("unitDamagedTarget",)
    UNITDAMAGEDTARGET_FIELD_NUMBER: _ClassVar[int]
    unitDamagedTarget: RequestTargetTriggerInfo
    def __init__(self, unitDamagedTarget: _Optional[_Union[RequestTargetTriggerInfo, _Mapping]] = ...) -> None: ...

class RequestSetUnitDetectedTrigger(_message.Message):
    __slots__ = ("unitDamagedTarget", "detectorSideID", "MCL", "area")
    UNITDAMAGEDTARGET_FIELD_NUMBER: _ClassVar[int]
    DETECTORSIDEID_FIELD_NUMBER: _ClassVar[int]
    MCL_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    unitDamagedTarget: RequestTargetTriggerInfo
    detectorSideID: str
    MCL: str
    area: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unitDamagedTarget: _Optional[_Union[RequestTargetTriggerInfo, _Mapping]] = ..., detectorSideID: _Optional[str] = ..., MCL: _Optional[str] = ..., area: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetUnitEntersAreaTrigger(_message.Message):
    __slots__ = ("unitDamagedTarget", "earliestTime", "latestTime", "notArea", "exitArea", "area", "setExitArea")
    UNITDAMAGEDTARGET_FIELD_NUMBER: _ClassVar[int]
    EARLIESTTIME_FIELD_NUMBER: _ClassVar[int]
    LATESTTIME_FIELD_NUMBER: _ClassVar[int]
    NOTAREA_FIELD_NUMBER: _ClassVar[int]
    EXITAREA_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    SETEXITAREA_FIELD_NUMBER: _ClassVar[int]
    unitDamagedTarget: RequestTargetTriggerInfo
    earliestTime: str
    latestTime: str
    notArea: str
    exitArea: str
    area: _containers.RepeatedScalarFieldContainer[str]
    setExitArea: bool
    def __init__(self, unitDamagedTarget: _Optional[_Union[RequestTargetTriggerInfo, _Mapping]] = ..., earliestTime: _Optional[str] = ..., latestTime: _Optional[str] = ..., notArea: _Optional[str] = ..., exitArea: _Optional[str] = ..., area: _Optional[_Iterable[str]] = ..., setExitArea: bool = ...) -> None: ...

class RequestSetUnitRemainsInAreaTrigger(_message.Message):
    __slots__ = ("unitDamagedTarget", "TD", "area")
    UNITDAMAGEDTARGET_FIELD_NUMBER: _ClassVar[int]
    TD_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    unitDamagedTarget: RequestTargetTriggerInfo
    TD: str
    area: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unitDamagedTarget: _Optional[_Union[RequestTargetTriggerInfo, _Mapping]] = ..., TD: _Optional[str] = ..., area: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetUnitBaseStatusTrigger(_message.Message):
    __slots__ = ("targetStatus", "delayedSec")
    TARGETSTATUS_FIELD_NUMBER: _ClassVar[int]
    DELAYEDSEC_FIELD_NUMBER: _ClassVar[int]
    targetStatus: str
    delayedSec: str
    def __init__(self, targetStatus: _Optional[str] = ..., delayedSec: _Optional[str] = ...) -> None: ...

class RequestSetTrigger(_message.Message):
    __slots__ = ("mode", "type", "name", "rename", "score", "randomTime", "regularTime", "time", "unitDamaged", "unitDestroyed", "unitDetected", "unitEntersArea", "unitRemainsInArea", "unitBaseStatus", "ISTIDY")
    MODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    RANDOMTIME_FIELD_NUMBER: _ClassVar[int]
    REGULARTIME_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    UNITDAMAGED_FIELD_NUMBER: _ClassVar[int]
    UNITDESTROYED_FIELD_NUMBER: _ClassVar[int]
    UNITDETECTED_FIELD_NUMBER: _ClassVar[int]
    UNITENTERSAREA_FIELD_NUMBER: _ClassVar[int]
    UNITREMAINSINAREA_FIELD_NUMBER: _ClassVar[int]
    UNITBASESTATUS_FIELD_NUMBER: _ClassVar[int]
    ISTIDY_FIELD_NUMBER: _ClassVar[int]
    mode: str
    type: str
    name: str
    rename: str
    score: RequestSetPointsTrigger
    randomTime: RequestSetRandomTimeTrigger
    regularTime: RequestSetRegularTimeTrigger
    time: RequestSetTimeTrigger
    unitDamaged: RequestSetUnitDamagedTrigger
    unitDestroyed: RequestSetUnitDestroyedTrigger
    unitDetected: RequestSetUnitDetectedTrigger
    unitEntersArea: RequestSetUnitEntersAreaTrigger
    unitRemainsInArea: RequestSetUnitRemainsInAreaTrigger
    unitBaseStatus: RequestSetUnitBaseStatusTrigger
    ISTIDY: str
    def __init__(self, mode: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., rename: _Optional[str] = ..., score: _Optional[_Union[RequestSetPointsTrigger, _Mapping]] = ..., randomTime: _Optional[_Union[RequestSetRandomTimeTrigger, _Mapping]] = ..., regularTime: _Optional[_Union[RequestSetRegularTimeTrigger, _Mapping]] = ..., time: _Optional[_Union[RequestSetTimeTrigger, _Mapping]] = ..., unitDamaged: _Optional[_Union[RequestSetUnitDamagedTrigger, _Mapping]] = ..., unitDestroyed: _Optional[_Union[RequestSetUnitDestroyedTrigger, _Mapping]] = ..., unitDetected: _Optional[_Union[RequestSetUnitDetectedTrigger, _Mapping]] = ..., unitEntersArea: _Optional[_Union[RequestSetUnitEntersAreaTrigger, _Mapping]] = ..., unitRemainsInArea: _Optional[_Union[RequestSetUnitRemainsInAreaTrigger, _Mapping]] = ..., unitBaseStatus: _Optional[_Union[RequestSetUnitBaseStatusTrigger, _Mapping]] = ..., ISTIDY: _Optional[str] = ...) -> None: ...

class RequestSetChangeMissionStatusAction(_message.Message):
    __slots__ = ("sideId", "missionID", "newStatus")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    MISSIONID_FIELD_NUMBER: _ClassVar[int]
    NEWSTATUS_FIELD_NUMBER: _ClassVar[int]
    sideId: str
    missionID: str
    newStatus: str
    def __init__(self, sideId: _Optional[str] = ..., missionID: _Optional[str] = ..., newStatus: _Optional[str] = ...) -> None: ...

class RequestSetLuaScriptAction(_message.Message):
    __slots__ = ("scriptText",)
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    scriptText: str
    def __init__(self, scriptText: _Optional[str] = ...) -> None: ...

class RequestSetMessageAction(_message.Message):
    __slots__ = ("sideId", "messageText")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    MESSAGETEXT_FIELD_NUMBER: _ClassVar[int]
    sideId: str
    messageText: str
    def __init__(self, sideId: _Optional[str] = ..., messageText: _Optional[str] = ...) -> None: ...

class RequestSetPointsAction(_message.Message):
    __slots__ = ("sideId", "pointChange")
    SIDEID_FIELD_NUMBER: _ClassVar[int]
    POINTCHANGE_FIELD_NUMBER: _ClassVar[int]
    sideId: str
    pointChange: str
    def __init__(self, sideId: _Optional[str] = ..., pointChange: _Optional[str] = ...) -> None: ...

class RequestSetTeleportInAreaAction(_message.Message):
    __slots__ = ("unitIDs", "area")
    UNITIDS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    unitIDs: _containers.RepeatedScalarFieldContainer[str]
    area: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unitIDs: _Optional[_Iterable[str]] = ..., area: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetAction(_message.Message):
    __slots__ = ("mode", "type", "name", "rename", "changeMissionStatus", "luaScript", "msg", "points", "teleportInArea", "ISTIDY")
    MODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    CHANGEMISSIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    LUASCRIPT_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    TELEPORTINAREA_FIELD_NUMBER: _ClassVar[int]
    ISTIDY_FIELD_NUMBER: _ClassVar[int]
    mode: str
    type: str
    name: str
    rename: str
    changeMissionStatus: RequestSetChangeMissionStatusAction
    luaScript: RequestSetLuaScriptAction
    msg: RequestSetMessageAction
    points: RequestSetPointsAction
    teleportInArea: RequestSetTeleportInAreaAction
    ISTIDY: str
    def __init__(self, mode: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., rename: _Optional[str] = ..., changeMissionStatus: _Optional[_Union[RequestSetChangeMissionStatusAction, _Mapping]] = ..., luaScript: _Optional[_Union[RequestSetLuaScriptAction, _Mapping]] = ..., msg: _Optional[_Union[RequestSetMessageAction, _Mapping]] = ..., points: _Optional[_Union[RequestSetPointsAction, _Mapping]] = ..., teleportInArea: _Optional[_Union[RequestSetTeleportInAreaAction, _Mapping]] = ..., ISTIDY: _Optional[str] = ...) -> None: ...

class RequestSetEvent(_message.Message):
    __slots__ = ("name", "mode", "rename", "isActive", "isRepeatable", "IsShown", "probability", "trigger", "condition", "action")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    ISREPEATABLE_FIELD_NUMBER: _ClassVar[int]
    ISSHOWN_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    mode: str
    rename: str
    isActive: bool
    isRepeatable: bool
    IsShown: bool
    probability: int
    trigger: _containers.RepeatedScalarFieldContainer[str]
    condition: _containers.RepeatedScalarFieldContainer[str]
    action: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., mode: _Optional[str] = ..., rename: _Optional[str] = ..., isActive: bool = ..., isRepeatable: bool = ..., IsShown: bool = ..., probability: _Optional[int] = ..., trigger: _Optional[_Iterable[str]] = ..., condition: _Optional[_Iterable[str]] = ..., action: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSetSidePostureCondition(_message.Message):
    __slots__ = ("ObserverSideID", "TargetSideID", "TargetPosture")
    OBSERVERSIDEID_FIELD_NUMBER: _ClassVar[int]
    TARGETSIDEID_FIELD_NUMBER: _ClassVar[int]
    TARGETPOSTURE_FIELD_NUMBER: _ClassVar[int]
    ObserverSideID: str
    TargetSideID: str
    TargetPosture: int
    def __init__(self, ObserverSideID: _Optional[str] = ..., TargetSideID: _Optional[str] = ..., TargetPosture: _Optional[int] = ...) -> None: ...

class RequestSetLuaScriptCondition(_message.Message):
    __slots__ = ("scriptText",)
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    scriptText: str
    def __init__(self, scriptText: _Optional[str] = ...) -> None: ...

class RequestSetCondition(_message.Message):
    __slots__ = ("mode", "type", "name", "rename", "NOT", "sidePosture", "luaScript")
    MODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    NOT_FIELD_NUMBER: _ClassVar[int]
    SIDEPOSTURE_FIELD_NUMBER: _ClassVar[int]
    LUASCRIPT_FIELD_NUMBER: _ClassVar[int]
    mode: str
    type: str
    name: str
    rename: str
    NOT: str
    sidePosture: RequestSetSidePostureCondition
    luaScript: RequestSetLuaScriptCondition
    def __init__(self, mode: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., rename: _Optional[str] = ..., NOT: _Optional[str] = ..., sidePosture: _Optional[_Union[RequestSetSidePostureCondition, _Mapping]] = ..., luaScript: _Optional[_Union[RequestSetLuaScriptCondition, _Mapping]] = ...) -> None: ...

class RequestSetEventTrigger(_message.Message):
    __slots__ = ("eventName", "mode", "name")
    EVENTNAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    eventName: str
    mode: str
    name: str
    def __init__(self, eventName: _Optional[str] = ..., mode: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RequestSetEventAction(_message.Message):
    __slots__ = ("eventName", "mode", "name")
    EVENTNAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    eventName: str
    mode: str
    name: str
    def __init__(self, eventName: _Optional[str] = ..., mode: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RequestSetEventCondition(_message.Message):
    __slots__ = ("eventName", "mode", "name")
    EVENTNAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    eventName: str
    mode: str
    name: str
    def __init__(self, eventName: _Optional[str] = ..., mode: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RequestExecuteEventAction(_message.Message):
    __slots__ = ("eventDescriptionOrID", "script")
    EVENTDESCRIPTIONORID_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    eventDescriptionOrID: str
    script: str
    def __init__(self, eventDescriptionOrID: _Optional[str] = ..., script: _Optional[str] = ...) -> None: ...

class RequestUpdateEvent(_message.Message):
    __slots__ = ("eventDescriptionOrID", "type", "description", "script")
    EVENTDESCRIPTIONORID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    eventDescriptionOrID: str
    type: str
    description: str
    script: str
    def __init__(self, eventDescriptionOrID: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., script: _Optional[str] = ...) -> None: ...

class RequestSetSpecialAction(_message.Message):
    __slots__ = ("side", "actionNameOrID", "description", "scriptText", "isActive", "isRepeatable", "newName")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ACTIONNAMEORID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCRIPTTEXT_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    ISREPEATABLE_FIELD_NUMBER: _ClassVar[int]
    NEWNAME_FIELD_NUMBER: _ClassVar[int]
    side: str
    actionNameOrID: str
    description: str
    scriptText: str
    isActive: bool
    isRepeatable: bool
    newName: str
    def __init__(self, side: _Optional[str] = ..., actionNameOrID: _Optional[str] = ..., description: _Optional[str] = ..., scriptText: _Optional[str] = ..., isActive: bool = ..., isRepeatable: bool = ..., newName: _Optional[str] = ...) -> None: ...

class RequestExecuteSpecialAction(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class RequestQueryMessageLog(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class RequestSendMessage(_message.Message):
    __slots__ = ("msgString",)
    MSGSTRING_FIELD_NUMBER: _ClassVar[int]
    msgString: str
    def __init__(self, msgString: _Optional[str] = ...) -> None: ...

class RequestSetUserData(_message.Message):
    __slots__ = ("side", "sKey", "base64Json")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SKEY_FIELD_NUMBER: _ClassVar[int]
    BASE64JSON_FIELD_NUMBER: _ClassVar[int]
    side: str
    sKey: str
    base64Json: bytes
    def __init__(self, side: _Optional[str] = ..., sKey: _Optional[str] = ..., base64Json: _Optional[bytes] = ...) -> None: ...

class RequestGetUserData(_message.Message):
    __slots__ = ("side", "sKey")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    SKEY_FIELD_NUMBER: _ClassVar[int]
    side: str
    sKey: str
    def __init__(self, side: _Optional[str] = ..., sKey: _Optional[str] = ...) -> None: ...

class RequestGetEngineGUID(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class RequestRequestCurrentFullSituation(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class RequestAddZone(_message.Message):
    __slots__ = ("side", "zoneType", "description")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ZONETYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    side: str
    zoneType: int
    description: str
    def __init__(self, side: _Optional[str] = ..., zoneType: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class RequestSetZone(_message.Message):
    __slots__ = ("side", "zoneType", "description", "rename", "altitude", "isActive", "area", "affects", "locked", "markAs", "diameter")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ZONETYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    ISACTIVE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    AFFECTS_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    MARKAS_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    side: str
    zoneType: int
    description: str
    rename: str
    altitude: float
    isActive: bool
    area: _containers.RepeatedScalarFieldContainer[str]
    affects: _containers.RepeatedScalarFieldContainer[int]
    locked: bool
    markAs: int
    diameter: float
    def __init__(self, side: _Optional[str] = ..., zoneType: _Optional[int] = ..., description: _Optional[str] = ..., rename: _Optional[str] = ..., altitude: _Optional[float] = ..., isActive: bool = ..., area: _Optional[_Iterable[str]] = ..., affects: _Optional[_Iterable[int]] = ..., locked: bool = ..., markAs: _Optional[int] = ..., diameter: _Optional[float] = ...) -> None: ...

class RequestRemoveZone(_message.Message):
    __slots__ = ("side", "zoneType", "zoneGuid")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ZONETYPE_FIELD_NUMBER: _ClassVar[int]
    ZONEGUID_FIELD_NUMBER: _ClassVar[int]
    side: str
    zoneType: int
    zoneGuid: str
    def __init__(self, side: _Optional[str] = ..., zoneType: _Optional[int] = ..., zoneGuid: _Optional[str] = ...) -> None: ...

class RequestSetSideNetwork(_message.Message):
    __slots__ = ("sideGuid", "networkType", "subNetworkType")
    SIDEGUID_FIELD_NUMBER: _ClassVar[int]
    NETWORKTYPE_FIELD_NUMBER: _ClassVar[int]
    SUBNETWORKTYPE_FIELD_NUMBER: _ClassVar[int]
    sideGuid: str
    networkType: int
    subNetworkType: int
    def __init__(self, sideGuid: _Optional[str] = ..., networkType: _Optional[int] = ..., subNetworkType: _Optional[int] = ...) -> None: ...

class RequestAddClusterNetwork(_message.Message):
    __slots__ = ("sideGuid", "clusterGuid", "clusterName", "clusterType", "color", "maxUnits", "supUnitType")
    SIDEGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERNAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTERTYPE_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    MAXUNITS_FIELD_NUMBER: _ClassVar[int]
    SUPUNITTYPE_FIELD_NUMBER: _ClassVar[int]
    sideGuid: str
    clusterGuid: str
    clusterName: str
    clusterType: int
    color: int
    maxUnits: int
    supUnitType: int
    def __init__(self, sideGuid: _Optional[str] = ..., clusterGuid: _Optional[str] = ..., clusterName: _Optional[str] = ..., clusterType: _Optional[int] = ..., color: _Optional[int] = ..., maxUnits: _Optional[int] = ..., supUnitType: _Optional[int] = ...) -> None: ...

class RequestUpdateClusterNetwork(_message.Message):
    __slots__ = ("sideGuid", "clusterGuid", "clusterName", "color", "maxUnits", "supUnitType", "startTime", "endTime", "areaType", "bindUnitID", "areaRadius", "referencePoints")
    SIDEGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERNAME_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    MAXUNITS_FIELD_NUMBER: _ClassVar[int]
    SUPUNITTYPE_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    AREATYPE_FIELD_NUMBER: _ClassVar[int]
    BINDUNITID_FIELD_NUMBER: _ClassVar[int]
    AREARADIUS_FIELD_NUMBER: _ClassVar[int]
    REFERENCEPOINTS_FIELD_NUMBER: _ClassVar[int]
    sideGuid: str
    clusterGuid: str
    clusterName: str
    color: int
    maxUnits: int
    supUnitType: int
    startTime: int
    endTime: int
    areaType: int
    bindUnitID: str
    areaRadius: int
    referencePoints: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sideGuid: _Optional[str] = ..., clusterGuid: _Optional[str] = ..., clusterName: _Optional[str] = ..., color: _Optional[int] = ..., maxUnits: _Optional[int] = ..., supUnitType: _Optional[int] = ..., startTime: _Optional[int] = ..., endTime: _Optional[int] = ..., areaType: _Optional[int] = ..., bindUnitID: _Optional[str] = ..., areaRadius: _Optional[int] = ..., referencePoints: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestUpdateClusterMember(_message.Message):
    __slots__ = ("operation", "sideGuid", "clusterGuid", "memberList")
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    SIDEGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERGUID_FIELD_NUMBER: _ClassVar[int]
    MEMBERLIST_FIELD_NUMBER: _ClassVar[int]
    operation: int
    sideGuid: str
    clusterGuid: str
    memberList: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, operation: _Optional[int] = ..., sideGuid: _Optional[str] = ..., clusterGuid: _Optional[str] = ..., memberList: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestDeleteClusterNetwork(_message.Message):
    __slots__ = ("sideGuid", "clusterGuid")
    SIDEGUID_FIELD_NUMBER: _ClassVar[int]
    CLUSTERGUID_FIELD_NUMBER: _ClassVar[int]
    sideGuid: str
    clusterGuid: str
    def __init__(self, sideGuid: _Optional[str] = ..., clusterGuid: _Optional[str] = ...) -> None: ...

class RequestAddNetworkPlan(_message.Message):
    __slots__ = ("sendGuid", "recGuid")
    SENDGUID_FIELD_NUMBER: _ClassVar[int]
    RECGUID_FIELD_NUMBER: _ClassVar[int]
    sendGuid: str
    recGuid: str
    def __init__(self, sendGuid: _Optional[str] = ..., recGuid: _Optional[str] = ...) -> None: ...

class RequestSetNetworkProperty(_message.Message):
    __slots__ = ("sendGuid", "recGuid", "msgPassProbability", "msgDelayMin", "msgDelayMax")
    SENDGUID_FIELD_NUMBER: _ClassVar[int]
    RECGUID_FIELD_NUMBER: _ClassVar[int]
    MSGPASSPROBABILITY_FIELD_NUMBER: _ClassVar[int]
    MSGDELAYMIN_FIELD_NUMBER: _ClassVar[int]
    MSGDELAYMAX_FIELD_NUMBER: _ClassVar[int]
    sendGuid: str
    recGuid: str
    msgPassProbability: float
    msgDelayMin: float
    msgDelayMax: float
    def __init__(self, sendGuid: _Optional[str] = ..., recGuid: _Optional[str] = ..., msgPassProbability: _Optional[float] = ..., msgDelayMin: _Optional[float] = ..., msgDelayMax: _Optional[float] = ...) -> None: ...

class RequestRemoveNetworkPlan(_message.Message):
    __slots__ = ("sendGuid", "recGuid")
    SENDGUID_FIELD_NUMBER: _ClassVar[int]
    RECGUID_FIELD_NUMBER: _ClassVar[int]
    sendGuid: str
    recGuid: str
    def __init__(self, sendGuid: _Optional[str] = ..., recGuid: _Optional[str] = ...) -> None: ...

class RequestSetIntelligenceCenter(_message.Message):
    __slots__ = ("centerGuid", "aircraftDownloadCycle", "shipDownloadCycle", "submarineDownloadCycle", "facilityDownloadCycle")
    CENTERGUID_FIELD_NUMBER: _ClassVar[int]
    AIRCRAFTDOWNLOADCYCLE_FIELD_NUMBER: _ClassVar[int]
    SHIPDOWNLOADCYCLE_FIELD_NUMBER: _ClassVar[int]
    SUBMARINEDOWNLOADCYCLE_FIELD_NUMBER: _ClassVar[int]
    FACILITYDOWNLOADCYCLE_FIELD_NUMBER: _ClassVar[int]
    centerGuid: str
    aircraftDownloadCycle: int
    shipDownloadCycle: int
    submarineDownloadCycle: int
    facilityDownloadCycle: int
    def __init__(self, centerGuid: _Optional[str] = ..., aircraftDownloadCycle: _Optional[int] = ..., shipDownloadCycle: _Optional[int] = ..., submarineDownloadCycle: _Optional[int] = ..., facilityDownloadCycle: _Optional[int] = ...) -> None: ...

class RequestRemoveIntelligenceCenter(_message.Message):
    __slots__ = ("centerGuid",)
    CENTERGUID_FIELD_NUMBER: _ClassVar[int]
    centerGuid: str
    def __init__(self, centerGuid: _Optional[str] = ...) -> None: ...

class RequestUpdateAutoDetection(_message.Message):
    __slots__ = ("unitGuid",)
    UNITGUID_FIELD_NUMBER: _ClassVar[int]
    unitGuid: str
    def __init__(self, unitGuid: _Optional[str] = ...) -> None: ...

class RequestHeartBeat(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: SimpleRequest
    def __init__(self, request: _Optional[_Union[SimpleRequest, _Mapping]] = ...) -> None: ...

class RequestAssignUnitAsTarget(_message.Message):
    __slots__ = ("targetGuids", "missionName")
    TARGETGUIDS_FIELD_NUMBER: _ClassVar[int]
    MISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    targetGuids: _containers.RepeatedScalarFieldContainer[str]
    missionName: str
    def __init__(self, targetGuids: _Optional[_Iterable[str]] = ..., missionName: _Optional[str] = ...) -> None: ...

class RequestRemoveUnitAsTarget(_message.Message):
    __slots__ = ("targetGuids", "missionName")
    TARGETGUIDS_FIELD_NUMBER: _ClassVar[int]
    MISSIONNAME_FIELD_NUMBER: _ClassVar[int]
    targetGuids: _containers.RepeatedScalarFieldContainer[str]
    missionName: str
    def __init__(self, targetGuids: _Optional[_Iterable[str]] = ..., missionName: _Optional[str] = ...) -> None: ...
