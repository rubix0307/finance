from typing import TypedDict, Dict, TypeAlias


Seconds: TypeAlias = int

KeyName: TypeAlias = str
KeyFull: TypeAlias = str
KeyIdentifier: TypeAlias = str
Keys: TypeAlias = Dict[KeyName, KeyFull]

class ProcessPhotoResponse(TypedDict):
    status: str

class ProcessPhotoError(TypedDict):
    error: str

