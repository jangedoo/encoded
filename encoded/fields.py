from __future__ import annotations

from typing import TYPE_CHECKING, Type, overload

from encoded.base import BaseEncoder

if TYPE_CHECKING:
    from encoded.document import Document


class FieldValue:
    def __init__(self, value, encoded_value=None):
        self.value = value
        self.encoded_value = encoded_value

    @property
    def is_encoded(self):
        return self.encoded_value is not None

    def __str__(self):
        return f"FieldValue(value={self.value}, encoded_value={self.encoded_value})"

    def __repr__(self):
        return self.__str__()


class EncoderInput:
    def __init__(self, value):
        self.value = value


class Field:
    def __init__(self, encoder: BaseEncoder | None = None, allow_none=False):
        self.allow_none = allow_none
        self.encoder = encoder

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name

    @overload
    def __get__(self, obj: None, objtype: Type["Document"]) -> Field:
        ...

    @overload
    def __get__(self, obj: "Document", objtype: Type["Document"]) -> FieldValue:
        ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if self.allow_none is False and value is None:
            raise ValueError(
                f"{self.public_name} cannot be None since allow_none is set to False"
            )
        if isinstance(value, EncoderInput):
            if self.encoder is None:
                raise Exception(
                    f"encoder for {obj.__class__}.{self.public_name} is not configured. Did you call {obj.__class__}.{self.public_name}.set_encoder(...)?"
                )
            raw_value = value.value
            encoded = self.encoder.encode(raw_value)
            fv = FieldValue(value=raw_value, encoded_value=encoded)
        elif isinstance(value, FieldValue):
            fv = value
        else:
            fv = FieldValue(value=value)
        setattr(obj, self.private_name, fv)

    @property
    def is_encodeable(self):
        return self.encoder is not None

    def set_encoder(self, encoder):
        self.encoder = encoder

    def __repr__(self):
        return f"Field(name={self.public_name}, allow_none={self.allow_none}, is_encodeable={self.is_encodeable})"
