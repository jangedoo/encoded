from __future__ import annotations

from typing import Iterable

from encoded.fields import EncoderInput, Field, FieldValue


class DocumentMeta(type):
    def __new__(cls, clsname, bases, attrs):
        parents = [b for b in bases if isinstance(b, DocumentMeta)]
        if not parents:
            return super().__new__(cls, clsname, bases, attrs)
        fields = {}
        basic_attrs = dict(attrs)
        contributable_attrs = {}
        for attr_name, attr in attrs.items():
            if isinstance(attr, Field):
                fields[attr_name] = attr
            if hasattr(attr, "contribute_to_class"):
                contributable_attrs[attr_name] = attr
                del basic_attrs[attr_name]
        basic_attrs["__fields"] = fields
        new_cls = super().__new__(cls, clsname, bases, basic_attrs)
        for attr_name, attr in contributable_attrs.items():
            attr.contribute_to_class(new_cls, attr_name)
        return new_cls


class Document(metaclass=DocumentMeta):
    def __init__(self, **kwargs):
        for field_name, field in self.get_fields().items():
            passed_value = kwargs.get(field_name)
            if field.allow_none is False and passed_value is None:
                raise ValueError(f"{field_name} cannot be None")
            setattr(self, field_name, passed_value)

    @classmethod
    def get_fields(cls) -> dict[str, Field]:
        return getattr(cls, "__fields")

    def encode(self):
        for field_name, field in self.get_fields().items():
            if not field.is_encodeable:
                continue
            existing_value: FieldValue = getattr(self, field_name)
            encoder_input = EncoderInput(value=existing_value.value)
            setattr(self, field_name, encoder_input)
        return self

    @classmethod
    def batch_encode(cls, docs: Iterable[Document]):
        for field_name, field in cls.get_fields().items():
            if not field.is_encodeable:
                continue
            field_values = [getattr(doc, field.public_name) for doc in docs]
            encoded_values = field.encoder.encode([v.value for v in field_values])
            for doc, orig_field_value, encoded_value in zip(
                docs, field_values, encoded_values
            ):
                new_field_value = FieldValue(
                    value=orig_field_value.value, encoded_value=encoded_value
                )
                setattr(doc, field.public_name, new_field_value)
        return docs

    @classmethod
    def batch_create(cls, **kwargs):
        docs = []
        for row in [dict(zip(kwargs, t)) for t in zip(*kwargs.values())]:
            doc = cls(**row)
            docs.append(doc)
        return docs

    def __repr__(self):
        return f"{self.__class__.__name__}(fields={list(self.get_fields().keys())})"
