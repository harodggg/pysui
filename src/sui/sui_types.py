"""Sui Types."""

import json
from numbers import Number
from typing import TypeVar
from abstracts import (
    ClientObjectDescriptor,
    ClientType,
    ClientPackage,
    ClientAbstractClassType,
    ClientAbstractScalarType,
)


class SuiScalarType(ClientAbstractScalarType):
    """Base most SUI scalar type."""


class SuiString(SuiScalarType):
    """Sui String type."""


class SuiNumber(SuiScalarType):
    """Sui Number type."""


class ObjectID(SuiString):
    """Sui Object id type."""

    def __init__(self, value: str) -> None:
        """Initialize with identifier."""
        super().__init__(value)
        self.object_id = value


class SuiType(ClientAbstractClassType):
    """Base most SUI object type."""


class SuiRawDescriptor(ClientObjectDescriptor, SuiType):
    """Base descriptor type."""

    def __init__(self, indata: dict, identifier: ObjectID) -> None:
        """Initiate base SUI type."""
        super().__init__(identifier)
        self._type_raw = indata

    def json(self) -> str:
        """Return as JSON compressed string."""
        return json.dumps(self._type_raw)

    def json_pretty(self, indent: int = 4) -> str:
        """Return as JSON pretty print string."""
        return json.dumps(self._type_raw, indent=indent)


class ObjectInfo(SuiRawDescriptor):
    """Base SUI Type Descriptor."""

    def __init__(self, indata: dict) -> None:
        """Initialize the base descriptor."""
        super().__init__(indata, ObjectID(indata["objectId"]))
        self._version = indata["version"]
        self._digest = indata["digest"]
        # TODO: Convert to SuiAddress
        self._owner = indata["owner"]["AddressOwner"]
        self._previous_transaction = indata["previousTransaction"]
        self._type_signature = indata["type"]

    @property
    def version(self) -> int:
        """Return the types version."""
        return self._version

    @property
    def digest(self) -> str:
        """Return the type digest."""
        return self._digest

    @property
    def owner(self) -> str:
        """Return the types instance owner."""
        return self._owner

    @property
    def previous_transaction(self) -> str:
        """Return the previous transaction base64 signature string."""
        return self._previous_transaction

    @property
    def type_signature(self) -> str:
        """Return the types type."""
        return self._type_signature


class SuiDataDescriptor(ObjectInfo):
    """Sui Data base type."""


class SuiNftDescriptor(ObjectInfo):
    """Sui NFT base type."""


class SuiCoinDescriptor(ObjectInfo):
    """Sui Coin but not necessarily gas."""


class SuiNativeCoinDescriptor(SuiCoinDescriptor):
    """Sui gas is a coin."""


class SuiRawObject(ClientType, SuiType):
    """Base object type."""

    def __init__(self, indata: dict, identifier: ObjectID) -> None:
        """Initiate base SUI type."""
        super().__init__(identifier)
        self._type_raw = indata

    def json(self) -> str:
        """Return as JSON compressed string."""
        return json.dumps(self._type_raw)

    def json_pretty(self, indent: int = 4) -> str:
        """Return as JSON pretty print string."""
        return json.dumps(self._type_raw, indent=indent)


class ObjectRead(SuiRawObject):
    """Base SUI Type."""

    def __init__(self, indata: dict, descriptor: ObjectInfo) -> None:
        """Initialize the base type data."""
        super().__init__(indata, ObjectID(indata["fields"]["id"]["id"]))
        self._type_signature = indata["type"]
        self._data_type = indata["dataType"]
        self._has_public_transfer = indata["has_public_transfer"]
        self._descriptor = descriptor
        self._previous_transaction = indata["previousTransaction"]
        self._storage_rebate = indata["storageRebate"]

    @property
    def version(self) -> int:
        """Return the types version."""
        return self._descriptor.version

    @property
    def digest(self) -> str:
        """Return the types digest."""
        return self._descriptor.digest

    @property
    def data_type(self) -> str:
        """Return the data type."""
        return self._data_type

    @property
    def type_signature(self) -> str:
        """Return the types type."""
        return self._type_signature

    @property
    def has_public_transfer(self) -> bool:
        """Return the types transferability."""
        return self._has_public_transfer

    @property
    def previous_transaction(self) -> str:
        """Return the previous transaction base64 signature string."""
        return self._previous_transaction

    @property
    def storage_rebate(self) -> int:
        """Return the storage rebate if object deleted."""
        return self._storage_rebate

    @property
    def descriptor(self) -> ObjectInfo:
        """Return the objects type descriptor."""
        return self._descriptor


