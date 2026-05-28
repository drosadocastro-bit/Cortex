"""JSON-compatible serialization for project dataclasses."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, get_args, get_origin, get_type_hints

import roswell_uap_cortex.models as models


MODEL_REGISTRY = {
    name: value
    for name, value in vars(models).items()
    if isinstance(value, type) and is_dataclass(value)
}


class Serializer:
    """Serialize and deserialize known project models without dropping unknown fields."""

    def to_json_compatible(self, value: Any) -> Any:
        if is_dataclass(value):
            return {
                field.name: self.to_json_compatible(getattr(value, field.name))
                for field in fields(value)
            }
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, set):
            return sorted(self.to_json_compatible(item) for item in value)
        if isinstance(value, tuple):
            return [self.to_json_compatible(item) for item in value]
        if isinstance(value, list):
            return [self.to_json_compatible(item) for item in value]
        if isinstance(value, dict):
            return {
                str(key): self.to_json_compatible(value[key])
                for key in sorted(value, key=lambda item: str(item))
            }
        return value

    def serialize_record(self, value: Any) -> models.PersistenceRecord:
        payload = self.to_json_compatible(value)
        return models.PersistenceRecord(
            record_type=type(value).__name__,
            payload=payload,
            record_id=payload.get("id") or payload.get("source_id") or payload.get("evidence_id"),
        )

    def deserialize_record(self, record: models.PersistenceRecord) -> Any:
        cls = MODEL_REGISTRY.get(record.record_type)
        if cls is None:
            return record
        return self.deserialize_model(record.record_type, record.payload, record.unknown_fields)

    def deserialize_model(
        self,
        record_type: str,
        payload: dict[str, Any],
        unknown_fields: dict[str, Any] | None = None,
    ) -> Any:
        cls = MODEL_REGISTRY[record_type]
        field_map = {field.name: field for field in fields(cls)}
        type_hints = get_type_hints(cls)
        init_values: dict[str, Any] = {}
        extras = dict(unknown_fields or {})

        for key, value in payload.items():
            if key in field_map:
                init_values[key] = self._restore_value(value, type_hints.get(key, field_map[key].type))
            else:
                extras[key] = value

        if extras and "metadata" in field_map:
            metadata = dict(init_values.get("metadata") or {})
            metadata["unknown_fields"] = extras
            init_values["metadata"] = metadata

        return cls(**init_values)

    def _restore_value(self, value: Any, annotation: Any) -> Any:
        if value is None:
            return None
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is list:
            subtype = args[0] if args else Any
            return [self._restore_value(item, subtype) for item in value]
        if origin is set:
            subtype = args[0] if args else Any
            return {self._restore_value(item, subtype) for item in value}
        if origin is dict:
            return dict(value)
        if origin is tuple:
            subtype = args[0] if args else Any
            return tuple(self._restore_value(item, subtype) for item in value)
        if origin in {type(None), object}:
            return value
        if origin is not None and args:
            non_none = [arg for arg in args if arg is not type(None)]
            if len(non_none) == 1:
                return self._restore_value(value, non_none[0])

        if annotation is datetime:
            return datetime.fromisoformat(value)
        if annotation is date:
            return date.fromisoformat(value)
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return annotation(value)
        if isinstance(annotation, type) and is_dataclass(annotation) and isinstance(value, dict):
            return self.deserialize_model(annotation.__name__, value)
        return value