class SuiNftType(ObjectRead):
    """Sui NFT base type."""

    def __init__(self, indata: dict, descriptor: ObjectInfo) -> None:
        """Initialize the base Nft type."""
        super().__init__(indata, descriptor)
        self._description = indata["fields"]["description"]
        self._name = indata["fields"]["name"]
        self._url = indata["fields"]["url"]

    @property
    def name(self) -> str:
        """Get name for Nft."""
        return self._name

    @property
    def description(self) -> str:
        """Get description for Nft."""
        return self._description

    @property
    def url(self) -> str:
        """Get Url for Nft."""
        return self._url


DT = TypeVar("DT", bound="SuiDataType")


class SuiDataType(ObjectRead):
    """Sui Data type."""

    def __init__(self, indata: dict, descriptor: ObjectInfo) -> None:
        """Initialize the base Data type."""
        super().__init__(indata, descriptor)
        self._children = []
        self._data = {}
        split = self.type_signature.split("::", 2)
        self._data_definition = dict(zip(["package", "module", "structure"], split))
        for key, value in indata["fields"].items():
            if not key == "id":
                self._data[key] = value

    @property
    def data_definition(self) -> dict:
        """Get the data definition meta data."""
        return self._data_definition

    @property
    def package(self) -> str:
        """Get the data objects owning package id."""
        return self.data_definition["package"]

    @property
    def module(self) -> str:
        """Get the data objects owning module id."""
        return self.data_definition["module"]

    @property
    def structure(self) -> str:
        """Get the data objects structure id."""
        return self.data_definition["structure"]

    @property
    def data(self) -> dict:
        """Get the actual objects data."""
        return self._data

    @property
    def children(self) -> list[DT]:
        """Get the children of this data."""
        return self._children

    def add_child(self, child: DT) -> None:
        """Store data child owned by self."""
        self.children.append(child)


class SuiCoinType(ObjectRead):
    """Sui Coin type but not necessarily gas type."""


class SuiGasType(SuiCoinType):
    """Sui gas is a coin."""

    def __init__(self, indata: dict, descriptor: ObjectInfo) -> None:
        """Initialize the base type."""
        super().__init__(indata, descriptor)
        self._balance = indata["fields"]["balance"]

    @property
    def balance(self) -> Number:
        """Get the balance for this coin object."""
        return self._balance


class SuiPackage(ClientPackage):
    """Sui package."""

    def __init__(self, package_id: str, blob) -> None:
        """Initialize a package construct."""
        super().__init__()
        self._package_id = package_id
        self._blob = blob

    @property
    def package_id(self) -> str:
        """Get the packages id."""
        return self._package_id


def from_object_descriptor(indata: dict) -> ObjectInfo:
    """Parse an inbound JSON like dictionary to a Sui type."""
    # print(indata)
    split = indata["type"].split("::", 2)
    if split[0] == "0x2":
        match split[1]:
            case "coin":
                split2 = split[2][5:-1].split("::")
                if split2[2] == "SUI":
                    return SuiNativeCoinDescriptor(indata)
                return SuiCoinDescriptor(indata)
            case "devnet_nft":
                if split[2] == "DevNetNFT":
                    return SuiNftDescriptor(indata)
    else:
        if len(split) == 3:
            return SuiDataDescriptor(indata)

    return ObjectInfo(indata)


def from_object_type(descriptor: ObjectInfo, inblock: dict) -> ObjectRead:
    """Parse an inbound JSON like dictionary to a Sui type."""
    indata = inblock["data"]
    indata["previousTransaction"] = inblock["previousTransaction"]
    indata["storageRebate"] = inblock["storageRebate"]
    split = indata["type"].split("::", 2)

    if split[0] == "0x2":
        match split[1]:
            case "coin":
                split2 = split[2][5:-1].split("::")
                if split2[2] == "SUI":
                    return SuiGasType(indata, descriptor)
                return SuiCoinType(indata, descriptor)
            case "devnet_nft":
                if split[2] == "DevNetNFT":
                    return SuiNftType(indata, descriptor)
    else:
        if len(split) == 3:
            return SuiDataType(indata, descriptor)
    return ObjectRead(indata, descriptor)
